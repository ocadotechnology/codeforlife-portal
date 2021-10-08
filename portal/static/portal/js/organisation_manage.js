/* global showPopupConfirmation */

function showRemoveConfirmation(path, name) {
    let title = "Remove teacher";
    let text = "<div class='popup-text'><p>The teacher " + name + ", will be removed from the school or club. If they have any classes you will be asked to move them to other teachers of this school or club.</p><p>Are you sure?</p></div>";
    let confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}

function showToggleAdminConfirmation(path, name) {
    let title = "Make teacher admin";
    let text = "<div class='popup-text'><p>The teacher " + name + ", will be made an administrator of this school or club. They will gain all of the powers that you currently have.</p><p>Are you sure?</p></div>";
    let confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}

function showDisable2FAConfirmation(path, name) {
    let title = "Disable 2FA for " + name;
    let text = "<div class='popup-text'><p>The teacher " + name + ", will have their two factor authentication disabled. This will make their account less secure.</p><p>Are you sure?</p></div>";
    let confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}
