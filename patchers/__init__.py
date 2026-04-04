"""Targeted evidence recovery patchers."""

from patchers.patch_api_concentration import patch_api_concentration
from patchers.patch_area import patch_area
from patchers.patch_endpoint_time import patch_endpoint_time

__all__ = [
    "patch_api_concentration",
    "patch_area",
    "patch_endpoint_time",
]
