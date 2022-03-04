import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.helpers import Helper


class AutoTagPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        

    
    # IResourceController

    def after_create(self, context, resource):
        if resource['url_type'] == 'upload':
            dataframe_columns = []
            xls_dataframes_columns = {}
            if Helper.is_csv(resource):
                try:
                    dataframe_columns = Helper.get_csv_columns(resource['id'])
                except:
                    return resource

            elif Helper.is_xlsx(resource):
                try:
                    xls_dataframes_columns = Helper.get_xlsx_columns(resource['id'])
                except:
                    # return resource
                    raise

            else:
                return resource
            
            if len(dataframe_columns) != 0:
                # resource is csv
                




                return resource
            
            if len(xls_dataframes_columns.keys()) != 0:
                # resource is xlsx
                return resource
  
        return resource


    
    def before_create(self, context, resource):
        return resource

    def before_update(self, context, current, resource):
        return resource
    
    def after_update(self, context, resource):
        return resource
    
    def before_delete(self, context, resource, resources):
        return resources
    
    def after_delete(self, context, resources):
        return resources
    
    def before_show(self, resource_dict):
        return resource_dict