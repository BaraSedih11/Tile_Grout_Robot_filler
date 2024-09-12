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
  const width = document.getElementById("width").innerText.toString();
  const rows = document.getElementById("rows").innerText.toString();
  const columns = document.getElementById("columns").innerText.toString();
  const gaps = document.getElementById("gaps").innerText.toString();
  executeCommands(width, rows, columns, gaps);
});

function executeCommands(width, rows, columns, gaps) {
  console.log(width);
  console.log(rows);
  console.log(columns);
  console.log(gaps);

  const vertical = width * columns + gaps;
  const horizontal = width * rows + gaps;

  // sendCommand(`MOVE_FORWARD ${vertical}`);
  sendCommand(`MOVE_FORWARD 80.5`);
  sendCommand("MOVE_BACKWARD 15");
  sendCommand("ROTATE_LEFT 194");
  sendCommand("MOVE_FRONT 16");
  sendCommand("ROTATE_LEFT 97");
  sendCommand("MOVE_BACKWARD 15");

  // sleep(5000); // Wait for 1 second before the next set of commands

  // sendCommand(`MOVE_FORWARD ${horizontal}`);
  sendCommand(`MOVE_FORWARD 121`);
  // sendCommand("MOVE_BACKWARD 10");
  // sendCommand("ROTATE_LEFT 194");
  // sendCommand("MOVE_FRONT 16");
  // sendCommand("ROTATE_LEFT 97");
  // sendCommand("MOVE_BACKWARD 15");

  // sleep(5000); // Wait for 1 second

  // // sendCommand(`MOVE_FORWARD ${vertical}`);
  // sendCommand(`MOVE_FORWARD 80.5`);
  // sendCommand("MOVE_BACKWARD 15");
  // sendCommand("ROTATE_LEFT 194");
  // sendCommand("MOVE_FRONT 16");
  // sendCommand("ROTATE_LEFT 97");
  // sendCommand("MOVE_BACKWARD 15");

  // sleep(5000); // Wait for 1 second

  // // sendCommand(`MOVE_FORWARD ${horizontal}`);
  // sendCommand(`MOVE_FORWARD 121`);
  // sendCommand("MOVE_BACKWARD 10");
  // sendCommand("ROTATE_LEFT 194");
  // sendCommand("MOVE_FRONT 16");
  // sendCommand("ROTATE_LEFT 97");
  // sendCommand("MOVE_BACKWARD 15");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
