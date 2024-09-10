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
  const width = document.getElementById("width");
  const rows = document.getElementById("rows");
  const columns = document.getElementById("columns");
  const gaps = document.getElementById("gaps");
  executeCommands(width, rows, columns, gaps);
});

async function executeCommands(width, rows, columns, gaps) {
  console.log("width");
  console.log("rows");
  console.log("columns");
  console.log("gaps");

  const vertical = width * columns + gaps;
  const horizontal = width * rows + gaps;

  await sendCommand(`MOVE_FORWARD ${vertical}`);
  await sendCommand("MOVE_BACKWARD 15");
  await sendCommand("ROTATE_LEFT 194");
  await sendCommand("MOVE_FRONT 16");
  await sendCommand("ROTATE_LEFT 97");
  await sendCommand("MOVE_BACKWARD 10");

  await sleep(5000); // Wait for 1 second before the next set of commands

  await sendCommand(`MOVE_FORWARD ${horizontal}`);
  await sendCommand("MOVE_BACKWARD 10");
  await sendCommand("ROTATE_LEFT 194");
  await sendCommand("MOVE_FRONT 16");
  await sendCommand("ROTATE_LEFT 97");
  await sendCommand("MOVE_BACKWARD 10");

  await sleep(5000); // Wait for 1 second

  await sendCommand(`MOVE_FORWARD ${vertical}`);
  await sendCommand("MOVE_BACKWARD 15");
  await sendCommand("ROTATE_LEFT 194");
  await sendCommand("MOVE_FRONT 16");
  await sendCommand("ROTATE_LEFT 97");
  await sendCommand("MOVE_BACKWARD 10");

  await sleep(5000); // Wait for 1 second

  await sendCommand(`MOVE_FORWARD ${horizontal}`);
  await sendCommand("MOVE_BACKWARD 10");
  await sendCommand("ROTATE_LEFT 194");
  await sendCommand("MOVE_FRONT 16");
  await sendCommand("ROTATE_LEFT 97");
  await sendCommand("MOVE_BACKWARD 10");
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
