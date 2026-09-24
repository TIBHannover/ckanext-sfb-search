import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.sfb_search_extension.libs.commons import CommonHelper


log = logging.getLogger(__name__)


class AutoTagPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController)


    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        


    # IResourceController

    def after_resource_create(self, context, resource):
        self._auto_tag_resource(context, resource)
        return resource

    def _auto_tag_resource(self, context, resource):
        if resource.get('url_type') != 'upload':
            return

        try:
            dataset = toolkit.get_action('package_show')(context, {'id': resource['package_id']})
            columns = []
            if CommonHelper.is_csv(resource):
                columns, fit_for_autotag = CommonHelper.get_csv_columns(resource['id'])
                if not fit_for_autotag:
                    return
            elif CommonHelper.is_xlsx(resource):
                for _sheet, columns_object in CommonHelper.get_xlsx_columns(resource['id']).items():
                    if columns_object[1]:
                        columns.extend(columns_object[0])
            else:
                return

            if not columns:
                return

            existing_tags = {tag.get('name') for tag in dataset.get('tags', [])}
            for col in columns:
                tag_name = str(col).title()
                if tag_name not in existing_tags:
                    dataset.setdefault('tags', []).append({'name': tag_name})
                    existing_tags.add(tag_name)

            toolkit.get_action('package_patch')(
                context,
                {'id': dataset['id'], 'tags': dataset['tags']},
            )
        except (toolkit.ObjectNotFound, toolkit.ValidationError, toolkit.NotAuthorized, KeyError, TypeError) as exc:
            log.warning("Could not auto-tag resource %s: %s", resource.get('id'), exc)
        except Exception as exc:
            log.exception("Unexpected auto-tag failure for resource %s", resource.get('id'))

    
    def before_resource_create(self, context, resource):
        return resource

    def before_resource_update(self, context, current, resource):
        return resource
    
    def after_resource_update(self, context, resource):
        self._auto_tag_resource(context, resource)
        return resource
    
    def before_resource_delete(self, context, resource, resources):
        return resources
    
    def after_resource_delete(self, context, resources):
        return resources
    
    def before_resource_show(self, resource_dict):
        return resource_dict




    
 
