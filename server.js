const { SerialPort } = require("serialport");
const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

const serialPortPath = "/dev/ttyACM0"; // Set to the correct port on Raspberry Pi
const port = new SerialPort({
  path: serialPortPath,
  baudRate: 9600,
  autoOpen: false,
});

port.open((err) => {
  if (err) {
    return console.log("Error opening port: ", err.message);
  }
  console.log(`Serial port ${serialPortPath} opened`);
});

app.post("/command", (req, res) => {
  const { command } = req.body;
  if (!command) {
    return res.status(400).json({ error: "No command received" });
  }

  setTimeout(() => {
    port.write(`${command}\n`, (err) => {
      if (err) {
        return res.status(500).json({ error: "Failed to write to serial port" });
      }
      console.log(`Command sent to serial port: ${command}`);
    });
  }, 2000);

  res.json({ response: `Command ${command} sent` });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
