function post(path, params) {

    var form = document.createElement("form");
    form.setAttribute("method", 'POST');
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}

var defaultConfirmationOptions = {
    autoOpen: false,
    resizable: false,
    width:350,
    height:250,
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
