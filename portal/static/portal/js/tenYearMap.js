let currentActivePin;

function setActivePin(city) {
  if (currentActivePin) {
    currentActivePin.setAttribute("fill", "#00A3E0");
  }

  currentActivePin = document.getElementById(city + "-pin").getElementsByTagName("svg")[0]
  currentActivePin.setAttribute("fill", "#EE0857");
}