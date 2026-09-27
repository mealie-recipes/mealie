import pytest
from unittest.mock import patch, MagicMock
from mealie.core.dependencies.dependencies import is_logged_in

@pytest.mark.asyncio
async def test_is_logged_in_valid_normal_token():
    payload = {"sub": "user_123"}
    with patch("jwt.decode", return_value=payload):
        result = await is_logged_in(token="valid_token", session=MagicMock())
        assert result is True

@pytest.mark.asyncio
async def test_is_logged_in_valid_long_token_success():
    payload = {"sub": "user_123", "long_token": "abc", "id": 1}
    with patch("jwt.decode", return_value=payload), \
         patch("mealie.core.dependencies.dependencies.validate_long_live_token", return_value=True):
        result = await is_logged_in(token="valid_long_token", session=MagicMock())
        assert result is True

@pytest.mark.asyncio
async def test_is_logged_in_valid_long_token_exception():
    payload = {"sub": "user_123", "long_token": "abc", "id": 1}
    with patch("jwt.decode", return_value=payload), \
         patch("mealie.core.dependencies.dependencies.validate_long_live_token", side_effect=Exception("DB Error")):
        result = await is_logged_in(token="valid_long_token", session=MagicMock())
        assert result is False

@pytest.mark.asyncio
async def test_is_logged_in_no_sub_in_payload():
    payload = {}  
    with patch("jwt.decode", return_value=payload):
        result = await is_logged_in(token="no_sub_token", session=MagicMock())
        assert result is False

@pytest.mark.asyncio
async def test_is_logged_in_jwt_decode_exception():
    with patch("jwt.decode", side_effect=Exception("Invalid Token")):
        result = await is_logged_in(token="invalid_token", session=MagicMock())
        assert result is False
