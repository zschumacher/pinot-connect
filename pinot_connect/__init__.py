from ._result_set import Column
from .connection import AsyncConnection
from .connection import Connection
from .cursor import AsyncCursor
from .cursor import Cursor
from .cursor import QueryStatistics
from .exceptions import DatabaseError
from .exceptions import DataError
from .exceptions import Error
from .exceptions import InterfaceError
from .exceptions import InternalError
from .exceptions import NotSupportedError
from .exceptions import OperationalError
from .exceptions import ProgrammingError
from .options import ClientOptions
from .options import QueryOptions
from .options import RequestOptions

connect = Connection.connect  # pointer to pypinot.Connection.connect

apilevel = "2.0"  # implements dbapi spec 2.0
threadsafety = 2  # threads may share module and connections, NOT cursors
paramstyle = "pyformat"  # %s and %(name)s
