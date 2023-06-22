let password_strengths = [
  { name: 'No password!', colour: '#FF0000' },
  { name: 'Password too weak!', colour: '#DBA901' },
  { name: 'Password too common!', colour: '#DBA901' },
  { name: 'Strong password!', colour: '#088A08' }
];

async function handlePasswordStrength() {
  const teacherPassword = $('#id_teacher_signup-teacher_password').val();
  const independentStudentPassword = $(
    '#id_independent_student_signup-password'
  ).val();

  const isTeacherPasswordNonEmpty = teacherPassword.length > 0;
  const isIndependentStudentPasswordNonEmpty = independentStudentPassword.length > 0;

  const isTeacherPasswordComplex = isPasswordStrong(teacherPassword, true) && isTeacherPasswordNonEmpty;
  const isIndependentStudentPasswordComplex = isPasswordStrong(independentStudentPassword, false) && isIndependentStudentPasswordNonEmpty;

  const isTeacherPasswordNotPwned = await getPwnedStatus(teacherPassword) && isTeacherPasswordComplex;
  const isIndependentStudentPasswordNotPwned = await getPwnedStatus(independentStudentPassword) && isIndependentStudentPasswordComplex;

  const teacherPasswordStrength = [isTeacherPasswordNonEmpty, isTeacherPasswordComplex, isTeacherPasswordNotPwned].filter(value => value).length;
  const independentStudentPasswordStrength = [isIndependentStudentPasswordNonEmpty, isIndependentStudentPasswordComplex, isIndependentStudentPasswordNotPwned].filter(value => value).length;

    console.log(teacherPasswordStrength, independentStudentPasswordStrength)
    console.log(password_strengths)

    $('#teacher-password-sign').css(
      'background-color',
      password_strengths[teacherPasswordStrength].colour
    );
    $('#teacher-password-text').html(password_strengths[teacherPasswordStrength].name);
    $('#student-password-sign').css(
      'background-color',
      password_strengths[independentStudentPasswordStrength].colour
    );
    $('#student-password-text').html(password_strengths[independentStudentPasswordStrength].name);
}


const getPwnedStatus = async (password) => {
  const computeSHA1Hash = (password) =>
    CryptoJS.SHA1(password).toString().toUpperCase();

  const doesSuffixExist = (data, suffix) => data.includes(suffix);

  const calculateLevenshteinDistance = async (a, b) => {
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

    if (doesSuffixExist(data, suffix)) {
      return false;
    }

    const similarPasswords = data
      .split('\n')
      .map((line) => line.split(':'))
      .filter(
        ([hashSuffix]) => calculateLevenshteinDistance(suffix, hashSuffix) <= 2
      );

    if (similarPasswords.length > 0) {
      similarPasswords.forEach(([hashSuffix, count]) =>
        console.log(`Hash: ${hashSuffix}, Occurrences: ${count}`)
      );
    } else {
      return true;
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
