# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.commons import CommonHelper
from ckanext.sfb_search_extension.models.data_resource_column_index import DataResourceColumnIndex



class ColumnSearchHelper():

    @staticmethod
    def run(search_phrase, search_filters, search_results):
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

        column_indexer_model = DataResourceColumnIndex()
        all_indexes = column_indexer_model.get_all()
        already_included_datasets = []  
        for record in all_indexes:
            resource_id = record.resource_id
            resource_index_value = record.columns_names
            context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
            resource = ""
            dataset = ""        
            if search_phrase.lower() in resource_index_value.lower():
                try:
                    toolkit.check_access('resource_show', context, {'id':resource_id})
                    resource = toolkit.get_action('resource_show')({}, {'id': resource_id})
                except toolkit.NotAuthorized:
                    continue

                try:
                    toolkit.check_access('package_show', context, {'name_or_id': resource['package_id']})
                    dataset = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
                except toolkit.NotAuthorized:
                    continue

                if dataset['state'] != "active":
                    continue

                # only consider dataset in an organization. If search triggers from an organization page.
                if 'owner_org' in search_filters:
                    owner_org_id = search_filters.split('owner_org:')[1]
                    if ' ' in owner_org_id:
                        owner_org_id = owner_org_id.split(' ')[0]                    
                    if '"' + dataset['owner_org'] + '"' != owner_org_id:
                        continue
                

                # only consider dataset in a group. If search triggers from a group page.
                if 'groups' in search_filters:
                    this_dataset_groups = dataset['groups']
                    target_group_title = search_filters.split('groups:')[1]
                    if ' ' in target_group_title:
                        target_group_title = target_group_title.split(' ')[0]
                    is_part_of_group = False
                    for g in this_dataset_groups:
                        if '"' + g['title'] + '"' != target_group_title:
                            is_part_of_group = True
                            break
                    if not is_part_of_group:
                        continue

                
                if dataset['id'] not in already_included_datasets:                                    
                    search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                    search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                    search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                    search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                    search_results = CommonHelper.add_search_result(dataset, search_filters, search_results)
                    already_included_datasets.append(dataset['id'])
                
                search_results['detected_resources_ids'].append(resource_id)
        
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']
        return search_results
    
    

   
