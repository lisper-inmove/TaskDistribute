import proto.api.api_task_p2p as api_task_pb
from fastapi import APIRouter

router = APIRouter(prefix="/task-template")


@router.post("/create")
async def create_task_template(
        template: api_task_pb.CreateTaskTemplateRequest
):
    return template


@router.post("/delete")
async def delete_task_template(template: api_task_pb.DeleteTaskTemplateRequest):
    return template
