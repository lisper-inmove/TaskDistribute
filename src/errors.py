# -*- coding: utf-8 -*-


class Error(Exception):

    def __init__(self, code=None, msg=None, resp=None):
        self.code = code
        self.msg = msg
        if resp is not None:
            self.code = resp[0]
            self.msg = resp[1]
        super().__init__(self.msg)


class PopupError(Error):

    def __init__(self, msg):
        super().__init__(code=9, msg=msg)
