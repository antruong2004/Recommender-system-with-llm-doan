import importlib
import json
import sys

import pytest


@pytest.fixture()
def app_module(monkeypatch):
    original_json_load = json.load

    def patched_json_load(file_obj, *args, **kwargs):
        file_name = getattr(file_obj, "name", "").replace("\\", "/")
        if file_name.endswith("/data/product_vectors.json"):
            return {
                "meta": {"model": "test", "dimension": 0},
                "vectors": [],
            }
        return original_json_load(file_obj, *args, **kwargs)

    monkeypatch.setattr(json, "load", patched_json_load)

    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config.update(TESTING=True)
    return module


@pytest.fixture()
def client(app_module):
    return app_module.app.test_client()
