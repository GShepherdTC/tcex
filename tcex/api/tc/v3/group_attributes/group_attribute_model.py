"""Group_Attribute / Group_Attributes Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class GroupAttributesModel(
    BaseModel,
    title='GroupAttributes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Group_Attributes Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['GroupAttributeModel']] = Field(
        [],
        description='The data for the GroupAttributes.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class GroupAttributeDataModel(
    BaseModel,
    title='GroupAttribute Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Group_Attributes Data Model"""

    data: Optional[List['GroupAttributeModel']] = Field(
        [],
        description='The data for the GroupAttributes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class GroupAttributeModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='GroupAttribute Model',
    validate_assignment=True,
):
    """Group_Attribute Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    created_by: Optional['UserModel'] = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Group_Attribute.',
        read_only=True,
        title='createdBy',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    default: bool = Field(
        None,
        description=(
            'A flag indicating that this is the default attribute of its type within the object. '
            'Only applies to certain attribute and data types.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='default',
    )
    group: Optional['GroupModel'] = Field(
        None,
        description='Details of group associated with attribute.',
        methods=['POST'],
        read_only=False,
        title='group',
    )
    group_id: Optional[int] = Field(
        None,
        description='Group associated with attribute.',
        methods=['POST'],
        read_only=False,
        title='groupId',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastModified',
    )
    pinned: bool = Field(
        None,
        description='A flag indicating that the attribute has been noted for importance.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='pinned',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    source: Optional[str] = Field(
        None,
        description='The attribute source.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='source',
    )
    type: Optional[str] = Field(
        None,
        description='The attribute type.',
        methods=['POST'],
        read_only=False,
        title='type',
    )
    value: Optional[str] = Field(
        None,
        description='The attribute value.',
        methods=['POST', 'PUT'],
        min_length=1,
        read_only=False,
        title='value',
    )

    @validator('group', always=True)
    def _validate_group(cls, v):
        if not v:
            return GroupModel()
        return v

    @validator('security_labels', always=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()
        return v

    @validator('created_by', always=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()
        return v


# first-party
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel

# add forward references
GroupAttributeDataModel.update_forward_refs()
GroupAttributeModel.update_forward_refs()
GroupAttributesModel.update_forward_refs()
