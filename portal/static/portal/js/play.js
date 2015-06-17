function init() {
  $('#switchToSolo').click(function() {
    $('#school-login').hide();
    $('#solo-login').show();
    return false;
  });

  $('#switchToSchool').click(function() {
    $('#solo-login').hide();
    $('#school-login').show();
    return false;
  });

  $('#signupShow').click(function() {
    $('#signup-warning').hide();
    $('#form-signup-solo-student').show();
    return false;
  });

  $('#register-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#signup-warning').hide();
    $('#form-signup-solo-student').show();
    return false;
  });

  $('#solo-login-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#switchToSolo').click();
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
    if (!SIGNUP_VIEW) {
      $('#signup-form').hide();
    }
    else {
      $('#signup-warning').hide();
    }
    if (SOLO_VIEW) {
      $('#switchToSolo').click();
    }
    else {
      $('#switchToSchool').click();
    }
});