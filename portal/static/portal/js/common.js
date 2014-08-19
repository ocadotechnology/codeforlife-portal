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
    draggable: false,
    modal: true,
    buttons: {
        Cancel: function() {
            $(this).dialog('close');
        }
    }
}

function openConfirmationBox(name) {
    var data = CONFIRMATION_DATA[name]

    // copy the default options, overriding with our own where appropriate
    opts = $.extend(defaultConfirmationOptions, data.options)

    // add in the confirmation function if supplied
    if (data.confirm) {
        opts.buttons.Confirm = function() {
            $(this).dialog('close');
            data.confirm();
        }
    }

    $('#confirmation-dialog').dialog('option', opts)
    $('#confirmation-dialog').html(data.html)
    $('#confirmation-dialog').dialog('open');
}

$(function() {
    $('#confirmation-dialog').dialog(defaultConfirmationOptions);
});
