import express from "express";
import pg from "pg";
import cors from "cors";

const app = express();
const port = process.env.PORT || 8080;

// middleware
app.use(cors());
app.use(express.json());

// conexão PostgreSQL (Railway usa DATABASE_URL)
const db = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

// --------------------
// ROTA PRINCIPAL
// --------------------
app.get("/", (req, res) => {
  res.send("🚀 Antifraude API rodando com sucesso");
});

// --------------------
// LISTA LOGINS (dashboard)
// --------------------
app.get("/api/logins", async (req, res) => {
  try {
    const result = await db.query(`
      SELECT id, username, email, ip_address, country, city,
             browser, account_status
      FROM users
      ORDER BY id DESC
    `);

    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao buscar logins" });
  }
});

// --------------------
// USUÁRIO POR ID
// --------------------
app.get("/api/user/:id", async (req, res) => {
  try {
    const { id } = req.params;

    const result = await db.query(
      "SELECT * FROM users WHERE id = $1",
      [id]
    );

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao buscar usuário" });
  }
});

// --------------------
// BLOQUEAR USUÁRIO
// --------------------
app.post("/api/block_user/:id", async (req, res) => {
  try {
    const { id } = req.params;

    await db.query(`
      UPDATE users
      SET account_status = 'blocked',
          blocked = true,
          blocked_at = NOW()
      WHERE id = $1
    `, [id]);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao bloquear usuário" });
  }
});

// --------------------
// DESBLOQUEAR USUÁRIO
// --------------------
app.post("/api/unblock_user/:id", async (req, res) => {
  try {
    const { id } = req.params;

    await db.query(`
      UPDATE users
      SET account_status = 'active',
          blocked = false,
          blocked_at = NULL
      WHERE id = $1
    `, [id]);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao desbloquear usuário" });
  }
});

// --------------------
// NOTIFICAR (mock simples)
// --------------------
app.post("/api/notify_user/:id", async (req, res) => {
  try {
    const { id } = req.params;

    console.log(`📢 Notificação enviada para usuário ${id}`);

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro ao notificar usuário" });
  }
});

// --------------------
// START SERVER
// --------------------
app.listen(port, () => {
  console.log(`API rodando na porta ${port}`);
});
