$(document).ready(() => {
  $('#form-login-teacher').on('click', '#password-field-icon', () => {
    let inputType;
    let dataIcon = $('#password-field-icon').attr('data-icon');
    if (dataIcon === 'material-symbols:visibility') {
      inputType = 'password';
      dataIcon = 'material-symbols:visibility-off';
    } else {
      inputType = 'text';
      dataIcon = 'material-symbols:visibility';
    }

    $('#id_auth-password').attr('type', inputType);
    $('#password-field-icon').attr('data-icon', dataIcon);
  });
});
