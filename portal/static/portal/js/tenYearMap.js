let currentActivePin;
let currentActiveCarousel;

function setActivePin(city) {
  if (currentActivePin) {
    currentActivePin.setAttribute("fill", "#00A3E0");
  }

  currentActivePin = document.getElementById(city + "-pin").getElementsByTagName("svg")[0]
  currentActivePin.setAttribute("fill", "#EE0857");

  if (currentActiveCarousel) {
    currentActiveCarousel.setAttribute("class", "item");
  }

  currentActiveCarousel = document.getElementById(city + "-carousel");
  currentActiveCarousel.setAttribute("class", "item active");
}