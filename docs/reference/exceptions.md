<a id="pinot_connect.exceptions"></a>

# pinot\_connect.exceptions

<a id="pinot_connect.exceptions.Error"></a>

---
## Error

```python
class Error(Exception)
```

Exception that is the base class of all other error exceptions.
You can use this to catch all errors with one single except statement.

<a id="pinot_connect.exceptions.InterfaceError"></a>

---
## InterfaceError

```python
class InterfaceError(Error)
```

Exception raised for errors that are related to the database interface rather than the database itself

<a id="pinot_connect.exceptions.DatabaseError"></a>

---
## DatabaseError

```python
class DatabaseError(Error)
```

Exception raised for errors that are related to the database

<a id="pinot_connect.exceptions.DataError"></a>

---
## DataError

```python
class DataError(DatabaseError)
```

Exception raised for errors that are due to problems with the processed data like division by zero,
numeric value out of range, etc

<a id="pinot_connect.exceptions.OperationalError"></a>

---
## OperationalError

```python
class OperationalError(DatabaseError)
```

Exception raised for errors that are related to the database’s operation and not necessarily under the control
of the programmer, e.g. an unexpected disconnect occurs, the data source name is not found, a transaction could not
be processed, a memory allocation error occurred during processing, etc

<a id="pinot_connect.exceptions.InternalError"></a>

---
## InternalError

```python
class InternalError(DatabaseError)
```

Exception raised when the database encounters an internal error, e.g. the cursor is not valid anymore, the
transaction is out of sync, etc

<a id="pinot_connect.exceptions.ProgrammingError"></a>

---
## ProgrammingError

```python
class ProgrammingError(DatabaseError)
```

Exception raised for programming errors, e.g. table not found or already exists, syntax error in the SQL
statement, wrong number of parameters specified, etc

<a id="pinot_connect.exceptions.NotSupportedError"></a>

---
## NotSupportedError

```python
class NotSupportedError(DatabaseError)
```

Exception raised in case a method or database API was used which is not supported by the database

