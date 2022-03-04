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
            dataframe = []
            xls_dataframes = {}
            if Helper.is_csv(resource):
                try:
                    dataframe = Helper.csv_to_dataframe(resource['id'])
                except:
                    return resource

            elif Helper.is_xlsx(resource):
                try:
                    xls_dataframes = Helper.xlsx_to_dataframe(resource['id'])
                except:
                    # return resource
                    raise

            else:
                return resource
            
            if len(dataframe) != 0:
                # resource is csv
                if not Helper.is_possible_to_automate(dataframe):
                    return resource
                
                resource['material_combination'] = Helper.get_metadata_value(dataframe, 'Werkstoff-1') + ', ' + Helper.get_metadata_value(dataframe, 'Werkstoff-2')
                resource['atmosphere'] = Helper.get_metadata_value(dataframe, 'Atmosphaere')
                resource['data_type'] = Helper.get_metadata_value(dataframe, 'Datentyp')
                resource['surface_preparation'] = Helper.get_metadata_value(dataframe, 'Vorbehandlung')
                resource['is_automated_processed'] = True
                return resource
            
            if len(xls_dataframes.keys()) != 0:
                # resource is xlsx
                for sheet, sheet_dataframe in xls_dataframes.items():
                    if not Helper.is_possible_to_automate(sheet_dataframe):
                        print(sheet_dataframe)
                        continue

                    resource['material_combination'] = Helper.get_metadata_value(sheet_dataframe, 'Werkstoff-1') + ', ' + Helper.get_metadata_value(sheet_dataframe, 'Werkstoff-2')
                    resource['atmosphere'] = Helper.get_metadata_value(sheet_dataframe, 'Atmosphaere')
                    resource['data_type'] = Helper.get_metadata_value(sheet_dataframe, 'Datentyp')
                    resource['surface_preparation'] = Helper.get_metadata_value(sheet_dataframe, 'Vorbehandlung')
                    resource['is_automated_processed'] = True
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