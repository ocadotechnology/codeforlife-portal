$(function() {
    password_field = $('#' + PASSWORD_FIELD_ID);
    password_field.on('keydown', updatePasswordStrength);
    password_field.on('paste', updatePasswordStrength);
    password_field.on('cut', updatePasswordStrength);
    updatePasswordStrength();
});

var password_strengths = [
    { name: 'Pasword quality', colour: '' },
    { name: 'Poor quality', colour: '#FF0000' },
    { name: 'Not quite', colour: '#DBA901' },
    { name: 'Nearly there', colour: '#D7DF01' },
    { name: 'Good password', colour: '#088A08' }
];

function updatePasswordStrength() {
    // The reason for the timeout is that if we just got $('#...').val() we'd get the
    // old value before the keypress / change. Apparently even jQuery itself implements
    // things this way, so maybe there is no better workaround.

    setTimeout(function() {
        var password = $('#' + PASSWORD_FIELD_ID).val();

        var strength = password_strengths.length - 1;
        if (password.length < PASSWORD_LENGTH) { strength--; }
        if (PASSWORD_UPPER && password.search(/[A-Z]/) === -1) { strength--; }
        if (PASSWORD_LOWER && password.search(/[a-z]/) === -1) { strength--; }
        if (PASSWORD_NUMBERS && password.search(/[0-9]/) === -1) { strength--; }

        $('.password-strength-bar').css('width', strength / (password_strengths.length - 1) * 100 + '%');
        $('.password-strength-bar').css('background-color', password_strengths[strength].colour);
        $('.password-strength-text').html(password_strengths[strength].name);
    });
}