function sendCommand(command, value = 0) {
  // Ensure the command is properly defined
  if (!command) {
    console.error("Command is missing");
    return;
  }

  // Log the command and value for debugging
  console.log("Sending command:", command, "with value:", value);

  // Send the POST request to the Flask server
  fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      command: command, // Just the command (e.g., "MOVE_FORWARD")
      value: value, // The value (e.g., distance in cm)
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Command sent successfully:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Event listeners for manual mode buttons
document.getElementById("front").addEventListener("click", function () {
  sendCommand("MOVE_FORWARD", 10);
});

document.getElementById("back").addEventListener("click", function () {
  sendCommand("MOVE_BACKWARD", 10);
});

document.getElementById("left").addEventListener("click", function () {
  sendCommand("ROTATE_LEFT", 10);
});

document.getElementById("right").addEventListener("click", function () {
  sendCommand("ROTATE_RIGHT", 10);
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

// Event listener for automatic mode
document.getElementById("automatic").addEventListener("click", function () {
  const width = document.getElementById("width").value;
  const rows = document.getElementById("rows").value;
  const columns = document.getElementById("columns").value;
  let gaps = document.getElementById("gaps").value;

  // Convert gaps from mm to cm
  gaps = gaps / 10;

  // Validate inputs
  if (!width || !rows || !columns || !gaps) {
    alert("Please fill in all values for automatic mode.");
    return;
  }

  // Prepare the command data for automatic mode
  const commandData = {
    width: parseInt(width),
    rows: parseInt(rows),
    columns: parseInt(columns),
    gaps: parseFloat(gaps), // Ensure gaps is a float in centimeters
  };

  // Log the automatic mode command data for debugging
  console.log("Starting automatic mode with:", commandData);

  // Send the automatic mode data to the server
  fetch("/automatic-mode", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(commandData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Automatic mode initiated successfully:", data);
    })
    .catch((error) => {
      console.error("Error starting automatic mode:", error);
    });
});

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
