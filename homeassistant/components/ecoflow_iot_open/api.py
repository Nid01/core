"""API Interface for EcoFlow IoT Open Integration."""
import hashlib
import hmac
import json
import logging
import random
import time
from typing import TypeVar

from aiohttp import ClientSession

from .errors import EcoFlowIoTOpenError, GenericHTTPError, InvalidResponseFormat

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
        accessKey: str,
        secretKey: str,
        # Arguments missing for parameters "certificateAccount", "certificatePassword"PylancereportCallIssue" for "cls(accessKey, secretKey)
        # certificateAccount: str,
        # certificatePassword: str,
    ) -> None:
        """Create an EcoFlow IoT Open API interface object.

        Args:
            accessKey (str): accessKey for EcoFlow IoT Open API generated on https://developer-eu.ecoflow.com/us/security.
            secretKey (str): secretKey for EcoFlow IoT Open API generated on https://developer-eu.ecoflow.com/us/security.

        """

        self.accessKey: str = accessKey
        self.secretKey: str = secretKey
        # self.mqtt_port = 8883
        self._certificateAccount: str  # = certificateAccount
        self._certificatePassword: str  # = certificatePassword
        self._devices: dict = {}
        self._mqtt_client = None

    @property
    def certificateAccount(self) -> str:
        """Return the current certificateAccount."""
        return self._certificateAccount

    @property
    def certificatePassword(self) -> str:
        """Return the current certificatePassword."""
        return self._certificatePassword

    @classmethod
    async def login(cls: type[ApiType], accessKey: str, secretKey: str) -> ApiType:
        """Create an EcoFlowIoTOpenAPI object using accessKey and secretKey.

        Args:
            accessKey (str): accessKey for EcoFlow IoT Open API generated on https://developer-eu.ecoflow.com/us/security.
            secretKey (str): secretKey for EcoFlow IoT Open API generated on https://developer-eu.ecoflow.com/us/security.

        """
        # Arguments missing for parameters "certificateAccount", "certificatePassword"PylancereportCallIssue" for "cls(accessKey, secretKey)
        this_class = cls(accessKey, secretKey)
        await this_class._authenticate(accessKey, secretKey)
        return this_class

    async def _authenticate(self, accessKey: str, secretKey: str) -> None:
        # """Authenticate against {REST_URL}/sign/certification in exchange for MQTT credentials."""

        _headers = create_headers(accessKey, secretKey, None)
        _session = ClientSession()
        async with _session.get(
            f"{REST_URL}/sign/certification", headers=_headers, timeout=30
        ) as resp:
            if resp.status == 200:
                _json = await resp.json()
                _LOGGER.debug(_json)
                # @Nid01 - 20240320: does if _json.get("message")["success"]: work, too?
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

    # async def get_devices_by_model(self, device_model: list) -> dict:
    #     """Get a list of equipment by the equipment model"""
    #     if not self._devices:
    #         await self._get_devices()

    #     deviceListUrl = self.IoTOpen_url + "/sign/device/list"

    #     payload = create_headers(deviceListUrl, self.accessKey, self.secretKey)

    #     try:
    #         self.devices = payload["data"]
    #     except KeyError as key:
    #         raise EcoFlowIoTOpenError(
    #             f"Failed to extract key {key} from {payload}"
    #         ) from key


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
    # response = requests.get(url, headers=headers, json=params, timeout=30)

    # if response.status_code != 200:
    #     raise EcoFlowIoTOpenException(
    #         "Got HTTP status code {response.status_code}: {response.text}"
    #     )

    # return get_json_response(response)
    return headers


def get_json_response(response):
    """Extract json payload from response."""

    payload = None

    try:
        payload = json.loads(response.text)
        response_message = payload["message"]
    except KeyError as key:
        raise EcoFlowIoTOpenError(
            f"Failed to extract key {key} from {payload}"
        ) from key
    except Exception as error:
        raise EcoFlowIoTOpenError(
            f"Failed to parse response: {response.text} Error: {error}"
        ) from error

    if response_message.lower() != "success":
        raise EcoFlowIoTOpenError(f"{response_message}")

    return payload
