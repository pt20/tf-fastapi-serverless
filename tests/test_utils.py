import pytest
from fastapi.exceptions import HTTPException

from src.pydantic_models import MlModelsConfig
from src.utils import load_ml_config, validate_model_by_id


def test_load_ml_config():
    result = load_ml_config()

    assert isinstance(result, MlModelsConfig)


def test_validate_model_by_id():
    result = validate_model_by_id(1)

    assert isinstance(result, MlModelsConfig)


def test_validate_model_by_id_raises(monkeypatch):
    def fake_cfg():
        fpath = "tests/mock_data/fake-ml-config.yaml"
        return load_ml_config(fpath)

    monkeypatch.setattr("src.utils.load_ml_config", fake_cfg)

    with pytest.raises(HTTPException) as err:
        validate_model_by_id(5)
        assert err.status_code == 404
        assert err.detail == "Model not found"
