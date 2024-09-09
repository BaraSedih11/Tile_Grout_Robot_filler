// Helper function to send commands to the server
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
      document.getElementById("responseOutput").innerText = data.response
        ? data.response
        : "No response from Arduino";
    })
    .catch((error) => {
      document.getElementById("responseOutput").innerText =
        "Error: " + error.message;
    });
}

// Event listeners for the buttons
document.getElementById("front").addEventListener("click", function () {
  sendCommand("MOVE_FORWARD 10");
});

document.getElementById("back").addEventListener("click", function () {
  sendCommand("MOVE_BACKWARD 10");
});

document.getElementById("left").addEventListener("click", function () {
  sendCommand("ROTATE_LEFT 10");
});

document.getElementById("right").addEventListener("click", function () {
  sendCommand("ROTATE_RIGHT 10");
});

document.getElementById("stop").addEventListener("click", function () {
  sendCommand("STOP");
});

document.getElementById("applyGrout").addEventListener("click", function () {
  sendCommand("APPLY");
});

document.getElementById("emptyGrout").addEventListener("click", function () {
  sendCommand("EMPTY");
});

document.getElementById("automatic").addEventListener("click", function () {
  sendCommand("MOVE_FORWARD 80.5");
  sendCommand("MOVE_BACKWARD 15");
  sendCommand("ROTATE_LEFT 194");
  sendCommand("MOVE_FRONT 16");
  sendCommand("ROTATE_LEFT 97");
  sendCommand("MOVE_BACKWARD 10");

  sleep(1000);

  sendCommand("MOVE_FORWARD 121");
  sendCommand("MOVE_BACKWARD 10");
  sendCommand("ROTATE_LEFT 194");
  sendCommand("MOVE_FRONT 16");
  sendCommand("ROTATE_LEFT 97");
  sendCommand("MOVE_BACKWARD 10");

  sleep(1000);

  sendCommand("MOVE_FORWARD 80.5");
  sendCommand("MOVE_BACKWARD 15");
  sendCommand("ROTATE_LEFT 194");
  sendCommand("MOVE_FRONT 16");
  sendCommand("ROTATE_LEFT 97");
  sendCommand("MOVE_BACKWARD 10");

  sleep(1000);

  sendCommand("MOVE_FORWARD 121");
  sendCommand("MOVE_BACKWARD 10");
  sendCommand("ROTATE_LEFT 194");
  sendCommand("MOVE_FRONT 16");
  sendCommand("ROTATE_LEFT 97");
  sendCommand("MOVE_BACKWARD 10");
});

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
