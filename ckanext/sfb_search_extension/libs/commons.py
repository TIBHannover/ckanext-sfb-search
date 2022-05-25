# encoding: utf-8

import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd
from ckan.model import Package
import ckan.model as model
import ckan.logic as logic
from ckanext.sfb_search_extension.models.data_resource_column_index import DataResourceColumnIndex


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'
STANDARD_HEADERS = ['X-Kategorie', 'Y-Kategorie', 'Datentyp', 'Werkstoff-1', 'Werkstoff-2', 'Atmosphaere', 'Vorbehandlung']

class CommonHelper():



    @staticmethod
    def indexer():
        '''
            Index the already added csv/xlsx data resource for column search.
        '''

        context = {'model': model, 'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        try:
            logic.check_access('sysadmin', context, {})
        except logic.NotAuthorized:
            toolkit.abort(403, 'Not allowed')

        all_datasets = Package.search_by_name('')
        for package in all_datasets:
            if package.state != 'active':
                continue
            
            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            for resource in dataset['resources']:
                 if resource['url_type'] == 'upload':
                    if CommonHelper.is_csv(resource):
                        dataframe_columns, fit_for_autotag = CommonHelper.get_csv_columns(resource['id'])
                        columns_names = ""
                        for col in dataframe_columns:
                            columns_names += (col + ",")
                        if len(dataframe_columns) != 0:
                            column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                            column_indexer.save()
                    
                    elif CommonHelper.is_xlsx(resource):
                        xls_dataframes_columns = CommonHelper.get_xlsx_columns(resource['id'])
                        if len(xls_dataframes_columns) == 0:
                            continue

                        columns_names = ""
                        for sheet, columns_object in xls_dataframes_columns.items():
                            for col in columns_object[0]:  
                                columns_names += (col + ",")
                        
                        column_indexer = DataResourceColumnIndex(resource_id=resource['id'], columns_names=columns_names)
                        column_indexer.save()
        
        return "Indexed"



    @staticmethod
    def is_possible_to_automate(resource_df):
        df_columns = resource_df.columns
        if len(df_columns) != len(STANDARD_HEADERS):
            return False
        for header in df_columns:
            if header.strip() not in STANDARD_HEADERS:
                return False
        return True
    


    @staticmethod
    def is_csv(resource):
        '''
            Check if a data resource in csv or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
        '''

        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource['format']
            name = resource['name']
        else:
            format = resource.format
            name = resource.name
        
        return (format in ['CSV']) or ('.csv' in name)
    


    @staticmethod
    def get_csv_columns(resource_id):
        '''
            Read a csv file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        try:
            df = clevercsv.read_dataframe(file_path)
            df = df.fillna(0)        
            if not CommonHelper.is_possible_to_automate(df):
                return [list(df.columns), False]
            else:
                # skip the first row to get the actual columns names
                return [list(df.iloc[0]), True]
        except:
            return[[], False]
    



    @staticmethod
    def is_xlsx(resource):
        '''
            Check if a data resource in xlsx or not.

            Args:
                - resource: the data resource object.
            
            Returns:
                - Boolean        
        '''

        format = ''
        name = ''
        if isinstance(resource, dict):
            format = resource['format']
            name = resource['name']
        else:
            format = resource.format
            name = resource.name
        
        return (format in ['XLSX']) or ('.xlsx' in name)



    @staticmethod
    def get_xlsx_columns(resource_id):
        '''
            Read a xlsx file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        result_df = {}
        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        try:
            data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        except:
            return {}

        for sheet, data_f in data_sheets.items():
            temp_df = data_f.dropna(how='all').dropna(how='all', axis=1)
            if len(temp_df) > 0:
                headers = temp_df.iloc[0]
                final_data_df  = pd.DataFrame(temp_df.values[1:], columns=headers)
                if not CommonHelper.is_possible_to_automate(final_data_df):
                    result_df[sheet] = [final_data_df, False]
                else:
                    result_df[sheet] = [list(final_data_df.iloc[0]), True]

        return result_df



    def check_plugin_enabled(plugin_name):
        plugins = toolkit.config.get("ckan.plugins")
        if plugin_name in plugins:
            return True
        return False
    


    def check_access_package(package_id):
        context = {'user': toolkit.g.user, 'auth_user_obj': toolkit.g.userobj}
        data_dict = {'id':package_id}
        try:
            toolkit.check_access('package_show', context, data_dict)
            return True

        except toolkit.NotAuthorized:
            return False
