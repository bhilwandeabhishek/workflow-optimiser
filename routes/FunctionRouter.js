const express = require("express");
const path = require("path");
const { exec } = require("child_process");

const router = express.Router();

router.get("/", (req, res) => {
  res.send("This is the run route");
});

router.get("/:functionName", (req, res) => {
  const functionName = req.params.functionName;
  const scriptPath = `"${path.join(__dirname, '../app.py')}"`; 

  exec(`python ${scriptPath} ${functionName}`, (error, stdout, stderr) => {
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
