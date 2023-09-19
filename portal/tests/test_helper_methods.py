import hashlib
from unittest.mock import patch, Mock

from portal.helpers.password import is_password_pwned


class TestClass:
    def test_is_password_pwned(self):
        weak_password = "Password123$"
        strong_password = "£EDCVFR$%TGBnhy667ujm"
        assert is_password_pwned(weak_password)
        assert not is_password_pwned(strong_password)

    @patch("requests.get")
    def test_is_password_pwned__status_code_not_200(self, mock_get):
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
