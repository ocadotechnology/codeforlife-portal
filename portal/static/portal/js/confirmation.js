var defaultConfirmationOptions = {
    autoOpen: false,
    resizable: false,
    height:200,
    modal: true,
    buttons: {
        Cancel: function() {
            $(this).dialog('close');
        }
    }
}

function openConfirmationBox(name) {
    var data = CONFIRMATION_DATA[name]

    // copy the default options
    opts = $.extend(defaultConfirmationOptions, {})

    // add in the confirmation function if supplied
    if (data.confirm) {
        opts.buttons.Confirm = function() {
            $(this).dialog('close');
            data.confirm();
        }
    }

    // now override with any user supplied options
    opts = $.extend(opts, data.options | {})

    $('#confirmation-dialog').dialog('option', opts)
    $('#confirmation-dialog').html(CONFIRMATION_DATA[name].html)
    $('#confirmation-dialog').attr('title', data.title | '');
    $('#confirmation-dialog').dialog('open');
}

$(function() {
    $('#confirmation-dialog').dialog(defaultConfirmationOptions);
});