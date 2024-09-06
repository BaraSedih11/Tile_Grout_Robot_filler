// Add event listeners for movement buttons
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

// Toggle functionality for Apply and Empty Grout buttons
document.getElementById("applyGrout").addEventListener("click", function () {
  sendCommand("play");
});

document.getElementById("emptyGrout").addEventListener("click", function () {
  sendCommand("empty");
});

// Function to send commands to the Flask server
function sendCommand(command) {
  fetch("http://localhost:5000/command", {
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
