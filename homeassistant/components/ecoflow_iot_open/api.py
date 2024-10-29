"""EcoFlow IoT Open API Interface.

This module provides an interface to interact with EcoFlow's IoT Open API.
It supports authentication, device management, MQTT subscription, and more.

Attributes:
    HOST (str): Base URL for EcoFlow's API.
    HTTP_BASE_URL (str): Base URL for HTTP requests.

Classes:
    EcoFlowIoTOpenAPIInterface:
        Represents an interface to interact with EcoFlow IoT Open API.

Constants:
    HOST (str): Base URL for EcoFlow's API.
    HTTP_BASE_URL (str): Base URL for HTTP requests.

"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import random
import ssl
import time
from typing import Any, Optional, TypeVar

from aiohttp import ClientSession
import aiomqtt
from aiomqtt import Client, MqttCodeError
from multidict import CIMultiDict

# from paho.mqtt import client as mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import DOMAIN as HA_DOMAIN, HomeAssistant
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue

from .const import DELTA_MAX, DOMAIN, POWERSTREAM, SINGLE_AXIS_SOLAR_TRACKER, SMART_PLUG
from .data_holder import EcoFlowIoTOpenDataHolder
from .errors import (
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidCredentialsError,
    InvalidResponseFormat,
)

# from .products import BaseDevice
from .products import ProductType
from .products.delta_max import DELTAMax
from .products.powerstream import PowerStream
from .products.single_axis_solar_tracker import SingleAxisSolarTracker
from .products.smart_plug import SmartPlug

_LOGGER = logging.getLogger(__name__)
_CLIENT_LOGGER = logging.getLogger(f"{__name__}.client")

ApiType = TypeVar("ApiType", bound="EcoFlowIoTOpenAPIInterface")


class EcoFlowIoTOpenAPIInterface:
    """Represents an interface to interact with EcoFlow IoT Open API.

    Args:
        accessKey (str): Access key for authentication.
        secretKey (str): Secret key for authentication.
        data_holder (Optional[EcoFlowIoTOpenDataHolder]): Holder for EcoFlow IoT Open data.

    Methods:
        __init__(self, accessKey: str, secretKey: str, data_holder: Optional[EcoFlowIoTOpenDataHolder] = None) -> None:
            Initialize an EcoFlowIoTOpenAPIInterface instance.
        certification(cls: type[ApiType], accessKey: str, secretKey: str, data_holder: Optional[EcoFlowIoTOpenDataHolder] = None) -> ApiType:
            Class method for creating a certified EcoFlowIoTOpenAPIInterface instance.
        _get_devices(self) -> None:
            Retrieve device information from EcoFlow's API.
        _process_device(self, device: dict[str, Any], products: dict[ProductType, dict[str, Any]]) -> None:
            Process device information and adds it to products.
        _get_product_type(self, sn_prefix: str) -> Optional[ProductType]:
            Determine the product type based on serial number prefix.
        _create_product_instance(self, product_type: ProductType, device: dict[str, Any]) -> Any:
            Create an instance of a specific product type.
        get_devices_by_product(self, product_types: list[ProductType]) -> dict[ProductType, dict[str, Any]]:
            Retrieve devices filtered by product type.
        _authenticate(self) -> None:
            Authenticate the client with EcoFlow's API.
        connect(self) -> None:
            Establish a connection to the MQTT broker.
        disconnect(self) -> None:
            Disconnect from the MQTT broker.
        subscribe(self) -> None:
            Subscribe to MQTT topics.
        _handle_mqtt_message(self, message) -> None:
            Handle incoming MQTT messages.
        getDeviceQuota(self, serial_number: str) -> dict[str, Any]:
            Retrieve quota information for a device.
        initializeDevices(self) -> None:
            Initialize devices and updates data holder.
        _get_client_id(self) -> str:
            Generate a unique client ID.
        _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
            Make an HTTP request to EcoFlow's API.

    """

    def __init__(
        self,
        accessKey: str,
        secretKey: str,
        base_url: str,
        data_holder: Optional[EcoFlowIoTOpenDataHolder] = None,
    ) -> None:
        """Initialize an EcoFlowIoTOpenAPIInterface instance.

        Args:
            accessKey (str): Access key for authentication.
            secretKey (str): Secret key for authentication.
            base_url (str): Base URL for the API.
            data_holder (Optional[EcoFlowIoTOpenDataHolder]): Holder for EcoFlow IoT Open data. Defaults to None.

        Attributes:
            _accessKey (str): Stores the provided access key.
            _secretKey (str): Stores the provided secret key.
            _base_url (str): Stores the provided base URL.
            _certification (dict[str, Any]): Dictionary to hold certification data.
            _products (dict[ProductType, dict[str, Any]]): Dictionary to hold products data.
            _mqtt_client (Client): MQTT client for communication.
            mqtt_listener (Optional[asyncio.Task]): Task for handling MQTT messages. Defaults to None.
            _data_holder (Optional[EcoFlowIoTOpenDataHolder]): Holder for EcoFlow IoT Open data.

        """
        self._accessKey = accessKey
        self._secretKey = secretKey
        self._base_url = base_url
        self._certification: dict[str, Any]
        # self._products: dict[ProductType, dict[str, BaseDevice]] = {}
        self._products: dict[ProductType, dict[str, Any]] = {}
        self._mqtt_client: Client
        self._mqtt_listener: Optional[asyncio.Task] = None
        self._data_holder = data_holder
        self._reconnects = 0
        self._max_reconnects = 3

    @classmethod
    async def certification(
        cls: type[ApiType],
        accessKey: str,
        secretKey: str,
        base_url: str,
        data_holder: Optional[EcoFlowIoTOpenDataHolder] = None,
    ) -> ApiType:
        """Class method for creating a certified EcoFlowIoTOpenAPIInterface instance.

        Args:
            cls (type[ApiType]): Class object of type ApiType.
            accessKey (str): Access key for authentication.
            secretKey (str): Secret key for authentication.
            base_url (str): Base URL for the API.
            data_holder (Optional[EcoFlowIoTOpenDataHolder]): Holder for EcoFlow IoT Open data. Defaults to None.

        Returns:
            ApiType: Certified EcoFlowIoTOpenAPIInterface instance.

        """
        this_class = cls(accessKey, secretKey, base_url, data_holder)
        await this_class._authenticate()
        return this_class

    async def _process_device(
        self,
        device: dict[str, Any],
        filtered_products: dict[ProductType, dict[str, Any]],
        product_types: list[ProductType],
    ) -> None:
        """Process device information and adds it to filtered_products if it matches the specified types.

        Args:
            device (dict[str, Any]): Device information dictionary.
            filtered_products (dict[ProductType, dict[str, Any]]): Filtered products dictionary.
            product_types (list[ProductType]): List of product types to filter.

        """
        device_quota = await self.getDeviceQuota(device["sn"])
        device.update(device_quota)
        sn_prefix = device["sn"][:4]
        product_type = self._get_product_type(sn_prefix)
        if product_type and product_type in product_types:
            if product_type not in filtered_products:
                filtered_products[product_type] = {}
            product_instance = self._create_product_instance(product_type, device)
            filtered_products[product_type][product_instance.serial_number] = (
                product_instance
            )

    def _get_product_type(self, sn_prefix: str) -> Optional[ProductType]:
        """Determine the product type based on serial number prefix.

        Args:
            sn_prefix (str): Serial number prefix.

        Returns:
            Optional[ProductType]: Product type if determined, else None.

        """
        if sn_prefix == DELTA_MAX:
            return ProductType.DELTA_MAX
        if sn_prefix == SINGLE_AXIS_SOLAR_TRACKER:
            return ProductType.SINGLE_AXIS_SOLAR_TRACKER
        if sn_prefix == POWERSTREAM:
            return ProductType.POWERSTREAM
        if sn_prefix == SMART_PLUG:
            return ProductType.SMART_PLUG
        # To-Do: Return diagnostic/base product type in case of unknown prefix.
        return None

    def _create_product_instance(
        self, product_type: ProductType, device: dict[str, Any]
    ) -> Any:
        """Create an instance of a specific product type.

        Args:
            product_type (ProductType): Type of product.
            device (dict[str, Any]): Device information.

        Returns:
            Any: Instance of the specified product type.

        """
        if product_type == ProductType.DELTA_MAX:
            return DELTAMax(device, self)
        if product_type == ProductType.SINGLE_AXIS_SOLAR_TRACKER:
            return SingleAxisSolarTracker(device, self)
        if product_type == ProductType.POWERSTREAM:
            return PowerStream(device, self)
        if product_type == ProductType.SMART_PLUG:
            return SmartPlug(device, self)
        # To-Do: Return diagnostic/base product instance in case of unknown prefix.
        return None

    async def get_devices_by_product(
        self, product_types: list[ProductType]
    ) -> dict[ProductType, dict[str, Any]]:
        """Retrieve devices filtered by product type.

        Args:
            product_types (list[ProductType]): List of product types.

        Returns:
            dict[ProductType, dict[str, Any]]: Dictionary of devices by product type.

        """
        headers = create_headers(self._accessKey, self._secretKey, None)
        device_list = await self._request(
            "GET", f"{self._base_url}/sign/device/list", headers=headers, timeout=30
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
        """Authenticate the client with EcoFlow's API."""
        headers = create_headers(self._accessKey, self._secretKey)
        response = await self._request(
            "GET", f"{self._base_url}/sign/certification", headers=headers, timeout=30
        )
        if response.get("message") == "Success":
            self._certification = response["data"]
        elif response.get("message") == "accessKey is invalid":
            raise InvalidCredentialsError(response)
        else:
            raise InvalidResponseFormat(response)
        _LOGGER.info("Successfully retrieved MQTT credentials")

    async def connect(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Establish a connection to the MQTT broker."""
        if self._mqtt_listener:
            _LOGGER.warning("MQTT listener is already running")
            return
        self._reconnects = 0
        self._mqtt_listener = asyncio.create_task(self.subscribe(hass, config_entry))

    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self._mqtt_listener:
            self._mqtt_listener.cancel()
            try:
                await self._mqtt_listener
            except asyncio.CancelledError:
                _LOGGER.info("MQTT listener task has been cancelled")
            self._mqtt_listener = None
        else:
            _LOGGER.warning("MQTT listener is not running")

    async def subscribe(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Subscribe to MQTT topics."""
        if not self._products:
            _LOGGER.error("No products found. Did you call setup before subscribing?")
            return

        while self._reconnects < self._max_reconnects:
            try:
                async with Client(
                    hostname=self._certification["url"],
                    port=int(self._certification["port"]),
                    username=self._certification["certificateAccount"],
                    password=self._certification["certificatePassword"],
                    logger=_CLIENT_LOGGER,
                    identifier=self._get_client_id(),
                    tls_insecure=False,
                    tls_params=aiomqtt.TLSParameters(
                        cert_reqs=ssl.CERT_REQUIRED,
                    ),
                ) as client:
                    topics_qos: list[tuple[str, int]] = [
                        (
                            f"/open/{self._certification["certificateAccount"]}/{device.serial_number}/status",
                            1,
                        )
                        for devices in self._products.values()
                        for device in devices.values()
                    ]
                    topics_qos += [
                        (
                            f"/open/{self._certification["certificateAccount"]}/{device.serial_number}/quota",
                            1,
                        )
                        for devices in self._products.values()
                        for device in devices.values()
                    ]
                    await client.subscribe(topics_qos)
                    async for message in client.messages:
                        if isinstance(message.payload, bytes):
                            await self._handle_mqtt_message(message)

            except MqttCodeError as exception:
                self._reconnects = self._reconnects + 1
                _LOGGER.exception(
                    "Exception during subscription. %s reconnects left",
                    self._max_reconnects - self._reconnects,
                )
                if self._reconnects == self._max_reconnects:
                    async_create_issue(
                        hass,
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

    async def _handle_mqtt_message(self, message):
        """Handle incoming MQTT messages.

        Args:
            message: MQTT message.

        """
        unpacked_json = json.loads(message.payload)
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
            if isinstance(self._data_holder, EcoFlowIoTOpenDataHolder):
                self._data_holder.update_params(
                    raw=unpacked_json["params"], serial_number=serial_number
                )
        else:
            _LOGGER.error("Device with serial number %s not found", serial_number)

    async def getDeviceQuota(self, serial_number: str) -> dict[str, Any]:
        """Retrieve quota information for a device.

        Args:
            serial_number (str): Serial number of the device.

        Returns:
            dict[str, Any]: Quota information.

        """
        params = {"sn": serial_number}
        headers = create_headers(self._accessKey, self._secretKey, params)
        response = await self._request(
            "GET",
            f"{self._base_url}/sign/device/quota/all",
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
        if isinstance(self._data_holder, EcoFlowIoTOpenDataHolder):
            for devices in self._products.values():
                for device in devices.values():
                    quota_data = await self.getDeviceQuota(device.serial_number)
                    self._data_holder.update_params(
                        raw=quota_data, serial_number=device.serial_number
                    )
        else:
            raise EcoFlowIoTOpenError("Missing EcoFlowIoTOpenDataHolder")

    def _get_client_id(self) -> str:
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

        return f"{HA_DOMAIN}_{environment}_{self._accessKey}"

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
                response_json = await response.json()
                sorted_response = recursively_sort_dict(response_json)
                _LOGGER.debug(sorted_response)
                return sorted_response
            _LOGGER.error(response)
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
    accessKey: str, secretKey: str, params: Optional[dict[str, str]] = None
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
