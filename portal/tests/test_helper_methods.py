from portal.helpers.password import is_password_pwned


def test_is_password_pwned():
    weak_password = "Password123$"
    strong_password = "£EDCVFR$%TGBnhy667ujm"
    assert is_password_pwned(weak_password)
    assert not is_password_pwned(strong_password)
