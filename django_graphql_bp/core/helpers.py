class ObjectHelper:
    @staticmethod
    def multi_getattr(obj: object, attr, default=None):
        """
        :param attr: string with path to attribute separated with dots or None to return obj
        :type attr: str | None

        Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is equivalent to x.a.b.c.d. When a default
        argument is given, it is returned when any attribute in the chain doesn't exist; without it, an exception is
        raised when a missing attribute is encountered.
        """
        if attr is not None:
            attributes = attr.split('.')

            for i in attributes:
                try:
                    obj = getattr(obj, i)
                except AttributeError:
                    if default:
                        return default
                    else:
                        raise

        return obj
