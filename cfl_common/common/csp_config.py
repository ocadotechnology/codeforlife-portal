"""CSP Config"""

from .app_settings import domain, MODULE_NAME

CSP_DEFAULT_SRC = ("self",)
CSP_CONNECT_SRC = (
    "'self'",
    "https://*.onetrust.com/",
    "https://api.pwnedpasswords.com",
    "https://euc-widget.freshworks.com/",
    "https://codeforlife.freshdesk.com/",
    "https://api.iconify.design/",
    "https://api.simplesvg.com/",
    "https://api.unisvg.com/",
    "https://www.google-analytics.com/",
    "https://pyodide-cdn2.iodide.io/v0.15.0/full/",
    "https://crowdin.com/",
)
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com/", "https://fonts.googleapis.com/", "https://use.typekit.net/")
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.0.0/crypto-js.min.js",
    "https://cdn.crowdin.com/",
    "https://*.onetrust.com/",
    "https://code.jquery.com/",
    "https://euc-widget.freshworks.com/",
    "https://cdn-ukwest.onetrust.com/",
    "https://code.iconify.design/2/2.0.3/iconify.min.js",
    "https://www.googletagmanager.com/",
    "https://www.recaptcha.net/",
    "https://www.google.com/recaptcha/",
    "https://www.gstatic.com/recaptcha/",
    "https://use.typekit.net/mrl4ieu.js",
    "https://pyodide-cdn2.iodide.io/v0.15.0/full/",
    f"{domain()}/static/portal/",
    f"{domain()}/static/common/",
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://euc-widget.freshworks.com/",
    "https://cdn-ukwest.onetrust.com/",
    "https://fonts.googleapis.com/",
    "https://code.jquery.com/ui/1.13.1/themes/base/jquery-ui.css",
    "https://cdn.crowdin.com/",
    f"{domain()}/static/portal/",
)
CSP_FRAME_SRC = (
    "https://storage.googleapis.com/",
    "https://2662351606-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/",
    "https://files.gitbook.com/v0/b/gitbook-x-prod.appspot.com/",
    "https://www.recaptcha.net/",
    "https://www.google.com/recaptcha/",
    "https://crowdin.com/",
    f"{domain()}/static/common/img/",
    f"{domain()}/static/game/image/",
)
CSP_IMG_SRC = (
    "'self'",
    "https://storage.googleapis.com/codeforlife-assets/images/",
    "https://cdn-ukwest.onetrust.com/",
    "https://p.typekit.net/",
    "https://cdn.crowdin.com/",
    "https://crowdin-static.downloads.crowdin.com/",
    "data:",
    f"{domain()}/static/portal/img/",
    f"{domain()}/static/portal/static/portal/img/",
    f"{domain()}/static/portal/img/",
    f"{domain()}/favicon.ico",
    f"{domain()}/img/",
    f"{domain()}/account/two_factor/qrcode/",
    f"{domain()}/static/",
    f"{domain()}/static/game/image/",
    f"{domain()}/static/game/raphael_image/",
    f"{domain()}/static/game/js/blockly/media/",
    f"{domain()}/static/icons/",
)
CSP_OBJECT_SRC = (f"{domain()}/static/common/img/", f"{domain()}/static/game/image/")
CSP_MEDIA_SRC = (f"{domain()}/static/game/sound/", f"{domain()}/static/game/js/blockly/media/")
