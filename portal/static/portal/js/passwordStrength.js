var TEACHER_PASSWORD_FIELD_ID = '';
var INDEP_STUDENT_PASSWORD_FIELD_ID = '';
let teacher_password_field = '';
let indep_student_password_field = '';
let most_used_passwords = ['Abcd1234', 'Password1', 'Qwerty123'];

let password_strengths = [
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
        let password;

        if (isTeacher) {
            password = $('#' + TEACHER_PASSWORD_FIELD_ID).val();
        }
        else {
            password = $('#' + INDEP_STUDENT_PASSWORD_FIELD_ID).val();
        }

        let strength = 0;
        if (password.length > 0) { strength++; }
        if (isPasswordStrong(password, isTeacher)) { strength++; }

        if ($.inArray(password, most_used_passwords) >= 0 && strength == 2) { strength = 3; }

        if (isTeacher) {
            updatePasswordCSS('#teacher-password-sign', '#teacher-password-text', strength);
        }
        else {
            updatePasswordCSS('#student-password-sign', '#student-password-text', strength);
        }

    });
}

function isPasswordStrong(password, isTeacher) {
    if (isTeacher) {
        return password.length >= 10 && !(password.search(/[A-Z]/) === -1 || password.search(/[a-z]/) === -1 || password.search(/[0-9]/) === -1 || password.search(/[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/) === -1)
    }
    else {
        return password.length >= 8 && !(password.search(/[A-Z]/) === -1 || password.search(/[a-z]/) === -1 || password.search(/[0-9]/) === -1)
    }
}

function updatePasswordCSS(passwordStrengthSign, passwordStrengthText, strength) {
    $(passwordStrengthSign).css('background-color', password_strengths[strength].colour);
    $(passwordStrengthText).html(password_strengths[strength].name);
}

