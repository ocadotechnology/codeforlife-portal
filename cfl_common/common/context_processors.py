from common import app_settings


def env(request):
    return {"env": app_settings.ENV}


def cookie_management_enabled(request):
    return {"cookie_management_enabled": app_settings.COOKIE_MANAGEMENT_ENABLED}
