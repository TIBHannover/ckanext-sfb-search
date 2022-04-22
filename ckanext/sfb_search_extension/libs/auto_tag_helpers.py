# encoding: utf-8

# import ckan.plugins.toolkit as toolkit
# import clevercsv
# import pandas as pd


RESOURCE_DIR = toolkit.config['ckan.storage_path'] + '/resources/'
STANDARD_HEADERS = ['X-Kategorie', 'Y-Kategorie', 'Datentyp', 'Werkstoff-1', 'Werkstoff-2', 'Atmosphaere', 'Vorbehandlung']


class AutoTagHelper():

    def index():
        return None