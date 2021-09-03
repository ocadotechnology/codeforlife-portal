function post(path, params) {

    let form = document.createElement("form");
    form.setAttribute("method", 'POST');
    form.setAttribute("action", path);

    for (let key in params) {
        if (params.hasOwnProperty(key)) {
            let hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}

function showPopupConfirmation(title, text, confirm_handler) {
    let popup = $(".popup-wrapper");
    $(".popup-box__title").text(title);
    $(".popup-box__msg").append(text);
    $("#confirm_button").attr("onclick", confirm_handler);

    popup.addClass("popup--fade");
}

function hidePopupConfirmation() {
    $(".popup-wrapper").removeClass("popup--fade");
    $(".popup-text").remove();
}

function postWithCsrf(path) {
    post(path, {
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    });
}

function disableOnClick(id) {
    return function () {
        let button = $(id);
        button.addClass('button--primary--disabled');
        button.attr('disabled', true);
        return true;
    }
}
