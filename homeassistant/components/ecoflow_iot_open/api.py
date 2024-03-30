"""API Interface for EcoFlow IoT Open Integration."""

import hashlib
import hmac
import json
import logging
import random
import ssl
import time
from typing import TypeVar

from aiohttp import ClientSession
from aiomqtt import Client, MqttError as AioMqttError
from multidict import CIMultiDict
from paho.mqtt import client as mqtt

from .devices import DELTA_MAX
from .devices.delta_max import DELTAMax
from .errors import GenericHTTPError, InvalidResponseFormat, MqttError

HOST = "api.ecoflow.com"
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
    ) -> None:
        """Create an EcoFlow IoT Open API interface object."""

        self._accessKey: str = accessKey
        self._secretKey: str = secretKey

        self._certificateAccount: str
        self._certificatePassword: str
        self._devices: dict = {}
        self._mqtt_client: mqtt.Client

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
        cls: type[ApiType], accessKey: str, secretKey: str
    ) -> ApiType:
        """Connect to EcoFlow IoT Open API and fetch MQTT credentials."""

        this_class = cls(accessKey, secretKey)
        await this_class._authenticate(accessKey, secretKey)
        return this_class

    async def verify_mqtt_config(self) -> None:
        """Verify config by connecting to the broker."""
        try:
            async with await self._get_client():
                _LOGGER.debug("Connection successful")
        except AioMqttError as ex:
            _LOGGER.warning("Cannot connect", exc_info=True)
            raise MqttError("Cannot connect") from ex

    async def _get_client(self) -> Client:
        """Get MQTT client."""
        return Client(
            hostname=MQTT_HOST,
            port=MQTT_PORT,
            username=self.certificateAccount,
            password=self.certificatePassword,
            logger=_CLIENT_LOGGER,
            identifier=self._get_client_id(),
        )

    async def _get_devices(self) -> None:
        """Get a list of all devices for this user."""
        _headers = create_headers(self._accessKey, self._secretKey, None)
        _session = ClientSession()
        try:
            async with _session.get(
                f"{REST_BASE_URL}/sign/device/list", headers=_headers
            ) as response:
                if response.status == 200:
                    _json_device_list = await response.json()
                    _LOGGER.debug(_json_device_list)
                else:
                    raise GenericHTTPError(response.status)
        finally:
            await _session.close()

        if _json_device_list.get("message") == "Success":
            for _device in _json_device_list.get("data", {}):
                if str(_device.get("sn"))[:4] == DELTA_MAX:
                    _device_obj = DELTAMax(_device, self)
                    self._devices[_device_obj.serial_number] = _device_obj

    async def refresh_devices(self) -> None:
        """Refresh all devices for this user."""
        for _device in self._devices.values():
            _params = {"sn": _device.get("sn")}
            _headers = create_headers(self._accessKey, self._secretKey, _params)
            _session = ClientSession()
            try:
                async with _session.get(
                    f"{REST_BASE_URL}/sign/device/quota/all",
                    headers=_headers,
                    params=_params,
                ) as response:
                    if response.status == 200:
                        _json_quota_all = await response.json()
                        _LOGGER.debug(_json_quota_all)
                    else:
                        raise GenericHTTPError(response.status)
            finally:
                await _session.close()

            _device.update_device_info(_json_quota_all)

    async def get_devices(self, product_type: list) -> dict:
        """Get a list of all devices for this user."""
        if not self._devices:
            await self._get_devices()

        _devices: dict = {}
        for _product_type in product_type:
            _devices[_product_type] = []
        for value in self._devices.values():
            if value.type in product_type:
                _devices[value.type].append(value)
        return _devices

    async def _authenticate(self, accessKey: str, secretKey: str) -> None:
        """Authenticate in exchange for MQTT credentials."""

        _session = ClientSession()
        _headers = create_headers(accessKey, secretKey, None)
        async with _session.get(
            f"{REST_BASE_URL}/sign/certification", headers=_headers, timeout=30
        ) as resp:
            if resp.status == 200:
                _json = await resp.json()
                _LOGGER.debug(_json)
                if _json.get("message") == "Success":
                    self._certificateAccount = _json.get("data").get(
                        "certificateAccount"
                    )
                    self._certificatePassword = _json.get("data").get(
                        "certificatePassword"
                    )
                else:
                    raise InvalidResponseFormat(_json)
            else:
                raise GenericHTTPError(resp.status)
            await _session.close()
        _LOGGER.info("Successfully retrieved MQTT credentials")

    def subscribe(self):
        """Subscribe to the MQTT updates."""

        if not self._devices:
            _LOGGER.error(
                "Devices list is empty, did you call setup before subscribing?"
            )
            return False

        self._mqtt_client = mqtt.Client(
            client_id=self._get_client_id(),
            clean_session=True,
            reconnect_on_failure=True,
        )
        self._mqtt_client.username_pw_set(
            self.certificateAccount, self.certificatePassword
        )
        self._mqtt_client.tls_set(
            certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED
        )
        self._mqtt_client.tls_insecure_set(False)
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.connect_async(MQTT_HOST, MQTT_PORT)
        self._mqtt_client.loop_start()

    def unsubscribe(self) -> None:
        """Unsubscribe to the MQTT updates."""
        self._mqtt_client.loop_stop(force=True)

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._mqtt_client.disconnect()

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: None,
        _flags: dict[str, int],
        result_code: int,
    ):
        match result_code:
            case 0:
                _LOGGER.debug("Connected with result code: %s", str(result_code))
                topics_QoSs = []
                for device in self._devices:
                    topics_QoSs.append(
                        (f"/open/{self.certificateAccount}/{device}/status", 1)
                    )
                    topics_QoSs.append(
                        (f"/open/{self.certificateAccount}/{device}/quota", 1)
                    )
                client.subscribe(topics_QoSs)
            case -1:
                _LOGGER.error("Failed to connect to MQTT: connection timed out")
            case 1:
                _LOGGER.error("Failed to connect to MQTT: incorrect protocol version")
            case 2:
                _LOGGER.error("Failed to connect to MQTT: invalid client identifier")
            case 3:
                _LOGGER.error("Failed to connect to MQTT: server unavailable")
            case 4:
                _LOGGER.error("Failed to connect to MQTT: bad username or password")
            case 5:
                _LOGGER.error("Failed to connect to MQTT: not authorised")
            case _:
                _LOGGER.error(
                    "Failed to connect to MQTT: another error occurred: %s", result_code
                )

    def _on_message(self, client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage):
        """When a MQTT message comes in push that update to the specified devices."""
        unpacked_json = json.loads(msg.payload)
        _LOGGER.debug("MQTT message from topic: %s", msg.topic)
        _LOGGER.debug(json.dumps(unpacked_json, indent=2))
        _serial_number: str = msg.topic.split("/")[3]
        device = self._devices.get(_serial_number)
        if device is not None:
            device.update_device_info(unpacked_json)
        else:
            _LOGGER.error("Device with serial %s not found", _serial_number)

    def _on_disconnect(self, client: mqtt.Client, userdata: None, result_code: int):
        _LOGGER.debug("Disconnected with result code: %s", str(result_code))
        if result_code != 0:
            _LOGGER.error(
                "EcoFlowIoTOpen MQTT unexpected disconnect. Attempting no reconnect"
            )

    def _get_client_id(self) -> str:
        return f"{self._accessKey}_HomeAssistant"


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
