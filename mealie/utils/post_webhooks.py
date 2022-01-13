from asyncio.log import logger

from sqlalchemy.orm.session import Session


def post_webhooks(group: int, session: Session = None, force=True):
    logger.error("post_webhooks is depreciated")
