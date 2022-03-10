# encoding: utf-8

from os import stat
import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'
STANDARD_HEADERS = ['X-Kategorie', 'Y-Kategorie', 'Datentyp', 'Werkstoff-1', 'Werkstoff-2', 'Atmosphaere', 'Vorbehandlung']


class Helper():

    @staticmethod
    def is_possible_to_automate(resource_df):
        df_columns = resource_df.columns
        if len(df_columns) != len(STANDARD_HEADERS):
            return False
        for header in df_columns:
            if header.strip() not in STANDARD_HEADERS:
                return False
        return True

   
    @staticmethod
    def get_csv_columns(resource_id):
        '''
            Read a csv file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        df = clevercsv.read_dataframe(file_path)
        df = df.fillna(0)        
        if not Helper.is_possible_to_automate(df):
            return list(df.columns)
        else:
            # skip the first row to get the actual columns names
            return list(df.iloc[0])



    @staticmethod
    def get_xlsx_columns(resource_id):
        '''
            Read a xlsx file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        result_df = {}
        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        for sheet, data_f in data_sheets.items():
            temp_df = data_f.dropna(how='all').dropna(how='all', axis=1)
            if len(temp_df) > 0:
                headers = temp_df.iloc[0]
                final_data_df  = pd.DataFrame(temp_df.values[1:], columns=headers)
                if not Helper.is_possible_to_automate(final_data_df):
                    result_df[sheet] = final_data_df
                else:
                    result_df[sheet] = list(final_data_df.iloc[0])                

        return result_df
    

    @staticmethod
    def is_csv(resource):
        '''
            Check if a data resource in csv or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
        '''
        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource['format']
            name = resource['name']
        else:
            format = resource.format
            name = resource.name
        
        return (format in ['CSV']) or ('.csv' in name)

    
    @staticmethod
    def is_xlsx(resource):
        '''
            Check if a data resource in xlsx or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
        '''

        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource['format']
            name = resource['name']
        else:
            format = resource.format
            name = resource.name
        
        return (format in ['XLSX']) or ('.xlsx' in name)
    

    @staticmethod
    def add_search_result(dataset, search_filters_string, search_results):
        '''
            Add a dataset to search result based on the search filter.

            Args:
                - dataset: target dataset
                - search_filters_string: ckan facet filter string. exist in search_params['fq]
                - search_result: search result array
        '''

        org_filter = Helper.apply_filters_organization(dataset, search_filters_string)
        tag_filter = Helper.apply_filters_tags(dataset, search_filters_string)
        group_filter = Helper.apply_filters_groups(dataset, search_filters_string)
        type_filter = Helper.apply_filters_type(dataset, search_filters_string)

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


