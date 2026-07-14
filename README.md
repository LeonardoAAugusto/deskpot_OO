# Sistema de Gestão para Clínica de Psicologia

Projeto de Programação Orientada a Objetos em Python — cobre os 4 níveis da
tarefa (POO pura, menu funcional, banco de dados e GUI) em um único app
desktop funcional.

## Demonstração:

| Papel      | E-mail              | Senha |
|------------|---------------------|-------|
| Psicólogo  | ana@clinica.com     | 123   |
| Secretária | carla@clinica.com   | 123   |
| Paciente   | joao@paciente.com   | 123   |

(Login de paciente ainda não tem tela própria — o foco do app é
Secretaria/Psicólogo)

## Estrutura de arquivos

```
clinica_psicologia/
├── main.py            -> ponto de entrada (rode este arquivo)
├── models.py           -> Nível 1: classes POO puras (herança, composição,
│                          associação, polimorfismo, dependência)
├── database.py         -> Nível 3: persistência SQLite + regra de sigilo
├── gui.py               -> Níveis 2 e 4: menu funcional + interface gráfica
├── diagrama_uml.svg      -> Diagrama de classes UML para a apresentação
└── clinica.db           -> criado automaticamente na 1ª execução
```

## Onde está cada relação de POO (para sua apresentação)

| Relação      | Onde está no código |
|--------------|----------------------|
| **Herança**      | `Usuario` (abstrata) → `Psicologo`, `Secretaria`, `Paciente` em `models.py` |
| **Composição**   | `Paciente` cria seu próprio `Prontuario` no `__init__`; `Prontuario` contém uma lista de `Sessao` |
| **Associação**   | `Consulta` referencia um `Paciente` e um `Psicologo` sem ser "dona" deles |
| **Polimorfismo** | `Consulta.calcularValor()` é sobrescrito em `ConsultaIndividual`, `TerapiaCasal` (+30%) e `ConsultaOnline` (-10%) |
| **Dependência**  | `GeradorRecibo.gerar(consulta)` recebe a `Consulta` só como parâmetro, não guarda como atributo |

## Regra de segurança (Nível 3)

Em `database.py`, o método `_checar_acesso_prontuario()` bloqueia qualquer
tentativa de leitura/escrita nas tabelas `prontuarios`/`sessoes` quando o
usuário logado é do tipo `secretaria`, lançando `AcessoNegadoError`. Isso
é testado tanto na camada de banco quanto refletido na GUI (o botão de
prontuário só aparece/funciona para o psicólogo).
