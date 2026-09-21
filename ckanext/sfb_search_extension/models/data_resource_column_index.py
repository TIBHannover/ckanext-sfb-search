# encoding: utf-8

from sqlalchemy import Column, Table, ForeignKey, orm
from sqlalchemy import types as _types
from ckan.model import meta, Resource, domain_object


__all__ = [u"DataResourceColumnIndex", u"data_resource_column_index_table"]

data_resource_column_index_table = Table(
    u"data_resource_column_index",
    meta.metadata,
    Column(u"id", _types.Integer, primary_key=True, nullable=False),
    Column(u"resource_id", _types.UnicodeText, ForeignKey(u"resource.id"), nullable=False),
    Column(u"columns_names", _types.UnicodeText, nullable=False)
)

class DataResourceColumnIndex(domain_object.DomainObject):
    def __init__(self, resource_id=None, columns_names=None):
        self.resource_id = resource_id
        self.columns_names = columns_names      



    @classmethod
    def get_all(cls, autoflush=True):
        query = meta.Session.query(cls)  
        query = query.autoflush(autoflush)
        return query.all()
     

    @classmethod
    def get_by_resource(cls, id, autoflush=True):
        if not id:
            return []
        query = meta.Session.query(cls).filter(cls.resource_id==id)
        query = query.autoflush(autoflush)
        record = query.all()
        return record

    @classmethod
    def get_by_package(cls, package_id, autoflush=True):
        if not package_id:
            return []
        query = meta.Session.query(cls).join(Resource).filter(Resource.package_id == package_id)
        query = query.autoflush(autoflush)
        return query.all()

    @classmethod
    def delete_by_resource(cls, resource_id):
        for record in cls.get_by_resource(resource_id):
            record.delete()
        meta.Session.commit()

    @classmethod
    def delete_by_package(cls, package_id):
        for record in cls.get_by_package(package_id):
            record.delete()
        meta.Session.commit()

    
    def get_resource(self):
        return self.resource



meta.mapper(
    DataResourceColumnIndex,
    data_resource_column_index_table,
    properties={
        u"resource": orm.relation(
            Resource, backref=orm.backref(u"data_resource_column_index", cascade=u"all, delete, delete-orphan")
        )
    },
)
