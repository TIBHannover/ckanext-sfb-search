from numpy import append
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.helpers import Helper


class ResourceColumnSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')