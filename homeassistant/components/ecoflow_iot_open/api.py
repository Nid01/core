"""API Interface for EcoFlow IoT Open Integration."""

import asyncio
import hashlib
import hmac
import json
import logging
import random
import ssl
import time
from typing import Any, Optional, TypeVar

from aiohttp import ClientSession
import aiomqtt
from aiomqtt import Client, MqttCodeError
from multidict import CIMultiDict

# from paho.mqtt import client as mqtt
from .const import DELTA_MAX, POWERSTREAM, SINGLE_AXIS_SOLAR_TRACKER, SMART_PLUG
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

# from .products.powerstream import PowerStream
# from .products.single_axis_solar_tracker import SingleAxisSolarTracker
# from .products.smart_plug import SmartPlug

# US: https://api-a.ecoflow.com
# EU: https://api-e.ecoflow.com
HOST = "api-e.ecoflow.com"
REST_BASE_URL = f"https://{HOST}/iot-open"
MQTT_HOST = "mqtt-e.ecoflow.com"
MQTT_PORT = 8883

_LOGGER = logging.getLogger(__name__)
_CLIENT_LOGGER = logging.getLogger(f"{__name__}.client")

ApiType = TypeVar("ApiType", bound="EcoFlowIoTOpenAPIInterface")


class EcoFlowIoTOpenAPIInterface:
    """API interface object."""

    def __init__(
        self,
        accessKey: str,
        secretKey: str,
        data_holder: EcoFlowIoTOpenDataHolder | None,
    ) -> None:
        """Create an EcoFlow IoT Open API interface object."""

        self._accessKey: str = accessKey
        self._secretKey: str = secretKey

        self._certificateAccount: str
        self._certificatePassword: str
        # self._products: dict[ProductType, dict[str, BaseDevice]] = {}
        self._products: dict[ProductType, dict[str, Any]] = {}
        self._mqtt_client: Client
        # self._mqtt_client: (
        #     mqtt.Client
        # )  # Done: replace with aiomqtt, to make the client thread safe?
        self.mqtt_listener: Optional[asyncio.Task] = None
        self._data_holder = data_holder

    @property
    def certificateAccount(self) -> str:
        """Return the current certificateAccount."""
        return self._certificateAccount

    @property
    def certificatePassword(self) -> str:
        """Return the current certificatePassword."""
        return self._certificatePassword

    @classmethod
    async def certification(
        cls: type[ApiType],
        accessKey: str,
        secretKey: str,
        data_holder: EcoFlowIoTOpenDataHolder | None,
    ) -> ApiType:
        """Connect to EcoFlow IoT Open API and fetch MQTT credentials."""

        this_class = cls(accessKey, secretKey, data_holder)
        await this_class._authenticate(accessKey, secretKey)
        return this_class

    # async def verify_mqtt_config(self) -> None:
    #     """Verify config by connecting to the broker."""
    #     try:
    #         async with await self._get_client():
    #             _LOGGER.debug("Connection successful")
    #     except AioMqttError as ex:
    #         _LOGGER.warning("Cannot connect", exc_info=True)
    #         raise MqttError("Cannot connect") from ex

    # async def _get_client(self) -> Client:
    #     """Get MQTT client."""
    #     return Client(
    #         hostname=MQTT_HOST,
    #         port=MQTT_PORT,
    #         username=self.certificateAccount,
    #         password=self.certificatePassword,
    #         logger=_CLIENT_LOGGER,
    #         identifier=self._get_client_id(),
    #     )

    async def _get_devices(self) -> None:
        """Get a list of all devices for this user."""
        headers = create_headers(self._accessKey, self._secretKey, None)
        _json_device_list = await self._request(
            "GET", f"{REST_BASE_URL}/sign/device/list", headers=headers, timeout=30
        )

        if _json_device_list.get("message") == "Success":
            products: dict[ProductType, dict[str, Any]] = {}
            tasks = []
            for _device in _json_device_list.get("data", {}):
                device: dict[str, Any] = _device
                tasks.append(self._process_device(device, products))

            await asyncio.gather(*tasks)
            self._products = products

    async def _process_device(self, device: dict[str, Any], products: dict) -> None:
        device_quota: dict = await self.getDeviceQuota(device["sn"])
        device.update(device_quota)
        sn_prefix: str = device["sn"][:4]
        if sn_prefix == DELTA_MAX:
            if ProductType.DELTA_MAX not in products:
                products[ProductType.DELTA_MAX] = {}
            deltaMax = DELTAMax(device, self)
            products[ProductType.DELTA_MAX][deltaMax.serial_number] = deltaMax
        elif sn_prefix == SINGLE_AXIS_SOLAR_TRACKER:
            if ProductType.SINGLE_AXIS_SOLAR_TRACKER not in products:
                products[ProductType.SINGLE_AXIS_SOLAR_TRACKER] = {}
            singleAxisSolarTracker = SingleAxisSolarTracker(device, self)
            products[ProductType.SINGLE_AXIS_SOLAR_TRACKER][
                singleAxisSolarTracker.serial_number
            ] = singleAxisSolarTracker
        elif sn_prefix == POWERSTREAM:
            if ProductType.POWERSTREAM not in products:
                products[ProductType.POWERSTREAM] = {}
            powerStream = PowerStream(device, self)
            products[ProductType.POWERSTREAM][powerStream.serial_number] = powerStream
        elif sn_prefix == SMART_PLUG:
            if ProductType.SMART_PLUG not in products:
                products[ProductType.SMART_PLUG] = {}
            smartPlug = SmartPlug(device, self)
            products[ProductType.SMART_PLUG][smartPlug.serial_number] = smartPlug

    # async def refresh_devices(self) -> None:
    #     """Refresh all devices for this user."""
    #     for _product in self._products.values():
    #         for _device in _product.values():
    #             _params = {"sn": _device.serial_number}
    #             _headers = create_headers(self._accessKey, self._secretKey, _params)
    #             _session = ClientSession()
    #             try:
    #                 async with _session.get(
    #                     f"{REST_BASE_URL}/sign/device/quota/all",
    #                     headers=_headers,
    #                     params=_params,
    #                 ) as response:
    #                     if response.status == 200:
    #                         _json_quota_all = await response.json()
    #                         _LOGGER.debug(_json_quota_all)
    #                     else:
    #                         raise GenericHTTPError(response.status)
    #             finally:
    #                 await _session.close()

    #             _device.update_device_info(_json_quota_all)

    async def get_devices_by_product(self, product_type: list[ProductType]) -> dict:
        """Get a list of all devices for this user."""
        if not self._products:
            await self._get_devices()

        # _products: dict[ProductType, dict[str, BaseDevice]] = {}
        _products: dict[ProductType, dict[str, Any]] = {}
        for _product_type in product_type:
            _products[_product_type] = {}
        for _devices in self._products.values():
            for _device in _devices.values():
                if _device.type in product_type:
                    _products[_device.type][_device.serial_number] = _device
        self._products = _products
        return _products

    async def _authenticate(self, accessKey: str, secretKey: str) -> None:
        """Authenticate in exchange for MQTT credentials."""
        headers = create_headers(accessKey, secretKey, None)
        _json = await self._request(
            "GET", f"{REST_BASE_URL}/sign/certification", headers=headers, timeout=30
        )
        if _json.get("message") == "Success":
            self._certificateAccount = _json["data"].get("certificateAccount")
            self._certificatePassword = _json["data"].get("certificatePassword")
        elif _json.get("message") == "accessKey is invalid":
            raise InvalidCredentialsError(_json)
        else:
            raise InvalidResponseFormat(_json)
        _LOGGER.info("Successfully retrieved MQTT credentials")

    async def connect(self):
        """Connect to EcoFlow IoT Open mqtt broker."""
        if self.mqtt_listener is not None:
            _LOGGER.warning("MQTT listener is already running")
            return
        self.mqtt_listener = asyncio.create_task(self.subscribe())

    async def disconnect(self):
        """Disconnect the MQTT listener."""
        if self.mqtt_listener:
            self.mqtt_listener.cancel()
            try:
                await self.mqtt_listener
            except asyncio.CancelledError:
                _LOGGER.info("MQTT listener task has been cancelled")
            self.mqtt_listener = None
        else:
            _LOGGER.warning("MQTT listener is not running")

    async def subscribe(self):
        """Subscribe to the MQTT updates."""
        try:
            while True:
                if not self._products:
                    _LOGGER.error(
                        "No products found. Did you call setup before subscribing?"
                    )
                    return False

                # class TLSParameters:
                #     ca_certs: str | None = None
                #     certfile: str | None = None
                #     keyfile: str | None = None
                #     cert_reqs: ssl.VerifyMode | None = None
                #     tls_version: Any | None = None
                #     ciphers: str | None = None
                #     keyfile_password: str | None = None

                async with Client(
                    hostname=MQTT_HOST,
                    port=MQTT_PORT,
                    username=self.certificateAccount,
                    password=self.certificatePassword,
                    logger=_CLIENT_LOGGER,
                    identifier=self._get_client_id(),
                    tls_insecure=False,
                    tls_params=aiomqtt.TLSParameters(
                        cert_reqs=ssl.CERT_REQUIRED,
                        certfile=None,
                        keyfile=None,
                    ),
                ) as client:
                    _topic_QoS: list = []
                    for _devices in self._products.values():
                        for _device in _devices.values():
                            _topic_QoS.append(
                                (
                                    f"/open/{self.certificateAccount}/{_device.serial_number}/status",
                                    1,
                                )
                            )
                            _topic_QoS.append(
                                (
                                    f"/open/{self.certificateAccount}/{_device.serial_number}/quota",
                                    1,
                                )
                            )
                    await client.subscribe(_topic_QoS)
                    async for message in client.messages:
                        if isinstance(message.payload, bytes):
                            unpacked_json: dict[str, Any] = json.loads(message.payload)
                            _LOGGER.debug("MQTT message from topic: %s", message.topic)
                            _LOGGER.debug(
                                json.dumps(unpacked_json, indent=2, sort_keys=True)
                            )
                            _serial_number: str = message.topic.value.split("/")[3]
                            _productType: ProductType = ProductType.UNKNOWN
                            _sn_prefix: str = _serial_number[:4]
                            if _sn_prefix == DELTA_MAX:
                                _productType = ProductType.DELTA_MAX
                            elif _sn_prefix == SINGLE_AXIS_SOLAR_TRACKER:
                                _productType = ProductType.SINGLE_AXIS_SOLAR_TRACKER
                            elif _sn_prefix == POWERSTREAM:
                                _productType = ProductType.POWERSTREAM
                            elif _sn_prefix == SMART_PLUG:
                                _productType = ProductType.SMART_PLUG

                            if _productType != ProductType.UNKNOWN:
                                # _device = self._products[_productType][_serial_number]
                                # _device.update_params(unpacked_json)

                                if unpacked_json.get("param"):
                                    unpacked_json["params"] = unpacked_json["param"]

                                if isinstance(unpacked_json.get("addr"), str):
                                    prefixed_params = {
                                        f"{unpacked_json.get("addr")}.{key}": value
                                        for key, value in unpacked_json[
                                            "params"
                                        ].items()
                                    }
                                    unpacked_json["params"] = prefixed_params
                                if isinstance(
                                    self._data_holder, EcoFlowIoTOpenDataHolder
                                ):
                                    self._data_holder.update_params(
                                        raw=unpacked_json["params"],
                                        # product=_productType.name,
                                        serial_number=_serial_number,
                                    )
                                # _device.update_device_info(unpacked_json)
                            else:
                                _LOGGER.error(
                                    "Device with serial number %s not found",
                                    _serial_number,
                                )
        except MqttCodeError:
            _LOGGER.exception("Exception during subscription")

    async def getDeviceQuota(self, serial_number: str) -> dict:
        """Retrieve device quota via HTTP request."""
        params = {"sn": serial_number}
        headers = create_headers(self._accessKey, self._secretKey, params)
        _json_device_quota_all = await self._request(
            "GET",
            f"{REST_BASE_URL}/sign/device/quota/all",
            headers=headers,
            params=params,
        )

        if _json_device_quota_all.get("message") == "Success":
            _sn_prefix: str = serial_number[:4]
            if _sn_prefix == POWERSTREAM:
                modified_prefix_params = {
                    f"iot.{str(key).split('.', 2)[-1]}": value
                    for key, value in _json_device_quota_all["data"].items()
                }
                _json_device_quota_all["data"] = modified_prefix_params
            return _json_device_quota_all.get("data", {})
        return {}

    async def initializeDevices(self) -> None:
        """Retrieve initial data of all devices via HTTP request."""

        if isinstance(self._data_holder, EcoFlowIoTOpenDataHolder):
            for _devices in self._products.values():
                for _device in _devices.values():
                    self._data_holder.update_params(
                        raw=await self.getDeviceQuota(_device.serial_number),
                        serial_number=_device.serial_number,
                    )
        else:
            raise EcoFlowIoTOpenError("Missing EcoFlowIoTOpenDataHolder")

    def _get_client_id(self) -> str:
        return f"HomeAssistant_{self._accessKey}"  # _{str(uuid.uuid4()).upper()}"

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make an HTTP request and handle the response."""
        async with (
            ClientSession() as session,
            session.request(method, url, **kwargs) as response,
        ):
            if response.status == 200:
                response_json = await response.json()
                response_json = recursively_sort_dict(response_json)
                _LOGGER.debug(response_json)
                return response_json

            _LOGGER.error(response)
            raise GenericHTTPError(response.status)


def hmac_sha256(data, key):
    """Create hash."""
    hashed = hmac.new(
        key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).digest()
    return "".join(format(byte, "02x") for byte in hashed)


def get_map(json_obj, prefix=""):
    """Get map."""

    def flatten(obj, pre=""):
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


def get_map_qstr(params: dict[str, str]):
    """Get query string."""
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def get_header_qstr(params: CIMultiDict[str]):
    """Get query string."""
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def create_headers(accessKey: str, secretKey: str, params=None) -> dict:
    """Create headers optionally with params and sign it."""
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
    """Recursively sort a dictionary by keys."""
    sorted_dict = {}
    for key, value in sorted(unsorted_dict.items()):
        if isinstance(value, dict):
            sorted_dict[key] = recursively_sort_dict(value)
        else:
            sorted_dict[key] = value
    return sorted_dict
