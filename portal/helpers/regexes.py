import re

ACCESS_CODE_REGEX = "[A-Z]{5}|[A-Z]{2}[0-9]{3}"
ACCESS_CODE_PATTERN = re.compile(rf"^{ACCESS_CODE_REGEX}$")
