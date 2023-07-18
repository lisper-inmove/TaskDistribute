from base import Base
from submodules.utils.misc import Misc
from submodules.utils.idate import IDate


class BaseManager(Base):

    def create_obj(self, cls):
        obj = cls()
        obj.id = Misc.uuid()
        if hasattr(obj, 'createTime'):
            obj.createTime = IDate.now_timestamp()
        if hasattr(obj, 'updateTime'):
            obj.updateTime = IDate.now_timestamp()
        return obj

    def update_obj(self, obj):
        if hasattr(obj, 'updateTime'):
            obj.updateTime = IDate.now_timestamp()
