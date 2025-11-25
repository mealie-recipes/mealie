from mealie.db.db_setup import session_context
from mealie.services.tesco.tesco_service import TescoService

def sync_tesco_prices():
    """
    Daily task to sync prices for all ingredients with a Tesco URL.
    """
    with session_context() as session:
        service = TescoService()
        service.sync_all_prices(session)
