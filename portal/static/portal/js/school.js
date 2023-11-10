$(document).ready(() => {
  if ($("#id_country").val() !== 'GB') {
    $('#form-row-county').hide();
  }

  $('#id_country').on('change', (event) => {
    if (event.target.value === 'GB') {
      $('#form-row-county').show();
    } else {
      $('#form-row-county').hide();
    }
  });
});
