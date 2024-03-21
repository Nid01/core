"""API Interface for EcoFlow IoT Open Integration."""
import hashlib
import hmac
import logging
import random
import ssl
import time
from typing import TypeVar

from aiohttp import ClientSession
import paho.mqtt.client as mqtt

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED
from .errors import GenericHTTPError, InvalidResponseFormat

HOST = "api.ecoflow.com"
REST_URL = "https://{HOST}/iot-open"
MQTT_HOST = "mqtt.ecoflow.com"
# HEADERS = {"accessKey": str, "nonce": str, "timestamp": str, "sign": str}

_LOGGER = logging.getLogger(__name__)

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
        self._devices: dict = {}
        self.data: dict = {"device": {}}
        self._mqtt_client = None
        self.mqtt_port = 8883

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

        await self._authenticate()

    async def update_devices(self):
        """Update the registered devices."""

        _session = ClientSession()
        for _device in self._devices:
            sn = _device["sn"]
            _headers = create_headers(self._accessKey, self._secretKey, None)
            async with _session.get(
                f"{REST_URL}/sign/device/quota/all?={_device["sn"]}",
                headers=_headers,
                timeout=30,
            ) as resp:
                if resp.status == 200:
                    _json = await resp.json()
                    _LOGGER.debug(_json)
                    if _json.get("message") == "success":
                        _device["sn"] = _json
                        self.data["device"][sn] = _device
                        _LOGGER.debug(
                            "Dispatching update to device %s: %s",
                            sn,
                            _device,
                        )
                        dispatcher_send(
                            self.hass,
                            SIGNAL_ECOFLOW_IOT_OPEN_UPDATE_RECEIVED.format(
                                "device", sn
                            ),
                        )

    async def _get_devices(self):
        """Get a list of all the equipment for this user."""
        _headers = create_headers(self._accessKey, self._secretKey, None)
        _session = ClientSession()
        async with _session.get(
            f"{REST_URL}/sign/device/list", header=_headers, timeout=30
        ) as resp:
            if resp.status == 200:
                _json = await resp.json()
                _LOGGER.debug(_json)
                if _json.get["message"] == "success":
                    self._devices = _json.get("data")
                    # return self._equipment
                else:
                    raise InvalidResponseFormat()
            else:
                raise GenericHTTPError(resp.status)
        await _session.close()

    async def _authenticate(self) -> None:
        """Authenticate in exchange for MQTT credentials."""

        _headers = create_headers(self._accessKey, self._secretKey, None)
        _session = ClientSession()
        async with _session.get(
            f"{REST_URL}/sign/certification", headers=_headers, timeout=30
        ) as resp:
            if resp.status == 200:
                _json = await resp.json()
                _LOGGER.debug(_json)
                if _json.get["message"] == "success":
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

        if not self.data.get("device"):
            _LOGGER.error(
                "Devices list is empty, did you call setup before subscribing?"
            )
            return False

        self._mqtt_client = mqtt.Client(
            self._get_client_id(), clean_session=True, reconnect_on_failure=True
        )
        self._mqtt_client.username_pw_set(
            self.certificateAccount, self.certificatePassword
        )
        self._mqtt_client.tls_set(
            certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED
        )
        self._mqtt_client.tls_insecure_set(False)
        self._mqtt_client.on_connect = self._on_connect

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):
        _LOGGER.debug("Connected with result code: %s", str(rc))
        for device in self.data["device"]:
            client.subscribe(
                f"	/open/${self.certificateAccount}/${device["sn"]}/quota"
            )

    def _get_client_id(self) -> str:
        time_string = str(time.time()).replace(".", "")[:13]
        return f"{self._accessKey}_HomeAssistant_{time_string}"


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


def get_qstr(params: dict[str, str]):
    """Get query string."""
    return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])


def create_headers(accessKey, secretKey, params=None) -> dict:
    """Create headers optionally with params and sign it."""
    nonce = str(random.randint(100000, 999999))
    timestamp = str(int(time.time() * 1000))
    headers = {"accessKey": accessKey, "nonce": nonce, "timestamp": timestamp}
    sign_str = (get_qstr(get_map(params)) + "&" if params else "") + get_qstr(headers)
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
