/* global showPopupConfirmation */

function showRemoveConfirmation(path, name) {
    var title = "Remove teacher";
    var text = "<div class='popup-text'><p>The teacher " + name + ", will be removed from the school or club. If they have any classes you will be asked to move them to other teachers of this school or club.</p><p>Are you sure?</p></div>";
    var confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}

function showToggleAdminConfirmation(path, name) {
    var title = "Remove teacher";
    var text = "<div class='popup-text'><p>The teacher " + name + ", will be made an administrator of this school or club. They will gain all of the powers that you currently have.</p><p>Are you sure?</p></div>";
    var confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}

function showDisable2FAConfirmation(path, name) {
    var title = "Disable 2FA for " + name;
    var text = "<div class='popup-text'><p>The teacher " + name + ", will have their two factor authentication disabled. This will make their account less secure.</p><p>Are you sure?</p></div>";
    var confirm_handler = "postWithCsrf('" + path + "')";

    showPopupConfirmation(title, text, confirm_handler);
}
