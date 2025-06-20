const express = require('express');
const app = express();
const FunctionRouter = require('./routes/FunctionRouter');
const ApiRoute = require("./routes/ApiRoute");
app.use('/run', FunctionRouter);
app.use("/api",ApiRoute);
app.get("/",(req,res)=>{
  res.send("server is live")
});
app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
