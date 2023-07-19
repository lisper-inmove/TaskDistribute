from fastapi import APIRouter

import proto.api.api_task_p2p as api_task_pb
from manager.task_manager import TaskManager
from manager.task_template_manager import TaskTemplateManager
from msgq.producer import Producer
from msgq.msg_config import MsgConfig
from submodules.utils.load_config import LoadConfig
from submodules.utils.sys_env import SysEnv

router = APIRouter(prefix="/task")


@router.post("/create")
async def create_task(
        request: api_task_pb.CreateTaskRequest
):
    manager = TaskManager()
    taskTemplateManager = TaskTemplateManager()
    taskTemplate = await taskTemplateManager.get_task_template_by_id(request.templateId)
    task = manager.create_task(request, taskTemplate)
    await manager.add_task(task)
    # for test
    config = MsgConfig(MsgConfig.REDIS)
    config.host = SysEnv.get("REDIS_HOST")
    config.port = int(SysEnv.get("REDIS_PORT"))
    config.stream_name = request.templateId
    producer = Producer().get_producer(config)
    producer.push({"id": task.id})
    return request
