/* global showPopupConfirmation */
/* global hidePopupConfirmation */

function classesText(classes) {
  return classes
    .map(
      (name, index) =>
        `${
          index === 0
            ? ""
            : index === classes.length - 1
            ? " and "
            : ", "
        }<strong>${$("<div>").text(name).html()}</strong>`
    )
    .join("");
}

function clickDeleteGames() {
  let selectedGameIds = [];
  let selectedClasses = [];
  $("input[name='game_ids']:checked").each(function () {
    selectedGameIds.push($(this).val());
    selectedClasses.push($(this).data("className"));
  });

  if (!selectedGameIds.length) {
    return;
  }

  let title = "Delete class games";
  let text = `
    <div class='popup-text'>
      <p>Are you sure that you want to delete the game${
          selectedClasses.length > 1 ? "s" : ""
        } for ${classesText(selectedClasses)}?</p>
      <p>This action will delete any progress ${
        selectedClasses.length > 1 ? "those classes have" : "that class has"
      } made.</p>
    </div>`;
  let confirmHandler = "deleteGames()";

  showPopupConfirmation(title, text, confirmHandler);
  let popup = $(".popup-wrapper");
  popup.data("gameIds", selectedGameIds);
}

function deleteGames() {
  let gameIds = $("#popup").data("gameIds");

  $.ajax({
    url: "/kurono/api/games/delete_games/",
    type: "POST",
    data: { game_ids: gameIds },
    traditional: true,
    headers: {
      "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
    },
    success: function (data) {
      hidePopupConfirmation();
      document.location.reload(true);
    },
  });
}

function changeWorksheetConfirmation(gameID, className, worksheetID) {
  let title = "Change Challenge";
  let text =
    "<div class='popup-text'><p>Please confirm that you would like to change the challenge for class: " +
    "<strong class='popup__class-name'></strong>. This will change the level for the students when they rejoin " +
    "the game.</p></div>";
  let confirmHandler = "changeWorksheet()";

  showPopupConfirmation(title, text, confirmHandler);
  let popup = $(".popup-wrapper");
  popup.data("gameId", gameID);
  popup.data("worksheetId", worksheetID);
  $(".popup__class-name").text(className);
}

function changeWorksheet() {
  let gameID = $("#popup").data("gameId");
  let worksheetID = $("#popup").data("worksheetId");

  $.ajax({
    url: "/kurono/api/games/" + gameID + "/",
    type: "PUT",
    data: { worksheet_id: worksheetID },
    success: function (data) {
      hidePopupConfirmation();
      document.location.reload(true);
    },
  });
}
