from common import app_settings


def module_name(request):
    return {"module_name": app_settings.MODULE_NAME}


def cookie_management_enabled(request):
    return {"cookie_management_enabled": app_settings.COOKIE_MANAGEMENT_ENABLED}
