const SerialPort = require("serialport").SerialPort;
const ReadlineParser = require("@serialport/parser-readline").ReadlineParser;
const express = require("express");
const cors = require("cors");
const path = require("path");

// Create an instance of Express
const app = express();

// Use CORS middleware to allow cross-origin requests
app.use(cors());

// To parse JSON body in POST requests
app.use(express.json());

// Serve static files (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, "public")));

// Adjust the serial port to match your Arduino
const serialPortPath = "COM3"; // Ensure this is the correct port for your Arduino
const port = new SerialPort({
  path: serialPortPath,
  baudRate: 9600,
  autoOpen: false,
});
const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));

// Open the serial port connection
port.open((err) => {
  if (err) {
    return console.log("Error opening port: ", err.message);
  }
  console.log(`Serial port ${serialPortPath} opened`);

  // Add a small delay after opening the port to ensure the Arduino is ready
  setTimeout(() => {
    console.log("Arduino should now be ready to receive commands");
  }, 2000); // 2-second delay
});

// Route to serve the index.html file (your front-end)
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Route to send commands to Arduino
app.post("/command", (req, res) => {
  const { command } = req.body;

  if (!command) {
    return res.status(400).json({ error: "No command received" });
  }

  // Write the command to the Arduino after a short delay (to avoid command flooding)
  setTimeout(() => {
    port.write(`${command}\n`, (err) => {
      if (err) {
        return res.status(500).json({ error: "Failed to write to Arduino" });
      }
      console.log(`Command sent to Arduino: ${command}`);
    });
  }, 2000);

  // Listen for the Arduino's response
  parser.once("data", (response) => {
    res.json({ response: response.trim() });
  });
});

// Route to handle automatic mode
app.post("/automatic-mode", (req, res) => {
  const { width, rows, columns, gaps } = req.body;

  if (!width || !rows || !columns || !gaps) {
    return res
      .status(400)
      .json({ error: "Missing parameters for automatic mode" });
  }

  // Pass the data to the Raspberry Pi (assumed to run the Python script with the input values)
  const spawn = require("child_process").spawn;
  const pythonProcess = spawn("python3", [
    "raspberry/main.py",
    "AUTOMATIC",
    JSON.stringify({ width, rows, columns, gaps }),
  ]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Output from Python: ${data}`);
    res.json({
      message: "Automatic mode started successfully",
      output: data.toString(),
    });
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Error from Python: ${data}`);
    res.status(500).json({ error: "Failed to start automatic mode" });
  });
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
