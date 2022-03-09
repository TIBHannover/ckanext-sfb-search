from numpy import append
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.helpers import Helper


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
            return search_results
        
       


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