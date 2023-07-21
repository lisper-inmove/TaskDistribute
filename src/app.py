import os
import re
import time
import importlib.util

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pathlib import Path

from submodules.utils.logger import Logger
from submodules.utils.sys_env import SysEnv
from errors import Error
from unify_response import UnifyResponse

logger = Logger()


class RouterHelper:

    pattern = re.compile('(?!^)([A-Z]+)')

    def __init__(self, app, directory):
        self.directory = directory
        self.routers = dict()
        self.app = app

    def load_router(self, path=None):
        """加载所有router."""
        if path is None:
            root_dir = SysEnv.get(SysEnv.APPROOT)
            path = os.path.join(root_dir, self.directory)
        for root, dirs, files in os.walk(path):
            for directory in dirs:
                self.load_router(os.path.join(root, directory))
            for _f in files:
                self.load_router_from_file(os.path.join(root, _f))

    def load_router_from_file(self, filepath):
        """加载某一个router."""
        if not filepath.endswith("py"):
            return
        filename = Path(filepath).name
        spec = importlib.util.spec_from_file_location(self.directory, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.__dict__.get('router'):
            self.app.include_router(module.__dict__.get('router'))


app = FastAPI()


@app.middleware("http")
async def cache_error(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Error as e:
        result = UnifyResponse.R(rs=(e.code, e.msg))
        return JSONResponse(result)
    except Exception as e:
        logger.error(e)
        raise e
    process_time = time.time() - start_time
    logger.info(f"Api processTime: {request.url} {process_time}")
    return response

RouterHelper(app, "routers").load_router()
