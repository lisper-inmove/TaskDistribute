from fastapi import APIRouter

import proto.api.api_task_p2p as api_task_pb
from manager.task_manager import TaskManager

router = APIRouter(prefix="/task")


@router.post("/create")
async def create_task(
        request: api_task_pb.CreateTaskRequest
):
    manager = TaskManager()
    task = manager.create_task(request)
    await manager.add_task(task)
    return request
