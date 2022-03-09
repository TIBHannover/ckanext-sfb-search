from numpy import append
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.helpers import Helper
from ckan.model import Package


class ResourceColumnSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
    

    # IPackageController

    def after_search(self, search_results, search_params):
        if 'column:' not in search_params['q']:
            # print(search_results['search_facets'])
            return search_results
        
        elif len(search_params['q'].split('column:')) > 1:
            search_phrase = search_params['q'].split('column:')[1].strip().lower()
        else:
            search_phrase = search_params['q'].strip().lower()

        # all_datasets = toolkit.get_action('package_list')({}, {'include_private': 'True'})

        all_datasets = Package.search_by_name('')
        for package in all_datasets:
            if package.state != 'active':
                continue

            dataset = toolkit.get_action('package_show')({}, {'name_or_id': package.name})
            for res in dataset['resources']:
                if Helper.is_csv(res):                    
                    # resource is csv
                    try:
                        csv_columns = Helper.get_csv_columns(res['id']) 
                    except:
                        csv_columns = []
                                       
                    for col_name in csv_columns:
                        if search_phrase in col_name.strip().lower():                            
                            search_results['results'].append(dataset)
                            search_results['count'] = int(search_results['count']) + 1 
                            search_results['search_facets'] = Helper.update_search_facet(search_results['search_facets'], dataset, 'organization')
                            break
                
                elif Helper.is_xlsx(res):
                    # resource is excel sheet
                    try:
                        xlsx_sheet = Helper.get_xlsx_columns(res['is'])
                    except:
                        xlsx_sheet = {}
                    
                    for sheet, columns in xlsx_sheet.items():
                        for col_name in columns:
                            if search_phrase in col_name.strip().lower():
                                search_results['results'].append(dataset)
                                break
                
                else:
                    continue
       
        print(search_results)
        return search_results



    def after_delete(self, context, pkg_dict):
        return pkg_dict

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_create(self, context, pkg_dict):
        return pkg_dict

    def after_update(self, context, pkg_dict):
        return pkg_dict

    def after_show(self, context, pkg_dict):
        return pkg_dict

    def before_search(self, search_params):
        return search_params

    def before_index(self, pkg_dict):
        return pkg_dict

    def before_view(self, pkg_dict):
        return pkg_dict