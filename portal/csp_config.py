"""CSP config"""

from common.app_settings import domain

CSP_CONFIG = {
    "CSP_DEFAULT_SRC": ("'self'",),
    "CSP_CONNECT_SRC": (
        "'self'",
        "https://*.onetrust.com/",
        "https://euc-widget.freshworks.com/",
        "https://codeforlife.freshdesk.com/",
        "https://api.iconify.design/",
        "https://api.simplesvg.com/",
        "https://api.unisvg.com/",
        "https://www.google-analytics.com/",
    ),
    "CSP_FONT_SRC": (
        "'self'",
        "https://fonts.gstatic.com/",
        "https://fonts.googleapis.com/",
    ),
    "CSP_IMG_SRC": (
        "https://storage.googleapis.com/codeforlife-assets/images/",
        "https://cdn-ukwest.onetrust.com/",
        f"{domain()}/static/portal/img/",
        f"{domain()}/account/two_factor/qrcode/",
        "data:",
    ),
    "CSP_SCRIPT_SRC": (
        "'self'",
        "'unsafe-inline'",
        "https://*.onetrust.com/",
        "https://code.jquery.com/",
        "https://euc-widget.freshworks.com/",
        "https://cdn-ukwest.onetrust.com/",
        "https://code.iconify.design/2/2.0.3/iconify.min.js",
        "https://www.googletagmanager.com/gtm.js",
        "https://cdn.mouseflow.com/",
        "https://www.google-analytics.com/analytics.js",
        "https://www.recaptcha.net/",
        "https://www.google.com/recaptcha/",
        "https://www.gstatic.com/recaptcha/",
        f"{domain()}/static/portal/",
        f"{domain()}/static/common/",
    ),
    "CSP_STYLE_SRC": (
        "'self'",
        "'unsafe-inline'",
        "https://euc-widget.freshworks.com/",
        "https://cdn-ukwest.onetrust.com/",
        "https://fonts.googleapis.com/",
        f"{domain()}/static/portal/",
    ),
    "CSP_FRAME_SRC": (
        "https://storage.googleapis.com/",
        "https://www.youtube-nocookie.com/",
        "https://www.recaptcha.net/",
        "https://www.google.com/recaptcha/",
    ),
}
