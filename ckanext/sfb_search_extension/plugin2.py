import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.sfb_search_extension.libs.column_search_helpers import ColumnSearchHelper
from ckanext.sfb_search_extension.libs.sample_search_helpers import SampleSearchHelper
from ckanext.sfb_search_extension.libs.commons import CommonHelper



class SfbSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
    

    # IPackageController

    def after_search(self, search_results, search_params):
        search_mode = ''
        if 'column:' not in search_params['q'] and 'sample:' not in search_params['q']:           
            return search_results
        
        elif len(search_params['q'].split('column:')) > 1:
            search_phrase = search_params['q'].split('column:')[1].strip().lower()
            search_mode = 'column'
        
        elif len(search_params['q'].split('sample:')) > 1:
            search_phrase = search_params['q'].split('sample:')[1].strip().lower()
            search_mode = 'sample'

        else:
            return search_results

        # empty the search result to remove unrelated search result by ckan.
        search_results['results'] = [] 
        search_results['count'] = 0
        search_results['detected_resources_ids'] = []
        search_filters = search_params['fq'][0]
        all_datasets = Package.search_by_name('')

        if search_mode == 'column':
            search_results = ColumnSearchHelper.run(datasets=all_datasets, 
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
                )
            
            return search_results
        
        elif search_mode == 'sample' and CommonHelper.check_plugin_enabled("sample_link"):
            search_results = SampleSearchHelper.run(datasets=all_datasets, 
                search_filters=search_filters, 
                search_phrase=search_phrase, 
                search_results=search_results
                )
            return search_results
        
        else:
            return search_results



    def after_delete(self, context, pkg_dict):
        return pkg_dict

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_create(self, context, pkg_dict):
        return pkg_dict

    def after_update(self, context, pkg_dict):
        return pkg_dict

    def after_show(self, context, pkg_dict):
        return pkg_dict

    def before_search(self, search_params):
        return search_params

    def before_index(self, pkg_dict):
        return pkg_dict

    def before_view(self, pkg_dict):
        return pkg_dict