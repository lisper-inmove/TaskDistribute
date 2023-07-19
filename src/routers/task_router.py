from fastapi import APIRouter

import proto.api.api_task_p2p as api_task_pb
from manager.task_manager import TaskManager
from manager.task_template_manager import TaskTemplateManager

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
    return request
