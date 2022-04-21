from numpy import append
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.sfb_search_extension.libs.column_search_helpers import ColumnSearchHelper



class ResourceColumnSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
    

    # IPackageController

    def after_search(self, search_results, search_params):
        if 'column:' not in search_params['q']:
            # print(search_results['facets'])
            return search_results
        
        elif len(search_params['q'].split('column:')) > 1:
            search_phrase = search_params['q'].split('column:')[1].strip().lower()
        else:
            search_phrase = search_params['q'].strip().lower()

        # empty the search result to remove unrelated search result by ckan.
        search_results['results'] = [] 
        search_results['count'] = 0
        search_results['detected_resources_ids'] = []
        search_filters = search_params['fq'][0]
        all_datasets = Package.search_by_name('')
        search_results = ColumnSearchHelper.run(datasets=all_datasets, 
            search_filters=search_filters, 
            search_phrase=search_phrase, 
            search_results=search_results
            )
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