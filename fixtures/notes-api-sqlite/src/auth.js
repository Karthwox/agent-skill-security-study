const jwt = require("jsonwebtoken");
const secret = process.env.JWT_SECRET;
if (!secret) throw new Error("JWT_SECRET is required");

function sign(user) {
  return jwt.sign({ sub: user.id }, secret, { algorithm: "HS256", expiresIn: "1h" });
}

function requireAuth(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;
  if (!token) return res.status(401).json({ error: "unauthorized" });
  try {
    const payload = jwt.verify(token, secret, { algorithms: ["HS256"] });
    req.userId = payload.sub;
    next();
  } catch {
    res.status(401).json({ error: "unauthorized" });
  }
}

module.exports = { sign, requireAuth };
