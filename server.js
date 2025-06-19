const express = require('express');
const app = express();
const FunctionRouter = require('./routes/FunctionRouter');
const ApiRoute = require("./routes/ApiRoute");
app.use('/run', FunctionRouter);
app.use("/api",ApiRoute);
app.get("/neha",(req,res)=>{
  const path = "D:/codes/websites/hackathon/output/common_paths.json";
  res.sendFile(path);
});
app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
