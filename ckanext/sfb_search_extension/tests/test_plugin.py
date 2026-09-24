import pytest

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.model import meta
from ckan.tests import factories, helpers
import pandas as pd

from ckanext.sfb_search_extension.libs.commons import CommonHelper
from ckanext.sfb_search_extension.libs.publication_search import PublicationSearchHelper
from ckanext.sfb_search_extension.models.data_resource_column_index import (
    DataResourceColumnIndex,
    data_resource_column_index_table,
)
from ckanext.sfb_search_extension.plugin import AutoTagPlugin
from ckanext.sfb_search_extension.plugin2 import SfbSearchPlugin


def _resource(format="CSV", resource_id="abcdef123456", name="data.csv"):
    return {
        "id": resource_id,
        "package_id": "pkg-id",
        "url_type": "upload",
        "format": format,
        "name": name,
    }


def _search_results():
    return {
        "count": 2,
        "results": [{"id": "original"}],
        "search_facets": {
            "organization": {"items": [{"name": "old", "count": 1}]},
            "tags": {"items": [{"name": "old", "count": 1}]},
            "groups": {"items": [{"name": "old", "count": 1}]},
            "sfb_dataset_type": {"items": [{"name": "old", "count": 1}]},
        },
    }


@pytest.mark.ckan_config("ckan.plugins", "auto_tag sfb_search")
def test_declared_plugins_load(with_plugins):
    assert plugins.plugin_loaded("auto_tag")
    assert plugins.plugin_loaded("sfb_search")


def test_csv_resource_is_indexed_and_auto_tagged(monkeypatch):
    resource = _resource()
    dataset = {"id": "pkg-id", "name": "pkg", "tags": [{"name": "Existing"}]}
    updated = {}
    indexed = {}

    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.CommonHelper.is_csv", lambda res: True)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.CommonHelper.is_xlsx", lambda res: False)
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin.CommonHelper.get_csv_columns",
        lambda resource_id: (["temperature", "pressure"], True),
    )
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.is_csv", lambda res: True)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.is_xlsx", lambda res: False)
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.CommonHelper.get_csv_columns",
        lambda resource_id: (["temperature", "pressure"], True),
    )
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.CommonHelper.add_index",
        lambda resource_id, value: indexed.update({"resource_id": resource_id, "value": value}),
    )

    def fake_get_action(name):
        if name == "package_show":
            return lambda context, data: dataset
        if name == "package_patch":
            return lambda context, data: updated.update(data)
        raise AssertionError(name)

    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.toolkit.get_action", fake_get_action)

    assert AutoTagPlugin().after_resource_create({}, resource) == resource
    assert updated["id"] == dataset["id"]
    assert {"name": "Temperature"} in updated["tags"]
    assert {"name": "Pressure"} in updated["tags"]

    assert SfbSearchPlugin().after_resource_create({}, resource) == resource
    assert indexed == {"resource_id": resource["id"], "value": "temperature,pressure,"}


def test_xlsx_resource_path_is_indexed_and_auto_tagged(monkeypatch):
    resource = _resource(format="XLSX", name="data.xlsx")
    dataset = {"id": "pkg-id", "name": "pkg", "tags": []}
    updated = {}
    indexed = {}
    sheets = {"Sheet1": [["roughness", "density"], True]}

    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.CommonHelper.is_csv", lambda res: False)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.CommonHelper.is_xlsx", lambda res: True)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.CommonHelper.get_xlsx_columns", lambda resource_id: sheets)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.is_csv", lambda res: False)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.is_xlsx", lambda res: True)
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.get_xlsx_columns", lambda resource_id: sheets)
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.CommonHelper.add_index",
        lambda resource_id, value: indexed.update({"resource_id": resource_id, "value": value}),
    )

    def fake_get_action(name):
        if name == "package_show":
            return lambda context, data: dataset
        if name == "package_patch":
            return lambda context, data: updated.update(data)
        raise AssertionError(name)

    monkeypatch.setattr("ckanext.sfb_search_extension.plugin.toolkit.get_action", fake_get_action)

    AutoTagPlugin().after_resource_create({}, resource)
    SfbSearchPlugin().after_resource_create({}, resource)

    assert {"name": "Roughness"} in updated["tags"]
    assert indexed == {"resource_id": resource["id"], "value": "roughness,density,"}


def test_resource_deletion_removes_column_indexes(monkeypatch):
    deleted = []
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.DataResourceColumnIndex.delete_by_resource",
        lambda resource_id: deleted.append(resource_id),
    )

    resources = [_resource()]
    assert SfbSearchPlugin().before_resource_delete({}, _resource(), resources) == resources
    assert deleted == ["abcdef123456"]


def test_dataset_deletion_removes_related_column_indexes(monkeypatch):
    deleted_resources = []
    deleted_packages = []
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.DataResourceColumnIndex.delete_by_resource",
        lambda resource_id: deleted_resources.append(resource_id),
    )
    monkeypatch.setattr(
        "ckanext.sfb_search_extension.plugin2.DataResourceColumnIndex.delete_by_package",
        lambda package_id: deleted_packages.append(package_id),
    )

    plugin = SfbSearchPlugin()
    plugin.after_dataset_delete({}, {"id": "pkg-id", "resources": [{"id": "res-1"}, {"id": "res-2"}]})
    plugin.after_dataset_delete({}, {"id": "pkg-without-resource-dict"})

    assert deleted_resources == ["res-1", "res-2"]
    assert deleted_packages == ["pkg-without-resource-dict"]


@pytest.mark.parametrize(
    ("query", "helper_path", "expected_kwargs"),
    [
        ("column: temp", "ckanext.sfb_search_extension.plugin2.ColumnSearchHelper.run", {"search_phrase": "temp"}),
        ("sample: s1", "ckanext.sfb_search_extension.plugin2.SampleSearchHelper.run", {"search_phrase": "s1"}),
        ("publication: smith", "ckanext.sfb_search_extension.plugin2.PublicationSearchHelper.run", {"search_phrase": "smith"}),
        (
            "material_combination: steel",
            "ckanext.sfb_search_extension.plugin2.ResourceMetadataSearchHelper.run",
            {"search_phrase": "steel", "target_metadata_name": "material_combination"},
        ),
        (
            "surface_preparation: polished",
            "ckanext.sfb_search_extension.plugin2.ResourceMetadataSearchHelper.run",
            {"search_phrase": "polished", "target_metadata_name": "surface_preparation"},
        ),
        (
            "atmosphere: argon",
            "ckanext.sfb_search_extension.plugin2.ResourceMetadataSearchHelper.run",
            {"search_phrase": "argon", "target_metadata_name": "atmosphere"},
        ),
        (
            "data_type: sem",
            "ckanext.sfb_search_extension.plugin2.ResourceMetadataSearchHelper.run",
            {"search_phrase": "sem", "target_metadata_name": "data_type"},
        ),
        (
            "analysis_method: xrd",
            "ckanext.sfb_search_extension.plugin2.ResourceMetadataSearchHelper.run",
            {"search_phrase": "xrd", "target_metadata_name": "analysis_method"},
        ),
    ],
)
def test_special_search_modes_return_filtered_shape(monkeypatch, query, helper_path, expected_kwargs):
    captured = {}

    def fake_run(**kwargs):
        captured.update(kwargs)
        results = kwargs["search_results"]
        results["results"] = [{"id": "filtered"}]
        results["count"] = 1
        return results

    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.Package.search_by_name", lambda name: ["dataset"])
    monkeypatch.setattr("ckanext.sfb_search_extension.plugin2.CommonHelper.check_plugin_enabled", lambda name: True)
    monkeypatch.setattr(helper_path, fake_run)

    results = SfbSearchPlugin().after_dataset_search(_search_results(), {"q": query, "fq": [""]})

    assert results["results"] == [{"id": "filtered"}]
    assert results["count"] == 1
    assert results["search_facets"]["organization"]["items"] == []
    assert captured["search_filters"] == ""
    for key, value in expected_kwargs.items():
        assert captured[key] == value


def test_normal_search_results_are_unchanged():
    results = _search_results()
    assert SfbSearchPlugin().after_dataset_search(results, {"q": "normal search", "fq": [""]}) is results


def test_empty_prefixed_search_is_unchanged():
    results = _search_results()

    assert SfbSearchPlugin().after_dataset_search(results, {"q": "column:  ", "fq": [""]}) is results


@pytest.mark.parametrize(("query", "document"), [("", "citation"), ("the", "and")])
def test_publication_similarity_handles_empty_vocabulary(query, document):
    assert PublicationSearchHelper.similarity_calc(query, document) == 0.0


@pytest.mark.ckan_config("ckan.plugins", "auto_tag sfb_search")
def test_indexer_blueprint_route_is_registered_and_responds(app):
    flask_app = getattr(app, "flask_app", None) or getattr(app, "app", None)
    route_paths = {rule.rule for rule in flask_app.url_map.iter_rules()}
    assert "/sfb_search/indexer" in route_paths

    response = app.get("/sfb_search/indexer", status=404)
    assert response.status_code == 404


def test_dataset_and_resource_callbacks_do_not_collide():
    methods = SfbSearchPlugin.__dict__

    assert "after_dataset_delete" in methods
    assert "before_resource_delete" in methods
    assert "after_resource_create" in methods
    assert "after_delete" not in methods
    assert "after_create" not in methods


@pytest.mark.parametrize(
    ("resource", "is_csv", "is_xlsx"),
    [
        ({"format": "csv", "name": None, "url": "upload"}, True, False),
        ({"format": "", "name": "DATA.CSV"}, True, False),
        ({"format": None, "name": None, "url": "report.XLSX"}, False, True),
        ({"format": "txt", "name": "notes.txt"}, False, False),
    ],
)
def test_resource_format_detection_is_case_insensitive_and_null_safe(resource, is_csv, is_xlsx):
    assert CommonHelper.is_csv(resource) is is_csv
    assert CommonHelper.is_xlsx(resource) is is_xlsx


def test_annotated_xlsx_columns_are_read_from_uploaded_file(tmp_path, monkeypatch):
    resource_id = "abcdef123456"
    monkeypatch.setitem(toolkit.config, "ckan.storage_path", str(tmp_path))
    resource_path = tmp_path / "resources" / "abc" / "def" / "123456"
    resource_path.parent.mkdir(parents=True)
    dataframe = pd.DataFrame(
        [
            ["X-Kategorie", "Y-Kategorie", "Datentyp", "Werkstoff-1", "Werkstoff-2", "Atmosphaere", "Vorbehandlung"],
            ["Temperature", "Pressure", "Mechanical", "Steel", "Aluminum", "Air", "Polished"],
        ]
    )
    dataframe.to_excel(resource_path, index=False, header=False)

    sheets = CommonHelper.get_xlsx_columns(resource_id)

    assert sheets["Sheet1"] == [
        ["Temperature", "Pressure", "Mechanical", "Steel", "Aluminum", "Air", "Polished"],
        True,
    ]


@pytest.mark.parametrize(
    ("configured_plugins", "expected"),
    [
        ("auto_tag sample_link sfb_search", True),
        (["auto_tag", "sample_link", "sfb_search"], True),
        ("auto_tag sample_link_extra sfb_search", False),
    ],
)
def test_plugin_detection_accepts_string_and_list_config(monkeypatch, configured_plugins, expected):
    monkeypatch.setitem(toolkit.config, "ckan.plugins", configured_plugins)

    assert CommonHelper.check_plugin_enabled("sample_link") is expected


def test_resource_update_refreshes_tags_and_column_index(monkeypatch):
    resource = _resource()
    auto_tagged = []
    indexed = []
    auto_tag_plugin = AutoTagPlugin()
    search_plugin = SfbSearchPlugin()

    monkeypatch.setattr(auto_tag_plugin, "_auto_tag_resource", lambda context, value: auto_tagged.append(value["id"]))
    monkeypatch.setattr(search_plugin, "_index_resource_columns", lambda value: indexed.append(value["id"]))

    assert auto_tag_plugin.after_resource_update({}, resource) is resource
    assert search_plugin.after_resource_update({}, resource) is resource
    assert auto_tagged == [resource["id"]]
    assert indexed == [resource["id"]]


@pytest.mark.ckan_config("ckan.plugins", "auto_tag sfb_search")
@pytest.mark.ckan_config("ckan.uploads_enabled", True)
def test_uploaded_annotated_csv_is_tagged_and_indexed(clean_db, create_with_upload, with_plugins):
    data_resource_column_index_table.create(bind=meta.engine, checkfirst=True)
    dataset = factories.Dataset()
    csv_content = (
        "X-Kategorie,Y-Kategorie,Datentyp,Werkstoff-1,Werkstoff-2,Atmosphaere,Vorbehandlung\n"
        "Temperature,Pressure,Mechanical,Steel,Aluminum,Air,Polished\n"
    )

    resource = create_with_upload(
        csv_content,
        "annotated.csv",
        context={"ignore_auth": True},
        package_id=dataset["id"],
        url="upload",
        name="annotated.csv",
        format="CSV",
    )

    shown_dataset = helpers.call_action("package_show", id=dataset["id"])
    tag_names = {tag["name"] for tag in shown_dataset["tags"]}
    indexes = DataResourceColumnIndex.get_by_resource(resource["id"])

    assert {"Temperature", "Pressure", "Mechanical", "Steel", "Aluminum", "Air", "Polished"} <= tag_names
    assert len(indexes) == 1
    assert indexes[0].columns_names == "Temperature,Pressure,Mechanical,Steel,Aluminum,Air,Polished,"


@pytest.mark.ckan_config("ckan.plugins", "auto_tag sfb_search")
def test_normal_dataset_search_page_renders_without_detected_resources(clean_db, app, with_plugins):
    factories.Dataset(resources=[{"url": "https://example.com/data.csv", "format": "CSV"}])

    response = app.get("/dataset?q=ordinary")

    assert response.status_code == 200
