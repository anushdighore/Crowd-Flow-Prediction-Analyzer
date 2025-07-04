const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.get("/", (req, res) => {
  res.json({
    message: "Hello from the backend!",
    timestamp: new Date().toISOString(),
    user: "Dark",
  });
});

app.listen(3001, () => {
  console.log("Server running on http://localhost:3001");
});
