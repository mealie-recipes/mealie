from pytest import fixture

from tests import utils


@fixture(scope="session")
def api_routes():
    return utils.AppRoutes()
