# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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


def is_message_showing(browser, message):
    return message in browser.find_element_by_id('messages').text


def is_email_verified_message_showing(browser):
    return is_message_showing(browser, 'Your email address was successfully verified, please log in.')


def is_teacher_details_updated_message_showing(browser):
    return is_message_showing(browser, 'Your account details have been successfully changed.')


def is_student_details_updated_message_showing(browser):
    return is_message_showing(browser, 'Your account details have been changed successfully.')


def is_indep_student_join_request_received_message_showing(browser):
    return is_message_showing(browser, 'Your request to join a school has been received successfully.')


def is_indep_student_join_request_revoked_message_showing(browser):
    return is_message_showing(browser, 'Your request to join a school has been cancelled successfully.')


def is_teacher_email_updated_message_showing(browser):
    return is_message_showing(browser, 'Your account details have been successfully changed. Your email will be '
                                       'changed once you have verified it, until then you can still log in with your '
                                       'old email.')


def is_organisation_created_message_showing(browser, name):
    return is_message_showing(browser, "The school or club '%s' has been successfully added." % name)


def is_class_created_message_showing(browser, name):
    return is_message_showing(browser, "The class '%s' has been created successfully." % name)


def is_class_nonempty_message_showing(browser):
    return is_message_showing(browser, "This class still has students, please remove or delete them all before "
                                       "deleting the class.")


def is_contact_message_sent_message_showing(browser):
    return is_message_showing(browser, "Your message was sent successfully.")
