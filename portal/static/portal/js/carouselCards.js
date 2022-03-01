function setUpCarouselCards(cardsLength) {
  $(document).ready(function () {
    $("#carouselCards").on("slide.bs.carousel", function (event) {
      let cardIndex = $(event.relatedTarget).index();
      let indexLimit = cardsLength - 3;

      // don't slide if the card is out of range
      if (cardIndex > indexLimit) {
        return false;
      }

      // add disabled classes if it's the first or last card
      if (cardIndex === 0) {
        $(".carousel-nav > .prev").addClass("disabled");
      } else {
        $(".carousel-nav > .prev").removeClass("disabled");
      }
      if (cardIndex >= indexLimit) {
        $(".carousel-nav > .next").addClass("disabled");
      } else {
        $(".carousel-nav > .next").removeClass("disabled");
      }
    });
  });
}
