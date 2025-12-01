"""
A requester is a class that contains a session and provides methods for
performing database operations.
"""
from abc import ABC

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

import src.db.helpers.session.session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class RequesterBase(ABC):

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_helper = sh

    async def scalar(self, query: Select):
        return await sh.scalar(self.session, query=query)

    async def mappings(self, query: Select):
        return await sh.mappings(self.session, query=query)

    async def run_query_builder(self, query_builder: QueryBuilderBase):
        return await query_builder.run(session=self.session)