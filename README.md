# Odyssey AV

**Ferramenta de linha de comando para análise e diagnóstico de segurança em Windows e Linux.**

O Odyssey AV reúne ferramentas locais para verificar arquivos, calcular e comparar hashes, avaliar e gerar senhas, analisar URLs e consultar o histórico das análises. Todas as operações são locais, somente leitura e explícitas: nada é executado, modificado ou enviado para a internet sem um comando seu.

> **Aviso:** o Odyssey AV **não é um antivírus**. Os indicadores que ele aponta são sinais de atenção, não confirmação de ameaça. Ele não substitui uma solução de proteção de endpoints.

---

## Status atual

| Área | Situação |
|---|---|
| `odyssey status` | Concluído |
| `odyssey hash calculate` | Concluído |
| `odyssey hash compare` | Concluído |
| `odyssey password generate` | Concluído |
| `odyssey password evaluate` | Concluído |
| `odyssey url analyze` | Concluído |
| `odyssey file analyze` | Concluído |
| `odyssey history list` | Parcial: só responde "não implementado" em sessão normal |
| `odyssey history show` | Planejado |
| `odyssey history export` | Planejado |
| `odyssey process list` | Planejado |
| Diagnóstico de rede (`network`) | Removido do escopo do MVP |

Os testes automatizados rodam em Windows e Linux, com Python 3.11 e 3.13, a cada alteração no repositório.

---

## Instalação

Requisitos: Python 3.11 ou superior e Git.

```bash
git clone https://github.com/Leonardo-Campos-2007/Odyssey-AV.git
cd Odyssey-AV
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\activate
# Linux:
source .venv/bin/activate

pip install -e ".[dev]"
odyssey --help
```

Para rodar os testes:

```bash
pytest
```

---

## Uso rápido

```bash
odyssey status                                  # estado da sessão
odyssey hash calculate arquivo.pdf              # SHA-256 de um arquivo
odyssey hash compare arquivo.pdf --reference <sha256>
odyssey password generate                       # senha de 16 caracteres
odyssey password evaluate                       # avalia uma senha digitada de forma oculta
odyssey url analyze "https://exemplo.com/caminho"
odyssey file analyze arquivo.exe                # identifica o formato pelo cabeçalho
```

Opções globais, usadas antes do comando:

| Opção | Efeito |
|---|---|
| `--json` | Saída estruturada em JSON, útil para scripts |
| `--log-level NIVEL` | Nível dos logs técnicos: `DEBUG`, `INFO`, `WARNING` ou `ERROR` |
| `--help` | Ajuda geral ou de um comando |

Exemplo: `odyssey --json hash calculate arquivo.pdf`.

---

## Funcionalidades em detalhe

### `odyssey status` (concluído)

**O que faz:** mostra o estado da sessão atual.

**Na prática:** use para confirmar se o histórico está disponível antes de uma análise importante. A saída indica:

- **Estado:** `NORMAL` (tudo funciona) ou `DEGRADED` (o histórico está indisponível nesta sessão).
- **Instância:** identificador único da execução atual.
- **Execuções recuperadas:** quantas execuções que ficaram em andamento numa sessão anterior foram marcadas como interrompidas.
- **Histórico:** disponível ou indisponível.

Este comando não cria nenhum registro no histórico.

### `odyssey hash calculate <arquivo>` (concluído)

**O que faz:** calcula o SHA-256 dos bytes reais do arquivo, lendo em blocos de 1 MiB. Com `--reference`, também compara o resultado com um valor que você informa.

**Na prática:**

- Serve para conferir a integridade de um download. Se o site publica o SHA-256 do arquivo, você calcula o hash localmente e compara.
- Sem `--reference`, o resultado é `NO_REFERENCE`, ou seja, só o cálculo, sem comparação.
- Com uma referência divergente, o comando mostra `MISMATCH` e avisa que o arquivo não confere. O código de saída continua `0`, porque calcular o hash foi concluído com sucesso.
- Diretórios, links simbólicos, dispositivos e arquivos especiais são recusados.

**Exemplo:**

```bash
odyssey hash calculate instalador.exe --reference 2d0b3948c1edc5c6a1d1f3e3658613252cfbbfa1b98b46cb7cc8e5bf2efb158f
```

**Registro no histórico:** SHA-256, tamanho, resultado da comparação e o **nome** do arquivo (não o caminho completo). A referência informada não é gravada.

### `odyssey hash compare <arquivo> --reference <sha256>` (concluído)

**O que faz:** verifica se o arquivo confere com a referência. A referência é obrigatória.

**Na prática:** é o comando para verificações em scripts, porque o código de saída indica o resultado:

- `0`: o arquivo confere (`MATCH`).
- `1`: o arquivo não confere (`MISMATCH`).
- `2`: a referência não foi informada ou tem formato inválido.

```powershell
odyssey hash compare instalador.exe --reference <sha256>
if ($LASTEXITCODE -eq 0) { "Arquivo íntegro" } else { "Arquivo não confere" }
```

### `odyssey password generate` (concluído)

**O que faz:** gera uma senha aleatória com o módulo `secrets`, que é a fonte criptográfica do Python.

**Na prática:**

- Por padrão, gera 16 caracteres com letras maiúsculas, minúsculas, dígitos e símbolos. Cada conjunto aparece pelo menos uma vez.
- `--length N` define o tamanho, entre 8 e 128.
- `--no-upper`, `--no-digits` e `--no-symbols` removem um conjunto. Minúsculas estão sempre presentes.

**Exemplos:**

```bash
odyssey password generate
odyssey password generate --length 24 --no-symbols
odyssey --json password generate
```

**Cuidados:**

- A senha aparece na tela, e é a única cópia. O Odyssey AV não a armazena. Copie-a para um gerenciador de senhas antes de fechar o terminal.
- No modo JSON, o aviso de que a senha não é armazenada vai para o `stderr`, sem afetar a saída.

**Registro no histórico:** apenas o comprimento e os conjuntos usados. A senha nunca é gravada.

### `odyssey password evaluate` (concluído)

**O que faz:** avalia a força de uma senha que você digita.

**Na prática:**

- A senha é pedida de forma oculta, sem eco na tela, e nunca aceita como argumento de linha de comando. Assim ela não fica no histórico do terminal.
- Se a entrada não vier de um terminal interativo, como um pipe ou um arquivo, o comando recusa e sai com código `2`. Isso evita ler senhas de lugares inesperados.

**Como a força é calculada:**

| Critério | Pontuação |
|---|---|
| Comprimento menor que 8 | 0 pontos |
| Comprimento de 8 a 11 | 1 ponto |
| Comprimento de 12 ou mais | 2 pontos |
| Cada conjunto presente (minúsculas, maiúsculas, dígitos, símbolos) | 1 ponto cada |
| Repetições ou sequências simples, como `aaa`, `abc` ou `321` | menos 1 ponto |

A classificação fica assim: até 2 pontos, muito fraca; 3, fraca; 4, razoável; 5 ou mais, forte.

Caracteres fora dos quatro conjuntos, como espaços e acentos, não pontuam.

**Limite:** a avaliação é uma estimativa. Ela não garante segurança absoluta.

**Registro no histórico:** apenas os indicadores (comprimento, conjuntos, presença de repetições, pontuação e classificação). A senha nunca é gravada.

### `odyssey url analyze "<url>"` (concluído)

**O que faz:** decompõe a URL e aponta sinais de atenção. **Não acessa o endereço.** Nenhuma requisição é feita e nenhuma consulta DNS é disparada.

**Na prática:** use antes de clicar em um link recebido por e-mail ou mensagem. A saída mostra:

- A URL normalizada, com esquema e domínio em minúsculas, porta padrão removida e segmentos `.` e `..` resolvidos.
- Esquema, domínio, porta, caminho e a presença de query e fragmento.
- Indicadores de atenção.

**Indicadores apontados:**

| Indicador | Por que chama atenção |
|---|---|
| Esquema diferente de `http` ou `https` | Protocolos incomuns em links comuns |
| Endereço IP no lugar do domínio | Sites legítimos quase sempre usam nomes |
| Porta não padrão | Pode indicar serviço improvisado |
| Caracteres não ASCII no domínio | Pode imitar outro nome (ataque de homógrafo) |
| Prefixo `xn--` | Domínio internacionalizado, que pode ocultar caracteres |
| Muitos subdomínios | Técnica comum para parecer um site conhecido |
| Muitos hífens no domínio | Padrão frequente em domínios falsos |
| Informações de usuário antes do domínio | Pode enganar sobre o destino real; os valores são omitidos |

**Exemplo:**

```bash
odyssey url analyze "https://usuario:senha@banco-exemplo.com/login"
```

A saída mostra que há credenciais no link e omite os valores.

**Limites:** URLs com mais de 2048 caracteres são recusadas. Links sem esquema, como `exemplo.com`, e esquemas sem host, como `mailto:`, também são recusados com código `2`.

**Registro no histórico:** componentes da URL e códigos dos indicadores. Credenciais, valores de query e fragmento **não** são gravados. O caminho é gravado e pode conter identificadores.

### `odyssey file analyze <arquivo>` (concluído)

**O que faz:** identifica o formato real do arquivo pelo cabeçalho e compara com a extensão. Lê apenas o início do arquivo, no máximo 4 KiB, e nunca executa nem altera o conteúdo.

**Na prática:** é útil para detectar arquivos disfarçados. Por exemplo, um arquivo chamado `relatorio.pdf` cujo conteúdo é um executável.

**Formatos identificados:** PE (executável Windows), ELF (executável Linux), PDF, PNG, JPEG, ZIP e GZIP. Para PE, o comando confere a assinatura `PE` no local indicado pelo cabeçalho, para não confundir um arquivo que apenas começa com `MZ`.

**Divergência:** o comando só aponta divergência quando a extensão pertence a uma família conhecida. Por exemplo, `.exe` deve ser PE, e `.pdf` deve ser PDF. Extensões desconhecidas não geram alerta, para evitar falsos positivos.

**Exemplo de saída com divergência:**

```text
Formato identificado: PDF
Formato esperado pela extensão: PE (executável Windows)
- A extensão .exe indica PE (executável Windows), mas o formato identificado é PDF.
```

**Proteções:**

- Diretórios, links simbólicos e arquivos especiais, como FIFOs e dispositivos, são recusados antes de qualquer leitura.
- O diretório de dados do próprio Odyssey AV, onde ficam o histórico e o bloqueio, é recusado com código `2`. Isso impede que a análise leia o histórico.
- O arquivo é aberto somente para leitura. Você pode confirmar isso comparando o hash e a data de modificação antes e depois.

**Registro no histórico:** extensão, tamanho, formato identificado, formato esperado e os códigos de indicadores. O **nome** do arquivo e o **caminho** não são gravados.

**Limite:** o comando identifica o formato, mas não diz se o arquivo é seguro. Um executável legítimo e um malicioso podem ter o mesmo cabeçalho.

### `odyssey history list` (parcial)

**Situação atual:** o comando existe, mas ainda não consulta o histórico. Em sessão normal, mostra "Consulta do histórico ainda não implementada." e sai com código `1`. Em sessão degradada, recusa a operação com mensagem clara.

**O que deve fazer quando estiver pronto:** listar as execuções registradas, com filtros por módulo, estado e período, e com limite de resultados.

**Planejado:**

```bash
odyssey history list --module HASH --status SUCCESS --limit 20
```

A sintaxe ainda está em definição. Para consultar o histórico agora, use o DB Browser for SQLite, como descrito na seção de histórico.

### `odyssey history show <id>` (planejado)

**O que vai fazer:** mostrar os detalhes de uma execução, com os resultados associados.

**Na prática:** depois de uma análise, você copia o ID da execução e consulta o que foi registrado. Não está implementado.

### `odyssey history export` (planejado)

**O que vai fazer:** exportar o histórico em JSON ou CSV, para um arquivo que você escolhe.

**Planejado:**

```bash
odyssey history export --format json --output relatorio.json
```

**Regras previstas:**

- O destino é obrigatório, para que dados do histórico não apareçam no terminal por acidente.
- O arquivo existente não é sobrescrito, a menos que você use `--force`.
- Não é possível exportar para dentro do diretório de dados do Odyssey AV.
- Senhas e segredos nunca fazem parte da exportação, porque nunca são gravados.

Não está implementado.

### `odyssey process list` (planejado)

**O que vai fazer:** listar os processos em execução que o seu usuário pode consultar, com PID, nome e métricas disponíveis. Permitirá filtrar por PID ou por nome.

**Na prática:** útil para descobrir qual programa está usando uma porta ou consumindo muitos recursos. O comando será somente leitura: não encerra, suspende nem altera nenhum processo.

Não está implementado. Está previsto para a Fase E, com a biblioteca `psutil`.

### Diagnóstico de rede (removido do escopo)

Este módulo foi retirado do MVP. Para verificar a conectividade e a resolução de nomes, use as ferramentas do próprio sistema, como `ping` e `nslookup` no Windows e no Linux.

---

## Histórico de análises

Cada operação funcional é registrada em um banco SQLite local, com metadados e resultados, não com o conteúdo analisado.

**Onde fica:**

- Windows: `%LOCALAPPDATA%\odyssey-av\history.db`
- Linux: `~/.odyssey-av/history.db`

**Como consultar agora:** abra o arquivo com um visualizador como o DB Browser for SQLite, na aba "Execute SQL", e rode, por exemplo, `SELECT * FROM analysis_runs;`.

**O que é gravado, por módulo:**

| Módulo | Gravado | Não gravado |
|---|---|---|
| HASH | Nome do arquivo, SHA-256, tamanho e resultado da comparação | Caminho completo e referência informada |
| PASSWORD | Comprimento e conjuntos usados, ou indicadores da avaliação | Senha em qualquer forma |
| URL | Componentes e códigos de indicadores | Credenciais, query, fragmento |
| FILE | Extensão, tamanho, formato e indicadores | Nome e caminho do arquivo |

Em todos os módulos, o histórico guarda também o horário, o estado da execução e o identificador da instância.

**Falhas também são registradas:** se um arquivo não existir, a tentativa aparece no histórico com estado `FAILED`.

---

## Estados da sessão

O Odyssey AV tem dois estados operacionais:

- **`NORMAL`:** tudo funciona. Resultados são gravados no histórico.
- **`DEGRADED`:** a recuperação do histórico falhou ao iniciar. As ferramentas continuam funcionando, mas nada é gravado e o `history` fica indisponível. A próxima inicialização tenta a recuperação de novo.

Uma falha de gravação isolada, durante uma sessão normal, não muda o estado. Ela afeta só o registro daquela operação, e a saída informa isso.

**Recuperação de execuções:** ao iniciar, execuções que ficaram em andamento numa sessão anterior, por exemplo porque o computador foi desligado, são marcadas como `INTERRUPTED`.

**Instância única:** só uma instância do Odyssey AV pode rodar por vez. Uma segunda é recusada com erro claro.

---

## Códigos de saída

Use estes códigos em scripts:

| Código | Significado |
|---|---|
| `0` | Operação concluída, com histórico confirmado quando aplicável |
| `1` | Falha na operação, ou arquivo que não confere em `hash compare` |
| `2` | Uso inválido: argumento, referência ou caminho recusado |
| `3` | Operação concluída, mas o histórico não foi gravado |
| `4` | Resultado parcial |

No PowerShell, use `echo $LASTEXITCODE`. No `cmd.exe`, use `echo %errorlevel%`.

---

## Configuração

O Odyssey AV funciona sem configuração. Se quiser, crie um arquivo `odyssey.toml` no diretório de onde você executa o comando:

```toml
output_format = "json"   # "text" ou "json"
log_level = "INFO"       # DEBUG, INFO, WARNING ou ERROR
```

Ou aponte outro arquivo com a variável `ODYSSEY_CONFIG`.

A precedência é: valores padrão, depois o arquivo TOML e, por fim, as opções passadas na linha de comando. Um arquivo inválido gera erro, e chaves desconhecidas são recusadas, para que nenhuma configuração seja ignorada em silêncio.

---

## Limitações conhecidas

- Não é antivírus. Não há proteção em tempo real, quarentena nem análise de comportamento.
- A análise de arquivos identifica formato, não segurança.
- No Windows, links simbólicos são seguidos pela abertura de arquivos. A proteção depende da verificação de tipo antes da leitura.
- A data de último acesso (`atime`) de um arquivo pode mudar durante a leitura. O conteúdo não muda.
- Senhas permanecem na memória do Python até o coletor de lixo liberá-las, porque o Python não permite apagá-las de forma garantida.
- Executar `odyssey --help` também abre o histórico e o bloqueio de instância.

---

## Documentação

A documentação completa fica em `docs/`:

| Documento | Conteúdo |
|---|---|
| `REQUISITOS.md` | Requisitos funcionais e não funcionais |
| `REGRAS-DE-NEGOCIO.md` | Regras que o comportamento deve respeitar |
| `ARQUITETURA.md` | Camadas, módulos e fluxos |
| `SEGURANCA.md` | Controles, ameaças e testes de segurança |
| `MODELO-DE-DADOS.md` | Tabelas, estados e relacionamentos |
| `API.md` | Contrato dos comandos e códigos de saída |
| `TESTES.md` | Estratégia e casos de teste |
| `BACKLOG.md` | Épicos, histórias e sprints |
| `PROGRESSO.md` | Estado atual, decisões e pendências |

---

## Desenvolvimento

O projeto segue um backlog incremental, com testes em Windows e Linux. Antes de cada alteração ser considerada concluída, a suíte precisa passar nos dois sistemas.

Para contribuir, leia `docs/PROGRESSO.md` para ver as decisões em aberto.

---

## Licença

Apache License 2.0. Veja o arquivo `LICENSE`.