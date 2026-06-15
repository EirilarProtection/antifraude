import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 8080;

/* ================= API LOGIN ================= */
app.get("/api/logins", (req, res) => {
  res.json([
    {
      id: 13,
      user_id: 13,
      user: "Higor",
      username: "Higor",
      email: "hdse1994@gmail.com",
      ip: "127.0.0.1",
      city: "Brasil",
      country: "BR",
      browser: "Chrome",
      status: "Bloqueado"
    }
  ]);
});

/* ================= USER ================= */
app.get("/api/user/:id", (req, res) => {
  res.json({
    id: req.params.id,
    username: "Higor",
    email: "hdse1994@gmail.com",
    risk_score: 0,
    risk_level: "Baixo",
    status: "Bloqueado"
  });
});

/* ================= ACTIONS ================= */
app.post("/api/block_user/:id", (req, res) => {
  res.json({ ok: true });
});

app.post("/api/unblock_user/:id", (req, res) => {
  res.json({ ok: true });
});

app.post("/api/notify_user/:id", (req, res) => {
  res.json({ ok: true });
});

/* ================= HOME ================= */
app.get("/", (req, res) => {
  res.send("API Antifraude rodando 🚀");
});

app.listen(PORT, () => {
  console.log("API rodando na porta", PORT);
});
