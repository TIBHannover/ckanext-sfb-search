# encoding: utf-8

from struct import pack

from sqlalchemy import false, true
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.commons import CommonHelper
from ckanext.sfb_search_extension.libs.column_search_helpers import ColumnSearchHelper
if CommonHelper.check_plugin_enabled("sample_link"):
    from ckanext.semantic_media_wiki.libs.sample_link import SampleLinkHelper


class SampleSearchHelper():


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
            if package.state != 'active' or not CommonHelper.check_access_package(package.id):
                continue
            
            if 'owner_org' in search_filters:
                owner_org_id = search_filters.split('owner_org:')[1]
                if ' ' in owner_org_id:
                    owner_org_id = owner_org_id.split(' ')[0]                    
                if '"' + package.owner_org + '"' != owner_org_id:
                    continue
            
            if 'groups' in search_filters:
                this_dataset_groups = package.get_groups()
                target_group_title = search_filters.split('groups:')[1]
                if ' ' in target_group_title:
                    target_group_title = target_group_title.split(' ')[0]
                is_part_of_group = false
                for g in this_dataset_groups:
                    if '"' + g.title + '"' != target_group_title:
                        is_part_of_group = true
                        break
                if not is_part_of_group:
                    continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            detected = False

            for res in dataset['resources']:
                samples = list(SampleLinkHelper.get_sample_link(res['id']).keys())
                for name in samples:
                    if search_phrase in name.lower():
                        if not detected:
                            search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                            search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                            search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                            search_results['search_facets'] = ColumnSearchHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                            search_results = ColumnSearchHelper.add_search_result(dataset, search_filters, search_results)                            
                        detected = True
                        search_results['detected_resources_ids'].append(res['id'])
                        break
        
        toolkit.g.detected_resources_ids = search_results['detected_resources_ids']
        return search_results

