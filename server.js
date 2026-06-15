import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const PORT = process.env.PORT || 8080;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(cors());
app.use(express.json());

// 🔥 AQUI ESTÁ O FIX PRINCIPAL (templates em vez de public)
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "templates", "dashboard.html"));
});

// serve outros HTML também
app.get("/login", (req, res) => {
  res.sendFile(path.join(__dirname, "templates", "login.html"));
});

app.get("/register", (req, res) => {
  res.sendFile(path.join(__dirname, "templates", "register.html"));
});

// MOCK API
let logins = [
  {
    id: 13,
    username: "Higor",
    email: "hdse1994@gmail.com",
    ip_address: "127.0.0.1",
    city: "Brasil",
    country: "BR",
    browser: "Chrome",
    account_status: "Bloqueado"
  }
];

app.get("/api/logins", (req, res) => {
  res.json(logins);
});

app.get("/api/user/:id", (req, res) => {
  res.json(logins.find(u => u.id == req.params.id) || {});
});

app.post("/api/block_user/:id", (req, res) => {
  const u = logins.find(x => x.id == req.params.id);
  if (u) u.account_status = "Bloqueado";
  res.json({ ok: true });
});

app.post("/api/unblock_user/:id", (req, res) => {
  const u = logins.find(x => x.id == req.params.id);
  if (u) u.account_status = "Ativo";
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log("API rodando na porta", PORT);
});
