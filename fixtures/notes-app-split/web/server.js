const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const types = { ".html": "text/html", ".js": "text/javascript" };
http.createServer((req, res) => {
  const name = req.url === "/" ? "index.html" : path.basename(req.url.split("?")[0]);
  const file = path.join(__dirname, name);
  if (!fs.existsSync(file)) { res.writeHead(404).end("Not found"); return; }
  res.writeHead(200, { "Content-Type": types[path.extname(file)] || "text/plain" });
  fs.createReadStream(file).pipe(res);
}).listen(process.env.PORT || 3000, () => console.log("Web on http://localhost:3000"));
