"""
database.py
------------
Persistência em SQLite (Nível 3). Substitui as listas em memória.

Esquema:
- usuarios (com coluna 'tipo' como discriminator: psicologo | secretaria | paciente)
- consultas (FKs para paciente e psicólogo)
- prontuarios (1:1 com paciente)
- sessoes (1:N com prontuario)

Regra de segurança: se o usuário logado for Secretaria, qualquer tentativa de
LER prontuários/sessões é bloqueada (PermissionError), garantindo sigilo ético.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "clinica.db"


class AcessoNegadoError(Exception):
    """Lançada quando um usuário sem permissão tenta acessar dados sigilosos."""
    pass


class ClinicaDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._criar_tabelas()

    # ------------------------------------------------------------------
    # SCHEMA
    # ------------------------------------------------------------------
    def _criar_tabelas(self):
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                telefone TEXT,
                tipo TEXT NOT NULL CHECK(tipo IN ('psicologo','secretaria','paciente')),
                crp TEXT,
                especialidade TEXT,
                num_carteira_trabalho TEXT,
                cpf TEXT,
                data_nascimento TEXT
            );

            CREATE TABLE IF NOT EXISTS prontuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER UNIQUE NOT NULL,
                FOREIGN KEY (paciente_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prontuario_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                anotacoes TEXT,
                sentimentos_observados TEXT,
                FOREIGN KEY (prontuario_id) REFERENCES prontuarios(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                psicologo_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('Individual','Casal','Online')),
                data_hora TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'agendada'
                    CHECK(status IN ('agendada','confirmada','cancelada','faltou')),
                FOREIGN KEY (paciente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (psicologo_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def autenticar(self, email, senha):
        cur = self.conn.execute(
            "SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # CRUD USUARIOS (pacientes / psicólogos / secretárias)
    # ------------------------------------------------------------------
    def cadastrar_usuario(self, nome, email, senha, telefone, tipo, **extra):
        cur = self.conn.execute(
            """INSERT INTO usuarios
               (nome, email, senha, telefone, tipo, crp, especialidade,
                num_carteira_trabalho, cpf, data_nascimento)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                nome, email, senha, telefone, tipo,
                extra.get("crp"), extra.get("especialidade"),
                extra.get("num_carteira_trabalho"),
                extra.get("cpf"), extra.get("data_nascimento"),
            ),
        )
        self.conn.commit()
        usuario_id = cur.lastrowid
        if tipo == "paciente":
            self.conn.execute(
                "INSERT INTO prontuarios (paciente_id) VALUES (?)", (usuario_id,)
            )
            self.conn.commit()
        return usuario_id

    def editar_usuario(self, usuario_id, **campos):
        if not campos:
            return
        colunas = ", ".join(f"{k} = ?" for k in campos)
        valores = list(campos.values()) + [usuario_id]
        self.conn.execute(f"UPDATE usuarios SET {colunas} WHERE id = ?", valores)
        self.conn.commit()

    def remover_usuario(self, usuario_id):
        # ON DELETE CASCADE cuida de prontuário/sessões/consultas ligadas
        self.conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        self.conn.commit()

    def listar_usuarios(self, tipo=None):
        if tipo:
            cur = self.conn.execute("SELECT * FROM usuarios WHERE tipo = ? ORDER BY nome", (tipo,))
        else:
            cur = self.conn.execute("SELECT * FROM usuarios ORDER BY nome")
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # CONSULTAS / AGENDA
    # ------------------------------------------------------------------
    def agendar_consulta(self, paciente_id, psicologo_id, tipo, data_hora):
        cur = self.conn.execute(
            """INSERT INTO consultas (paciente_id, psicologo_id, tipo, data_hora)
               VALUES (?,?,?,?)""",
            (paciente_id, psicologo_id, tipo, data_hora),
        )
        self.conn.commit()
        return cur.lastrowid

    def atualizar_status_consulta(self, consulta_id, status):
        self.conn.execute(
            "UPDATE consultas SET status = ? WHERE id = ?", (status, consulta_id)
        )
        self.conn.commit()

    def listar_agenda(self, psicologo_id=None, data=None):
        query = """
            SELECT c.*, p.nome AS paciente_nome, ps.nome AS psicologo_nome
            FROM consultas c
            JOIN usuarios p ON p.id = c.paciente_id
            JOIN usuarios ps ON ps.id = c.psicologo_id
            WHERE 1=1
        """
        params = []
        if psicologo_id:
            query += " AND c.psicologo_id = ?"
            params.append(psicologo_id)
        if data:
            query += " AND date(c.data_hora) = date(?)"
            params.append(data)
        query += " ORDER BY c.data_hora"
        cur = self.conn.execute(query, params)
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # PRONTUÁRIOS / SESSÕES  -> protegidos por controle de acesso
    # ------------------------------------------------------------------
    def _checar_acesso_prontuario(self, usuario_logado: dict, paciente_id: int):
        """Bloqueia Secretaria; permite Psicologo (qualquer, aqui simplificado
        como 'psicólogo autorizado da clínica') e o próprio Paciente."""
        if usuario_logado["tipo"] == "secretaria":
            raise AcessoNegadoError(
                "Acesso negado: secretárias não podem visualizar prontuários "
                "ou sessões (sigilo ético do paciente)."
            )

    def obter_prontuario(self, paciente_id, usuario_logado):
        self._checar_acesso_prontuario(usuario_logado, paciente_id)
        cur = self.conn.execute(
            "SELECT * FROM prontuarios WHERE paciente_id = ?", (paciente_id,)
        )
        prontuario = cur.fetchone()
        if not prontuario:
            return None
        cur2 = self.conn.execute(
            "SELECT * FROM sessoes WHERE prontuario_id = ? ORDER BY data",
            (prontuario["id"],),
        )
        return {
            "prontuario_id": prontuario["id"],
            "paciente_id": paciente_id,
            "sessoes": [dict(r) for r in cur2.fetchall()],
        }

    def registrar_sessao(self, paciente_id, data, anotacoes, sentimentos, usuario_logado):
        self._checar_acesso_prontuario(usuario_logado, paciente_id)
        cur = self.conn.execute(
            "SELECT id FROM prontuarios WHERE paciente_id = ?", (paciente_id,)
        )
        row = cur.fetchone()
        if not row:
            raise ValueError("Paciente não possui prontuário (inesperado).")
        prontuario_id = row["id"]
        self.conn.execute(
            """INSERT INTO sessoes (prontuario_id, data, anotacoes, sentimentos_observados)
               VALUES (?,?,?,?)""",
            (prontuario_id, data, anotacoes, sentimentos),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
