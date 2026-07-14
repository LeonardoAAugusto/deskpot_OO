# Sistema de Gestão para Clínica de Psicologia

Projeto de Programação Orientada a Objetos em Python — cobre os 4 níveis da
tarefa (POO pura, menu funcional, banco de dados e GUI) em um único app
desktop funcional.

## Como rodar (Windows)

1. Instale o Python 3.10+ (https://www.python.org/downloads/), marcando a
   opção **"Add Python to PATH"** durante a instalação.
2. Baixe/extraia esta pasta `clinica_psicologia`.
3. Abra o Prompt de Comando (cmd) ou PowerShell dentro da pasta e rode:

   ```
   python main.py
   ```

Não é necessário instalar nada extra: `tkinter` (interface gráfica) e
`sqlite3` (banco de dados) já vêm inclusos na instalação padrão do Python
no Windows.

Na primeira execução, o programa cria automaticamente o arquivo `clinica.db`
com 3 usuários de demonstração:

| Papel      | E-mail              | Senha |
|------------|---------------------|-------|
| Psicólogo  | ana@clinica.com     | 123   |
| Secretária | carla@clinica.com   | 123   |
| Paciente   | joao@paciente.com   | 123   |

(Login de paciente ainda não tem tela própria — o foco do app é
Secretaria/Psicólogo, conforme o enunciado.)

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

## Roteiro sugerido para os vídeos

- **Nível 1 (3 min):** mostre o `diagrama_uml.svg`, explique as 5 relações,
  rode um teste rápido no terminal (`python -c "from models import ..."`)
  mostrando o polimorfismo de `calcularValor()`.
- **Nível 2 (6 min):** rode `python main.py`, faça login como secretária e
  psicólogo, navegue pelos menus, agende uma consulta, registre uma sessão.
- **Nível 3 (6 min):** mostre o arquivo `clinica.db` sendo criado, feche e
  reabra o programa provando que os dados persistem; tente logar como
  secretária e mostre que o acesso ao prontuário é bloqueado.
- **Nível 4 (6 min):** destaque a tela de login, o menu lateral, os
  indicadores coloridos da agenda (verde/amarelo/vermelho) e os pop-ups de
  "Novo Agendamento" e "Prontuário".

## Observações

- Todo o código foi testado ponta a ponta (login, CRUD, agendamento,
  prontuário e regra de acesso) antes da entrega.
- Sinta-se à vontade para trocar os dados de demonstração em
  `App._seed_demo_data()` dentro de `gui.py`.
