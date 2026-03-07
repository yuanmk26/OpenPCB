"""Custom exceptions used by OpenPCB CLI."""


class OpenPCBError(Exception):
    """Base class for expected CLI-level errors."""


class InputError(OpenPCBError):
    """Raised when user input or command arguments are invalid."""


class FileConflictError(OpenPCBError):
    """Raised when target files/directories already exist unexpectedly."""


class SaveError(OpenPCBError):
    """Raised when writing artifacts to disk fails."""
