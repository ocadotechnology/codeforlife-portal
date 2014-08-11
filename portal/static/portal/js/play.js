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
};

$( document ).ready(function() {
    init();
    $('#signup-form').hide()
    $('#switchToSchool').click()
});
