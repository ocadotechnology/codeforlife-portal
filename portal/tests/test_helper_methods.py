import hashlib
from unittest.mock import patch, Mock

from portal.helpers.password import is_password_pwned
from portal.helpers.organisation import sanitise_uk_postcode


class TestClass:
    def test_is_password_pwned(self):
        weak_password = "Password123$"
        strong_password = "£EDCVFR$%TGBnhy667ujm"
        assert is_password_pwned(weak_password)
        assert not is_password_pwned(strong_password)

    def test_sanitise_uk_postcode(self):
        postcode_with_space = "AL10 9NE"
        postcode_without_space = "AL109UL"
        invalid_postcode = "123"

        assert sanitise_uk_postcode(postcode_with_space) == "AL10 9NE"  # Check it stays the same
        assert sanitise_uk_postcode(postcode_without_space) == "AL10 9UL"  # Check a space is added
        assert sanitise_uk_postcode(invalid_postcode) == "123"  # Check nothing happens


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
    assert result


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
    assert not result
