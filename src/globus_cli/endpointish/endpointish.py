import uuid
from typing import Type, Union, cast

import click

from globus_cli.services.transfer import get_client

from .endpoint_type import EndpointType
from .errors import ExpectedCollectionError, WrongEndpointTypeError


class Endpointish:
    def __init__(
        self,
        endpoint_id: Union[str, uuid.UUID],
    ):
        self._client = get_client()
        self.endpoint_id = endpoint_id

        res = self._client.get_endpoint(endpoint_id)
        self.data = res.data

        self.ep_type = EndpointType.determine_endpoint_type(self.data)

    def assert_ep_type(
        self,
        *expect_types: EndpointType,
        error_class: Type[WrongEndpointTypeError] = WrongEndpointTypeError,
    ):
        if self.ep_type not in expect_types:
            raise error_class(
                click.get_current_context().command_path,
                str(self.endpoint_id),
                self.ep_type,
                expect_types,
            )

    def assert_is_gcsv5_collection(self):
        self.assert_ep_type(
            EndpointType.GUEST_COLLECTION,
            EndpointType.MAPPED_COLLECTION,
            error_class=ExpectedCollectionError,
        )

    def get_collection_endpoint_id(self) -> str:
        self.assert_is_gcsv5_collection()
        return cast(str, self.data["owner_id"])
