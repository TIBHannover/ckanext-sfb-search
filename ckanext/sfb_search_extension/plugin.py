import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.helpers import Helper


class AutoTagPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        

    
    # IPackageController


    def after_create(self, context, pkg_dict):
        if resource['url_type'] == 'upload':
            dataframe_columns = []
            xls_dataframes_columns = {}
            if Helper.is_csv(resource):
                try:
                    dataframe_columns = Helper.get_csv_columns(resource['id'])
                except:
                    return pkg_dict

            elif Helper.is_xlsx(resource):
                try:
                    xls_dataframes_columns = Helper.get_xlsx_columns(resource['id'])
                except:
                    # return pkg_dict
                    raise

            else:
                return pkg_dict
            
            if len(dataframe_columns) != 0:
                # resource is csv
                




                return pkg_dict
            
            if len(xls_dataframes_columns.keys()) != 0:
                # resource is xlsx
                return pkg_dict
  
        return pkg_dict


    

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity
    
    def edit(self, entity):
        return entity
    def delete(self, entity):
        return entity
    
    def after_update(self, context, pkg_dict):
        return pkg_dict
    
    def after_delete(self, context, pkg_dict):
        return pkg_dict
    
    def before_show(self, resource_dict):
        return resource_dict

    def after_show(self, pkg_dict):
        return pkg_dict
    
    def before_search(self, search_params):
        return search_params
    
    def after_search(self, search_results, search_params):
        return search_results
    
    def before_index(self, pkg_dict):
        return pkg_dict
    
    def before_view(self, pkg_dict):
        return pkg_dict