from submodules.utils.protobuf_helper import ProtobufHelper
from submodules.utils.sys_env import SysEnv


class Base:

    def __init__(self, *args, **kargs):
        self.PH = ProtobufHelper()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return None

    @property
    def is_test(self):
        return SysEnv.get("RUNTIME_ENVIRONMENT") == "test"

    @property
    def is_k8s(self):
        return SysEnv.get("IS_K8S") == "true"
