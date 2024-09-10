// Helper function to send commands to the server
function sendCommand(command) {
  return fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command: command }),
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("responseOutput").innerText = data.response ? data.response : "No response from Arduino";
    return data.response; // Return response for further processing
  })
  .catch(error => {
    document.getElementById("responseOutput").innerText = "Error: " + error.message;
    throw error;
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
  const width = parseFloat(document.getElementById("width").value);
  const rows = parseInt(document.getElementById("rows").value, 10);
  const columns = parseInt(document.getElementById("columns").value, 10);
  const gaps = parseFloat(document.getElementById("gaps").value);

  startAutomaticMode(width, rows, columns, gaps);
});

async function startAutomaticMode(width, rows, columns, gaps) {
  const vertical = width * columns + gaps;
  const horizontal = width * rows + gaps;

  await followGap(vertical, horizontal);
}

async function followGap(vertical, horizontal) {
  // Adjust the following commands based on real-time feedback
  let detectedGap = false;

  while (!detectedGap) {
    await sendCommand(`MOVE_FORWARD ${vertical}`);
    detectedGap = await checkForGap();
    if (!detectedGap) {
      await sendCommand("ROTATE_RIGHT 10"); // Adjust angle as needed
    }
  }

  // Continue with the remaining commands
  await sendCommand("MOVE_BACKWARD 15");
  await sendCommand("ROTATE_LEFT 194");
  await sendCommand("MOVE_FRONT 16");
  await sendCommand("ROTATE_LEFT 97");
  await sendCommand("MOVE_BACKWARD 10");

  // Repeat as necessary
}

async function checkForGap() {
  return fetch("/check-gap")
    .then(response => response.json())
    .then(data => data.gapDetected)
    .catch(error => {
      console.error("Error checking for gap:", error);
      return false;
    });
}
