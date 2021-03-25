/*
Code for Life

Copyright (C) 2021, Ocado Innovation Limited

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

ADDITIONAL TERMS – Section 7 GNU General Public Licence

This licence does not grant any right, title or interest in any “Ocado” logos,
trade names or the trademark “Ocado” or any other trademarks or domain names
owned by Ocado Innovation Limited or the Ocado group of companies or any other
distinctive brand features of “Ocado” as may be secured from time to time. You
must not distribute any modification of this program using the trademark
“Ocado” or claim any affiliation or association with Ocado or its employees.

You are not authorised to use the name Ocado (or any of its trade names) or
the names of any author or contributor in advertising or for publicity purposes
pertaining to the distribution of this program, without the prior written
authorisation of Ocado.

Any propagation, distribution or conveyance of this program must include this
copyright notice and these terms. You must not misrepresent the origins of this
program; modified versions of the program must be marked as such and not
identified as the original program.
*/

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
