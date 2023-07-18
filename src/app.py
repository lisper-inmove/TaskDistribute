import os
import re
import inspect
import importlib.util

from fastapi import FastAPI
from pathlib import Path

from submodules.utils.logger import Logger
from submodules.utils.sys_env import SysEnv
logger = Logger()


class HandlerHelper:

    pattern = re.compile('(?!^)([A-Z]+)')

    def __init__(self, app, directory):
        self.directory = directory
        self.handlers = dict()
        self.app = app

    def load_handler(self, path=None):
        """加载所有handler."""
        if path is None:
            root_dir = SysEnv.get(SysEnv.APPROOT)
            path = os.path.join(root_dir, self.directory)
        for root, dirs, files in os.walk(path):
            for directory in dirs:
                self.load_handler(os.path.join(root, directory))
            for _f in files:
                self.load_handler_from_file(os.path.join(root, _f))

    def load_handler_from_file(self, filepath):
        """加载某一个handler."""
        if not filepath.endswith("py"):
            return
        filename = Path(filepath).name
        spec = importlib.util.spec_from_file_location(self.directory, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.__dict__.get('router'):
            self.app.include_router(module.__dict__.get('router'))


app = FastAPI()
HandlerHelper(app, "routers").load_handler()
