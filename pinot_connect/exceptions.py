class Error(Exception):
    """Exception that is the base class of all other error exceptions.
    You can use this to catch all errors with one single except statement.
    """


class InterfaceError(Error):
    """Exception raised for errors that are related to the database interface rather than the database itself"""


class DatabaseError(Error):
    """Exception raised for errors that are related to the database"""


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the processed data like division by zero,
    numeric value out of range, etc"""


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database’s operation and not necessarily under the control
    of the programmer, e.g. an unexpected disconnect occurs, the data source name is not found, a transaction could not
    be processed, a memory allocation error occurred during processing, etc"""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error, e.g. the cursor is not valid anymore, the
    transaction is out of sync, etc"""


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors, e.g. table not found or already exists, syntax error in the SQL
    statement, wrong number of parameters specified, etc"""


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not supported by the database"""


# fmt: off
CODE_EXCEPTION_MAP = {
    100: InterfaceError,    # JSON_PARSING_ERROR_CODE
    101: InterfaceError,    # JSON_COMPILATION_ERROR_CODE
    150: ProgrammingError,  # SQL_PARSING_ERROR_CODE
    160: OperationalError,  # SEGMENT_PLAN_EXECUTION_ERROR_CODE
    170: OperationalError,  # COMBINE_SEGMENT_PLAN_TIMEOUT_ERROR_CODE
    180: OperationalError,  # ACCESS_DENIED_ERROR_CODE
    190: ProgrammingError,  # TABLE_DOES_NOT_EXIST_ERROR_CODE
    191: OperationalError,  # TABLE_IS_DISABLED_ERROR_CODE
    200: OperationalError,  # QUERY_EXECUTION_ERROR_CODE
    210: DatabaseError,     # SERVER_SHUTTING_DOWN_ERROR_CODE
    211: OperationalError,  # SERVER_OUT_OF_CAPACITY_ERROR_CODE
    230: OperationalError,  # SERVER_TABLE_MISSING_ERROR_CODE
    235: OperationalError,  # SERVER_SEGMENT_MISSING_ERROR_CODE
    240: OperationalError,  # QUERY_SCHEDULING_TIMEOUT_ERROR_CODE
    245: OperationalError,  # SERVER_RESOURCE_LIMIT_EXCEEDED_ERROR_CODE
    250: OperationalError,  # EXECUTION_TIMEOUT_ERROR_CODE
    260: InternalError,     # DATA_TABLE_SERIALIZATION_ERROR_CODE
    300: OperationalError,  # BROKER_GATHER_ERROR_CODE
    305: OperationalError,  # BROKER_SEGMENT_UNAVAILABLE_ERROR_CODE
    310: InternalError,     # DATA_TABLE_DESERIALIZATION_ERROR_CODE
    350: InternalError,     # FUTURE_CALL_ERROR_CODE
    400: DatabaseError,     # BROKER_TIMEOUT_ERROR_CODE
    410: DatabaseError,     # BROKER_RESOURCE_MISSING_ERROR_CODE
    420: DatabaseError,     # BROKER_INSTANCE_MISSING_ERROR_CODE
    425: DatabaseError,     # BROKER_REQUEST_SEND_ERROR_CODE
    427: DatabaseError,     # SERVER_NOT_RESPONDING_ERROR_CODE
    429: ProgrammingError,  # TOO_MANY_REQUESTS_ERROR_CODE
    450: InternalError,     # INTERNAL_ERROR_CODE
    500: DatabaseError,     # MERGE_RESPONSE_ERROR_CODE
    503: DatabaseError,     # QUERY_CANCELLATION_ERROR_CODE
    550: DatabaseError,     # FEDERATED_BROKER_UNAVAILABLE_ERROR_CODE
    600: OperationalError,  # COMBINE_GROUP_BY_EXCEPTION_ERROR_CODE
    700: ProgrammingError,  # QUERY_VALIDATION_ERROR_CODE
    710: ProgrammingError,  # UNKNOWN_COLUMN_ERROR_CODE
    720: DatabaseError,     # QUERY_PLANNING_ERROR_CODE
    1000: Error,            # UNKNOWN_ERROR_CODE
}
# fmt: on
