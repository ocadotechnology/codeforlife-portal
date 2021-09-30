function init() {
  $('#switchToIndependentStudent').click(function() {
    $('#school-login').hide();
    $('#independent-student-login').show();
    return false;
  });

  $('#switchToSchool').click(function() {
    $('#independent-student-login').hide();
    $('#school-login').show();
    return false;
  });

  $('#signupShow').click(function() {
    $('#signup-warning').hide();
    $('#form-signup-independent-student').show();
    return false;
  });

  $('#register-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#signup-warning').hide();
    $('#form-signup-independent-student').show();
    return false;
  });

  $('#independent-student-login-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#switchToIndependentStudent').click();
    return false;
  });

  $('#school-login-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#switchToSchool').click();
    return false;
  });

};

$(function() {
    init();
    if (SIGNUP_VIEW) {
      $('#signupShow').click();
    }
    if (INDEPENDENT_STUDENT_VIEW) {
      $('#switchToIndependentStudent').click();
    }
    else {
      $('#switchToSchool').click();
    }
});
