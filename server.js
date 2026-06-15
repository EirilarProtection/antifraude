import express from "express";
import pg from "pg";

const app = express();
app.use(express.json());

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// LISTAR USUÁRIOS
app.get("/api/logins", async (req, res) => {
  const r = await pool.query("SELECT * FROM users ORDER BY id DESC");
  res.json(r.rows);
});

// DETALHES
app.get("/api/user/:id", async (req, res) => {
  const r = await pool.query("SELECT * FROM users WHERE id=$1", [req.params.id]);
  res.json(r.rows[0]);
});

// BLOQUEAR
app.post("/api/block_user/:id", async (req, res) => {
  await pool.query(`
    UPDATE users
    SET account_status='blocked',
        blocked=true,
        blocked_at=NOW()
    WHERE id=$1
  `, [req.params.id]);

  res.json({ ok: true });
});

// DESBLOQUEAR
app.post("/api/unblock_user/:id", async (req, res) => {
  await pool.query(`
    UPDATE users
    SET account_status='active',
        blocked=false,
        blocked_at=NULL
    WHERE id=$1
  `, [req.params.id]);

  res.json({ ok: true });
});

// PORTA DO RAILWAY
const PORT = process.env.PORT || 8080;

app.listen(PORT, () => {
  console.log("API rodando na porta", PORT);
});
