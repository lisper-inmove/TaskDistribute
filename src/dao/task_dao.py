from pymongo.errors import DuplicateKeyError

import proto.entities.task_pb2 as task_pb
from base import Base
from dao.mongodb import MongoDBHelper
from errors import PopupError
from submodules.utils.logger import Logger

logger = Logger()


class TaskDA(MongoDBHelper, Base):

    coll = "___task_db___tasks___"

    async def create_task(self, task):
        json_data = self.PH.to_dict(task)
        try:
            await self.insert_one(json_data)
        except DuplicateKeyError as ex:
            logger.error(ex)
            raise PopupError("Already add this task")

    async def get_task_by_id(self, id):
        matcher = {"id": id}
        task = await self.find_one(matcher)
        return self.PH.to_obj(task, task_pb.Task)

    async def delete_task_by_id(self, id):
        matcher = {"id": id}
        await self.delete_one(matcher)

    async def list_task(self):
        matcher = {}
        async for task in self.find_many(matcher):
            task = self.PH.to_obj(task, task_pb.Task)
            yield task

    async def update_task(self, task):
        matcher = {"id": task.id}
        json_data = self.PH.to_dict(task)
        await self.update_one(matcher, json_data)
