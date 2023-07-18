import proto.entities.task_pb2 as task_pb
from base import Base
from dao.mongodb import MongoDBHelper


class TaskTemplateDA(MongoDBHelper, Base):

    coll = "___task_db___task_templates___"

    async def create_task_template(self, template):
        matcher = {"id": template.id}
        json_data = self.PH.to_dict(template)
        await self.update_one(matcher, json_data, upsert=True)

    async def get_task_template_by_id(self, id):
        matcher = {"id": id}
        template = await self.find_one(matcher)
        return self.PH.to_obj(template, task_pb.TaskTemplate)

    async def delete_template_by_id(self, id):
        matcher = {"id": id}
        await self.delete_one(matcher)

    async def list_task_template(self):
        matcher = {}
        async for template in self.find_many(matcher):
            template = self.PH.to_obj(template, task_pb.TaskTemplate)
            yield template

    async def update_task_template(self, template):
        matcher = {"id": template.id}
        json_data = self.PH.to_dict(template)
        await self.update_one(matcher, json_data)
