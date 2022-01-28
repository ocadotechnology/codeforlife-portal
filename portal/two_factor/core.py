import logging
from base64 import b32encode
from binascii import unhexlify
from uuid import uuid4

from django.views.generic import TemplateView
import django_otp
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django_otp.decorators import otp_required
from django_otp.util import random_hex

from two_factor.models import get_available_methods

from two_factor.forms import (
    DeviceValidationForm,
    MethodForm,
    TOTPDeviceForm,
    YubiKeyDeviceForm,
)
from two_factor.models import PhoneDevice, get_available_phone_methods
from two_factor.utils import default_device
from two_factor.views.utils import class_view_decorator

from .utils import IdempotentSessionWizardView

try:
    from otp_yubikey.models import ValidationService, RemoteYubikeyDevice
except ImportError:
    ValidationService = RemoteYubikeyDevice = None


logger = logging.getLogger(__name__)

REMEMBER_COOKIE_PREFIX = getattr(
    settings, "TWO_FACTOR_REMEMBER_COOKIE_PREFIX", "remember-cookie_"
)


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class SetupView(IdempotentSessionWizardView):
    """
    View for handling OTP setup using a wizard.

    The first step of the wizard shows an introduction text, explaining how OTP
    works and why it should be enabled. The user has to select the verification
    method (generator / call / sms) in the second step. Depending on the method
    selected, the third step configures the device. For the generator method, a
    QR code is shown which can be scanned using a mobile phone app and the user
    is asked to provide a generated token. For call and sms methods, the user
    provides the phone number which is then validated in the final step.
    """

    success_url = "two_factor:setup_complete"
    qrcode_url = "two_factor:qr"
    template_name = "two_factor/core/setup.html"
    session_key_name = "django_two_factor-qr_secret_key"
    initial_dict = {}
    form_list = (
        ("generator", TOTPDeviceForm),
        ("method", MethodForm),
        ("validation", DeviceValidationForm),
        ("yubikey", YubiKeyDeviceForm),
    )
    condition_dict = {
        "generator": lambda self: self.get_method() == "generator",
        "call": lambda self: self.get_method() == "call",
        "sms": lambda self: self.get_method() == "sms",
        "validation": lambda self: self.get_method() in ("sms", "call"),
        "yubikey": lambda self: self.get_method() == "yubikey",
    }
    idempotent_dict = {
        "yubikey": False,
    }

    def get_method(self):
        method_data = self.storage.validated_step_data.get("method", {})
        return method_data.get("method", None)

    def get(self, request, *args, **kwargs):
        """
        Start the setup wizard. Redirect if already enabled.
        """
        if default_device(self.request.user):
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_form_list(self):
        """
        Check if there is only one method, then skip the MethodForm from form_list
        """
        form_list = super().get_form_list()
        available_methods = get_available_methods()
        if len(available_methods) == 1:
            form_list.pop("method", None)
            method_key, _ = available_methods[0]
            self.storage.validated_step_data["method"] = {"method": method_key}
        return form_list

    def render_next_step(self, form, **kwargs):
        """
        In the validation step, ask the device to generate a challenge.
        """
        next_step = self.steps.next
        if next_step == "validation":
            try:
                self.get_device().generate_challenge()
                kwargs["challenge_succeeded"] = True
            except Exception:
                logger.exception("Could not generate challenge")
                kwargs["challenge_succeeded"] = False
        return super().render_next_step(form, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Finish the wizard. Save all forms and redirect.
        """
        # Remove secret key used for QR code generation
        try:
            del self.request.session[self.session_key_name]
        except KeyError:
            pass

        # TOTPDeviceForm
        if self.get_method() == "generator":
            form = [form for form in form_list if isinstance(form, TOTPDeviceForm)][0]
            device = form.save()

        # PhoneNumberForm / YubiKeyDeviceForm
        elif self.get_method() in ("call", "sms", "yubikey"):
            device = self.get_device()
            device.save()

        else:
            raise NotImplementedError("Unknown method '%s'" % self.get_method())

        django_otp.login(self.request, device)
        return redirect(self.success_url)

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == "generator":
            kwargs.update(
                {
                    "key": self.get_key(step),
                    "user": self.request.user,
                }
            )
        if step in ("validation", "yubikey"):
            kwargs.update({"device": self.get_device()})
        metadata = self.get_form_metadata(step)
        if metadata:
            kwargs.update(
                {
                    "metadata": metadata,
                }
            )
        return kwargs

    def get_device(self, **kwargs):
        """
        Uses the data from the setup step and generated key to recreate device.

        Only used for call / sms -- generator uses other procedure.
        """
        method = self.get_method()
        kwargs = kwargs or {}
        kwargs["name"] = "default"
        kwargs["user"] = self.request.user

        if method in ("call", "sms"):
            kwargs["method"] = method
            kwargs["number"] = self.storage.validated_step_data.get(method, {}).get(
                "number"
            )
            return PhoneDevice(key=self.get_key(method), **kwargs)

        if method == "yubikey":
            kwargs["public_id"] = self.storage.validated_step_data.get(
                "yubikey", {}
            ).get("token", "")[:-32]
            try:
                kwargs["service"] = ValidationService.objects.get(name="default")
            except ValidationService.DoesNotExist:
                raise KeyError("No ValidationService found with name 'default'")
            except ValidationService.MultipleObjectsReturned:
                raise KeyError("Multiple ValidationService found with name 'default'")
            return RemoteYubikeyDevice(**kwargs)

    def get_key(self, step):
        self.storage.extra_data.setdefault("keys", {})
        if step in self.storage.extra_data["keys"]:
            return self.storage.extra_data["keys"].get(step)
        key = random_hex(20)
        self.storage.extra_data["keys"][step] = key
        return key

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        if self.steps.current == "generator":
            key = self.get_key("generator")
            rawkey = unhexlify(key.encode("ascii"))
            b32key = b32encode(rawkey).decode("utf-8")
            self.request.session[self.session_key_name] = b32key
            context.update({"QR_URL": reverse(self.qrcode_url)})
        elif self.steps.current == "validation":
            context["device"] = self.get_device()
        context["cancel_url"] = resolve_url(settings.LOGIN_REDIRECT_URL)
        return context

    def process_step(self, form):
        if hasattr(form, "metadata"):
            self.storage.extra_data.setdefault("forms", {})
            self.storage.extra_data["forms"][self.steps.current] = form.metadata
        return super().process_step(form)

    def get_form_metadata(self, step):
        self.storage.extra_data.setdefault("forms", {})
        return self.storage.extra_data["forms"].get(step, None)


@class_view_decorator(never_cache)
@class_view_decorator(otp_required)
class SetupCompleteView(TemplateView):
    """
    View congratulation the user when OTP setup has completed.
    """

    template_name = "two_factor/core/setup_complete.html"

    def get_context_data(self):
        return {
            "phone_methods": get_available_phone_methods(),
        }
