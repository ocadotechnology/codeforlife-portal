import typing as t

from django.apps.registry import Apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import migrations, models
from tink.integration import gcpkms

User = get_user_model()
TModel = t.TypeVar("TModel", bound=models.Model)
GetEncAudience = t.Callable[[TModel], t.Tuple[str, int]]
GetEncDekFunc = t.Callable[[TModel], bytes]
GetEncModelFunc = t.Callable[[TModel], models.Model]


def to_enc_field_name(field_name: str):
    return f"_{field_name}"


def encrypt_fields(
    model_type: t.Type[TModel],
    field_names: t.List[str],
    get_enc_aud: GetEncAudience[TModel],
    get_enc_dek: GetEncDekFunc[TModel],
    get_enc_model: t.Optional[GetEncModelFunc[TModel]] = None,
):
    gcp_kms_client = gcpkms.GcpKmsClient(
        settings.KMS_MASTER_KEY_URI, settings.KMS_CREDENTIALS_PATH
    )

    # Clean field names.
    field_names = [field_name.strip().lower() for field_name in field_names]

    for model in model_type.objects.all():
        enc_dek = get_enc_dek(model)
        enc_model = get_enc_model(model) if get_enc_model else model

        for field_name in field_names:
            # Get unencrypted value.
            value: str = getattr(model, field_name)

            # Create associated data to limit access to this field and model.
            # E.g. "school:1|school:name", "school:1|class:name"
            enc_aud = ":".join(get_enc_aud(model))
            enc_field = ":".join([model_type.__name__.lower(), field_name])
            associated_data = f"{enc_aud}|{enc_field}".encode()

            encrypted_value = ""

            setattr(enc_model, to_enc_field_name(field_name), encrypted_value)

        enc_model.save(
            update_fields=[
                to_enc_field_name(field_name) for field_name in field_names
            ]
        )


def encrypt_user_fields(apps: Apps, *args):
    encrypt_fields(
        model_type=User,
        field_names=["email", "username", "first_name", "last_name"],
        get_enc_aud=lambda user: ("user", user.id),
        get_enc_dek=lambda user: user.userprofile.enc_dek,
        get_enc_model=lambda user: user.userprofile,
    )


def encrypt_model_fields(
    model_name: str,
    field_names: t.List[str],
    get_enc_aud: GetEncAudience,
    get_enc_dek: GetEncDekFunc,
):

    def code(apps: Apps, *args):
        encrypt_fields(
            model_type=apps.get_model("common", model_name),
            field_names=field_names,
            get_enc_aud=get_enc_aud,
            get_enc_dek=get_enc_dek,
        )

    return [
        *[  # Add encrypted fields.
            migrations.AddField(
                model_name=model_name,
                name=to_enc_field_name(field_name),
                field=models.BinaryField(null=True),
            )
            for field_name in field_names
        ],
        # migrations.RunPython(
        #     code=code,
        #     reverse_code=migrations.RunPython.noop,
        # ),
        # *[  # Remove unencrypted fields.
        #     migrations.RemoveField(
        #         model_name=model_name,
        #         name=field_name,
        #     )
        #     for field_name in field_names
        # ],
        # *[  # Alter encrypted fields to use original column names.
        #     migrations.AlterField(
        #         model_name=model_name,
        #         name=to_enc_field_name(field_name),
        #         field=models.BinaryField(db_column=field_name),
        #     )
        #     for field_name in field_names
        # ],
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0058_userprofile_google_refresh_token_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="enc_dek",
            field=models.BinaryField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name="school",
            name="enc_dek",
            field=models.BinaryField(null=True, editable=False),
        ),
        migrations.RunPython(
            code=encrypt_user_fields,
            reverse_code=migrations.RunPython.noop,
        ),
        *encrypt_model_fields(
            model_name="school",
            field_names=["name"],  # county, country
            get_enc_aud=lambda school: ("school", school.id),
            get_enc_dek=lambda school: school.enc_dek,
        ),
        # *encrypt_model_fields(
        #     model_name="class",
        #     field_names=["name"],
        #     get_enc_aud=lambda klass: (
        #         "school",
        #         klass.class_teacher.teacher_school.id,
        #     ),
        #     get_enc_dek=lambda klass: klass.class_teacher.teacher_school.enc_dek,
        # ),
    ]
