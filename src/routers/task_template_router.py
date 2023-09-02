from fastapi import APIRouter

import proto.api.api_task_p2p as api_task_pb
from unify_response import UnifyResponse
from manager.task_template_manager import TaskTemplateManager


router = APIRouter(prefix="/task-template")


@router.post("/create")
async def create_task_template(
        request: api_task_pb.CreateTaskTemplateRequest
):
    manager = TaskTemplateManager()
    template = manager.create_task_template(request)
    await manager.save_task_template(template)
    resp = api_task_pb.TaskTemplateCommonResponse()
    resp.id = template.id
    resp.name = template.name
    return UnifyResponse.R(resp)


@router.post("/delete")
async def delete_task_template(template: api_task_pb.DeleteTaskTemplateRequest):
    manager = TaskTemplateManager();
    template = await manager.delete_task_template(template.id)
    return UnifyResponse.R()


@router.post("/list")
async def list_task_template(request: api_task_pb.ListTaskTemplateRequest):
    manager = TaskTemplateManager()
    resp = api_task_pb.ListTaskTemplateResponse()
    async for template in manager.list_task_template():
        resp.taskList.append(
            api_task_pb.TaskTemplateCommonResponse(
                id=template.id,
                name=template.name
            )
        )
    return resp
