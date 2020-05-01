# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from builtins import str
import string
import re


def follow_verify_email_link_to_onboarding(page, email):
    _follow_verify_email_link(page, email)

    return go_to_teacher_login_page(page.browser)


def follow_verify_email_link_to_login(page, email, user_type):
    _follow_verify_email_link(page, email)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def follow_duplicate_account_link_to_login(page, email, user_type):
    _follow_duplicate_account_email_link(page, email)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def _follow_verify_email_link(page, email):
    message = str(email.message())
    prefix = '<p>Please go to <a href="'
    i = str.find(message, prefix) + len(prefix)
    suffix = '" rel="nofollow">'
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def _follow_duplicate_account_email_link(page, email):
    message = str(email.message())
    prefix = 'please login: <a href="'
    i = str.find(message, prefix) + len(prefix)
    suffix = '" rel="nofollow">'
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def follow_reset_email_link(browser, email):
    message = str(email.body)

    link = re.search("http.+/", message).group(0)

    browser.get(link)

    from portal.tests.pageObjects.portal.password_reset_form_page import (
        PasswordResetPage,
    )

    return PasswordResetPage(browser)


def follow_change_email_link_to_dashboard(page, email):
    _follow_change_email_link(page, email)

    return go_to_teacher_login_page(page.browser)


def _follow_change_email_link(page, email):
    message = str(email.message())
    prefix = "please go to "
    i = str.find(message, prefix) + len(prefix)
    suffix = " to verify"
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def go_to_teacher_login_page(browser):
    from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage

    return TeacherLoginPage(browser)


def go_to_independent_student_login_page(browser):
    from portal.tests.pageObjects.portal.independent_login_page import (
        IndependentStudentLoginPage,
    )

    return IndependentStudentLoginPage(browser)
