import attr
import random
import paho.mqtt.client
import urllib.request
import asyncio
import aiohttp
from ._common import log, kw_only
from . import _util, _exception, _session, _events

from typing import AsyncGenerator, Optional, List

from yarl import URL

try:
    import socks
except ImportError:
    socks = None

TOPICS = [
    # Things that happen in chats (e.g. messages)
    "/t_ms",
    # Group typing notifications
    "/thread_typing",
    # Private chat typing notifications
    "/orca_typing_notifications",
    # Active notifications
    "/orca_presence",
    # Other notifications not related to chats (e.g. friend requests)
    "/legacy_web",
    # Facebook's continuous error reporting/logging?
    "/br_sr",
    # Response to /br_sr
    "/sr_res",
    # Data about user-to-user calls
    # TODO: Investigate the response from this! (A bunch of binary data)
    # "/t_rtc",
    # TODO: Find out what this does!
    # TODO: Investigate the response from this! (A bunch of binary data)
    # "/t_p",
    # TODO: Find out what this does!
    "/webrtc",
    # TODO: Find out what this does!
    "/onevc",
    # TODO: Find out what this does!
    "/notify_disconnect",
    # Old, no longer active topics
    # These are here just in case something interesting pops up
    "/inbox",
    "/mercury",
    "/messaging_events",
    "/orca_message_notifications",
    "/pp",
    "/webrtc_response",
]


def get_cookie_header(session: aiohttp.ClientSession, url: str) -> str:
    """Extract a cookie header from a requests session."""
    pass


def generate_session_id() -> int:
    """Generate a random session ID between 1 and 9007199254740991."""
    pass


def mqtt_factory(domain: str) -> paho.mqtt.client.Client:
    # Configure internal MQTT handler
    pass


@attr.s(slots=True, kw_only=kw_only, eq=False, auto_attribs=True)
class Listener:
    """Listen to incoming Facebook events.

    Initialize a connection to the Facebook MQTT service.

    Args:
        session: The session to use when making requests.
        chat_on: Whether ...
        foreground: Whether ...

    Example:
        >>> listener = fbchat.Listener(session, chat_on=True, foreground=True)
    """

    session: _session.Session
    _chat_on: bool
    _foreground: bool
    _loop: asyncio.AbstractEventLoop = attr.ib(factory=asyncio.get_event_loop)
    _mqtt: paho.mqtt.client.Client = None
    _disconnect_error: Optional[Exception] = None
    _sync_token: Optional[str] = None
    _sequence_id: Optional[int] = None
    _sequence_id_wait: Optional[asyncio.Future] = None
    _tmp_events: List[_events.Event] = attr.ib(factory=list)
    _message_queue: asyncio.Queue = attr.ib(factory=lambda: asyncio.Queue(maxsize=64))

    def __attrs_post_init__(self):
        self._mqtt = mqtt_factory(self.session.domain)
        self._mqtt.on_message = self._on_message_handler
        self._mqtt.on_connect = self._on_connect_handler
        self._mqtt.on_socket_open = self.on_socket_open
        self._mqtt.on_socket_close = self.on_socket_close
        self._mqtt.on_socket_register_write = self.on_socket_register_write
        self._mqtt.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        pass

    def on_socket_close(self, client, userdata, sock):
        pass

    def on_socket_register_write(self, client, userdata, sock):
        pass

    def on_socket_unregister_write(self, client, userdata, sock):
        pass

    def _handle_ms(self, j):
        """Handle /t_ms special logic.

        Returns whether to continue parsing the message.
        """
        pass

    def _on_message_handler(self, client, userdata, message):
        # Parse payload JSON
        pass

    def _on_connect_handler(self, client, userdata, flags, rc):
        pass

    def _messenger_queue_publish(self):
        # configure receiving messages.
        pass

    def _configure_connect_options(self):
        # Generate a new session ID on each reconnect
        pass

    async def _reconnect(self) -> None:
        # Try reconnecting
        pass

    def set_sequence_id(self, sequence_id: int) -> None:
        pass

    async def listen(self) -> AsyncGenerator[_events.Event, Optional[bool]]:
        """Run the listening loop continually.

        This is a blocking call, that will yield events as they arrive.

        Example:
            Print events continually.

            >>> listener = Listener(session)
            >>> async for event in listener.listen():
            ...     print(event)
        """
        pass

    def disconnect(self) -> None:
        """Disconnect the MQTT listener.

        Can be called while listening, which will stop the listening loop.

        The `Listener` object should not be used after this is called!

        Example:
            Stop the listener when receiving a message with the text "/stop"

            >>> for event in listener.listen():
            ...     if isinstance(event, fbchat.MessageEvent):
            ...         if event.message.text == "/stop":
            ...             listener.disconnect()  # Almost the same "break"
        """
        pass

    def set_foreground(self, value: bool) -> None:
        """Set the ``foreground`` value while listening."""
        pass
        # TODO: We can't wait for this, since the loop is running within the same thread
        # info.wait_for_publish()

    def set_chat_on(self, value: bool) -> None:
        """Set the ``chat_on`` value while listening."""
        pass
        # TODO: We can't wait for this, since the loop is running within the same thread
        # info.wait_for_publish()

    # def send_additional_contacts(self, additional_contacts):
    #     payload = _util.json_minimal({"additional_contacts": additional_contacts})
    #     info = self._mqtt.publish("/send_additional_contacts", payload=payload, qos=1)
    #
    # def browser_close(self):
    #     info = self._mqtt.publish("/browser_close", payload=b"{}", qos=1)
