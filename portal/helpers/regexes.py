import re

ACCESS_CODE_REGEX = "[a-zA-Z]{5}|[a-zA-Z]{2}[0-9]{3}"
ACCESS_CODE_PATTERN = re.compile(rf"^{ACCESS_CODE_REGEX}$")
EMAIL_REGEX = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
EMAIL_REGEX_PATTERN = re.compile(EMAIL_REGEX)
ACCESS_CODE_FROM_URL_REGEX = "/login/student/(\w+)"
ACCESS_CODE_FROM_URL_PATTERN = re.compile(ACCESS_CODE_FROM_URL_REGEX)
JWT_REGEX = "([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)"
