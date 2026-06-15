import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const PORT = process.env.PORT || 8080;

// necessário por causa do "type: module"
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// middleware
app.use(cors());
app.use(express.json());

// 🔥 SERVIR FRONTEND (dashboard.html)
app.use(express.static(path.join(__dirname, "public")));

// rota principal abre o dashboard
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "dashboard.html"));
});

// MOCK DB
let logins = [
  {
    id: 13,
    user_id: 13,
    username: "Higor",
    email: "hdse1994@gmail.com",
    ip_address: "127.0.0.1",
    city: "Brasil",
    country: "BR",
    browser: "Chrome",
    account_status: "Bloqueado"
  }
];

// API LOGINS
app.get("/api/logins", (req, res) => {
  res.json(logins);
});

// API USER DETAILS (pra modal funcionar)
app.get("/api/user/:id", (req, res) => {
  const user = logins.find(u => u.id == req.params.id);
  res.json(user || {});
});

// BLOCK
app.post("/api/block_user/:id", (req, res) => {
  const u = logins.find(x => x.id == req.params.id);
  if (u) u.account_status = "Bloqueado";
  res.json({ ok: true });
});

// UNBLOCK
app.post("/api/unblock_user/:id", (req, res) => {
  const u = logins.find(x => x.id == req.params.id);
  if (u) u.account_status = "Ativo";
  res.json({ ok: true });
});

// NOTIFY
app.post("/api/notify_user/:id", (req, res) => {
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log("API rodando na porta", PORT);
});
