# encoding: utf-8

import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.commons import CommonHelper
from sqlalchemy.sql.expression import false
import re
if CommonHelper.check_plugin_enabled("dataset_reference"):
    from ckanext.dataset_reference.models.package_reference_link import PackageReferenceLink



class PublicationSearchHelper():

    @staticmethod
    def run(datasets, search_phrase, search_filters, search_results):
        '''
            Run the search for dataset that are link to a publication based on the search term.

            Args:
                - datasets: the target datasets to search in. 
                - search_phrase: the search input
                - search_filters: the ckan search facets dictionary (search_params['fq'][0])
                - search_results: the ckan search results dictionary.
            
            Return:
                - search_results dictionary
        '''

        pub_model = PackageReferenceLink({})
        for package in datasets:
            if package.state != 'active' or not CommonHelper.check_access_package(package.id):
                continue
            
            # only consider dataset in an organization. If search triggers from an organization page.
            if 'owner_org' in search_filters:
                owner_org_id = search_filters.split('owner_org:')[1]
                if ' ' in owner_org_id:
                    owner_org_id = owner_org_id.split(' ')[0]                    
                if '"' + package.owner_org + '"' != owner_org_id:
                    continue
            
            # only consider dataset in a group. If search triggers from a group page.
            if 'groups' in search_filters:
                this_dataset_groups = package.get_groups()
                target_group_title = search_filters.split('groups:')[1]
                if ' ' in target_group_title:
                    target_group_title = target_group_title.split(' ')[0]
                is_part_of_group = False
                for g in this_dataset_groups:
                    if '"' + g.name + '"' == target_group_title:
                        is_part_of_group = True
                        break
                if not is_part_of_group:
                    continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            detected = False            
            linked_publications = pub_model.get_by_package(name=dataset['name'])
            if linked_publications == false:
                continue

            for pub in linked_publications:
                if not pub.citation:
                    continue            
                if re.search(search_phrase, pub.citation, re.IGNORECASE):
                    if not detected:
                        search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'sfb_dataset_type')
                        search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                        search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'tags')
                        search_results['search_facets'] = CommonHelper.update_search_facet(search_results['search_facets'], dataset, 'groups')
                        search_results = CommonHelper.add_search_result(dataset, search_filters, search_results)
                    detected = True 
        
        return search_results

    
    

   
