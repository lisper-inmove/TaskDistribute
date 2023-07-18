import proto.entities.task_pb2 as task_pb
from manager.base_manager import BaseManager
from dao.task_dao import TaskDA


class TaskManager(BaseManager):

    @property
    def dao(self):
        if self._dao is None:
            self._dao = TaskDA()
        return self._dao

    def create_task(self, request):
        obj = self.create_obj(task_pb.Task)
        obj.name = request.name
        obj.preposeStatusQueryApi = request.preposeStatusQueryApi
        obj.taskFinishSetApi = request.taskFinishSetApi
        return obj

    async def list_task(self, request):
        async for template in self.dao.list_task():
            yield template

    async def add_task(self, task):
        await self.dao.create_task(task)

    async def update_task(self, task):
        self.update_obj(task)
        await self.dao.update_task_template(task)
