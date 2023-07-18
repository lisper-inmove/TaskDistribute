from submodules.utils.protobuf_helper import ProtobufHelper


class Base:

    def __init__(self, *args, **kargs):
        self.PH = ProtobufHelper()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return None
