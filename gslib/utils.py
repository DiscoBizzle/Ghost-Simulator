class ExecOnChange(object):
    """Descriptor class to force update when changed.

    See http://tinyurl.com/PyDescriptors"""
    def __init__(self, name, funcs):
        self.name = name
        self._name = "_" + name
        self.funcs = funcs

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self._name)
        except AttributeError:
            raise AttributeError("{} has no attribute {}".format(instance, self.name))

    def __set__(self, instance, value):
        already_set = hasattr(instance, self._name)
        setattr(instance, self._name, value)
        if already_set:
            for func in self.funcs:
                getattr(instance, func)()

def exec_on_change_meta(funcs):
    """Do magic so that the ExecOnChange descriptor doesn't need explicit
    variable names.

    It's actually a lot simpler than it looks. To use, just put
        __metaclass__ = exec_on_change_meta([...])
    in the class definition with a list of strings naming methods to call when
    variables are changed.
    """
    class ExecOnChangeMeta(type):
        def __new__(cls, name, bases, attrs):
            for attr_name in attrs:
                if attrs[attr_name] == ExecOnChange:
                    attrs[attr_name] = ExecOnChange(attr_name, funcs)
            return type.__new__(cls, name, bases, attrs)

    return ExecOnChangeMeta

