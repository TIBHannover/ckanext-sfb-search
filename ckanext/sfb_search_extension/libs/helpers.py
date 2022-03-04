# encoding: utf-8

from os import stat
import ckan.plugins.toolkit as toolkit
import clevercsv
import pandas as pd


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'
STANDARD_HEADERS = ['X-Kategorie', 'Y-Kategorie', 'Datentyp', 'Werkstoff-1', 'Werkstoff-2', 'Atmosphaere', 'Vorbehandlung']


class Helper():

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
    def get_csv_columns(resource_id):
        '''
            Read a csv file as pandas dataframe and return the columns name.

            Args:
                - resource_id: the data resource id in ckan
            
            Returns:
                - a list of columns names
        '''

        file_path = RESOURCE_DIR + resource_id[0:3] + '/' + resource_id[3:6] + '/' + resource_id[6:]
        df = clevercsv.read_dataframe(file_path)
        df = df.fillna(0)        
        if not Helper.is_possible_to_automate(df):
            return list(df.columns)
        else:
            # skip the first row to get the actual columns names
            return list(df.iloc[0])



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
        data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        for sheet, data_f in data_sheets.items():
            temp_df = data_f.dropna(how='all').dropna(how='all', axis=1)
            if len(temp_df) > 0:
                headers = temp_df.iloc[0]
                final_data_df  = pd.DataFrame(temp_df.values[1:], columns=headers)
                if not Helper.is_possible_to_automate(final_data_df):
                    result_df[sheet] = final_data_df
                else:
                    result_df[sheet] = list(final_data_df.iloc[0])                

        return result_df
    

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
