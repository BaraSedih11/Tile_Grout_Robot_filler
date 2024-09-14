// Helper function to send commands to the server
function sendCommand(command) {
  fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command: command }),
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
  sendCommand("ROTATE_LEFT 1");
});

document.getElementById("right").addEventListener("click", function () {
  sendCommand("ROTATE_RIGHT 1");
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
  const width = document.getElementById("width").value;
  const rows = document.getElementById("rows").value;
  const columns = document.getElementById("columns").value;
  let gaps = document.getElementById("gaps").value;

  gaps = gaps / 10;  // Convert gaps from mm to cm

  const requestData = {
      width: parseInt(width),
      rows: parseInt(rows),
      columns: parseInt(columns),
      gaps: parseFloat(gaps)
  };

  fetch("/automatic-mode", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify(requestData)
  })
  .then(response => {
      if (!response.ok) {
          throw new Error("Error initiating automatic mode");
      }
      return response.json();
  })
  .then(data => {
      console.log("Automatic mode initiated:", data);
  })
  .catch(error => {
      console.error("Error:", error);
  });
});


function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
