from numpy import append
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
        dataset = toolkit.get_action('package_show')({}, {'name_or_id': resource['package_id']})
        if resource['url_type'] == 'upload':
            try:
                dataframe_columns = []
                xls_dataframes_columns = {}
                tags = []
                if Helper.is_csv(resource):
                    dataframe_columns = Helper.get_csv_columns(resource['id'])
                    for col in dataframe_columns:
                        if 'tags' in dataset.keys() and col not in dataset['tags']:
                            tag_dict = {'name': col}
                            dataset['tags'].append(tag_dict)
                    
                    toolkit.get_action('package_update')({}, dataset)
                    return resource
                    
                elif Helper.is_xlsx(resource):
                    xls_dataframes_columns = Helper.get_xlsx_columns(resource['id'])
                    for sheet, columns in xls_dataframes_columns.items():
                        for col in columns:
                            if 'tags' in dataset.keys() and col not in dataset['tags']:
                                tag_dict = {'name': col}
                                dataset['tags'].append(tag_dict)

                    toolkit.get_action('package_update')({}, dataset)
                    return resource
                        
                else:
                    return resource
            
            except:
                return resource
                # raise
  
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




    
 