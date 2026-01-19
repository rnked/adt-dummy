import pytest

from adt_dummy.core.errors import AppError
from adt_dummy.k8s import select_pod_from_json


def test_select_pod_prefers_running():
    data = {
        "items": [
            {"metadata": {"name": "pod-a"}, "status": {"phase": "Pending"}},
            {"metadata": {"name": "pod-b"}, "status": {"phase": "Running"}},
        ]
    }
    assert select_pod_from_json(data) == "pod-b"


def test_select_pod_explicit():
    data = {
        "items": [
            {"metadata": {"name": "pod-a"}, "status": {"phase": "Running"}},
            {"metadata": {"name": "pod-b"}, "status": {"phase": "Running"}},
        ]
    }
    assert select_pod_from_json(data, explicit_pod="pod-b") == "pod-b"


def test_select_pod_no_items():
    with pytest.raises(AppError):
        select_pod_from_json({"items": []})
