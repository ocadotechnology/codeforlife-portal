$(function() {
    var updateFunction = (PASSWORD_TYPE == 'STUDENT') ? updateStudentPasswordStrength : updateTeacherPasswordStrength;

    password_field = $('#' + PASSWORD_FIELD_ID);
    password_field.on('keydown', updateFunction);
    password_field.on('paste', updateFunction);
    password_field.on('cut', updateFunction);
    updateFunction();
});

var teacher_password_strengths = [
    { name: 'Pasword quality', colour: '' },
    { name: 'Poor quality', colour: '#FF0000' },
    { name: 'Not quite', colour: '#DBA901' },
    { name: 'Nearly there', colour: '#D7DF01' },
    { name: 'Good password', colour: '#088A08' }
];

function updateTeacherPasswordStrength() {
    // The reason for the timeout is that if we just got $('#...').val() we'd get the
    // old value before the keypress / change. Apparently even jQuery itself implements
    // things this way, so maybe there is no better workaround.

    setTimeout(function() {
        var password = $('#' + PASSWORD_FIELD_ID).val();

        var strength = 4;
        if (password.length < 8) { strength--; }
        if (password.search(/[A-Z]/) === -1) { strength--; }
        if (password.search(/[a-z]/) === -1) { strength--; }
        if (password.search(/[0-9]/) === -1) { strength--; }

        $('.password-strength-bar').css('width', strength / 4 * 100 + '%');
        $('.password-strength-bar').css('background-color', teacher_password_strengths[strength].colour);
        $('.password-strength-text').html(teacher_password_strengths[strength].name);
    });
}

var student_password_strengths = [
    { name: 'Pasword quality', colour: '' },
    { name: 'Not long enough', colour: '#DBA901' },
    { name: 'Good password', colour: '#088A08' }
];

function updateStudentPasswordStrength() {
    setTimeout(function() {
        var password = $('#' + PASSWORD_FIELD_ID).val();

        var strength = 0;
        if (password == '') { strength = 0; }
        else if (password.length < 6) { strength = 1; }
        else if (password.length >= 6) { strength = 2; }

        $('.password-strength-bar').css('width', strength / 2 * 100 + '%');
        $('.password-strength-bar').css('background-color', student_password_strengths[strength].colour);
        $('.password-strength-text').html(student_password_strengths[strength].name);
    });
}