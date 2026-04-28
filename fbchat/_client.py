from typing import Callable, Optional
import datetime

import attr

from ._common import log, req_log, kw_only
from . import _exception, _util, _graphql, _session, _threads, _models

from typing import Sequence, Iterable, Tuple, Optional, Set, BinaryIO, AsyncIterator


@attr.s(slots=True, kw_only=kw_only, auto_attribs=True)
class Client:
    """A client for Facebook Messenger.

    This contains methods that are generally needed to interact with Facebook.

    Example:
        Create a new client instance.

        >>> client = fbchat.Client(session=session)
    """

    #: The session to use when making requests.
    session: _session.Session
    sequence_id_callback: Optional[Callable[[int], None]] = None

    async def fetch_users(self) -> Sequence[_threads.UserData]:
        """Fetch users the client is currently chatting with.

        This is very close to your friend list, with the follow differences:

        It differs by including users that you're not friends with, but have chatted
        with before, and by including accounts that are "Messenger Only".

        But does not include deactivated, deleted or memorialized users (logically,
        since you can't chat with those).

        The order these are returned is arbitrary.

        Example:
            Get the name of an arbitrary user that you're currently chatting with.

            >>> users = client.fetch_users()
            >>> users[0].name
            "A user"
        """
        pass

    async def search_for_users(self, name: str, limit: int) -> Iterable[_threads.UserData]:
        """Find and get users by their name.

        The returned users are ordered by relevance.

        Args:
            name: Name of the user
            limit: The max. amount of users to fetch

        Example:
            Get the full name of the first found user.

            >>> (user,) = client.search_for_users("user", limit=1)
            >>> user.name
            "A user"
        """
        pass

    async def search_for_pages(self, name: str, limit: int) -> Iterable[_threads.PageData]:
        """Find and get pages by their name.

        The returned pages are ordered by relevance.

        Args:
            name: Name of the page
            limit: The max. amount of pages to fetch

        Example:
            Get the full name of the first found page.

            >>> (page,) = client.search_for_pages("page", limit=1)
            >>> page.name
            "A page"
        """
        pass

    async def search_for_groups(self, name: str, limit: int) -> Iterable[_threads.GroupData]:
        """Find and get group threads by their name.

        The returned groups are ordered by relevance.

        Args:
            name: Name of the group thread
            limit: The max. amount of groups to fetch

        Example:
            Get the full name of the first found group.

            >>> (group,) = client.search_for_groups("group", limit=1)
            >>> group.name
            "A group"
        """
        pass

    async def search_for_threads(self, name: str, limit: int) -> Iterable[_threads.ThreadABC]:
        """Find and get threads by their name.

        The returned threads are ordered by relevance.

        Args:
            name: Name of the thread
            limit: The max. amount of threads to fetch

        Example:
            Search for a user, and get the full name of the first found result.

            >>> (user,) = client.search_for_threads("user", limit=1)
            >>> assert isinstance(user, fbchat.User)
            >>> user.name
            "A user"
        """
        pass

    async def _search_messages(self, query, offset, limit):
        pass

    async def search_messages(
        self, query: str, limit: Optional[int]
    ) -> AsyncIterator[Tuple[_threads.ThreadABC, int]]:
        """Search for messages in all threads.

        Intended to be used alongside `ThreadABC.search_messages`.

        Warning! If someone send a message to a thread that matches the query, while
        we're searching, some snippets will get returned twice, and some will be lost.

        This is fundamentally not fixable, it's just how the endpoint is implemented.

        Args:
            query: Text to search for
            limit: Max. number of items to retrieve. If ``None``, all will be retrieved

        Example:
            Search for messages, and print the amount of snippets in each thread.

            >>> for thread, count in client.search_messages("abc", limit=3):
            ...     print(f"{thread.id} matched the search {count} time(s)")
            ...
            1234 matched the search 2 time(s)
            2345 matched the search 1 time(s)
            3456 matched the search 100 time(s)

        Return:
            Iterable with tuples of threads, and the total amount of matches.
        """
        pass

    async def _fetch_info(self, *ids):
        pass

    async def fetch_thread_info(self, ids: Iterable[str]) -> AsyncIterator[_threads.ThreadABC]:
        """Fetch threads' info from IDs, unordered.

        Warning:
            Sends two requests if users or pages are present, to fetch all available info!

        Args:
            ids: Thread ids to query

        Example:
            Get data about the user with id "4".

            >>> (user,) = client.fetch_thread_info(["4"])
            >>> user.name
            "Mark Zuckerberg"
        """
        pass

    async def _fetch_threads(self, limit, before, folders):
        pass

    async def fetch_threads(
        self,
        limit: Optional[int],
        location: _models.ThreadLocation = _models.ThreadLocation.INBOX,
    ) -> AsyncIterator[_threads.ThreadABC]:
        """Fetch the client's thread list.

        The returned threads are ordered by last active first.

        Args:
            limit: Max. number of threads to retrieve. If ``None``, all threads will be
                retrieved.
            location: INBOX, PENDING, ARCHIVED or OTHER

        Example:
            Fetch the last three threads that the user chatted with.

            >>> for thread in client.fetch_threads(limit=3):
            ...     print(f"{thread.id}: {thread.name}")
            ...
            1234: A user
            2345: A group
            3456: A page
        """
        pass

    async def fetch_unread(self) -> Sequence[_threads.ThreadABC]:
        """Fetch unread threads.

        Warning:
            This is not finished, and the API may change at any point!
        """
        pass

    async def fetch_unseen(self) -> Sequence[_threads.ThreadABC]:
        """Fetch unseen / new threads.

        Warning:
            This is not finished, and the API may change at any point!
        """
        pass

    async def fetch_image_url(self, image_id: str) -> str:
        """Fetch URL to download the original image from an image attachment ID.

        Args:
            image_id: The image you want to fetch

        Example:
            >>> client.fetch_image_url("1234")
            "https://scontent-arn1-1.xx.fbcdn.net/v/t1.123-4/1_23_45_n.png?..."

        Returns:
            An URL where you can download the original image
        """
        pass

    async def _get_private_data(self):
        pass

    async def get_phone_numbers(self) -> Sequence[str]:
        """Fetch the user's phone numbers."""
        pass

    async def get_emails(self) -> Sequence[str]:
        """Fetch the user's emails."""
        pass

    async def upload(
        self, files: Iterable[Tuple[str, BinaryIO, str]], voice_clip: bool = False
    ) -> Sequence[Tuple[str, str]]:
        """Upload files to Facebook.

        `files` should be a list of files that requests can upload, see
        `requests.request <https://docs.python-requests.org/en/master/api/#requests.request>`_.

        Example:
            >>> with open("file.txt", "rb") as f:
            ...     (file,) = client.upload([("file.txt", f, "text/plain")])
            ...
            >>> file
            ("1234", "text/plain")
        Return:
            Tuples with a file's ID and mimetype.
            This result can be passed straight on to `ThreadABC.send_files`, or used in
            `Group.set_image`.
        """
        pass

    async def mark_as_delivered(self, message: _models.Message):
        """Mark a message as delivered.

        Warning:
            This is not finished, and the API may change at any point!

        Args:
            message: The message to set as delivered
        """
        pass

    async def _read_status(self, read, threads, at):
        pass

    async def mark_as_read(
        self, threads: Iterable[_threads.ThreadABC], at: datetime.datetime
    ):
        """Mark threads as read.

        All messages inside the specified threads will be marked as read.

        Args:
            threads: Threads to set as read
            at: Timestamp to signal the read cursor at
        """
        pass

    async def mark_as_unread(
        self, threads: Iterable[_threads.ThreadABC], at: datetime.datetime
    ):
        """Mark threads as unread.

        All messages inside the specified threads will be marked as unread.

        Args:
            threads: Threads to set as unread
            at: Timestamp to signal the read cursor at
        """
        pass

    async def mark_as_seen(self, at: datetime.datetime):
        # TODO: Documenting this
        pass

    async def move_threads(
        self, location: _models.ThreadLocation, threads: Iterable[_threads.ThreadABC]
    ):
        """Move threads to specified location.

        Args:
            location: INBOX, PENDING, ARCHIVED or OTHER
            threads: Threads to move
        """
        pass

    async def delete_threads(self, threads: Iterable[_threads.ThreadABC]):
        """Bulk delete threads.

        Args:
            threads: Threads to delete

        Example:
            >>> group = fbchat.Group(session=session, id="1234")
            >>> client.delete_threads([group])
        """
        pass

    async def delete_messages(self, messages: Iterable[_models.Message]):
        """Bulk delete specified messages.

        Args:
            messages: Messages to delete

        Example:
            >>> message1 = fbchat.Message(thread=thread, id="1234")
            >>> message2 = fbchat.Message(thread=thread, id="2345")
            >>> client.delete_threads([message1, message2])
        """
        pass
