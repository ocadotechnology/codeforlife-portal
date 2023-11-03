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

function showToggleAdminConfirmation(path) {
  let confirm_handler = "postWithCsrf('" + path + "')";
  const popup = $("#popup-make-admin-teacher")
  popup.addClass("popup--fade")
  const add_admin_button = $("#add_admin_button")
  add_admin_button.attr("onclick", confirm_handler)
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
 * Popup for inviting a teacher
**/
function showMakeAdminTeacherPopup(event) {
  const popup = $("#popup-make-admin-teacher")
  const is_invite_admin = document.getElementById("id_make_admin_ticked").checked
  if (is_invite_admin) {
    event.preventDefault()
    popup.addClass("popup--fade");
    const add_admin_button = $("#add_admin_button")

    add_admin_button.on("click", () => event.target.submit())
  }
}

function hideMakeAdminTeacherPopup() {
  $("#popup-make-admin-teacher").removeClass("popup--fade");
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

$(document).ready(() => {
  $('#edit_account_details_password, #student_account_form').on(
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

  $('#edit_account_details_password, #student_account_form').on(
    'click',
    '#current-password-field-icon',
    () => {
      let inputType;
      let dataIcon = $('#current-password-field-icon').attr('data-icon');
      if (dataIcon === 'material-symbols:visibility') {
        inputType = 'password';
        dataIcon = 'material-symbols:visibility-off';
      } else {
        inputType = 'text';
        dataIcon = 'material-symbols:visibility';
      }

      $('#id_current_password').attr('type', inputType);
      $('#current-password-field-icon').attr('data-icon', dataIcon);
    }
  );

  $('#delete-account, #delete-indy-account').on(
    'click',
    '#delete-password-field-icon',
    () => {
      let inputType;
      let dataIcon = $('#delete-password-field-icon').attr('data-icon');
      if (dataIcon === 'material-symbols:visibility') {
        inputType = 'password';
        dataIcon = 'material-symbols:visibility-off';
      } else {
        inputType = 'text';
        dataIcon = 'material-symbols:visibility';
      }

      $('#id_delete_password').attr('type', inputType);
      $('#delete-password-field-icon').attr('data-icon', dataIcon);
    }
  );
});
