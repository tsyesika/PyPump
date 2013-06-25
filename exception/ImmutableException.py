
class ImmutableException(Exception):

    message = "You can't set %s on %s, the object is immutable."

    def __init__(self, item, obj, *args, **kwargs):
        message = self.message % (item, obj)
        super(ImmutableException, self).__init__(message, *args, **kwargs)
