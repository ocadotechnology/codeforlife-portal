$(document).ready(() => {
  $('#edit-student-password-form').on(
    'click',
    '#password-field-icon, #confirm-password-field-icon',
    () => {
      let inputType;
      let dataIcon = $('#password-field-icon').attr('data-icon');
      if (dataIcon === 'material-symbols:visibility') {
        inputType = 'password';
        dataIcon = 'material-symbols:visibility-off';
      } else {
        inputType = 'text';
        dataIcon = 'material-symbols:visibility';
      }

      $('#id_password').attr('type', inputType);
      $('#id_confirm_password').attr('type', inputType);

      $('#password-field-icon').attr('data-icon', dataIcon);
      $('#confirm-password-field-icon').attr('data-icon', dataIcon);
    }
  );
});