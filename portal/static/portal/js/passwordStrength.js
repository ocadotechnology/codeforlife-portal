var TEACHER_PASSWORD_FIELD_ID = '';
var INDEP_STUDENT_PASSWORD_FIELD_ID = '';
let teacher_password_field = '';
let indep_student_password_field = '';
let most_used_passwords = ['Abcd1234', 'Password1', 'Qwerty123'];

let password_strengths = [
    { name: 'No password!', colour: '#FF0000' },
    { name: 'Password too weak!', colour: '#DBA901' },
    { name: 'Strong password!', colour: '#088A08' },
    { name: 'Password too common!', colour: '#DBA901' }
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

const getPwnedStatus = async (password) => {
  const sha1Hash = (password) =>
    CryptoJS.SHA1(password).toString().toUpperCase();

  const checkIfHashExists = (data, suffix) => data.includes(suffix);

  const getLevenshteinDistance = (a, b) => {
    if (a.length === 0) return b.length;
    if (b.length === 0) return a.length;

    const matrix = Array.from({ length: a.length + 1 }, (_, i) => [i]);
    for (let j = 1; j <= b.length; j++) matrix[0][j] = j;

    for (let i = 1; i <= a.length; i++) {
      for (let j = 1; j <= b.length; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        matrix[i][j] = Math.min(
          matrix[i - 1][j] + 1, // deletion
          matrix[i][j - 1] + 1, // insertion
          matrix[i - 1][j - 1] + cost // substitution
        );
      }
    }

    return matrix[a.length][b.length];
  };

  try {
    const hashedPassword = sha1Hash(password);
    const [prefix, suffix] = [hashedPassword.substring(0, 5), hashedPassword.substring(5)];
    const url = `https://api.pwnedpasswords.com/range/${prefix}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error(`Request failed with status code: ${response.status}`);
    const data = await response.text();

    if (checkIfHashExists(data, suffix)) {
      console.log(`Password is pwned`);
      return;
    }

    const similarPasswords = data
      .split('\n')
      .map((line) => line.split(':'))
      .filter(([hashSuffix]) => getLevenshteinDistance(suffix, hashSuffix) <= 2);

    if (similarPasswords.length > 0) {
      console.log(`Similar passwords found within Levenshtein distance of 2:`);
      similarPasswords.forEach(([hashSuffix, count]) =>
        console.log(`Hash: ${hashSuffix}, Occurrences: ${count}`)
      );
    } else {
      console.log(`Password is not pwned`);
    }
  } catch (error) {
    console.error(`Request failed with error: ${error.message}`);
  }
};


function isPasswordStrong(password, isTeacher) {
    const isPasswordBreached = getPwnedStatus(password);
    if (isTeacher) {
        return password.length >= 10 && !(isPasswordBreached || password.search(/[A-Z]/) === -1 || password.search(/[a-z]/) === -1 || password.search(/[0-9]/) === -1 || password.search(/[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/) === -1)
    }
    else {
        return password.length >= 8 && !(password.search(/[A-Z]/) === -1 || password.search(/[a-z]/) === -1 || password.search(/[0-9]/) === -1)
    }
}

function updatePasswordCSS(passwordStrengthSign, passwordStrengthText, strength) {
    $(passwordStrengthSign).css('background-color', password_strengths[strength].colour);
    $(passwordStrengthText).html(password_strengths[strength].name);
}

