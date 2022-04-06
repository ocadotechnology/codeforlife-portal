/* global showPopupConfirmation */

function showRemoveConfirmation(path, name) {
  let title = "Remove teacher";
  let text =
    "<div class='popup-text'><p>The teacher " +
    name +
    ", will be removed from the school or club. If they have any classes you will be asked to move them to other teachers of this school or club.</p><p>Are you sure?</p></div>";
  let confirm_handler = "postWithCsrf('" + path + "')";

  showPopupConfirmation(title, text, confirm_handler);
}

function showToggleAdminConfirmation(path, name) {
  let title = "Make teacher admin";
  let text =
    "<div class='popup-text'><p>The teacher " +
    name +
    ", will be made an administrator of this school or club. They will gain all of the powers that you currently have.</p><p>Are you sure?</p></div>";
  let confirm_handler = "postWithCsrf('" + path + "')";

  showPopupConfirmation(title, text, confirm_handler);
}

function showDisable2FAConfirmation(path, name) {
  let title = "Disable 2FA for " + name;
  let text =
    "<div class='popup-text'><p>The teacher " +
    name +
    ", will have their two factor authentication disabled. This will make their account less secure.</p><p>Are you sure?</p></div>";
  let confirm_handler = "postWithCsrf('" + path + "')";

  showPopupConfirmation(title, text, confirm_handler);
}

/**
 * Show an account delete confirmation popup with a red delete button and either a Cancel or a Review classes button.
 * See dashboard.html for the popup declaration.
 */
function showDeleteAccountConfirmation(delete_password, unsubscribe_newsletter, has_class = true) {
  const popup = $("#popup-delete-review");

  if (has_class) {
    popup.find(".popup-box__title").text("You still have classes associated with this account");
    popup
      .find(".popup-box__msg")
      .append("Review classes if you would like to download the scoreboard or transfer students first.");

    popup.find("#cancel_popup_button").hide();
  } else {
    popup.find(".popup-box__title").text("You are about to delete your account");
    popup.find(".popup-box__msg").append("This action is not reversible. Are you sure you wish to proceed?");

    popup.find("#review_button").hide();
  }

  const delete_button = popup.find("#delete_button");
  const delete_path = delete_button.data("delete-path");
  const handler =
    "postWithCsrf('" +
    delete_path +
    "', {password: '" +
    delete_password +
    "', unsubscribe_newsletter: '" +
    unsubscribe_newsletter +
    "'})";

  delete_button.attr("onclick", handler);

  popup.addClass("popup--fade");
}

function hideDeleteAccountPopup() {
  $("#popup-delete-review").removeClass("popup--fade");
}
