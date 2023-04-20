from portal.helpers.regexes import ACCESS_CODE_FROM_URL_PATTERN


def get_access_code_from_request(request):
    try:
        access_code = ACCESS_CODE_FROM_URL_PATTERN.search(request.get_full_path()).group(1)
    except AttributeError:
        access_code = ""
        print(f"Access code not found in {request.get_full_path()}")
    return access_code
