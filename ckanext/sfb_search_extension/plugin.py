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
        for res in pkg_dict['resources']:
            if res['url_type'] == 'upload':
                try:
                    dataframe_columns = []
                    xls_dataframes_columns = {}
                    if Helper.is_csv(res):                        
                        dataframe_columns = Helper.get_csv_columns(res['id'])
                        for col in dataframe_columns:
                            if col not in pkg_dict['tags']:
                                pkg_dict['tags'].append(col)
                        
                    elif Helper.is_xlsx(res):
                        xls_dataframes_columns = Helper.get_xlsx_columns(res['id'])
                        for sheet, columns in xls_dataframes_columns.items():
                            for col in columns:
                                if col not in pkg_dict['tags']:
                                    pkg_dict['tags'].append(col)
                    else:
                        continue
                
                except:
                    # continue
                    raise
  
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