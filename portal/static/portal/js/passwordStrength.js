const TEACHER_PASSWORD_FIELD = $(`#${TEACHER_PASSWORD_FIELD_ID}`);
const INDEP_STUDENT_PASSWORD_FIELD = $(`#${INDEP_STUDENT_PASSWORD_FIELD_ID}`);

let password_strengths = [
  { name: 'No password!', colour: '#FF0000' },
  { name: 'Password too weak!', colour: '#DBA901' },
  { name: 'Password too common!', colour: '#DBA901' },
  { name: 'Strong password!', colour: '#088A08' }
];

async function handlePasswordStrength() {
  const teacherPwd = TEACHER_PASSWORD_FIELD.val();
  const studentPwd = INDEP_STUDENT_PASSWORD_FIELD.val();

  const isTeacherPwdTyped = teacherPwd.length > 0;
  const isStudentPwdTyped = studentPwd.length > 0;

  const isTeacherPwdStrong =
    isTeacherPwdTyped && isPasswordStrong(teacherPwd, true);
  const isStudentPwdStrong =
    isStudentPwdTyped && isPasswordStrong(studentPwd, false);

  const isTeacherPwdSafe =
    isTeacherPwdStrong && !(await isPasswordPwned(teacherPwd));
  const isStudentPwdSafe =
    isStudentPwdStrong && !(await isPasswordPwned(studentPwd));

  const teacherPwdStrength = [
    isTeacherPwdTyped,
    isTeacherPwdStrong,
    isTeacherPwdSafe
  ].filter(Boolean).length;
  const studentPwdStrength = [
    isStudentPwdTyped,
    isStudentPwdStrong,
    isStudentPwdSafe
  ].filter(Boolean).length;

  $('#teacher-password-sign').css(
    'background-color',
    password_strengths[teacherPwdStrength].colour
  );
  $('#teacher-password-text').html(password_strengths[teacherPwdStrength].name);
  $('#student-password-sign').css(
    'background-color',
    password_strengths[studentPwdStrength].colour
  );
  $('#student-password-text').html(password_strengths[studentPwdStrength].name);
}

const isPasswordPwned = async (password) => {
  const computeSHA1Hash = (password) =>
    CryptoJS.SHA1(password).toString().toUpperCase();

  try {
    const hashedPassword = computeSHA1Hash(password);
    const prefix = hashedPassword.substring(0, 5);
    const suffix = hashedPassword.substring(5);
    const apiUrl = `https://api.pwnedpasswords.com/range/${prefix}`;

    const response = await fetch(apiUrl);

    if (!response.ok) {
      return false; // ignore the check if the server is down as the popup warns
      // the user that we cannot check the password
    }

    const data = await response.text();

    return data.includes(suffix);
  } catch (error) {
    console.error(`Request failed with error: ${error.message}`);
    return false;
  }
};

function isPasswordStrong(password, isTeacher) {
  if (isTeacher) {
    return (
      password.length >= 10 &&
      !(
        password.search(/[A-Z]/) === -1 ||
        password.search(/[a-z]/) === -1 ||
        password.search(/[0-9]/) === -1 ||
        password.search(/[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/) === -1
      )
    );
  } else {
    return (
      password.length >= 8 &&
      !(
        password.search(/[A-Z]/) === -1 ||
        password.search(/[a-z]/) === -1 ||
        password.search(/[0-9]/) === -1
      )
    );
  }
}

async function isPwnedPasswordApiAvailable(url) {
  try {
    const response = await fetch(url, { metheod: 'GET' });
    return response.ok;
  } catch (error) {
    console.error(error);
    return false;
  }
}
async function handlePwnedPasswordApiAvailability() {
  const url = 'https://api.pwnedpasswords.com/range/00000';
  const isAvailable = await isPwnedPasswordApiAvailable(url);
  const errorTitle = 'Password Vulnerability Check Unavailable';
  const errorMessage =
    'We are currently unable to check your password vulnerability. Please ensure that you are using a strong password. If you are happy to continue, please confirm.';
  if (!isAvailable) {
    showServiceUnavailable(errorTitle, errorMessage);
  }
}

$(document).ready(function () {
  handlePasswordStrength(); // the password strength text is updated dynamically hence this is the initial first call
  handlePwnedPasswordApiAvailability();
  $(
    `#${TEACHER_PASSWORD_FIELD_ID}, #${INDEP_STUDENT_PASSWORD_FIELD_ID}`
  ).on('input change focus blur', handlePasswordStrength);
});
