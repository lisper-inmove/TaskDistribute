# -*- coding: utf-8 -*-

"""统一返回结构."""


class UnifyResponse:

    SUCCESS = (0, "成功")
    PAGE_NOT_FOUND = (404, "页面不存在")
    SYSTEM_ERROR = (-1, "系统繁忙")

    @staticmethod
    def R(data=None, rs=None):
        if data is None:
            data = {}
        if rs is None:
            rs = UnifyResponse.SUCCESS
        result = {
            "code": rs[0],
            "msg": rs[1]
        }
        if data is not None:
            result.update({"data": data})
        return result
