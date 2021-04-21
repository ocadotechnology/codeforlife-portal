from portal.forms.dotmailer import ConsentForm


# def test_consent_form():
#     fake_email_form = ConsentForm(
#         data={
#             "email": "fakeemail",
#             "consent_ticked": True,
#         },
#     )
#     assert not fake_email_form.is_valid()
#
#     consent_not_ticked_form = ConsentForm(
#         data={
#             "email": "real@email.com",
#             "consent_ticked": False,
#         },
#     )
#
#     assert not consent_not_ticked_form.is_valid()
#
#     correct_form = ConsentForm(
#         data={
#             "email": "real@email.com",
#             "consent_ticked": True,
#         },
#     )
#
#     assert correct_form.is_valid()
