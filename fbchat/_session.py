import attr
import datetime
import aiohttp
import random
import re
import json
import os
import time
import errno
import string
import urllib.request
from yarl import URL
from http.cookies import SimpleCookie, BaseCookie

# TODO: Only import when required
# Or maybe just replace usage with `html.parser`?
import bs4

from ._common import log, req_log, kw_only
from . import _graphql, _util, _exception

from typing import Optional, Mapping, Callable, Any, Awaitable, Dict, List, NamedTuple

try:
    from aiohttp_socks import ProxyType, ProxyConnector, ProxyTimeoutError
except ImportError:
    ProxyType = None
    ProxyConnector = None


    class ProxyTimeoutError(Exception):
        pass

SERVER_JS_DEFINE_REGEX = re.compile(r'(?:'
                                    r'\(new ServerJS\(\)\)(?:;s)?'
                                    r'|\(require\("ServerJS(?:Define)?"\)\)\(\)'
                                    r').handle(?:Defines|WithCustomApplyEach)?\('
                                    r'(?:ScheduledApplyEach,)?')
SERVER_JS_DEFINE_JSON_DECODER = json.JSONDecoder()


def write_html_to_temp(html: str) -> str:
    random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    file_path = f"/tmp/fbchat-debug/serverjsdefine-{int(time.time())}-{random_id}"
    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    with open(file_path, "w") as file:
        file.write(html)
    return file_path


def parse_server_js_define(html: str) -> Mapping[str, Any]:
    """Parse ``ServerJSDefine`` entries from a HTML document."""
    # Find points where we should start parsing
    define_splits = SERVER_JS_DEFINE_REGEX.split(html)

    # TODO: Extract jsmods "require" and "define" from `bigPipe.onPageletArrive`?

    # Skip leading entry
    _, *define_splits = define_splits

    if not define_splits:
        file_name = write_html_to_temp(html)
        raise _exception.ParseError("Could not find any ServerJSDefine", data_file=file_name)
    # if len(define_splits) > 2:
    #     file_name = write_html_to_temp(html)
    #     raise _exception.ParseError("Found too many ServerJSDefine", data_file=file_name)
    try:
        parsed, _ = SERVER_JS_DEFINE_JSON_DECODER.raw_decode(define_splits[0], idx=0)
    except json.JSONDecodeError as e:
        file_name = write_html_to_temp(html)
        raise _exception.ParseError("Invalid ServerJSDefine: not json", data_file=file_name) from e
    try:
        rtn = parsed["define"]
    except KeyError:
        file_name = write_html_to_temp(html)
        raise _exception.ParseError("Invalid ServerJSDefine: missing define key",
                                    data_file=file_name)

    if not isinstance(rtn, list):
        file_name = write_html_to_temp(html)
        raise _exception.ParseError("Invalid ServerJSDefine: define value is not a list",
                                    data_file=file_name)

    # Convert to a dict
    return _util.get_jsmods_define(rtn)


def parse_kv(vals: List[str]) -> Dict[str, str]:
    pass


class AltSvc(NamedTuple):
    alt_authority: str
    max_age: int
    persist: bool
    extra_meta: Dict[str, str]


def parse_alt_svc(r: aiohttp.ClientResponse) -> Dict[str, AltSvc]:
    pass


def base36encode(number: int) -> str:
    """Convert from Base10 to Base36."""
    # Taken from https://en.wikipedia.org/wiki/Base36#Python_implementation
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"

    sign = "-" if number < 0 else ""
    number = abs(number)
    result = ""

    while number > 0:
        number, remainder = divmod(number, 36)
        result = chars[remainder] + result

    return sign + result


def generate_message_id(now: datetime.datetime, client_id: str) -> str:
    k = _util.datetime_to_millis(now)
    l = int(random.random() * 4294967295)
    return "<{}:{}-{}@mail.projektitan.com>".format(k, l, client_id)


def get_user_id(domain: str, session: aiohttp.ClientSession) -> str:
    pass


def session_factory(domain: str, user_agent: Optional[str] = None) -> aiohttp.ClientSession:
    from . import __version__
    connector = None
    try:
        http_proxy = urllib.request.getproxies()["http"]
    except KeyError:
        pass
    else:
        if ProxyConnector:
            connector = ProxyConnector.from_url(http_proxy)
        else:
            log.warning("http_proxy is set, but aiohttp-socks is not installed")
    return aiohttp.ClientSession(connector=connector,
                                 headers={
                                     "Referer": f"https://www.{domain}/",
                                     "User-Agent": user_agent or f"fbchat-asyncio/{__version__}",
                                 })


def login_cookies(at: datetime.datetime):
    pass


def client_id_factory() -> str:
    return hex(int(random.random() * 2 ** 31))[2:]


def find_form_request(html: str):
    soup = bs4.BeautifulSoup(html, "html.parser", parse_only=bs4.SoupStrainer("form"))

    form = soup.form
    if not form:
        raise _exception.ParseError("Could not find form to submit", data=html)

    url = form.get("action")
    if not url:
        raise _exception.ParseError("Could not find url to submit to", data=form)

    # From what I've seen, it'll always do this!
    if url.startswith("/"):
        url = "https://www.facebook.com" + url

    # It's okay to set missing values to something crap, the values are localized, and
    # hence are not available in the raw HTML
    data = {
        x["name"]: x.get("value", "[missing]")
        for x in form.find_all(["input", "button"])
    }
    return url, data


async def two_factor_helper(session: aiohttp.ClientSession, r: aiohttp.ClientResponse,
                            on_2fa_callback: Callable[[], Awaitable[int]]) -> str:
    pass


def get_error_data(html: str) -> Optional[str]:
    """Get error message from a request."""
    soup = bs4.BeautifulSoup(
        html, "html.parser", parse_only=bs4.SoupStrainer("form", id="login_form")
    )
    # Attempt to extract and format the error string
    # The error message is in the user's own language!
    return " ".join(list(soup.stripped_strings)[1:3]) or None


def get_fb_dtsg(define) -> Optional[str]:
    pass


def prefix_url(domain: str, path: str) -> URL:
    if path.startswith("/"):
        return URL(f"https://www.{domain}" + path)
    return URL(path)


@attr.s(slots=True, kw_only=kw_only, repr=False, eq=False, auto_attribs=True)
class Session:
    """Stores and manages state required for most Facebook requests.

    This is the main class, which is used to login to Facebook.
    """

    _user_id: str
    _fb_dtsg: str
    _revision: int
    domain: str
    _onion: Optional[str] = None
    _session: aiohttp.ClientSession = attr.ib(factory=session_factory)
    _counter: int = 0
    _client_id: str = attr.ib(factory=client_id_factory)

    def _prefix_url(self, path: str) -> URL:
        pass

    @property
    def user(self):
        """The logged in user."""
        pass

    def __repr__(self) -> str:
        # An alternative repr, to illustrate that you can't create the class directly
        return "<fbchat.Session user_id={}>".format(self._user_id)

    def _get_params(self):
        pass

    @classmethod
    async def login(cls, email: str, password: str,
                    on_2fa_callback: Callable[[], Awaitable[int]] = None,
                    user_agent: Optional[str] = None) -> 'Session':
        """Login the user, using ``email`` and ``password``.

        Args:
            email: Facebook ``email``, ``id`` or ``phone number``
            password: Facebook account password
            on_2fa_callback: Function that will be called, in case a two factor
                authentication code is needed. This should return the requested code.

                Tested using SMS and authentication applications. If you have both
                enabled, you might not receive an SMS code, and you'll have to use the
                authentication application.

                Note: Facebook limits the amount of codes they will give you, so if you
                don't receive a code, be patient, and try again later!
            user_agent: The user agent to send to Facebook

        Example:
            >>> import fbchat
            >>> import getpass
            >>> session = fbchat.Session.login(
            ...     input("Email: "),
            ...     getpass.getpass(),
            ...     on_2fa_callback=lambda: input("2FA Code: ")
            ... )
            Email: abc@gmail.com
            Password: ****
            2FA Code: 123456
            >>> session.user.id
            "1234"
        """
        pass

    async def is_logged_in(self) -> bool:
        """Send a request to Facebook to check the login status.

        Returns:
            Whether the user is still logged in

        Example:
            >>> assert session.is_logged_in()
        """
        pass

    async def logout(self) -> None:
        """Safely log out the user.

        The session object must not be used after this action has been performed!

        Example:
            >>> session.logout()
        """
        pass

    @classmethod
    async def _from_session(cls, session: aiohttp.ClientSession, domain: str
                            ) -> Optional['Session']:
        # TODO: Automatically set user_id when the cookie changes in the session
        pass

    def get_cookies(self) -> Optional[Mapping[str, str]]:
        """Retrieve session cookies, that can later be used in `from_cookies`.

        Returns:
            A dictionary containing session cookies

        Example:
            >>> cookies = session.get_cookies()
        """
        pass

    @classmethod
    async def from_cookies(cls, cookies: Mapping[str, str], user_agent: Optional[str] = None,
                           domain: str = "messenger.com") -> 'Session':
        """Load a session from session cookies.

        Args:
            cookies: A dictionary containing session cookies

        Example:
            >>> cookies = session.get_cookies()
            >>> # Store cookies somewhere, and then subsequently
            >>> session = fbchat.Session.from_cookies(cookies)
        """
        pass

    async def _post(self, url, data, files=None, as_graphql=False):
        pass

    async def _payload_post(self, url, data, files=None):
        pass

    async def _graphql_requests(self, *queries):
        # TODO: Explain usage of GraphQL, probably in the docs
        # Perhaps provide this API as public?
        pass

    async def _do_send_request(self, data):
        pass
