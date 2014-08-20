function init() {
  $('#switchToSolo').click(function() {
    $('#school-login').hide()
    $('#solo-login').show()
  });

  $('#switchToSchool').click(function() {
    $('#solo-login').hide()
    $('#school-login').show()
  });

  $('#signupShow').click(function() {
    $('#signup-warning').hide()
    $('#signup-form').show()
  });

  $('#register-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#signup-warning').hide()
    $('#signup-form').show()
  });

  $('#solo-login-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#switchToSolo').click()
  });

  $('#school-login-link').click(function() {
    // TODO test if logged in and show popup box saying logged in, please log out first, etc.
    $('#switchToSchool').click()
  });

};

$( document ).ready(function() {
    init();
    if (!SIGNUP_VIEW) {
      $('#signup-form').hide()
    }
    else {
      $('#signup-warning').hide()
    }
    if (SOLO_VIEW) {
      $('#switchToSolo').click()
    }
    else {
      $('#switchToSchool').click()
    }

});