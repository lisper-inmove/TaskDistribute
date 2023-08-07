import proto.entities.task_pb2 as task_pb
from manager.base_manager import BaseManager
from dao.task_dao import TaskDA


class TaskManager(BaseManager):

    @property
    def dao(self):
        if self._dao is None:
            self._dao = TaskDA()
        return self._dao

    def create_task(self, request, template):
        obj = self.create_obj(task_pb.Task)
        obj.uniqueId = request.uniqueId
        obj.preposeParams = request.preposeParams
        obj.finishParams = request.finishParams
        obj.template.CopyFrom(template)
        return obj

    async def list_task(self):
        async for task in self.dao.list_task():
            yield task

    async def list_created_task(self):
        async for task in self.dao.list_created_task():
            yield task

    async def add_task(self, task):
        await self.dao.create_task(task)

    async def get_task_by_id(self, id):
        return await self.dao.get_task_by_id(id)

    async def update_task(self, task):
        self.update_obj(task)
        await self.dao.update_task(task)
