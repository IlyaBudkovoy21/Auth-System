# tests/test_auth.py
from datetime import datetime, timedelta
from unittest.mock import patch

from jose import JWTError

from src.utils.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestPasswordFunctions:
    def test_verify_password_correct(self):
        plain_password = "testpassword123"
        hashed_password = get_password_hash(plain_password)

        assert verify_password(plain_password, hashed_password) is True

    def test_verify_password_incorrect(self):
        plain_password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed_password = get_password_hash(plain_password)

        assert verify_password(wrong_password, hashed_password) is False

    def test_get_password_hash_creates_hash(self):
        password = "testpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestTokenFunctions:
    def setup_method(self):
        self.test_data = {"sub": "testuser", "user_id": "123"}

    def test_create_access_token_with_default_expiry(self):
        token = create_access_token(self.test_data)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_create_access_token_with_custom_expiry(self):
        expires_delta = timedelta(minutes=30)
        token = create_access_token(self.test_data, expires_delta=expires_delta)

        payload = verify_token(token)
        assert payload is not None

        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        expected_expiry = datetime.utcnow() + expires_delta

        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        assert time_diff <= 1

    def test_create_refresh_token(self):
        token = create_refresh_token(self.test_data)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert "exp" in payload

    def test_verify_token_valid(self):
        token = create_access_token(self.test_data)
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"

    def test_verify_token_expired(self):
        expired_data = self.test_data.copy()
        expired_data["exp"] = datetime.utcnow() - timedelta(hours=1)

        with patch("src.auth.utils.jwt.encode") as mock_encode:
            mock_encode.return_value = "expired_token"
            with patch("src.auth.utils.jwt.decode") as mock_decode:
                mock_decode.side_effect = JWTError("Token expired")

                payload = verify_token("expired_token")
                assert payload is None

    def test_verify_token_invalid_signature(self):

        with patch("src.auth.utils.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid signature")

            payload = verify_token("invalid_token")
            assert payload is None

    def test_verify_token_malformed(self):
        payload = verify_token("not.a.valid.token")
        assert payload is None

    def test_token_payload_structure(self):
        token = create_access_token(self.test_data)
        payload = verify_token(token)

        assert "sub" in payload
        assert "user_id" in payload
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
