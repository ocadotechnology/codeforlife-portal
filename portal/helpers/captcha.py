from builtins import map


def is_captcha_in_form(form):
    return "captcha" in form.fields


def remove_captcha_from_forms(*args):
    list(map(remove_captcha_from_form, args))


def remove_captcha_from_form(form):
    form.fields.pop("captcha", None)
