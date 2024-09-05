document.getElementById("front").addEventListener("click", function () {
  sendCommand("front");
});

document.getElementById("back").addEventListener("click", function () {
  sendCommand("back");
});

document.getElementById("left").addEventListener("click", function () {
  sendCommand("left");
});

document.getElementById("right").addEventListener("click", function () {
  sendCommand("right");
});

document.getElementById("stop").addEventListener("click", function () {
  sendCommand("stop");
});

document.getElementById("play").addEventListener("click", function () {
  sendCommand("play");
});

function sendCommand(command) {
  fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command: command }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
