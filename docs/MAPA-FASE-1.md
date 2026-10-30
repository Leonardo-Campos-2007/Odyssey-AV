# MAPA-FASE-1.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Primeira versão

---

# 1. Objetivo

Este documento define a estrutura de diretórios, pacotes e arquivos prevista para o desenvolvimento do Odyssey AV.

O mapa funciona como uma referência estrutural para orientar a implementação, mantendo a organização modular, a separação de responsabilidades e a rastreabilidade com a documentação do projeto.

A estrutura considera:

- Python como linguagem principal.
- Typer para interface de linha de comando.
- Arquitetura modular em camadas.
- SQLite para persistência local.
- pytest para testes automatizados.
- Compatibilidade com Windows e Linux.

# 2. Estrutura geral do projeto

```text
odyssey-av/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── REQUISITOS.md
│   ├── REGRAS-DE-NEGOCIO.md
│   ├── ARQUITETURA.md
│   ├── SEGURANCA.md
│   ├── MODELO-DE-DADOS.md
│   ├── TESTES.md
│   ├── BACKLOG.md
│   ├── MAPA-FASE-1.md
│   └── API.md
│
├── src/
│   └── odyssey_av/
│       │
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── commands/
│       │       ├── __init__.py
│       │       ├── file.py
│       │       ├── hash.py
│       │       ├── network.py
│       │       ├── password.py
│       │       ├── url.py
│       │       ├── process.py
│       │       └── history.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   ├── contracts/
│       │   │   ├── __init__.py
│       │   │   └── execution.py
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   └── execution_service.py
│       │   └── use_cases/
│       │       ├── __init__.py
│       │       ├── analyze_file.py
│       │       ├── calculate_hash.py
│       │       ├── compare_hash.py
│       │       ├── diagnose_network.py
│       │       ├── generate_password.py
│       │       ├── evaluate_password.py
│       │       ├── analyze_url.py
│       │       ├── list_processes.py
│       │       ├── list_history.py
│       │       └── export_history.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── analysis_run.py
│       │   │   └── analysis_result.py
│       │   ├── enums/
│       │   │   ├── __init__.py
│       │   │   ├── execution_status.py
│       │   │   ├── result_status.py
│       │   │   └── module.py
│       │   └── exceptions/
│       │       └── __init__.py
│       │
│       ├── modules/
│       │   ├── __init__.py
│       │   ├── file/
│       │   │   ├── __init__.py
│       │   │   ├── analyzer.py
│       │   │   └── signatures.py
│       │   ├── hash/
│       │   │   ├── __init__.py
│       │   │   └── calculator.py
│       │   ├── network/
│       │   │   ├── __init__.py
│       │   │   └── diagnostics.py
│       │   ├── password/
│       │   │   ├── __init__.py
│       │   │   ├── generator.py
│       │   │   └── evaluator.py
│       │   ├── url/
│       │   │   ├── __init__.py
│       │   │   └── analyzer.py
│       │   ├── process/
│       │   │   ├── __init__.py
│       │   │   └── monitor.py
│       │   └── history/
│       │       ├── __init__.py
│       │       └── service.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── persistence/
│       │   │   ├── __init__.py
│       │   │   ├── database.py
│       │   │   ├── repositories/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── analysis_run_repository.py
│       │   │   │   └── analysis_result_repository.py
│       │   │   └── migrations/
│       │   │       └── 001_initial_schema.sql
│       │   ├── platform/
│       │   │   ├── __init__.py
│       │   │   ├── system.py
│       │   │   └── process_adapter.py
│       │   └── network/
│       │       ├── __init__.py
│       │       └── network_adapter.py
│       │
│       └── shared/
│           ├── __init__.py
│           ├── config/
│           │   ├── __init__.py
│           │   └── loader.py
│           ├── logging/
│           │   ├── __init__.py
│           │   └── logger.py
│           ├── validation/
│           │   ├── __init__.py
│           │   └── validators.py
│           └── errors/
│               ├── __init__.py
│               └── handlers.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_file_analyzer.py
│   │   ├── test_hash_calculator.py
│   │   ├── test_network_diagnostics.py
│   │   ├── test_password_generator.py
│   │   ├── test_password_evaluator.py
│   │   ├── test_url_analyzer.py
│   │   ├── test_process_monitor.py
│   │   └── test_history_service.py
│   │
│   ├── integration/
│   │   ├── test_execution_flow.py
│   │   ├── test_persistence.py
│   │   ├── test_history.py
│   │   └── test_export.py
│   │
│   ├── cli/
│   │   └── test_commands.py
│   │
│   └── security/
│       ├── test_file_safety.py
│       ├── test_password_privacy.py
│       ├── test_url_safety.py
│       ├── test_process_safety.py
│       └── test_history_privacy.py
│
└── .github/
    └── workflows/
        └── tests.yml
```

# 3. Responsabilidade dos diretórios

## 3.1. `docs/`

Armazena a documentação oficial do projeto.

Os documentos devem acompanhar a evolução do desenvolvimento.

Alterações em requisitos, regras de negócio, arquitetura, segurança ou modelo de dados devem ser avaliadas quanto aos impactos nos demais documentos.

## 3.2. `src/odyssey_av/`

Contém o código-fonte principal da aplicação.

A organização interna separa a interface de entrada, a coordenação dos casos de uso, o domínio, os módulos funcionais e a infraestrutura.

## 3.3. `cli/`

Responsável pela interface de linha de comando.

Responsabilidades:

- Registrar comandos.
- Receber argumentos.
- Validar parâmetros de entrada da interface.
- Encaminhar operações para os casos de uso.
- Apresentar resultados e mensagens de erro.

A CLI não deve implementar regras de negócio.

## 3.4. `application/`

Responsável por coordenar a execução das funcionalidades.

### `contracts/`

Define contratos compartilhados entre a camada de aplicação e os componentes envolvidos na execução.

### `services/`

Contém serviços de aplicação que coordenam operações transversais, como o ciclo de execução e o registro de resultados.

### `use_cases/`

Contém os casos de uso que representam as operações disponibilizadas pela aplicação.

Exemplos:

- `AnalyzeFile`
- `CalculateHash`
- `CompareHash`
- `DiagnoseNetwork`
- `GeneratePassword`
- `EvaluatePassword`
- `AnalyzeUrl`
- `ListProcesses`
- `ListHistory`
- `ExportHistory`

Cada caso de uso deve possuir uma responsabilidade delimitada.

## 3.5. `domain/`

Contém os elementos centrais do domínio.

### `entities/`

Entidades persistentes:

- `AnalysisRun`
- `AnalysisResult`

### `enums/`

Estados e classificações utilizados pelo domínio:

- `ExecutionStatus`
- `ResultStatus`
- `Module`

### `exceptions/`

Exceções específicas do domínio, quando necessárias.

O domínio não deve depender da CLI, do SQLite ou de detalhes de infraestrutura.

## 3.6. `modules/`

Contém as sete ferramentas funcionais do Odyssey AV.

| Módulo | Responsabilidade |
|---|---|
| `file/` | Analisar arquivos e assinaturas |
| `hash/` | Calcular e comparar hashes |
| `network/` | Diagnosticar conectividade e DNS |
| `password/` | Gerar e avaliar senhas |
| `url/` | Analisar e normalizar URLs |
| `process/` | Consultar processos do sistema |
| `history/` | Consultar e organizar histórico |

Os módulos não devem depender diretamente uns dos outros.

A comunicação entre funcionalidades deve ocorrer por meio dos contratos e casos de uso da aplicação, quando necessário.

## 3.7. `infrastructure/`

Contém implementações técnicas que dependem de recursos externos ou do ambiente de execução.

### `persistence/`

Responsável pelo SQLite e pela persistência das entidades.

Contém:

- Conexão com o banco.
- Repositórios.
- Estrutura SQL inicial.

### `platform/`

Responsável por isolar particularidades dos sistemas operacionais.

### `network/`

Responsável pelos adaptadores utilizados nas operações de rede.

A infraestrutura implementa os mecanismos técnicos, sem definir as regras de negócio.

## 3.8. `shared/`

Contém serviços transversais utilizados por diferentes partes da aplicação.

| Diretório | Responsabilidade |
|---|---|
| `config/` | Carregamento e validação de configurações |
| `logging/` | Logs centralizados |
| `validation/` | Validações reutilizáveis |
| `errors/` | Tratamento compartilhado de erros |

Não devem ser adicionadas abstrações genéricas sem necessidade comprovada.

# 4. Responsabilidade dos arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Inicialização da aplicação |
| `cli/app.py` | Configuração da CLI |
| `application/services/execution_service.py` | Coordenar ciclo de execução |
| `domain/entities/analysis_run.py` | Representar execução |
| `domain/entities/analysis_result.py` | Representar resultado |
| `infrastructure/persistence/database.py` | Gerenciar conexão SQLite |
| `analysis_run_repository.py` | Persistir e consultar execuções |
| `analysis_result_repository.py` | Persistir e consultar resultados |
| `shared/config/loader.py` | Carregar configurações |
| `shared/logging/logger.py` | Centralizar logs |

# 5. Fluxo arquitetural

O fluxo padrão de uma operação será:

```text
Usuário
   |
   v
CLI (Typer)
   |
   v
Caso de uso
   |
   v
Módulo funcional
   |
   v
Resultado
   |
   v
Serviço de execução
   |
   +------> Repositório de execução
   |
   +------> Repositório de resultado
                 |
                 v
               SQLite
```

A camada de aplicação coordena o fluxo e utiliza os contratos definidos para acessar os recursos necessários.

Os módulos funcionais não devem acessar diretamente a CLI nem controlar a persistência do histórico.

# 6. Organização dos testes

Os testes deverão acompanhar a organização funcional do projeto.

## 6.1. `tests/unit/`

Verifica o comportamento isolado das funcionalidades.

Exemplos:

- Cálculo de SHA-256.
- Parsing de URLs.
- Geração de senhas.
- Identificação de assinaturas.
- Filtros de processos.

## 6.2. `tests/integration/`

Verifica a interação entre componentes.

Exemplos:

- Execução de caso de uso com persistência.
- Associação entre execução e resultado.
- Consulta do histórico.
- Exportação de relatórios.

## 6.3. `tests/cli/`

Verifica os comandos, parâmetros e respostas da interface.

## 6.4. `tests/security/`

Verifica os controles de segurança definidos no documento `SEGURANCA.md`.

## 6.5. `conftest.py`

Armazena fixtures compartilhadas, como:

- Banco SQLite temporário.
- Diretórios temporários.
- Arquivos de teste.
- Dados simulados.
- Dependências substituídas por mocks.

# 7. Configuração e arquivos auxiliares

## 7.1. `pyproject.toml`

Centraliza:

- Metadados do projeto.
- Dependências.
- Configuração do ambiente de desenvolvimento.
- Configuração do pytest.
- Configuração de cobertura.

## 7.2. `.gitignore`

Deve impedir o versionamento de arquivos locais e temporários.

Exemplos:

- Ambientes virtuais.
- Cache Python.
- Arquivos de banco locais.
- Logs.
- Arquivos temporários.
- Configurações locais que possam conter dados sensíveis.

## 7.3. Configuração TOML

A configuração da aplicação poderá ser carregada de um arquivo TOML local.

O arquivo de configuração real não deverá ser versionado quando contiver informações específicas do ambiente do usuário.

Um exemplo de configuração poderá ser disponibilizado posteriormente, sem segredos.

## 7.4. Banco de dados

O SQLite será armazenado localmente.

O arquivo de banco de dados real não deverá ser incluído no repositório.

A estrutura inicial do banco será mantida em SQL versionado.

# 8. Dependências entre camadas

As dependências deverão respeitar os seguintes princípios:

1. A CLI depende da camada de aplicação.
2. A aplicação coordena os casos de uso.
3. Os módulos funcionais não dependem da CLI.
4. O domínio não depende de infraestrutura.
5. A infraestrutura implementa os recursos técnicos necessários.
6. Os serviços compartilhados não devem concentrar regras de negócio.
7. Não devem existir dependências circulares.

# 9. Convenções de nomenclatura

| Elemento | Convenção | Exemplo |
|---|---|---|
| Diretórios | snake_case | `application/` |
| Arquivos Python | snake_case | `analyze_file.py` |
| Classes | PascalCase | `AnalysisRun` |
| Funções | snake_case | `calculate_hash()` |
| Constantes | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| Testes | `test_` + nome | `test_hash_calculator.py` |

Os nomes devem representar claramente a responsabilidade dos componentes.

# 10. Implementação incremental

A estrutura será criada progressivamente conforme o backlog.

| Sprint | Estrutura principal |
|---|---|
| Sprint 1 | `cli/`, `application/`, `shared/` e inicialização |
| Sprint 2 | `domain/` e `infrastructure/persistence/` |
| Sprint 3 | `modules/file/` e `modules/hash/` |
| Sprint 4 | `modules/password/`, `modules/url/` e `modules/network/` |
| Sprint 5 | `modules/process/`, `modules/history/` e comandos de histórico |
| Sprint 6 | Ampliação de `tests/`, validação de segurança e compatibilidade |

A criação de diretórios e arquivos deverá acompanhar a implementação real.

Não criar arquivos vazios apenas para reproduzir o mapa.

# 11. Itens técnicos ainda sujeitos a validação

Os seguintes detalhes precisam ser confirmados durante a consolidação técnica ou implementação:

| ID | Item | Observação |
|---|---|---|
| MAP-001 | Estratégia de migrations SQLite | A estrutura SQL inicial está prevista; o mecanismo de evolução ainda precisa ser definido |
| MAP-002 | Precedência da configuração TOML | Definir localização e comportamento quando o arquivo não existir |
| MAP-003 | Contrato de execução | Detalhar o formato comum de resultados e estados |
| MAP-004 | Tratamento de falha na persistência | Definir comportamento quando a ferramenta conclui, mas o histórico não pode ser gravado |
| MAP-005 | Compatibilidade dos adaptadores | Validar diferenças entre Windows e Linux |
| MAP-006 | Automação de testes | Validar o fluxo de CI antes de torná-lo obrigatório |

Esses pontos não autorizam a inclusão de novas funcionalidades no MVP.

# 12. Estado do documento

| Critério | Situação |
|---|---|
| Estrutura geral | Definida |
| Organização das camadas | Definida |
| Módulos funcionais | Definidos |
| Responsabilidades | Definidas |
| Organização dos testes | Definida |
| Arquivos de configuração | Mapeados |
| Dependências entre camadas | Definidas |
| Implementação incremental | Planejada |
| Pendências técnicas | Identificadas |
| Revisão de consistência | Pendente |

