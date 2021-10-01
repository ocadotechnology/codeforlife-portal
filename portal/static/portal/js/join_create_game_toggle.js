$(document).ready(function () {
  var formGameClassId = $("#id_game_class");
  var createGameForm = $("#create-game-form");

  $("#add-class-dropdown-menu > li > a")
    .filter(":not(.disabled)")
    .each(function () {
      let classId = $(this).data("classId");
      $(this).click(function () {
        formGameClassId.val(classId);
        createGameForm.submit();
      });
    });
});
