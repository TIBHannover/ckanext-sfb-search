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
            try:
                dataframe_columns = []
                xls_dataframes_columns = {}
                if Helper.is_csv(res):                        
                    dataframe_columns = Helper.get_csv_columns(resource['id'])
                    for col in dataframe_columns:
                        if col not in pkg_dict['tags']:
                            pkg_dict['tags'].append(col)
                    
                elif Helper.is_xlsx(res):
                    xls_dataframes_columns = Helper.get_xlsx_columns(resource['id'])
                    for sheet, columns in xls_dataframes_columns.items():
                        for col in columns:
                            if col not in pkg_dict['tags']:
                                pkg_dict['tags'].append(col)
                else:
                    continue
            
            except:
                # continue
                raise
  
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




    
 