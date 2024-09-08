// Helper function to send commands to the server
function sendCommand(command) {
  fetch('/command', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: command })
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById('responseOutput').innerText = data.response ? data.response : 'No response from Arduino';
  })
  .catch((error) => {
      document.getElementById('responseOutput').innerText = 'Error: ' + error.message;
  });
}

// Event listeners for the buttons
document.getElementById('front').addEventListener('click', function() {
  sendCommand('front');
});

document.getElementById('back').addEventListener('click', function() {
  sendCommand('back');
});

document.getElementById('left').addEventListener('click', function() {
  sendCommand('left');
});

document.getElementById('right').addEventListener('click', function() {
  sendCommand('right');
});

document.getElementById('stop').addEventListener('click', function() {
  sendCommand('stop');
});

document.getElementById('applyGrout').addEventListener('click', function() {
  sendCommand('play');
});

document.getElementById('emptyGrout').addEventListener('click', function() {
  sendCommand('empty');
});
