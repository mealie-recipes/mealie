from .post_webhooks import post_group_webhooks
from .purge_group_exports import purge_group_data_exports
from .purge_password_reset import purge_password_reset_tokens
from .purge_registration import purge_group_registration
from .reset_locked_users import locked_user_reset

__all__ = [
    "post_group_webhooks",
    "purge_password_reset_tokens",
    "purge_group_data_exports",
    "purge_group_registration",
    "locked_user_reset",
]

"""
Tasks Package

Common recurring tasks for the server to perform. Tasks here are registered to the SchedulerRegistry class
in the app.py file as a post-startup task. This is done to ensure that the tasks are run after the server has
started up and the Scheduler object is only available to a single worker.

"""
