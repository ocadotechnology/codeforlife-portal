/*
Code for Life

Copyright (C) 2019, Ocado Innovation Limited

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

ADDITIONAL TERMS – Section 7 GNU General Public Licence

This licence does not grant any right, title or interest in any “Ocado” logos,
trade names or the trademark “Ocado” or any other trademarks or domain names
owned by Ocado Innovation Limited or the Ocado group of companies or any other
distinctive brand features of “Ocado” as may be secured from time to time. You
must not distribute any modification of this program using the trademark
“Ocado” or claim any affiliation or association with Ocado or its employees.

You are not authorised to use the name Ocado (or any of its trade names) or
the names of any author or contributor in advertising or for publicity purposes
pertaining to the distribution of this program, without the prior written
authorisation of Ocado.

Any propagation, distribution or conveyance of this program must include this
copyright notice and these terms. You must not misrepresent the origins of this
program; modified versions of the program must be marked as such and not
identified as the original program.
*/
var TEACHER_PASSWORD_FIELD_ID = '';
var INDEP_STUDENT_PASSWORD_FIELD_ID = '';
var teacher_password_field = '';
var indep_student_password_field = '';
var most_used_passwords_2018 = ['Abcd1234', 'Password1', 'Qwerty123'];

var password_strengths = [
    { name: 'No password!', colour: '#FF0000' },
    { name: 'Password too weak', colour: '#DBA901' },
    { name: 'Strong password', colour: '#088A08' },
    { name: 'Password too common', colour: '#DBA901' }
];

$(function() {

    teacher_password_field = $('#' + TEACHER_PASSWORD_FIELD_ID);
    indep_student_password_field = $('#' + INDEP_STUDENT_PASSWORD_FIELD_ID);

    setUpDynamicUpdates(teacher_password_field, true);
    setUpDynamicUpdates(indep_student_password_field, false);

    updatePasswordStrength(true);
    updatePasswordStrength(false);
});

function setUpDynamicUpdates(password_field, isTeacher) {
    password_field.on('keyup', function(){
        updatePasswordStrength(isTeacher)
    });
    password_field.on('paste', function(){
        updatePasswordStrength(isTeacher)
    });
    password_field.on('cut', function(){
        updatePasswordStrength(isTeacher)
    });
}

function updatePasswordStrength(isTeacher) {
    // The reason for the timeout is that if we just got $('#...').val() we'd get the
    // old value before the keypress / change. Apparently even jQuery itself implements
    // things this way, so maybe there is no better workaround.

    setTimeout(function() {
        var password;

        if (isTeacher) {
            password = $('#' + TEACHER_PASSWORD_FIELD_ID).val();
        }
        else {
            password = $('#' + INDEP_STUDENT_PASSWORD_FIELD_ID).val();
        }

        var strength = 0;
        if (password.length > 0) { strength++; }
        if (password.length >= 8 && !(password.search(/[A-Z]/) === -1 || password.search(/[a-z]/) === -1 || password.search(/[0-9]/) === -1)) { strength++; }
        if ($.inArray(password, most_used_passwords_2018) >= 0 && strength == 2) { strength = 3; }

        if (isTeacher) {
            updatePasswordCSS('#teacher-password-sign', '#teacher-password-text', strength);
        }
        else {
            updatePasswordCSS('#student-password-sign', '#student-password-text', strength);
        }

    });
}

function updatePasswordCSS(passwordStrengthSign, passwordStrengthText, strength) {
    $(passwordStrengthSign).css('background-color', password_strengths[strength].colour);
    $(passwordStrengthText).html(password_strengths[strength].name);
}

