function post(path, params) {
  let form = document.createElement("form");
  form.setAttribute("method", "POST");
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

/**
 * Show a confirmation popup with Cancel and Confirm buttons.
 * @param {String} title The title of the popup.
 * @param {String} text The message of the popup.
 * @param {String} confirm_handler The Confirm button onclick attribute.
 */
function showPopupConfirmation(title, text, confirm_handler) {
  let popup = $("#popup");
  popup.find(".popup-box__title").text(title);
  popup.find(".popup-box__msg").append(text);
  popup.find("#confirm_button").attr("onclick", confirm_handler);

  popup.addClass("popup--fade");
}

function hidePopupConfirmation() {
  $("#popup").removeClass("popup--fade");
  $("#popup").find(".popup-text").remove();
}

function showDonateConfirmation(path) {
  let title = "We would love to have you support our non-profit mission! ❤️";
  let text =
      "<div class='popup-text'>" +
      "<h6>If you would like to be added to a mailing list and find out" +
      " more about how you could support our mission, please add your" +
      " email below.</h6>" +
      "</div>";
  let confirm_handler = "postWithCsrf('" + path + "')";

  showDonatePopup(title, text, confirm_handler);
}

/**
 * Show a service unavailable popup with a close button in the top-right corner.
 * @param {String} title The title of the popup.
 * @param {String} text The message of the popup.
 */

function showServiceUnavailable(title, text) {
  let popup = $("#service-unavailable-popup");
  popup.find(".popup-box__title > h5").text(title);
  popup.find(".popup-box__msg").append(text);

  popup.addClass("popup--fade");
}

function hideServiceUnavailable() {
  $("#service-unavailable-popup").removeClass("popup--fade");
}

/**
 * Show an info popup with a close button in the top-right corner.
 * @param {String} title The title of the popup.
 * @param {String} text The message of the popup.
 */

function showInfoPopup(title, text) {
  let popup = $("#info-popup");
  popup.find(".popup-box__title > h5").text(title);
  popup.find(".popup-box__msg").append(text);

  popup.addClass("popup--fade");
}

function hideInfoPopup() {
  $("#info-popup").removeClass("popup--fade");
}

function showScreentimePopup() {
  $("#screentime-popup").addClass("popup--fade");
}

function hideScreentimePopup() {
  $("#screentime-popup").removeClass("popup--fade");

  // Reset screentime warning for the user
  $.get("/user/reset_screentime_warning/");

  // Show the popup again after one hour - just in case the user stays on the same page
  setTimeout(showScreentimePopup, 3600000);
}

let interval;

function showSessionPopup() {
  $("#session-popup").addClass("popup--fade");
  const twoMinutes = 60 * 2
  const minutesDisplay = $('#minutes');
  const secondsDisplay = $('#seconds');
  startTimer(twoMinutes, minutesDisplay, secondsDisplay);
}

function hideSessionPopup() {
  $("#session-popup").removeClass("popup--fade");

  // Reset session time for the user
  $.get("/user/reset_session_time/");

  const minutesDisplay = $('#minutes');
  const secondsDisplay = $('#seconds');
  resetTimer(minutesDisplay, secondsDisplay)

  // Show the popup again after 28 minutes - just in case the user stays on the same page
  setTimeout(showSessionPopup, 1680000);
}

function startTimer(duration, minutesDisplay, secondsDisplay) {
  let timer = duration, minutes, seconds;
  interval = setInterval(function () {
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    minutes = minutes < 10 ? minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    minutesDisplay.text(minutes);
    secondsDisplay.text(seconds);

    if (--timer < 0) {
      document.location.reload(true);
    }
  }, 1000);
}

function resetTimer(minutesDisplay, secondsDisplay) {
  clearInterval(interval);
  minutesDisplay.text("2");
  secondsDisplay.text("00");
}

function postWithCsrf(path, params = undefined) {
  post(path, {
    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
    ...params,
  });
}

function disableOnClick(id) {
  return function () {
    let button = $(id);
    button.addClass("button--primary--disabled");
    button.attr("disabled", true);
    return true;
  };
}

function copyToClipboardFromElement(tooltipElement, elementSelector) {
  let value = document.querySelector(elementSelector).textContent;
  navigator.clipboard.writeText(value);

  // Show the tooltip
  $(tooltipElement).tooltip("show");

  // Clear the previous timeout
  clearTimeout($(tooltipElement).data("timeout"));

  // Set a timeout to hide the tooltip after 2 seconds
  let timeout = setTimeout(() => {
    $(tooltipElement).tooltip("hide");
    $(tooltipElement).removeData("timeout");
  }, 2000);
  $(tooltipElement).data("timeout", timeout);
}

// Enable copy-to-clipboard tooltips
$(document).ready(function () {
  $('[data-toggle="copyToClipboardTooltip"]').tooltip({
    title: "Copied to clipboard!",
    trigger: "manual",
    placement: "auto top",
  });
});

/**
 * OnChange function that parses the selected students CSV file and populate a target with the contents.
 * @param {String} targetSelector The ID of the element where the CSV contents will be prepended.
 */
function studentsCsvChange(targetSelector) {
  return function () {
    $(this).parse({
      config: {
        header: true,
        // make the header case insensitive
        transformHeader: function (header) {
          return header.toLowerCase();
        },
        complete: function (results) {
          if (!results.meta.fields.includes("name")) {
            return alert("'Name' column not found in CSV file.");
          }
          const newStudents = results.data.map((row) => row["name"]).join("\n");
          const currentStudents = $(targetSelector).val();
          $(targetSelector).val(`${newStudents}\n${currentStudents}`);
        },
        skipEmptyLines: true,
      },
    });
  };
}

/**
 * Import students' names from a 'Name' column in a CSV file and prepend them to an element.
 * @param {String} triggerSelector The selector of the element triggering the file input on click
 * @param {String} targetSelector The ID of the element where the CSV contents will be prepended
 */
function importStudentsFromCsv(triggerSelector, targetSelector) {
  $(triggerSelector).on("click", function () {
    const fileInput = $("<input>").attr({
      type: "file",
      accept: "text/csv",
    });
    fileInput.on("change", studentsCsvChange(targetSelector));
    fileInput.trigger("click");
  });
}
