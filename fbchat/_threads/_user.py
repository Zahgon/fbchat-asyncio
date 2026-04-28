import attr
import datetime
from ._abc import ThreadABC
from .._common import log, attrs_default
from .. import _util, _session, _models

from typing import Optional


GENDERS = {
    # For standard requests
    0: "unknown",
    1: "female_singular",
    2: "male_singular",
    3: "female_singular_guess",
    4: "male_singular_guess",
    5: "mixed",
    6: "neuter_singular",
    7: "unknown_singular",
    8: "female_plural",
    9: "male_plural",
    10: "neuter_plural",
    11: "unknown_plural",
    # For graphql requests
    "UNKNOWN": "unknown",
    "FEMALE": "female_singular",
    "MALE": "male_singular",
    # '': 'female_singular_guess',
    # '': 'male_singular_guess',
    # '': 'mixed',
    "NEUTER": "neuter_singular",
    # '': 'unknown_singular',
    # '': 'female_plural',
    # '': 'male_plural',
    # '': 'neuter_plural',
    # '': 'unknown_plural',
}


@attrs_default
class User(ThreadABC):
    """Represents a Facebook user. Implements `ThreadABC`.

    Example:
        >>> user = fbchat.User(session=session, id="1234")
    """

    #: The session to use when making requests.
    session: _session.Session
    #: The user's unique identifier.
    id: str = attr.ib(converter=str)

    def _to_send_data(self):
        pass

    def _copy(self) -> "User":
        pass

    async def confirm_friend_request(self):
        """Confirm a friend request, adding the user to your friend list.

        Example:
            >>> user.confirm_friend_request()
        """
        pass

    async def remove_friend(self):
        """Remove the user from the client's friend list.

        Example:
            >>> user.remove_friend()
        """
        pass

    async def block(self):
        """Block messages from the user.

        Example:
            >>> user.block()
        """
        pass

    async def unblock(self):
        """Unblock a previously blocked user.

        Example:
            >>> user.unblock()
        """
        pass


@attrs_default
class UserData(User):
    """Represents data about a Facebook user.

    Inherits `User`, and implements `ThreadABC`.
    """

    #: The user's picture
    photo: _models.Image
    #: The name of the user
    name: str
    #: Whether the user and the client are friends
    is_friend: bool
    #: The users first name
    first_name: str
    #: The users last name
    last_name: Optional[str] = None
    #: When the thread was last active / when the last message was sent
    last_active: Optional[datetime.datetime] = None
    #: Number of messages in the thread
    message_count: Optional[int] = None
    #: Set `Plan`
    plan: Optional[_models.PlanData] = None
    #: The profile URL. ``None`` for Messenger-only users
    url: Optional[str] = None
    #: The user's gender
    gender: Optional[str] = None
    #: From 0 to 1. How close the client is to the user
    affinity: Optional[float] = None
    #: The user's nickname
    nickname: Optional[str] = None
    #: The clients nickname, as seen by the user
    own_nickname: Optional[str] = None
    #: The message color
    color: Optional[str] = None
    #: The default emoji
    emoji: Optional[str] = None

    @staticmethod
    def _get_other_user(data):
        pass

    @classmethod
    def _from_graphql(cls, session, data):
        c_info = cls._parse_customization_info(data)

        plan = None
        if data.get("event_reminders") and data["event_reminders"].get("nodes"):
            plan = _models.PlanData._from_graphql(
                session, data["event_reminders"]["nodes"][0]
            )

        return cls(
            session=session,
            id=data["id"],
            url=data["url"],
            first_name=data["first_name"],
            last_name=data.get("last_name"),
            is_friend=data["is_viewer_friend"],
            gender=GENDERS.get(data["gender"]),
            affinity=data.get("viewer_affinity"),
            nickname=c_info.get("nickname"),
            color=c_info["color"],
            emoji=c_info["emoji"],
            own_nickname=c_info.get("own_nickname"),
            photo=_models.Image._from_uri(data["profile_picture"]),
            name=data["name"],
            message_count=data.get("messages_count"),
            plan=plan,
        )

    @classmethod
    def _from_thread_fetch(cls, session, data):
        pass

    @classmethod
    def _from_all_fetch(cls, session, data):
        pass
