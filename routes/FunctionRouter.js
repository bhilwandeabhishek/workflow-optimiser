const express = require("express");
const path = require("path");
const { exec } = require("child_process");
const fs = require("fs");

const router = express.Router();

router.get("/", (req, res) => {
  res.send("This is the run route");
});

router.get("/:functionName", (req, res) => {
  const functionName = req.params.functionName;
  const latestPath = path.join(__dirname, "..", "uploads", "latest.txt");
  let csvPath;
  try {
    csvPath = fs.readFileSync(latestPath, "utf-8");
  } catch (err) {
    return res.status(400).json({ error: "No CSV file uploaded. Please upload a CSV file first." });
  }
  const scriptPath = `"${path.join(__dirname, '../app.py')}"`;
  const csvArg = `"${csvPath}"`;
  exec(`python ${scriptPath} ${functionName} ${csvArg}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return res.status(500).json({ error: 'Failed to run Python script.' });
    }

    if (stderr) {
      console.error(`stderr: ${stderr}`);
    }

    console.log(`stdout: ${stdout}`);
    res.json({
      message: `Function "${functionName}" executed.`,
      output: stdout.trim()
    });
  });
});

module.exports = router;
