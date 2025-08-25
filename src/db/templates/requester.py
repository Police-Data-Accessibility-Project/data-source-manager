"""
A requester is a class that contains a session and provides methods for
performing database operations.
"""
from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

import src.db.helpers.session.session_helper as sh

class RequesterBase(ABC):

    def __init__(self, session: AsyncSession):
        self.session = session
        self.session_helper = sh