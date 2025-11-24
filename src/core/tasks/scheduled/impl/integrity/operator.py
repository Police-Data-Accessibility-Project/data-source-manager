from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


class IntegrityMonitorTaskOperator(
    ScheduledTaskOperatorBase,
    HasPrerequisitesMixin
):
    pass