from abc import ABC


class SgenError(Exception, ABC):
    """Base class for all Sgen errors."""
    pass

class InternalError(SgenError, ABC):
    """Internal error in Sgen."""
    pass

class CommandError(SgenError, ABC):
    """Base class for command errors."""
    pass
