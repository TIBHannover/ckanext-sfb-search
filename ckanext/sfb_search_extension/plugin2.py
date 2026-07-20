import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import Package
from ckanext.sfb_search_extension.libs.column_search_helpers import ColumnSearchHelper
from ckanext.sfb_search_extension.libs.sample_search_helpers import SampleSearchHelper
from ckanext.sfb_search_extension.libs.publication_search import PublicationSearchHelper
from ckanext.sfb_search_extension.libs.resource_metadata_search_helper import ResourceMetadataSearchHelper
from ckanext.sfb_search_extension.libs.commons import CommonHelper
from ckanext.sfb_search_extension.models.data_resource_column_index import DataResourceColumnIndex
from flask import Blueprint


log = logging.getLogger(__name__)


class SfbSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IBlueprint)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('public/statics', 'ckanext-sfb-search')
    


    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)        
        blueprint.add_url_rule(
            u'/sfb_search/indexer',
            u'indexer',
            CommonHelper.indexer,
            methods=['GET']
            )   
        

        return blueprint 
    

    # IPackageController

    def after_dataset_search(self, search_results, search_params):
        try:        
            search_mode = ''
            target_metadata = ""
            search_types = ['column', 'sample', 'material_combination', 'surface_preparation', 'atmosphere', 'data_type', 'analysis_method', 'publication']
            query = search_params.get('q') or ''
            if query.split(':')[0].lower() not in search_types:
                return search_results
            
            elif len(query.lower().split('column:')) > 1:            
                search_phrase = query.lower().split('column:')[1].strip().lower()
                search_mode = 'column'
            
            elif len(query.lower().split('publication:')) > 1:            
                search_phrase = query.lower().split('publication:')[1].strip().lower()
                search_mode = 'publication'
            
            elif len(query.lower().split('sample:')) > 1:
                search_phrase = query.lower().split('sample:')[1].strip().lower()
                search_mode = 'sample'
            
            elif len(query.lower().split('material_combination:')) > 1:
                search_phrase = query.lower().split('material_combination:')[1].strip().lower()
                target_metadata = 'material_combination'
                search_mode = "resource_metadata"
            
            elif len(query.lower().split('surface_preparation:')) > 1:
                search_phrase = query.lower().split('surface_preparation:')[1].strip().lower()
                target_metadata = 'surface_preparation'
                search_mode = "resource_metadata"
            
            elif len(query.lower().split('atmosphere:')) > 1:
                search_phrase = query.lower().split('atmosphere:')[1].strip().lower()
                target_metadata = 'atmosphere'
                search_mode = "resource_metadata"
            
            elif len(query.lower().split('data_type:')) > 1:
                search_phrase = query.lower().split('data_type:')[1].strip().lower()
                target_metadata = 'data_type'
                search_mode = "resource_metadata"
            
            elif len(query.lower().split('analysis_method:')) > 1:
                search_phrase = query.lower().split('analysis_method:')[1].strip().lower()
                target_metadata = 'analysis_method'
                search_mode = "resource_metadata"

            else:            
                return search_results

            # empty the search result to remove unrelated search result by ckan.
            search_results['results'] = []
            search_results['search_facets']['organization']['items'] = []
            search_results['search_facets']['tags']['items'] = []
            search_results['search_facets']['groups']['items'] = []
            if(search_results['search_facets'].get('sfb_dataset_type')):
                search_results['search_facets']['sfb_dataset_type']['items'] = []
            search_results['count'] = 0
            search_results['detected_resources_ids'] = []
            fq = search_params.get('fq', '')
            search_filters = fq[0] if isinstance(fq, (list, tuple)) else fq
            all_datasets = Package.search_by_name('')

            if search_mode.lower() == 'column':            
                search_results = ColumnSearchHelper.run(
                    search_filters=search_filters, 
                    search_phrase=search_phrase, 
                    search_results=search_results
                    )
                
                return search_results
            
            elif search_mode.lower() == 'sample' and CommonHelper.check_plugin_enabled("sample_link"):            
                search_results = SampleSearchHelper.run(datasets=all_datasets, 
                    search_filters=search_filters, 
                    search_phrase=search_phrase, 
                    search_results=search_results
                    )
                return search_results
            
            elif search_mode.lower() == 'resource_metadata':
                search_results = ResourceMetadataSearchHelper.run(
                    datasets=all_datasets,
                    target_metadata_name=target_metadata,
                    search_filters=search_filters, 
                    search_phrase=search_phrase, 
                    search_results=search_results
                )
                return search_results
            
            elif search_mode.lower() == 'publication':
                search_results = PublicationSearchHelper.run(
                    datasets=all_datasets,                
                    search_filters=search_filters, 
                    search_phrase=search_phrase, 
                    search_results=search_results
                )
                return search_results
            
            else:
                return search_results
        except (KeyError, TypeError, AttributeError) as exc:
            log.warning("Could not process SFB search query %r: %s", search_params.get('q'), exc)
            return search_results
        except Exception:
            log.exception("Unexpected SFB search failure for query %r", search_params.get('q'))
            return search_results



    def after_dataset_delete(self, context, pkg_dict):
        try:
            resource_ids = [resource['id'] for resource in pkg_dict.get('resources', []) if resource.get('id')]
            if resource_ids:
                for resource_id in resource_ids:
                    DataResourceColumnIndex.delete_by_resource(resource_id)
            else:
                DataResourceColumnIndex.delete_by_package(pkg_dict.get('id'))
            return pkg_dict
        except (KeyError, TypeError) as exc:
            log.warning("Could not remove column indexes for dataset %s: %s", pkg_dict.get('id'), exc)
            return pkg_dict
        except Exception:
            log.exception("Unexpected index cleanup failure for dataset %s", pkg_dict.get('id'))
            return pkg_dict
        

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_dataset_create(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_update(self, context, pkg_dict):
        return pkg_dict

    def after_dataset_show(self, context, pkg_dict):
        return pkg_dict

    def before_dataset_search(self, search_params):
        return search_params

    def before_dataset_index(self, pkg_dict):
        return pkg_dict

    def before_dataset_view(self, pkg_dict):
        return pkg_dict
    


     # IResourceController

    def after_resource_create(self, context, resource):
        try:
            self._index_resource_columns(resource)
            return resource
        except (KeyError, TypeError, AttributeError) as exc:
            log.warning("Could not index columns for resource %s: %s", resource.get('id'), exc)
            return resource
        except Exception:
            log.exception("Unexpected column indexing failure for resource %s", resource.get('id'))
            return resource

    def _index_resource_columns(self, resource):
        if resource.get('url_type') != 'upload':
            return

        columns = []
        if CommonHelper.is_csv(resource):
            columns, _fit_for_autotag = CommonHelper.get_csv_columns(resource['id'])
        elif CommonHelper.is_xlsx(resource):
            xls_dataframes_columns = CommonHelper.get_xlsx_columns(resource['id'])
            for _sheet, columns_object in xls_dataframes_columns.items():
                columns.extend(columns_object[0])
        else:
            return

        if columns:
            CommonHelper.add_index(resource['id'], ','.join(str(col) for col in columns) + ',')


    def before_resource_delete(self, context, resource, resources):
        try:
            DataResourceColumnIndex.delete_by_resource(resource.get('id'))
            return resources    
        except (KeyError, TypeError) as exc:
            log.warning("Could not remove column indexes for resource %s: %s", resource.get('id'), exc)
            return resources
        except Exception:
            log.exception("Unexpected index cleanup failure for resource %s", resource.get('id'))
            return resources
        

    
    def after_resource_delete(self, context, resources):        
        return resources

    def before_resource_create(self, context, resource):
        return resource

    def before_resource_update(self, context, current, resource):
        return resource
    
    def after_resource_update(self, context, resource):
        return resource    
    
    def before_resource_show(self, resource_dict):
        return resource_dict
