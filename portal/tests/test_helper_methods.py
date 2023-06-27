from portal.helpers.password import is_password_pwned
import pytest
from unittest.mock import patch, Mock
import hashlib


def test_is_password_pwned():
    weak_password = "Password123$"
    strong_password = "£EDCVFR$%TGBnhy667ujm"
    assert is_password_pwned(weak_password)
    assert not is_password_pwned(strong_password)


# This is your pytest test
@patch("requests.get")
def test_is_password_pwned(mock_get):
    # Arrange
    password = "password123"
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = f"{sha1_hash[5:]}\r\n"

    mock_get.return_value = mock_response

    # Act
    result = is_password_pwned(password)

    # Assert
    mock_get.assert_called_once_with(f"https://api.pwnedpasswords.com/range/{sha1_hash[:5]}")
    assert result == True


@patch("requests.get")
def test_is_password_pwned_status_code_not_200(mock_get):
    # Arrange
    password = "password123"
    sha1_hash = hashlib.sha1(password.encode()).hexdigest()

    mock_response = Mock()
    mock_response.status_code = 500

    mock_get.return_value = mock_response

    # Act
    result = is_password_pwned(password)

    # Assert
    mock_get.assert_called_once_with(f"https://api.pwnedpasswords.com/range/{sha1_hash[:5]}")
    assert result == True
