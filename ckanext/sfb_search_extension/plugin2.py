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

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def delete(self, entity):
        pass

    def after_create(self, context, pkg_dict):
        pass

    def after_update(self, context, pkg_dict):
        pass

    def after_delete(self, context, pkg_dict):
        pass

    def after_show(self, context, pkg_dict):
        pass

    def before_search(self, search_params):
        pass

    def after_search(self, search_results, search_params):
        pass

    def before_index(self, pkg_dict):
        pass

    def before_view(self, pkg_dict):
        pass 