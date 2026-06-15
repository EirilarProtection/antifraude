import express from "express";
import cors from "cors";

const app = express();
const PORT = process.env.PORT || 8080;

// middleware
app.use(cors());
app.use(express.json());

// ROTA PRINCIPAL (resolve "Cannot GET /")
app.get("/", (req, res) => {
  res.send(`
    <h1>API Antifraude rodando 🚀</h1>
    <p>Acesse: /api/logins</p>
  `);
});

// MOCK (se não tiver banco ainda)
let logins = [
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
];

// GET logins
app.get("/api/logins", (req, res) => {
  res.json(logins);
});

// POST login (exemplo)
app.post("/api/logins", (req, res) => {
  const newLogin = {
    id: logins.length + 1,
    ...req.body
  };

  logins.push(newLogin);

  res.status(201).json(newLogin);
});

// start server
app.listen(PORT, () => {
  console.log(`API rodando na porta ${PORT}`);
});
