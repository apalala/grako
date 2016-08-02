__REGISTRY = vars()


class __Synthetic(object):
    def __reduce__(self):
        return (
            synthesize(type(self).__name__, type(self).__bases__),
            (),
            vars(self),
        )


def synthesize(name, bases):
    typename = '%s.%s' % (__name__, name)

    if not isinstance(bases, tuple):
        bases = (bases,)

    if __Synthetic not in bases:
        bases = (__Synthetic,) + bases

    constructor = __REGISTRY.get(typename)
    if not constructor:
        constructor = type(name, bases, {})
        typename = constructor.__name__
        __REGISTRY[typename] = constructor

    return constructor