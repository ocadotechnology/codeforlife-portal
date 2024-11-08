from django import forms
from django.test import TestCase
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from portal.helpers.captcha import is_captcha_in_form, remove_captcha_from_forms


class FormCaptchaTest(TestCase):
    class FormWithCaptcha(forms.Form):
        captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def test_is_captcha_in_form(self):
        form_with_captcha = FormCaptchaTest.FormWithCaptcha()
        print(form_with_captcha.fields)
        self.assertTrue(is_captcha_in_form(form_with_captcha))

        form_without_captcha = forms.Form()
        self.assertFalse(is_captcha_in_form(form_without_captcha))

    def test_remove_captcha_from_forms(self):
        form1 = FormCaptchaTest.FormWithCaptcha()
        form2 = forms.Form()
        form3 = FormCaptchaTest.FormWithCaptcha()

        remove_captcha_from_forms(form1, form2, form3)

        for form in [form1, form2, form3]:
            self.assertFalse(is_captcha_in_form(form))
