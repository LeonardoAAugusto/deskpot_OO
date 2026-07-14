"""
gui.py
------
Interface gráfica em Tkinter (Nível 4), com toda a lógica de menu (Nível 2)
por trás das telas. Usa o banco SQLite (database.py) e as classes de
modelagem (models.py).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from database import ClinicaDB, AcessoNegadoError
from models import CONSULTA_CLASSES, GeradorRecibo

BG = "#f4f6f8"
SIDEBAR_BG = "#22313f"
SIDEBAR_FG = "#ecf0f1"
ACCENT = "#2e86de"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

STATUS_COLORS = {
    "confirmada": "#27ae60",  # verde
    "agendada": "#f1c40f",    # amarelo
    "cancelada": "#e74c3c",   # vermelho
    "faltou": "#e74c3c",      # vermelho
}


# =============================================================================
# APP PRINCIPAL
# =============================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clínica de Psicologia - Sistema de Gestão")
        self.geometry("1000x650")
        self.configure(bg=BG)
        self.minsize(900, 600)

        self.db = ClinicaDB()
        self.usuario_logado = None

        self._seed_demo_data()

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    # ------------------------------------------------------------------
    def _seed_demo_data(self):
        """Cria alguns registros de exemplo se o banco estiver vazio,
        só para facilitar a primeira execução/demonstração."""
        if self.db.listar_usuarios():
            return
        self.db.cadastrar_usuario(
            "Dra. Ana Souza", "ana@clinica.com", "123", "11999990000",
            "psicologo", crp="06/123456", especialidade="TCC",
        )
        self.db.cadastrar_usuario(
            "Carla Secretária", "carla@clinica.com", "123", "11988880000",
            "secretaria", num_carteira_trabalho="CT-001",
        )
        self.db.cadastrar_usuario(
            "João Paciente", "joao@paciente.com", "123", "11977770000",
            "paciente", cpf="123.456.789-00", data_nascimento="1995-04-12",
        )

    # ------------------------------------------------------------------
    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.usuario_logado = None
        self._clear_container()
        LoginScreen(self.container, self)

    def show_dashboard(self):
        self._clear_container()
        tipo = self.usuario_logado["tipo"]
        if tipo == "secretaria":
            SecretariaDashboard(self.container, self)
        elif tipo == "psicologo":
            PsicologoDashboard(self.container, self)
        else:
            messagebox.showinfo("Aviso", "Login de paciente ainda não implementado na GUI.")
            self.show_login()

    def logout(self):
        self.show_login()


# =============================================================================
# TELA DE LOGIN
# =============================================================================
class LoginScreen(tk.Frame):
    def __init__(self, master, app: App):
        super().__init__(master, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)

        card = tk.Frame(self, bg="white", bd=0, highlightbackground="#dcdde1",
                         highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380, height=340)

        tk.Label(card, text="Clínica de Psicologia", font=FONT_TITLE,
                  bg="white", fg=SIDEBAR_BG).pack(pady=(30, 5))
        tk.Label(card, text="Acesse sua conta", font=FONT_NORMAL,
                  bg="white", fg="#7f8c8d").pack(pady=(0, 20))

        tk.Label(card, text="E-mail", font=FONT_NORMAL, bg="white").pack(anchor="w", padx=40)
        self.email_var = tk.StringVar()
        tk.Entry(card, textvariable=self.email_var, font=FONT_NORMAL,
                  width=30).pack(padx=40, pady=(2, 12))

        tk.Label(card, text="Senha", font=FONT_NORMAL, bg="white").pack(anchor="w", padx=40)
        self.senha_var = tk.StringVar()
        tk.Entry(card, textvariable=self.senha_var, show="•", font=FONT_NORMAL,
                  width=30).pack(padx=40, pady=(2, 20))

        tk.Button(card, text="Entrar", font=FONT_BOLD, bg=ACCENT, fg="white",
                   activebackground="#1b6fc9", relief="flat", width=25, pady=6,
                   command=self.autenticar).pack()

        tk.Label(card, text="Demo: ana@clinica.com / carla@clinica.com  (senha: 123)",
                  font=("Segoe UI", 8), bg="white", fg="#95a5a6").pack(pady=(18, 0))

        self.bind_all("<Return>", lambda e: self.autenticar())

    def autenticar(self):
        email = self.email_var.get().strip()
        senha = self.senha_var.get().strip()
        usuario = self.app.db.autenticar(email, senha)
        if not usuario:
            messagebox.showerror("Erro de login", "E-mail ou senha inválidos.")
            return
        self.app.usuario_logado = usuario
        self.app.show_dashboard()


# =============================================================================
# BASE PARA DASHBOARDS (sidebar + área de conteúdo)
# =============================================================================
class BaseDashboard(tk.Frame):
    def __init__(self, master, app: App, menu_items):
        super().__init__(master, bg=BG)
        self.app = app
        self.pack(fill="both", expand=True)

        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text=self.app.usuario_logado["nome"], font=FONT_BOLD,
                  bg=SIDEBAR_BG, fg=SIDEBAR_FG, wraplength=190,
                  justify="left").pack(pady=(25, 2), padx=15, anchor="w")
        tk.Label(sidebar, text=self.app.usuario_logado["tipo"].capitalize(),
                  font=("Segoe UI", 9), bg=SIDEBAR_BG, fg="#95a5a6").pack(
            padx=15, anchor="w", pady=(0, 20))

        for label, cmd in menu_items:
            b = tk.Button(sidebar, text=label, font=FONT_NORMAL, bg=SIDEBAR_BG,
                           fg=SIDEBAR_FG, activebackground="#34495e",
                           activeforeground="white", relief="flat", anchor="w",
                           padx=15, pady=10, command=cmd)
            b.pack(fill="x")

        tk.Frame(sidebar, bg=SIDEBAR_BG).pack(fill="both", expand=True)  # spacer
        tk.Button(sidebar, text="Sair", font=FONT_NORMAL, bg="#c0392b", fg="white",
                   relief="flat", pady=8, command=self.app.logout).pack(fill="x", side="bottom")

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()


# =============================================================================
# DASHBOARD DA SECRETÁRIA
# =============================================================================
class SecretariaDashboard(BaseDashboard):
    def __init__(self, master, app: App):
        menu = [
            ("Pacientes", self.tela_pacientes),
            ("Psicólogos", self.tela_psicologos),
            ("Agendar Consulta", self.tela_agendar),
            ("Agenda Completa", self.tela_agenda),
        ]
        super().__init__(master, app, menu)
        self.tela_pacientes()

    # ---------------- Pacientes ----------------
    def tela_pacientes(self):
        self.clear_content()
        tk.Label(self.content, text="Pacientes", font=FONT_TITLE, bg=BG).pack(anchor="w")

        cols = ("id", "nome", "email", "cpf", "telefone")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=140)
        tree.pack(fill="both", expand=True, pady=10)

        for p in self.app.db.listar_usuarios("paciente"):
            tree.insert("", "end", iid=p["id"], values=(
                p["id"], p["nome"], p["email"], p["cpf"], p["telefone"]))

        btns = tk.Frame(self.content, bg=BG)
        btns.pack(fill="x")
        tk.Button(btns, text="Novo Paciente", command=lambda: self._form_paciente()).pack(side="left", padx=5)
        tk.Button(btns, text="Editar Selecionado",
                   command=lambda: self._form_paciente(self._selected_id(tree))).pack(side="left", padx=5)
        tk.Button(btns, text="Remover Selecionado",
                   command=lambda: self._remover(tree)).pack(side="left", padx=5)

    def _selected_id(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item na lista primeiro.")
            return None
        return int(sel[0])

    def _remover(self, tree):
        uid = self._selected_id(tree)
        if uid is None:
            return
        if messagebox.askyesno("Confirmar", "Remover este registro? Esta ação também apaga o prontuário associado, se houver."):
            self.app.db.remover_usuario(uid)
            self.tela_pacientes()

    def _form_paciente(self, paciente_id=None):
        FormPacienteDialog(self.app, paciente_id, on_saved=self.tela_pacientes)

    # ---------------- Psicólogos ----------------
    def tela_psicologos(self):
        self.clear_content()
        tk.Label(self.content, text="Psicólogos", font=FONT_TITLE, bg=BG).pack(anchor="w")

        cols = ("id", "nome", "email", "crp", "especialidade")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=150)
        tree.pack(fill="both", expand=True, pady=10)

        for p in self.app.db.listar_usuarios("psicologo"):
            tree.insert("", "end", iid=p["id"], values=(
                p["id"], p["nome"], p["email"], p["crp"], p["especialidade"]))

        btns = tk.Frame(self.content, bg=BG)
        btns.pack(fill="x")
        tk.Button(btns, text="Novo Psicólogo", command=lambda: self._form_psicologo()).pack(side="left", padx=5)
        tk.Button(btns, text="Editar Selecionado",
                   command=lambda: self._form_psicologo(self._selected_id(tree))).pack(side="left", padx=5)
        tk.Button(btns, text="Remover Selecionado",
                   command=lambda: self._remover_psi(tree)).pack(side="left", padx=5)

    def _remover_psi(self, tree):
        uid = self._selected_id(tree)
        if uid is None:
            return
        if messagebox.askyesno("Confirmar", "Remover este psicólogo?"):
            self.app.db.remover_usuario(uid)
            self.tela_psicologos()

    def _form_psicologo(self, psicologo_id=None):
        FormPsicologoDialog(self.app, psicologo_id, on_saved=self.tela_psicologos)

    # ---------------- Agendar ----------------
    def tela_agendar(self):
        self.clear_content()
        tk.Label(self.content, text="Agendar Nova Consulta", font=FONT_TITLE, bg=BG).pack(anchor="w", pady=(0, 15))
        AgendarConsultaForm(self.content, self.app, on_saved=self.tela_agenda)

    # ---------------- Agenda ----------------
    def tela_agenda(self):
        self.clear_content()
        tk.Label(self.content, text="Agenda Completa", font=FONT_TITLE, bg=BG).pack(anchor="w")
        render_agenda(self.content, self.app)


# =============================================================================
# DASHBOARD DO PSICÓLOGO
# =============================================================================
class PsicologoDashboard(BaseDashboard):
    def __init__(self, master, app: App):
        menu = [
            ("Consultas de Hoje", self.tela_consultas_hoje),
            ("Prontuários", self.tela_prontuarios),
        ]
        super().__init__(master, app, menu)
        self.tela_consultas_hoje()

    def tela_consultas_hoje(self):
        self.clear_content()
        tk.Label(self.content, text="Suas Consultas de Hoje", font=FONT_TITLE, bg=BG).pack(anchor="w")
        hoje = date.today().isoformat()
        render_agenda(self.content, self.app,
                       psicologo_id=self.app.usuario_logado["id"], data=hoje)

    def tela_prontuarios(self):
        self.clear_content()
        tk.Label(self.content, text="Prontuários de Pacientes", font=FONT_TITLE, bg=BG).pack(anchor="w")

        cols = ("id", "nome", "cpf")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c.capitalize())
        tree.pack(fill="both", expand=True, pady=10)

        for p in self.app.db.listar_usuarios("paciente"):
            tree.insert("", "end", iid=p["id"], values=(p["id"], p["nome"], p["cpf"]))

        def abrir():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um paciente.")
                return
            ProntuarioDialog(self.app, int(sel[0]))

        tk.Button(self.content, text="Abrir Prontuário", command=abrir).pack(anchor="w")


# =============================================================================
# COMPONENTE REUTILIZÁVEL: Agenda com indicador colorido de status
# =============================================================================
def render_agenda(parent, app: App, psicologo_id=None, data=None):
    consultas = app.db.listar_agenda(psicologo_id=psicologo_id, data=data)

    canvas_frame = tk.Frame(parent, bg=BG)
    canvas_frame.pack(fill="both", expand=True)

    header = tk.Frame(canvas_frame, bg=BG)
    header.pack(fill="x")
    for txt, w in [("Status", 8), ("Data/Hora", 18), ("Paciente", 20),
                    ("Psicólogo", 20), ("Tipo", 12), ("Valor", 10)]:
        tk.Label(header, text=txt, font=FONT_BOLD, bg=BG, width=w, anchor="w").pack(side="left")

    if not consultas:
        tk.Label(canvas_frame, text="Nenhuma consulta encontrada.", font=FONT_NORMAL,
                  bg=BG, fg="#7f8c8d").pack(pady=20)
        return

    for c in consultas:
        row = tk.Frame(canvas_frame, bg="white", pady=4)
        row.pack(fill="x", pady=2)

        dot = tk.Canvas(row, width=16, height=16, bg="white", highlightthickness=0)
        dot.create_oval(2, 2, 14, 14, fill=STATUS_COLORS.get(c["status"], "#bdc3c7"), outline="")
        dot.pack(side="left", padx=(8, 20))

        cls = CONSULTA_CLASSES[c["tipo"]]
        valor = cls.VALOR_BASE
        if c["tipo"] == "Casal":
            valor *= 1.30
        elif c["tipo"] == "Online":
            valor *= 0.90

        for txt, w in [(c["data_hora"], 18), (c["paciente_nome"], 20),
                        (c["psicologo_nome"], 20), (c["tipo"], 12),
                        (f"R$ {valor:.2f}", 10)]:
            tk.Label(row, text=txt, font=FONT_NORMAL, bg="white", width=w, anchor="w").pack(side="left")

        def make_menu(consulta_id=c["id"]):
            menu = tk.Menu(row, tearoff=0)
            for status in ["agendada", "confirmada", "cancelada", "faltou"]:
                menu.add_command(label=f"Marcar como {status}",
                                   command=lambda s=status, cid=consulta_id: _atualizar(app, cid, s, parent, psicologo_id, data))
            return menu

        row.bind("<Button-3>", lambda e, m=make_menu(): m.tk_popup(e.x_root, e.y_root))

    tk.Label(canvas_frame, text="Dica: clique com o botão direito em uma consulta para alterar o status.",
              font=("Segoe UI", 8), bg=BG, fg="#95a5a6").pack(anchor="w", pady=(10, 0))


def _atualizar(app, consulta_id, status, parent, psicologo_id, data):
    app.db.atualizar_status_consulta(consulta_id, status)
    for w in parent.winfo_children():
        w.destroy()
    render_agenda(parent, app, psicologo_id=psicologo_id, data=data)


# =============================================================================
# FORMULÁRIO: Agendar Consulta (combobox paciente/psicólogo/tipo)
# =============================================================================
class AgendarConsultaForm(tk.Frame):
    def __init__(self, master, app: App, on_saved):
        super().__init__(master, bg=BG)
        self.pack(fill="x")
        self.app = app
        self.on_saved = on_saved

        pacientes = app.db.listar_usuarios("paciente")
        psicologos = app.db.listar_usuarios("psicologo")
        self._pac_map = {f'{p["nome"]} (#{p["id"]})': p["id"] for p in pacientes}
        self._psi_map = {f'{p["nome"]} (#{p["id"]})': p["id"] for p in psicologos}

        tk.Label(self, text="Paciente", bg=BG, font=FONT_NORMAL).grid(row=0, column=0, sticky="w", pady=4)
        self.paciente_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.paciente_var, values=list(self._pac_map),
                      state="readonly", width=35).grid(row=0, column=1, pady=4, padx=10)

        tk.Label(self, text="Psicólogo", bg=BG, font=FONT_NORMAL).grid(row=1, column=0, sticky="w", pady=4)
        self.psi_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.psi_var, values=list(self._psi_map),
                      state="readonly", width=35).grid(row=1, column=1, pady=4, padx=10)

        tk.Label(self, text="Tipo de Consulta", bg=BG, font=FONT_NORMAL).grid(row=2, column=0, sticky="w", pady=4)
        self.tipo_var = tk.StringVar(value="Individual")
        ttk.Combobox(self, textvariable=self.tipo_var, values=list(CONSULTA_CLASSES),
                      state="readonly", width=35).grid(row=2, column=1, pady=4, padx=10)

        tk.Label(self, text="Data/Hora (AAAA-MM-DD HH:MM)", bg=BG, font=FONT_NORMAL).grid(row=3, column=0, sticky="w", pady=4)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        tk.Entry(self, textvariable=self.data_var, width=37).grid(row=3, column=1, pady=4, padx=10)

        tk.Button(self, text="Agendar", bg=ACCENT, fg="white", relief="flat",
                   padx=15, pady=6, command=self.salvar).grid(row=4, column=1, sticky="w", pady=15)

    def salvar(self):
        if not (self.paciente_var.get() and self.psi_var.get() and self.data_var.get()):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        paciente_id = self._pac_map[self.paciente_var.get()]
        psicologo_id = self._psi_map[self.psi_var.get()]
        tipo = self.tipo_var.get()
        self.app.db.agendar_consulta(paciente_id, psicologo_id, tipo, self.data_var.get())
        messagebox.showinfo("Sucesso", "Consulta agendada com sucesso!")
        self.on_saved()


# =============================================================================
# DIALOG: Cadastro/edição de Paciente
# =============================================================================
class FormPacienteDialog(tk.Toplevel):
    def __init__(self, app: App, paciente_id, on_saved):
        super().__init__()
        self.app = app
        self.paciente_id = paciente_id
        self.on_saved = on_saved
        self.title("Paciente")
        self.geometry("360x360")
        self.configure(bg="white")
        self.grab_set()

        dados = {}
        if paciente_id:
            dados = next((u for u in app.db.listar_usuarios("paciente") if u["id"] == paciente_id), {})

        self.vars = {}
        campos = [("nome", "Nome"), ("email", "E-mail"), ("senha", "Senha"),
                   ("telefone", "Telefone"), ("cpf", "CPF"), ("data_nascimento", "Data Nasc. (AAAA-MM-DD)")]
        for i, (key, label) in enumerate(campos):
            tk.Label(self, text=label, bg="white", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10 if i == 0 else 4, 0))
            v = tk.StringVar(value=dados.get(key, ""))
            tk.Entry(self, textvariable=v, width=35).pack(padx=20)
            self.vars[key] = v

        tk.Button(self, text="Salvar", bg=ACCENT, fg="white", relief="flat",
                   padx=15, pady=6, command=self.salvar).pack(pady=20)

    def salvar(self):
        dados = {k: v.get() for k, v in self.vars.items()}
        if not dados["nome"] or not dados["email"]:
            messagebox.showwarning("Aviso", "Nome e e-mail são obrigatórios.")
            return
        if self.paciente_id:
            self.app.db.editar_usuario(self.paciente_id, **dados)
        else:
            self.app.db.cadastrar_usuario(
                dados["nome"], dados["email"], dados["senha"] or "123",
                dados["telefone"], "paciente", cpf=dados["cpf"],
                data_nascimento=dados["data_nascimento"],
            )
        self.destroy()
        self.on_saved()


# =============================================================================
# DIALOG: Cadastro/edição de Psicólogo
# =============================================================================
class FormPsicologoDialog(tk.Toplevel):
    def __init__(self, app: App, psicologo_id, on_saved):
        super().__init__()
        self.app = app
        self.psicologo_id = psicologo_id
        self.on_saved = on_saved
        self.title("Psicólogo")
        self.geometry("360x340")
        self.configure(bg="white")
        self.grab_set()

        dados = {}
        if psicologo_id:
            dados = next((u for u in app.db.listar_usuarios("psicologo") if u["id"] == psicologo_id), {})

        self.vars = {}
        campos = [("nome", "Nome"), ("email", "E-mail"), ("senha", "Senha"),
                   ("telefone", "Telefone"), ("crp", "CRP"), ("especialidade", "Especialidade")]
        for i, (key, label) in enumerate(campos):
            tk.Label(self, text=label, bg="white", font=FONT_NORMAL).pack(anchor="w", padx=20, pady=(10 if i == 0 else 4, 0))
            v = tk.StringVar(value=dados.get(key, ""))
            tk.Entry(self, textvariable=v, width=35).pack(padx=20)
            self.vars[key] = v

        tk.Button(self, text="Salvar", bg=ACCENT, fg="white", relief="flat",
                   padx=15, pady=6, command=self.salvar).pack(pady=20)

    def salvar(self):
        dados = {k: v.get() for k, v in self.vars.items()}
        if not dados["nome"] or not dados["email"]:
            messagebox.showwarning("Aviso", "Nome e e-mail são obrigatórios.")
            return
        if self.psicologo_id:
            self.app.db.editar_usuario(self.psicologo_id, **dados)
        else:
            self.app.db.cadastrar_usuario(
                dados["nome"], dados["email"], dados["senha"] or "123",
                dados["telefone"], "psicologo", crp=dados["crp"],
                especialidade=dados["especialidade"],
            )
        self.destroy()
        self.on_saved()


# =============================================================================
# DIALOG: Prontuário (histórico + adicionar nova sessão via textarea)
# =============================================================================
class ProntuarioDialog(tk.Toplevel):
    def __init__(self, app: App, paciente_id):
        super().__init__()
        self.app = app
        self.paciente_id = paciente_id
        self.title("Prontuário do Paciente")
        self.geometry("520x520")
        self.configure(bg="white")
        self.grab_set()

        try:
            self.prontuario = app.db.obter_prontuario(paciente_id, app.usuario_logado)
        except AcessoNegadoError as e:
            messagebox.showerror("Acesso negado", str(e))
            self.destroy()
            return

        tk.Label(self, text="Histórico de Sessões", font=FONT_TITLE, bg="white").pack(
            anchor="w", padx=20, pady=(15, 5))

        hist_frame = tk.Frame(self, bg="white")
        hist_frame.pack(fill="both", expand=True, padx=20)
        text = tk.Text(hist_frame, height=12, wrap="word", font=FONT_NORMAL, bg="#f8f9fa")
        text.pack(fill="both", expand=True)
        if self.prontuario["sessoes"]:
            for s in self.prontuario["sessoes"]:
                text.insert("end", f"[{s['data']}] Sentimentos: {s['sentimentos_observados']}\n{s['anotacoes']}\n\n")
        else:
            text.insert("end", "Nenhuma sessão registrada ainda.")
        text.configure(state="disabled")

        tk.Label(self, text="Registrar Nova Sessão", font=FONT_BOLD, bg="white").pack(
            anchor="w", padx=20, pady=(15, 5))

        form = tk.Frame(self, bg="white")
        form.pack(fill="x", padx=20)
        tk.Label(form, text="Sentimentos observados:", bg="white", font=FONT_NORMAL).grid(row=0, column=0, sticky="w")
        self.sentimentos_var = tk.StringVar()
        tk.Entry(form, textvariable=self.sentimentos_var, width=50).grid(row=0, column=1, pady=4)

        tk.Label(self, text="Anotações da sessão:", bg="white", font=FONT_NORMAL).pack(anchor="w", padx=20)
        self.anotacoes_text = tk.Text(self, height=6, width=60, font=FONT_NORMAL)
        self.anotacoes_text.pack(padx=20, pady=(0, 10))

        tk.Button(self, text="Salvar Sessão", bg=ACCENT, fg="white", relief="flat",
                   padx=15, pady=6, command=self.salvar).pack(pady=10)

    def salvar(self):
        anotacoes = self.anotacoes_text.get("1.0", "end").strip()
        sentimentos = self.sentimentos_var.get().strip()
        if not anotacoes:
            messagebox.showwarning("Aviso", "Escreva as anotações da sessão.")
            return
        data_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            self.app.db.registrar_sessao(self.paciente_id, data_str, anotacoes,
                                           sentimentos, self.app.usuario_logado)
        except AcessoNegadoError as e:
            messagebox.showerror("Acesso negado", str(e))
            return
        messagebox.showinfo("Sucesso", "Sessão registrada com sucesso!")
        self.destroy()
