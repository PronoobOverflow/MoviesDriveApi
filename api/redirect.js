import crypto from "crypto";

const SECRET_KEY = "supersecretkey"; // Must match Python

export default function handler(req, res) {
  const { file, expires, token, hash } = req.query;


  if (!file || !expires || !token || !hash) {
    return res.status(400).json({ error: "Missing required parameters" });
  }

  const now = Math.floor(Date.now() / 1000);
  if (parseInt(expires) < now) {
    return res.status(403).json({ error: "This link has expired" });
  }

  const data = `${file}|${expires}|${hash}`;
  const expectedToken = crypto
    .createHash("sha256")
    .update(data + SECRET_KEY)
    .digest("hex");

  if (expectedToken !== token) {
    return res.status(403).json({ error: "Invalid token" });
  }

  return res.redirect(file);
}