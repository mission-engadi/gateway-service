"""Unit tests for security utilities."""

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functions."""
    
    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from password
        assert hashed != password
        
        # Verification should succeed
        assert verify_password(password, hashed)
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails verification."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert not verify_password(wrong_password, hashed)


class TestJWTTokens:
    """Test JWT token functions."""
    
    def test_create_and_decode_token(self):
        """Test token creation and decoding."""
        subject = "123"
        additional_claims = {"email": "test@example.com", "roles": ["user"]}
        
        token = create_access_token(subject, additional_claims=additional_claims)
        payload = decode_token(token)
        
        assert payload["sub"] == subject
        assert payload["email"] == additional_claims["email"]
        assert payload["roles"] == additional_claims["roles"]
    
    def test_decode_invalid_token(self):
        """Test that invalid token raises error."""
        with pytest.raises(JWTError):
            decode_token("invalid_token")
