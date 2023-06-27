let password_strengths = [
  { name: 'No password!', colour: '#FF0000' },
  { name: 'Password too weak!', colour: '#DBA901' },
  { name: 'Password too common!', colour: '#DBA901' },
  { name: 'Strong password!', colour: '#088A08' }
];

async function handlePasswordStrength() {
  const tPwd = $('#id_teacher_signup-teacher_password').val();
  const sPwd = $('#id_independent_student_signup-password').val();

  const isTPwdEmpty = tPwd.length > 0;
  const isSPwdEmpty = sPwd.length > 0;

  const isTPwdStrong = isTPwdEmpty && isPasswordStrong(tPwd, true);
  const isSPwdStrong = isSPwdEmpty && isPasswordStrong(sPwd, false);

  const isTPwdSafe = isTPwdStrong && (await getPwnedStatus(tPwd));
  const isSPwdSafe = isSPwdStrong && (await getPwnedStatus(sPwd));

  const tPwdStr = [isTPwdEmpty, isTPwdStrong, isTPwdSafe].filter(
    Boolean
  ).length;
  const sPwdStr = [isSPwdEmpty, isSPwdStrong, isSPwdSafe].filter(
    Boolean
  ).length;

  $('#teacher-password-sign').css(
    'background-color',
    password_strengths[tPwdStr].colour
  );
  $('#teacher-password-text').html(password_strengths[tPwdStr].name);
  $('#student-password-sign').css(
    'background-color',
    password_strengths[sPwdStr].colour
  );
  $('#student-password-text').html(password_strengths[sPwdStr].name);
}

const getPwnedStatus = async (password) => {
  const computeSHA1Hash = (password) =>
    CryptoJS.SHA1(password).toString().toUpperCase();

  const doesSuffixExist = (data, suffix) => data.includes(suffix);

  try {
    const hashedPassword = computeSHA1Hash(password);
    const prefix = hashedPassword.substring(0, 5);
    const suffix = hashedPassword.substring(5);
    const apiUrl = `https://api.pwnedpasswords.com/range/${prefix}`;

    const response = await fetch(apiUrl);

    if (!response.ok) {
      return true; // ignore the check if the server is down as the popup warns
      // the user that we cannot check the password
    }

    const data = await response.text();
    console.log(data);

    if (doesSuffixExist(data, suffix)) {
      return false;
    }
    return true;
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
