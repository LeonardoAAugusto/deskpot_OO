"""
models.py
---------
Modelagem completa em POO do sistema da clínica de psicologia (Nível 1).

Relações implementadas:
- Herança: Usuario -> Psicologo, Secretaria, Paciente
- Composição: Paciente -> Prontuario -> [Sessao]
- Associação: Consulta -> Paciente, Psicologo
- Polimorfismo: Consulta.calcularValor() sobrescrito em cada subclasse
- Dependência: GeradorRecibo depende de Consulta apenas via parâmetro
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ---------------------------------------------------------------------------
# HERANÇA: Usuario (classe abstrata / mãe) -> Psicologo, Secretaria, Paciente
# ---------------------------------------------------------------------------
class Usuario(ABC):
    def __init__(self, id, nome, email, senha, telefone):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone

    @abstractmethod
    def exibir_menu(self):
        """Cada tipo de usuário mostra um menu de terminal/GUI diferente."""
        raise NotImplementedError

    @property
    def tipo(self):
        return self.__class__.__name__.lower()

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, nome={self.nome!r})"


class Psicologo(Usuario):
    def __init__(self, id, nome, email, senha, telefone, crp, especialidade):
        super().__init__(id, nome, email, senha, telefone)
        self.crp = crp
        self.especialidade = especialidade

    def exibir_menu(self):
        return [
            "Ver consultas do dia",
            "Acessar prontuário de um paciente",
            "Registrar sessão",
        ]


class Secretaria(Usuario):
    def __init__(self, id, nome, email, senha, telefone, num_carteira_trabalho):
        super().__init__(id, nome, email, senha, telefone)
        self.num_carteira_trabalho = num_carteira_trabalho

    def exibir_menu(self):
        return [
            "Cadastrar/editar/remover pacientes",
            "Cadastrar/editar/remover psicólogos",
            "Agendar nova consulta",
            "Visualizar agenda completa",
        ]


class Paciente(Usuario):
    def __init__(self, id, nome, email, senha, telefone, cpf, data_nascimento):
        super().__init__(id, nome, email, senha, telefone)
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        # COMPOSIÇÃO: o Paciente "possui" um Prontuario. Se o paciente for
        # destruído, o prontuário não existe fora dele (ciclo de vida atrelado).
        self.prontuario = Prontuario(paciente=self)

    def exibir_menu(self):
        return ["Ver minhas consultas", "Ver meu prontuário (somente leitura)"]


# ---------------------------------------------------------------------------
# COMPOSIÇÃO: Prontuario "vive dentro" do Paciente e contém Sessao(s)
# ---------------------------------------------------------------------------
class Sessao:
    """Uma evolução clínica (registro de sessão) dentro de um prontuário."""

    def __init__(self, data, anotacoes, sentimentos_observados):
        self.data = data
        self.anotacoes = anotacoes
        self.sentimentos_observados = sentimentos_observados

    def __repr__(self):
        return f"Sessao({self.data}, sentimentos={self.sentimentos_observados!r})"


class Prontuario:
    """Composição: existe apenas enquanto o Paciente dono existir."""

    def __init__(self, paciente):
        self._paciente = paciente  # referência ao "dono" (composição)
        self.sessoes = []  # lista de objetos Sessao

    def adicionar_sessao(self, sessao: Sessao):
        self.sessoes.append(sessao)

    def __repr__(self):
        return f"Prontuario(paciente={self._paciente.nome!r}, sessoes={len(self.sessoes)})"


# ---------------------------------------------------------------------------
# ASSOCIAÇÃO + POLIMORFISMO: Consulta associa Paciente e Psicologo
# ---------------------------------------------------------------------------
class Consulta(ABC):
    VALOR_BASE = 150.00

    def __init__(self, id, paciente: Paciente, psicologo: Psicologo, data_hora, status="agendada"):
        # ASSOCIAÇÃO: Consulta apenas referencia Paciente e Psicologo,
        # não é dona do ciclo de vida deles.
        self.id = id
        self.paciente = paciente
        self.psicologo = psicologo
        self.data_hora = data_hora
        self.status = status  # 'agendada' | 'confirmada' | 'cancelada' | 'faltou'

    @abstractmethod
    def calcularValor(self):
        raise NotImplementedError

    @property
    def tipo(self):
        return self.__class__.__name__

    def __repr__(self):
        return (f"{self.tipo}(paciente={self.paciente.nome!r}, "
                f"psicologo={self.psicologo.nome!r}, data={self.data_hora}, "
                f"valor=R${self.calcularValor():.2f})")


class ConsultaIndividual(Consulta):
    def calcularValor(self):
        return self.VALOR_BASE


class TerapiaCasal(Consulta):
    def calcularValor(self):
        return self.VALOR_BASE * 1.30  # acréscimo de 30%


class ConsultaOnline(Consulta):
    def calcularValor(self):
        return self.VALOR_BASE * 0.90  # desconto de 10%


CONSULTA_CLASSES = {
    "Individual": ConsultaIndividual,
    "Casal": TerapiaCasal,
    "Online": ConsultaOnline,
}


# ---------------------------------------------------------------------------
# DEPENDÊNCIA: GeradorRecibo depende de Consulta apenas via parâmetro
# ---------------------------------------------------------------------------
class GeradorRecibo:
    """Classe utilitária. Não guarda nenhuma Consulta como atributo:
    apenas recebe uma no método gerar() -> relação de DEPENDÊNCIA."""

    @staticmethod
    def gerar(consulta: Consulta) -> str:
        recibo = (
            "==================== RECIBO ====================\n"
            f" Paciente:   {consulta.paciente.nome}\n"
            f" Psicólogo:  {consulta.psicologo.nome} (CRP {consulta.psicologo.crp})\n"
            f" Tipo:       {consulta.tipo}\n"
            f" Data/Hora:  {consulta.data_hora}\n"
            f" Valor:      R$ {consulta.calcularValor():.2f}\n"
            f" Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            "=================================================="
        )
        print(recibo)
        return recibo
