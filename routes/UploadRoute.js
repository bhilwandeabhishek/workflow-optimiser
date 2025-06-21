const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");

const router = express.Router();

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, "..", "uploads"));
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + "-" + file.originalname);
  },
});
const upload = multer({ storage: storage });

// Upload CSV endpoint
router.post("/upload_csv", upload.single("csvfile"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  }
  // Save the latest uploaded filename for analysis
  const latestPath = path.join(__dirname, "..", "uploads", "latest.txt");
  fs.writeFileSync(latestPath, req.file.path, "utf-8");
  res.json({
    message: "CSV file uploaded successfully!",
    filename: req.file.filename,
    path: req.file.path,
  });
});

module.exports = router;
