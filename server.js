const { spawn } = require("child_process");
const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, "public")));

app.post("/command", (req, res) => {
  const { command, params } = req.body;

  if (!command) {
    return res.status(400).json({ error: "No command received" });
  }

  // Run the Python script and pass the command and params
  const pythonProcess = spawn("python3", [
    "path/to/your_script.py",
    command,
    JSON.stringify(params),
  ]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Python response: ${data.toString()}`);
    res.json({ response: data.toString() });
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Python stderr: ${data.toString()}`);
    res.status(500).json({ error: `Python error: ${data.toString()}` });
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
