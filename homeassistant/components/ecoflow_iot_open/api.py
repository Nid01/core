"""EcoFlow IoT Open API Interface.

This module provides an interface to interact with the EcoFlow IoT Open API,
including authentication, device management, and MQTT communication.
It includes methods for retrieving device information, publishing commands,
and handling MQTT messages.
"""

import asyncio
import base64
from datetime import UTC, datetime
import hashlib
import hmac
import json
import logging
import os
import random
import time
from typing import Any

from aiohttp import ClientSession
from aiomqtt import Client, MqttCodeError
from aiomqtt.message import Message
from multidict import CIMultiDict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.util.dt import utcnow
from homeassistant.util.ssl import get_default_context

from .const import (
    DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC,
    DELTA_MAX,
    DOMAIN,
    POWERSTREAM,
    SINGLE_AXIS_SOLAR_TRACKER,
    SMART_PLUG,
)
from .data_holder import EcoFlowIoTOpenDataHolder
from .errors import EcoFlowIoTOpenError, GenericHTTPError, InvalidResponseFormat
from .products import BaseDevice, ProductType

_LOGGER = logging.getLogger(__name__)
_CLIENT_LOGGER = logging.getLogger(f"{__name__}.client")


class EcoFlowIoTOpenAPIInterface:
    """Represents an interface to interact with EcoFlow IoT Open API.

    This class handles authentication, device management, and MQTT communication
    with EcoFlow's IoT Open API. It provides methods to retrieve device information,
    publish commands, and handle incoming MQTT messages.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        open_access_key: str,
        open_secret_key: str,
        open_base_url: str,
        app_username: str,
        app_password: str,
        app_base_url: str,
        availability_check_interval_sec: int = DEFAULT_AVAILABILITY_CHECK_INTERVAL_SEC,
    ) -> None:
        """Initialize an EcoFlowIoTOpenAPIInterface instance."""
        self.availability_check_interval_sec = availability_check_interval_sec
        self.data_holder = EcoFlowIoTOpenDataHolder()
        self.hass = hass

        self._open_access_key = open_access_key
        self._open_secret_key = open_secret_key
        self._open_base_url = open_base_url
        self._open_certification: dict[str, Any]
        self._open_mqtt_client: Client
        self._open_mqtt_listener: asyncio.Task | None = None
        self._open_max_reconnects = 3
        self._open_reconnects = 0

        self._app_password = app_password
        self._app_username = app_username
        self._app_base_url = app_base_url
        self._app_certification: dict[str, Any]
        self._app_mqtt_certification: dict[str, Any]
        self._app_mqtt_client: Client | None = None
        self._app_mqtt_listener: asyncio.Task | None = None
        self._app_max_reconnects = 3
        self._app_reconnects = 0

        self._products: dict[ProductType, dict[str, Any]] = {}

    async def certification(
        self,
    ) -> None:
        """Authenticate the client with EcoFlow's API."""
        await self._authenticate()

    async def _process_device(
        self,
        device_info: dict[str, Any],
        filtered_products: dict[ProductType, dict[str, Any]],
        product_types: list[ProductType],
    ) -> None:
        """Process device information and adds it to filtered_products if it matches the specified types."""
        device_quota = await self.getDeviceQuota(device_info["sn"])
        device_info.update(device_quota)
        device_info["status"] = device_info["online"]
        sn_prefix = device_info["sn"][:4]
        product_type = self._get_product_type(sn_prefix)
        if product_type and product_type in product_types:
            if product_type not in filtered_products:
                filtered_products[product_type] = {}
            product_instance = self._create_product_instance(product_type, device_info)
            filtered_products[product_type][product_instance.serial_number] = (
                product_instance
            )

    def _get_product_type(self, sn_prefix: str) -> ProductType:
        """Get the product type based on the serial number prefix."""
        if sn_prefix == DELTA_MAX:
            return ProductType.DELTA_MAX
        if sn_prefix == SINGLE_AXIS_SOLAR_TRACKER:
            return ProductType.SINGLE_AXIS_SOLAR_TRACKER
        if sn_prefix == POWERSTREAM:
            return ProductType.POWERSTREAM
        if sn_prefix == SMART_PLUG:
            return ProductType.SMART_PLUG
        # To-Do: Return diagnostic/base product type in case of unknown prefix.
        return ProductType.UNKNOWN

    def _create_product_instance(
        self, product_type: ProductType, device: dict[str, Any]
    ) -> BaseDevice:
        """Create an instance of the product based on its type."""
        # pylint: disable=import-outside-toplevel
        from .products.delta_max import DELTAMax
        from .products.powerstream import PowerStream
        from .products.single_axis_solar_tracker import SingleAxisSolarTracker
        from .products.smart_plug import SmartPlug

        if product_type == ProductType.DELTA_MAX:
            return DELTAMax(device, self)
        if product_type == ProductType.SINGLE_AXIS_SOLAR_TRACKER:
            return SingleAxisSolarTracker(device, self)
        if product_type == ProductType.POWERSTREAM:
            return PowerStream(device, self)
        if product_type == ProductType.SMART_PLUG:
            return SmartPlug(device, self)

        raise EcoFlowIoTOpenError("Unknown Device")
        # TODO: Return diagnostic/base product instance in case of unknown prefix. # pylint: disable=fixme
        # return None

    async def get_devices_by_product(
        self, product_types: list[ProductType]
    ) -> dict[ProductType, dict[str, Any]]:
        """Retrieve devices by product type."""
        headers = create_headers(self._open_access_key, self._open_secret_key, None)
        device_list = await self._request(
            "GET",
            f"{self._open_base_url}/sign/device/list",
            headers=headers,
            timeout=30,
        )

        filtered_products: dict[ProductType, dict[str, Any]] = {}
        if device_list.get("message") == "Success":
            tasks = [
                self._process_device(device, filtered_products, product_types)
                for device in device_list.get("data", [])
            ]
            await asyncio.gather(*tasks)
        self._products = filtered_products
        return self._products

    async def _authenticate(self) -> None:
        """Authenticate the client with EcoFlow's open API."""
        headers = create_headers(self._open_access_key, self._open_secret_key)
        response = await self._request(
            "GET",
            f"{self._open_base_url}/sign/certification",
            headers=headers,
            timeout=30,
        )
        self._open_certification = response["data"]

        _LOGGER.info("Successfully retrieved credentials for open MQTT API")

        headers = {"lang": "en_US", "content-type": "application/json"}
        json_data = {
            "email": self._app_username,
            "password": base64.b64encode(self._app_password.encode()).decode(),
            "scene": "IOT_APP",
            "userType": "ECOFLOW",
        }
        response = await self._request(
            "POST",
            f"{self._app_base_url}/auth/login",
            headers=headers,
            timeout=30,
            json=json_data,
        )

        self._app_certification = response["data"]
        _LOGGER.info("Successfully retrieved credentials for app API")

        headers = {
            "lang": "en_US",
            "authorization": f"Bearer {self._app_certification['token']}",
            "content-type": "application/json",
        }

        response = await self._request(
            "GET",
            f"{self._app_base_url}/iot-auth/app/certification",
            headers=headers,
            timeout=30,
        )
        self._app_mqtt_certification = response["data"]
        _LOGGER.info("Successfully retrieved credentials for app MQTT API")

    async def connect(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Establish a connection to the MQTT broker."""
        if self._open_mqtt_listener:
            _LOGGER.warning("MQTT listener is already running")
            return
        self._open_reconnects = 0
        self._open_mqtt_listener = asyncio.create_task(self.subscribe(config_entry))

    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self._open_mqtt_listener:
            self._open_mqtt_listener.cancel()
            try:
                await self._open_mqtt_listener
            except asyncio.CancelledError:
                _LOGGER.info("MQTT listener task has been cancelled")
            self._open_mqtt_listener = None
        else:
            _LOGGER.warning("MQTT listener is not running")

    async def subscribe(self, config_entry: ConfigEntry):
        """Subscribe to MQTT topics."""
        if not self._products:
            _LOGGER.error("No products found. Did you call setup before subscribing?")
            return

        while self._open_reconnects < self._open_max_reconnects:
            try:
                async with Client(
                    hostname=self._open_certification["url"],
                    port=int(self._open_certification["port"]),
                    username=self._open_certification["certificateAccount"],
                    password=self._open_certification["certificatePassword"],
                    logger=_CLIENT_LOGGER,
                    identifier=self._get_client_id("open"),
                    tls_insecure=False,
                    tls_context=get_default_context(),
                ) as open_client:
                    self._open_mqtt_client = open_client
                    topics_qos: list[tuple[str, int]] = [
                        (
                            f"/open/{self._open_certification['certificateAccount']}/{device.serial_number}/status",
                            1,
                        )
                        for devices in self._products.values()
                        for device in devices.values()
                    ]
                    topics_qos += [
                        (
                            f"/open/{self._open_certification['certificateAccount']}/{device.serial_number}/quota",
                            1,
                        )
                        for devices in self._products.values()
                        for device in devices.values()
                    ]
                    await self._open_mqtt_client.subscribe(topics_qos)
                    async for message in self._open_mqtt_client.messages:
                        if isinstance(message.payload, bytes):
                            await self._handle_mqtt_message(message)

            except MqttCodeError as exception:
                self._open_reconnects = self._open_reconnects + 1
                _LOGGER.exception(
                    "Exception during subscription. %s reconnects left",
                    self._open_max_reconnects - self._open_reconnects,
                )
                if self._open_reconnects == self._open_max_reconnects:
                    async_create_issue(
                        self.hass,
                        DOMAIN,
                        DOMAIN + "_mqtt_connection",
                        is_fixable=True,
                        issue_domain=DOMAIN,
                        severity=IssueSeverity.ERROR,
                        translation_key="mqtt_connection",
                        data={"entry_id": config_entry.entry_id},
                        translation_placeholders={
                            "exception": f"[ReasonCode: {exception.rc}] {exception.args}"
                        },
                    )
                await asyncio.sleep(5)

    async def publish_open(
        self,
        serial_number: str,
        command: dict,
    ):
        """Publish command to open MQTT set topic."""
        message_id = random.randint(100000, 999999)
        payload: dict[str, str | int] = {
            "id": message_id,
            "version": "1.0",
        }
        payload.update(command)

        await self._open_mqtt_client.publish(
            f"/open/{self._open_certification['certificateAccount']}/{serial_number}/set",
            json.dumps(payload),
            1,
        )

    async def publish_app(
        self,
        serial_number: str,
        message_bytes: bytes,
    ):
        """Publish command to app MQTT set topic."""

        async with Client(
            hostname=self._app_mqtt_certification["url"],
            port=int(self._app_mqtt_certification["port"]),
            username=self._app_mqtt_certification["certificateAccount"],
            password=self._app_mqtt_certification["certificatePassword"],
            logger=_CLIENT_LOGGER,
            identifier=self._get_client_id("app"),
            tls_insecure=False,
            tls_context=get_default_context(),
        ) as app_client:
            await app_client.publish(
                f"/app/{self._app_certification['user']['userId']}/{serial_number}/thing/property/set",
                message_bytes,
                1,
            )

    async def _handle_mqtt_message(self, message: Message):
        """Handle incoming MQTT messages."""

        if not isinstance(message.payload, (bytes, bytearray)):
            raise TypeError(
                f"Expected payload type bytes or bytesarray, but received: {type(message.payload)}"
            )
        unpacked_json = json.loads(message.payload.decode("utf-8"))
        _LOGGER.debug("MQTT message from topic: %s", message.topic)
        _LOGGER.debug(json.dumps(unpacked_json, indent=2, sort_keys=True))

        serial_number = message.topic.value.split("/")[3]
        product_type = self._get_product_type(serial_number[:4])

        if product_type != ProductType.UNKNOWN:
            if "param" in unpacked_json:
                unpacked_json["params"] = unpacked_json.pop("param")
            if "addr" in unpacked_json:
                addr = unpacked_json["addr"]
                unpacked_json["params"] = {
                    f"{addr}.{key}": value
                    for key, value in unpacked_json["params"].items()
                }
            timestamp = unpacked_json.get("timestamp")
            if timestamp:
                last_updated = datetime.fromtimestamp(timestamp / 1000, UTC)
            else:
                last_updated = utcnow()
            unpacked_json["params"]["last_updated"] = last_updated

            if isinstance(self.data_holder, EcoFlowIoTOpenDataHolder):
                self.data_holder.update_params(
                    raw=unpacked_json["params"], serial_number=serial_number
                )

        else:
            _LOGGER.error(
                "ProductType for serial number %s not supported", serial_number
            )

    async def getDeviceQuota(self, serial_number: str) -> dict[str, Any]:
        """Retrieve quota information for a device.

        Args:
            serial_number (str): Serial number of the device.

        Returns:
            dict[str, Any]: Quota information.

        """
        params = {"sn": serial_number}
        headers = create_headers(self._open_access_key, self._open_secret_key, params)
        response = await self._request(
            "GET",
            f"{self._open_base_url}/sign/device/quota/all",
            headers=headers,
            params=params,
        )
        if response.get("message") == "Success" and serial_number[:4] in (
            POWERSTREAM,
            SMART_PLUG,
        ):
            response["data"] = {
                f"iot.{key.split('.', 2)[-1]}": value
                for key, value in response["data"].items()
            }
        return response.get("data", {})

    async def initializeDevices(self) -> None:
        """Initialize devices and updates data holder."""
        if isinstance(self.data_holder, EcoFlowIoTOpenDataHolder):
            for devices in self._products.values():
                for device in devices.values():
                    quota_data = await self.getDeviceQuota(device.serial_number)
                    quota_data["status"] = device.is_available()
                    quota_data["last_updated"] = utcnow()
                    self.data_holder.update_params(
                        raw=quota_data, serial_number=device.serial_number
                    )
        else:
            raise EcoFlowIoTOpenError("Missing EcoFlowIoTOpenDataHolder")

    def _get_client_id(self, api_variant: str) -> str:
        """Generate a client ID based on the environment and access key.

        This method checks for the existence of the `.devcontainer` directory
        to determine if the Home Assistant instance is running in a development
        environment. If the directory exists, the environment is set to
        "development"; otherwise, it is set to "production".

        The method then returns a client ID string formatted as
        "HomeAssistant_<environment>_<accessKey>", where `<environment>`
        is either "development" or "production" and `<accessKey>` is an
        instance attribute.

        Returns:
            str: A client ID string that includes the environment and access key.

        """
        if os.path.exists(".devcontainer"):
            environment = "development"
        else:
            environment = "production"

        if api_variant == "open":
            return f"{HOMEASSISTANT_DOMAIN}_{environment}_{self._open_access_key}"
        if api_variant == "app":
            return f"ANDROID_{environment}_{self._app_certification['user']['userId']}"
        raise EcoFlowIoTOpenError("Unknown API variant")

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make an HTTP request to EcoFlow's API.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            url (str): URL for the request.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            dict[str, Any]: Response data.

        """
        async with (
            ClientSession() as session,
            session.request(method, url, **kwargs) as response,
        ):
            if response.status == 200:
                try:
                    response_json = await response.json()
                    sorted_response = recursively_sort_dict(response_json)
                except json.JSONDecodeError as exc:
                    _LOGGER.error(
                        "Failed to decode JSON response from %s: %s", url, exc
                    )
                    raise InvalidResponseFormat(
                        f"Invalid JSON response from {url}"
                    ) from exc
                else:
                    _LOGGER.debug(
                        "HTTP Response: %s", json.dumps(sorted_response, indent=2)
                    )
                    return sorted_response
            else:
                _LOGGER.error(
                    "HTTP Error %s from %s: %s",
                    response.status,
                    url,
                    await response.text(),
                )
                raise GenericHTTPError(response.status)


def hmac_sha256(data: str, key: str) -> str:
    """Compute HMAC-SHA256 hash.

    Args:
        data (str): Data to be hashed.
        key (str): Secret key for hashing.

    Returns:
        str: Hashed HMAC-SHA256 result.

    """
    hashed = hmac.new(
        key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).digest()
    return "".join(format(byte, "02x") for byte in hashed)


def get_map(json_obj: Any, prefix: str = "") -> dict[str, Any]:
    """Flattens JSON object into a dictionary.

    Args:
        json_obj (Any): JSON object to be flattened.
        prefix (str, optional): Prefix to prepend to keys. Defaults to "".

    Returns:
        dict[str, Any]: Flattened dictionary.

    """

    def flatten(obj: Any, pre: str = "") -> dict[str, Any]:
        result = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                result.update(flatten(v, f"{pre}.{k}" if pre else k))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result.update(flatten(item, f"{pre}[{i}]"))
        else:
            result[pre] = obj
        return result

    return flatten(json_obj, prefix)


def get_map_qstr(params: dict[str, str]) -> str:
    """Convert dictionary to query string format.

    Args:
        params (dict[str, str]): Dictionary of parameters.

    Returns:
        str: Query string representation.

    """
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def get_header_qstr(params: CIMultiDict[str]):
    """Convert CIMultiDict to query string format.

    Args:
        params (CIMultiDict[str]): Multi-dictionary of parameters.

    Returns:
        str: Query string representation.

    """
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def create_headers(
    accessKey: str, secretKey: str, params: dict[str, str] | None = None
) -> dict[str, str]:
    """Create headers with authentication information.

    Args:
        accessKey (str): Access key for authentication.
        secretKey (str): Secret key for authentication.
        params (Optional[dict[str, str]], optional): Additional parameters. Defaults to None.

    Returns:
        dict[str, str]: Headers dictionary.

    """
    nonce = str(random.randint(100000, 999999))
    timestamp = str(int(time.time() * 1000))
    headers = {
        "accessKey": accessKey,
        "nonce": nonce,
        "timestamp": timestamp,
    }
    sign_str = (get_map_qstr(get_map(params)) + "&" if params else "") + get_map_qstr(
        headers
    )
    headers["sign"] = hmac_sha256(sign_str, secretKey)
    return headers


def recursively_sort_dict(unsorted_dict: dict[str, Any]) -> dict[str, Any]:
    """Recursively sort a dictionary.

    Args:
        unsorted_dict (dict[str, Any]): Unsorted dictionary.

    Returns:
        dict[str, Any]: Sorted dictionary.

    """
    sorted_dict = {}
    for key, value in sorted(unsorted_dict.items()):
        if isinstance(value, dict):
            sorted_dict[key] = recursively_sort_dict(value)
        else:
            sorted_dict[key] = value
    return sorted_dict
