"""Advanced Settings Model"""
# standard library
from typing import Any, Optional

# third-party
from pydantic import BaseModel, Field


class AdvancedSettingsModel(BaseModel):
    """Advanced Settings Model

    * why was input included -> feature (what feature?), runtime_level
    * where is input defined -> default (core), install.json

    Feature: advancedRequest

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_adv_req_body: Optional[Any] = Field(
        None,
        description='The HTTP body for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_exclude_null_params: bool = Field(
        False,
        description='Flag to exclude any null query parameters.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_fail_on_error: bool = Field(
        False,
        description='Flag to force fail on any error.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_headers: Optional[dict] = Field(
        None,
        description='The HTTP headers for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_http_method: str = Field(
        None,
        description='The HTTP method for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_params: Optional[dict] = Field(
        None,
        description='The HTTP query params for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_path: Optional[str] = Field(
        None,
        description='The API path for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_urlencode_body: bool = Field(
        False,
        description='Flag to set URL encoding for the request body.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )