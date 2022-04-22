# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.commons import CommonHelper



class ColumnSearchHelper():

    @staticmethod
    def run(datasets, search_phrase, search_filters, search_results):
        '''
            Run the search for column in data resources.

            Args:
                - datasets: the target datasets to search in. 
                - search_phrase: the search input
                - search_filters: the ckan search facets dictionary (search_params['fq'][0])
                - search_results: the ckan search results dictionary.
            
            Return:
                - search_results dictionary
        '''

        for package in datasets:
            if package.state != 'active':
                continue
            context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
            data_dict = {'id':package.id}
            try:
                toolkit.check_access('package_show', context, data_dict)
            except toolkit.NotAuthorized:
                continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            detected = False
            for res in dataset['resources']:
                if CommonHelper.is_csv(res):                    
                    # resource is csv
                    try:
                        csv_columns = CommonHelper.get_csv_columns(res['id']) 
                    except:
                        csv_columns = []
                    
                    for col_name in csv_columns:
                        try:
                            col_name = str(col_name)
                        except:
                            continue
                    
                        if search_phrase in col_name.strip().lower():                            
                            if not detected:
                                search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                                search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                                search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                                search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                                search_results = ColumnSearchHelper.add_search_result(dataset, search_filters, search_results)                            
                            detected = True
                            search_results['detected_resources_ids'].append(res['id'])
                            break
                
                elif CommonHelper.is_xlsx(res):
                    # resource is excel sheet
                    try:
                        xlsx_sheet = CommonHelper.get_xlsx_columns(res['id'])
                    except:
                        xlsx_sheet = {}
                                            
                    for sheet, columns in xlsx_sheet.items():
                        for col_name in columns:
                            try:
                                col_name = str(col_name)
                            except:
                                continue

                            if search_phrase in col_name.strip().lower():                                
                                if not detected:
                                    search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                                    search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                                    search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                                    search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                                    search_results = ColumnSearchHelper.add_search_result(dataset, search_filters, search_results)
                                search_results['detected_resources_ids'].append(res['id']) 
                                detected = True
                                break
                        
                        if detected:
                            break
                
                else:
                    continue
        
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']
        return search_results
    
    

    @staticmethod
    def add_search_result(dataset, search_filters_string, search_results):
        '''
            Add a dataset to search result based on the search filter.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq]
                - search_result: search result array
        '''

        org_filter = ColumnSearchHelper.apply_filters_organization(dataset, search_filters_string)
        tag_filter = ColumnSearchHelper.apply_filters_tags(dataset, search_filters_string)
        group_filter = ColumnSearchHelper.apply_filters_groups(dataset, search_filters_string)
        type_filter = ColumnSearchHelper.apply_filters_type(dataset, search_filters_string)

        if org_filter and type_filter and tag_filter and group_filter:
            search_results['results'].append(dataset)
            search_results['count'] = int(search_results['count']) + 1 
    
        return search_results



    @staticmethod
    def apply_filters_organization(dataset, search_filters_string):
        '''
            Apply organization facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
        '''

        if len(search_filters_string.split('organization:')) == 2:
            org_name =  search_filters_string.split('organization:"')[1].split('"')[0].strip()
            if dataset['organization']['name']  != org_name:
                return False
        
        elif 'organization:' in search_filters_string:            
                 return False
        
        else:
            return True
        
        return True



    @staticmethod
    def apply_filters_type(dataset, search_filters_string):
        '''
            Apply dataset type facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
        '''
       
        if 'sfb_dataset_type' in dataset.keys() and len(search_filters_string.split('sfb_dataset_type:')) == 2:
            dataset_type = search_filters_string.split('sfb_dataset_type:"')[1].split('"')[0].strip()
            if  dataset['sfb_dataset_type']  != dataset_type:
               return False
        
        elif 'sfb_dataset_type:' in search_filters_string:
            return False
        
        else:
            return True
        
        return True
    


    @staticmethod
    def apply_filters_tags(dataset, search_filters_string):
        '''
            Apply tags facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
        '''

        if 'tags:' not in search_filters_string:
            return True
        
        for tag in dataset['tags']:
            tag_query = 'tags:"' + tag['name'] + '"'
            if tag_query in search_filters_string:
                search_filters_string = search_filters_string.replace(tag_query, ' ')
        
        if 'tags:' in search_filters_string:
            return False

        return True 
    


    @staticmethod
    def apply_filters_tags(dataset, search_filters_string):
        '''
            Apply tags facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
        '''

        if 'tags:' not in search_filters_string:
            return True
        
        for tag in dataset['tags']:
            tag_query = 'tags:"' + tag['name'] + '"'
            if tag_query in search_filters_string:
                search_filters_string = search_filters_string.replace(tag_query, ' ')
        
        if 'tags:' in search_filters_string:
            return False

        return True 
    


    @staticmethod
    def apply_filters_groups(dataset, search_filters_string):
        '''
            Apply groups facet filters for a dataset.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq']

            Return:
                - Boolean
        '''

        if 'groups:' not in search_filters_string:
            return True
        
        for group in dataset['groups']:
            group_query = 'groups:"' + group['name'] + '"'
            if group_query in search_filters_string:
                search_filters_string = search_filters_string.replace(group_query, ' ')
        
        if 'groups:' in search_filters_string:
            return False

        return True 



    @staticmethod
    def update_search_facet(search_facet_object, dataset, facet_name):
        '''
            Update the search facet based on the search results.
        '''

        if facet_name == 'organization':
            place = 0
            exist = False
            for item in search_facet_object[facet_name]['items']:
                if dataset[facet_name]['name'] in item.values():
                    search_facet_object[facet_name]['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist:
                search_facet_object[facet_name]['items'].append({
                    'name': dataset['organization']['name'], 
                    'display_name': dataset['organization']['title'], 
                    'count': 1
                    }) 
        

        elif facet_name == 'tags':
            for tag in dataset['tags']:
                place = 0
                exist = False
                for item in search_facet_object[facet_name]['items']:
                    if tag['name'] in item.values():
                        search_facet_object[facet_name]['items'][place]['count'] += 1
                        exist = True
                        break
                    place += 1
                
                if not exist:
                    search_facet_object[facet_name]['items'].append({
                        'name': tag['name'], 
                        'display_name': tag['display_name'], 
                        'count': 1
                        }) 

        elif facet_name == 'groups':
            for group in dataset['groups']:
                place = 0
                exist = False
                for item in search_facet_object[facet_name]['items']:
                    if group['name'] in item.values():
                        search_facet_object[facet_name]['items'][place]['count'] += 1
                        exist = True
                        break
                    place += 1
                
                if not exist:
                    search_facet_object[facet_name]['items'].append({
                        'name': group['name'], 
                        'display_name': group['display_name'], 
                        'count': 1
                        }) 
        
        elif facet_name == 'sfb_dataset_type' and 'sfb_dataset_type' in dataset.keys():
            place = 0
            exist = False
            for item in search_facet_object[facet_name]['items']:
                if dataset[facet_name] in item.values():
                    search_facet_object[facet_name]['items'][place]['count'] += 1
                    exist = True
                    break
                place += 1
            
            if not exist and dataset['sfb_dataset_type'] not in ['', '0']:
                search_facet_object[facet_name]['items'].append({
                    'name': dataset['sfb_dataset_type'], 
                    'display_name': dataset['sfb_dataset_type'], 
                    'count': 1
                    }) 



        return search_facet_object


