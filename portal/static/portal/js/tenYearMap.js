let currentActivePin;

function setActivePin(city) {
  if (currentActivePin) {
    currentActivePin.setAttribute("fill", "#FFC709");
  }

  currentActivePin = document.getElementById(city + "-pin").getElementsByTagName("svg")[0]
  currentActivePin.setAttribute("fill", "#EE0857");
}

$(document).ready(function () {
  setActivePin("hatfield");
});
