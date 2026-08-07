from abc import ABC, abstractmethod

from .context import WorkflowContext


class WorkflowStep(ABC):
    """
    A single unit of work in the recipe import workflow.

    Steps run in order and communicate by reading and writing the context. To add a step,
    implement this class and add it to `DEFAULT_WORKFLOW_STEPS`.
    """

    name: str
    """Identifier used in logs and step outcomes"""

    progress_key: str | None = None
    """Translation key reported to the client before the step runs"""

    required: bool = True
    """If a required step fails the workflow aborts, otherwise the failure is logged and skipped"""

    def should_run(self, ctx: WorkflowContext) -> bool:
        return True

    @abstractmethod
    async def run(self, ctx: WorkflowContext) -> None: ...
