import proto.api.api_task_p2p as api_task_pb
from fastapi import APIRouter

router = APIRouter(prefix="/task")


@router.post("/create")
async def create_task(
        task: api_task_pb.CreateTaskRequest
):
    return task
