import proto.entities.task_pb2 as task_pb
from manager.base_manager import BaseManager
from dao.task_template_dao import TaskTemplateDA


class TaskTemplateManager(BaseManager):

    @property
    def dao(self):
        if self._dao is None:
            self._dao = TaskTemplateDA()
        return self._dao

    def create_task_template(self, request):
        obj = self.create_obj(task_pb.TaskTemplate)
        obj.name = request.name
        obj.preposeStatusQueryApi = request.preposeStatusQueryApi
        obj.taskFinishSetApi = request.taskFinishSetApi
        obj.tokenName = request.tokenName
        obj.tokenValue = request.tokenValue
        obj.successAssert = request.successAssert
        return obj

    async def get_task_template_by_id(self, id):
        return await self.dao.get_task_template_by_id(id)

    async def list_task_template(self):
        async for template in self.dao.list_task_template():
            yield template

    async def save_task_template(self, template):
        await self.dao.save_task_template(template)

    async def update_task_template(self, template):
        self.update_obj(template)
        await self.dao.update_task_template(template)

    async def delete_task_template(self, id):
        return await self.dao.delete_template_by_id(id)
