"""API Interface for EcoFlow IoT Open Integration."""

import hashlib
import hmac
import json
import random
import ssl
import time
from typing import Any, TypeVar

from aiohttp import ClientSession
from aiomqtt import Client, MqttError as AioMqttError
from deebot_client.logging_filter import get_logger
from multidict import CIMultiDict
from paho.mqtt import client as mqtt

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import DELTA_MAX, SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED, EcoFlowDevice
from .devices.delta_max import DELTAMax
from .errors import (
    EcoFlowIoTOpenError,
    GenericHTTPError,
    InvalidResponseFormat,
    MqttError,
)

HOST = "api.ecoflow.com"
REST_URL = f"https://{HOST}/iot-open"
MQTT_HOST = "mqtt-e.ecoflow.com"
MQTT_PORT = 8883
# HEADERS = {"accessKey": str, "nonce": str, "timestamp": str, "sign": str}

_LOGGER = get_logger(__name__)
_CLIENT_LOGGER = get_logger(f"{__name__}.client")

ApiType = TypeVar("ApiType", bound="EcoFlowIoTOpenAPI")


class EcoFlowIoTOpenAPI:
    """API interface object."""

    def __init__(
        self,
        hass: HomeAssistant,
        accessKey: str,
        secretKey: str,
    ) -> None:
        """Create an EcoFlow IoT Open API interface object."""

        self.hass = hass
        self._accessKey: str = accessKey
        self._secretKey: str = secretKey

        self._certificateAccount: str  # = certificateAccount
        self._certificatePassword: str  # = certificatePassword
        self.devices: dict[str, EcoFlowDevice] = {}
        # self.data: dict = {"device": {}}
        self._mqtt_client: mqtt.Client

    @property
    def certificateAccount(self) -> str:
        """Return the current certificateAccount."""
        return self._certificateAccount

    @property
    def certificatePassword(self) -> str:
        """Return the current certificatePassword."""
        return self._certificatePassword

    async def setup(self):
        """Connect to EcoFlow IoT Open API and fetch devices and MQTT credentials."""

        await self._get_devices()

        await self.authenticate()

    async def verify_mqtt_config(self) -> None:
        """Verify config by connecting to the broker."""
        try:
            async with await self._get_client():
                _LOGGER.debug("Connection successful")
        except AioMqttError as ex:
            _LOGGER.warning("Cannot connect", exc_info=True)
            raise MqttError("Cannot connect") from ex

    async def update_devices(self):
        """Update the registered devices."""
        for _device in self.devices.values():
            # device: dict[str, Any] = device
            # sn = _device["sn"]_device
            _headers = create_headers(
                self._accessKey, self._secretKey, {"sn": _device.serial_number}
            )
            async with (
                aiohttp_client.async_get_clientsession(self.hass) as session,
                session.get(
                    f"{REST_URL}/sign/device/quota/all",
                    headers=_headers,
                    params={"sn": _device.serial_number},
                    # , timeout=30
                ) as response,
            ):
                if response.status == 200:
                    _json = await response.json()
                    # _LOGGER.debug(_json)
                    if _json.get("message") == "Success":
                        _device.update_device_info(
                            _json.get("data")
                        )  # = _json.get("data")
                        # self.devices[_device.serial_number] = _device
                        _LOGGER.debug(
                            "Dispatching update to device %s: %s",
                            _device.serial_number,
                            _device,
                        )
                        dispatcher_send(
                            self.hass,
                            SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED.format(
                                "device", _device.serial_number
                            ),
                        )
                    else:
                        raise EcoFlowIoTOpenError(_json.get("message"))
                break

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

    # async def _get_devices(self):
    #     """Get a list of all the equipment for this user."""
    #     _headers = create_headers(self._accessKey, self._secretKey, None)
    #     async with (
    #         aiohttp_client.async_get_clientsession(self.hass) as session,
    #         session.get(
    #             f"{REST_URL}/sign/device/list",
    #             headers=_headers,
    #             # , timeout=30
    #         ) as response,
    #     ):
    #         if response.status == 200:
    #             _json = await response.json()
    #             _LOGGER.debug(_json)
    #             if _json.get("message") == "Success":
    #                 self._devices = _json.get("data")
    #                 # return self._equipment
    #             else:
    #                 raise InvalidResponseFormat()
    #         else:
    #             raise GenericHTTPError(response.status)

    async def _get_devices(self):
        """Get a list of all the equipment for this user."""
        _headers = create_headers(self._accessKey, self._secretKey, None)
        # _session = ClientSession()
        async with (
            aiohttp_client.async_get_clientsession(self.hass) as session,
            session.get(
                f"{REST_URL}/sign/device/list", headers=_headers, timeout=30
            ) as response,
        ):
            # response: requests.Response = requests.get(f"{REST_URL}/sign/device/list", headers=_headers)
            # requests.get(f"{REST_URL}/sign/device/list", headers=_headers, timeout=30) #as resp:
            if response.status == 200:
                _json = await response.json()
                _LOGGER.debug(_json)
                if _json.get("message") == "Success":
                    for device in _json.get("data", {}):
                        _device: dict[str, Any] = device
                        # _device_obj: Equipment = None
                        if str(_device.get("sn")).startswith(DELTA_MAX):
                            _device_obj = DELTAMax(_device)
                            self.devices[_device_obj.serial_number] = _device_obj
                        # self.devices =
                        break
                    # return self._equipment
                else:
                    raise InvalidResponseFormat()
            else:
                raise GenericHTTPError(response.status)

    # async def refresh_devices(self) -> None:
    #     """Get a list of all the devices for this"""

    async def authenticate(self) -> None:
        """Authenticate in exchange for MQTT credentials."""

        _session = ClientSession()
        _headers = create_headers(self._accessKey, self._secretKey, None)
        async with _session.get(
            f"{REST_URL}/sign/certification", headers=_headers, timeout=30
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
                    raise InvalidResponseFormat()
            else:
                raise GenericHTTPError(resp.status)
            await _session.close()
        _LOGGER.info("Successfully retrieved MQTT credentials")

    def subscribe(self):
        """Subscribe to the MQTT updates."""

        if not self.devices:
            _LOGGER.error(
                "Devices list is empty, did you call setup before subscribing?"
            )
            return False

        self._mqtt_client = mqtt.Client(
            client_id=self._get_client_id(),
            clean_session=True,
            reconnect_on_failure=False,  # True,
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
        self._mqtt_client.connect_async(MQTT_HOST, MQTT_PORT, 30)
        self._mqtt_client.loop_start()

    def unsubscribe(self) -> None:
        """Unsubscribe to the MQTT updates."""

        self._mqtt_client.loop_stop(force=True)

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
                for device in self.devices:
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

    def _on_disconnect(self, client: mqtt.Client, userdata: None, result_code: int):
        _LOGGER.debug("Disconnected with result code: %s", str(result_code))
        if result_code != 0:
            # _LOGGER.error("EcoFlowIoTOpen MQTT unexpected disconnect. Attempting to reconnect")
            # client.reconnect()
            _LOGGER.error(
                "EcoFlowIoTOpen MQTT unexpected disconnect. Attempting no reconnect"
            )

    def _on_message(self, client: mqtt.Client, userdata: None, msg: mqtt.MQTTMessage):
        """When a MQTT message comes in push that update to the specified devices."""
        # try:
        unpacked_json = json.loads(msg.payload)
        _LOGGER.debug("MQTT message from topic: %s", msg.topic)
        _LOGGER.debug(json.dumps(unpacked_json, indent=2))
        _serial: str = msg.topic.split("/")[3]
        device = self.devices.get(_serial)
        if device is not None:
            device.update_device_info(unpacked_json)
        else:
            _LOGGER.error("Device with serial %s not found", _serial)
        # except Exception as e:
        #     _LOGGER.exception(e)
        #     _LOGGER.error("Failed to parse the following MQTT message: %s", msg.payload)

    def _get_client_id(self) -> str:
        # time_string = str(time.time()).replace(".", "")[:13]
        return f"{self._accessKey}_HomeAssistant"  # _{time_string}"


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
    # headers = _session._prepare_headers(headers)
    sign_str = (get_map_qstr(get_map(params)) + "&" if params else "") + get_map_qstr(
        headers
    )
    headers["sign"] = hmac_sha256(sign_str, secretKey)
    return headers


# def get_json_response(response):
#     """Extract json payload from response."""

#     payload = None

#     try:
#         payload = json.loads(response.text)
#         response_message = payload["message"]
#     except KeyError as key:
#         raise EcoFlowIoTOpenError(
#             f"Failed to extract key {key} from {payload}"
#         ) from key
#     except Exception as error:
#         raise EcoFlowIoTOpenError(
#             f"Failed to parse response: {response.text} Error: {error}"
#         ) from error

#     if response_message.lower() != "success":
#         raise EcoFlowIoTOpenError(f"{response_message}")

#     return payload
