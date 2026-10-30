# MAPA-FASE-1.md

**Projeto:** Odyssey AV  
**Versão:** 2.0  
**Escopo:** MVP  
**Status:** Consolidado para revisão

---

# 1. Objetivo

Este documento define a estrutura de diretórios, pacotes e arquivos prevista para o desenvolvimento do Odyssey AV.

O mapa orienta a implementação, estabelecendo a organização dos componentes, suas responsabilidades e as dependências permitidas entre as camadas.

A estrutura deverá acompanhar o backlog e respeitar os documentos:

- `REQUISITOS.md`
- `REGRAS-DE-NEGOCIO.md`
- `ARQUITETURA.md`
- `SEGURANCA.md`
- `MODELO-DE-DADOS.md`
- `API.md`
- `TESTES.md`
- `BACKLOG.md`

O mapa representa a estrutura planejada. Sua presença neste documento não significa que todos os diretórios e arquivos devam ser criados imediatamente.

# 2. Estrutura geral do projeto

```text
odyssey-av/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── README.md
│   ├── REQUISITOS.md
│   ├── REGRAS-DE-NEGOCIO.md
│   ├── ARQUITETURA.md
│   ├── SEGURANCA.md
│   ├── MODELO-DE-DADOS.md
│   ├── API.md
│   ├── TESTES.md
│   ├── BACKLOG.md
│   └── MAPA-FASE-1.md
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
│       │   │
│       │   ├── contracts/
│       │   │   ├── __init__.py
│       │   │   ├── execution.py
│       │   │   └── repositories.py
│       │   │
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── execution_service.py
│       │   │   └── instance_service.py
│       │   │
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
│       │       ├── show_history.py
│       │       └── export_history.py
│       │
│       ├── domain/
│       │   ├── __init__.py
│       │   │
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── analysis_run.py
│       │   │   └── analysis_result.py
│       │   │
│       │   ├── enums/
│       │   │   ├── __init__.py
│       │   │   ├── execution_status.py
│       │   │   ├── result_status.py
│       │   │   └── module.py
│       │   │
│       │   └── exceptions/
│       │       └── __init__.py
│       │
│       ├── modules/
│       │   ├── __init__.py
│       │   │
│       │   ├── file/
│       │   │   ├── __init__.py
│       │   │   ├── analyzer.py
│       │   │   ├── signatures.py
│       │   │   └── file_validator.py
│       │   │
│       │   ├── hash/
│       │   │   ├── __init__.py
│       │   │   └── calculator.py
│       │   │
│       │   ├── network/
│       │   │   ├── __init__.py
│       │   │   └── diagnostics.py
│       │   │
│       │   ├── password/
│       │   │   ├── __init__.py
│       │   │   ├── generator.py
│       │   │   └── evaluator.py
│       │   │
│       │   ├── url/
│       │   │   ├── __init__.py
│       │   │   └── analyzer.py
│       │   │
│       │   ├── process/
│       │   │   ├── __init__.py
│       │   │   └── monitor.py
│       │   │
│       │   └── history/
│       │       ├── __init__.py
│       │       └── service.py
│       │
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   │
│       │   ├── persistence/
│       │   │   ├── __init__.py
│       │   │   ├── database.py
│       │   │   ├── repositories/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── analysis_run_repository.py
│       │   │   │   └── analysis_result_repository.py
│       │   │   └── migrations/
│       │   │       └── 001_initial_schema.sql
│       │   │
│       │   ├── platform/
│       │   │   ├── __init__.py
│       │   │   ├── system.py
│       │   │   ├── process_adapter.py
│       │   │   └── instance_lock.py
│       │   │
│       │   └── network/
│       │       ├── __init__.py
│       │       └── network_adapter.py
│       │
│       └── shared/
│           ├── __init__.py
│           │
│           ├── config/
│           │   ├── __init__.py
│           │   └── loader.py
│           │
│           ├── logging/
│           │   ├── __init__.py
│           │   └── logger.py
│           │
│           ├── validation/
│           │   ├── __init__.py
│           │   └── validators.py
│           │
│           └── errors/
│               ├── __init__.py
│               └── handlers.py
│
├── tests/
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── test_file_analyzer.py
│   │   ├── test_file_validator.py
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
│   │   ├── test_export.py
│   │   └── test_instance_recovery.py
│   │
│   ├── cli/
│   │   └── test_commands.py
│   │
│   ├── security/
│   │   ├── test_file_safety.py
│   │   ├── test_password_privacy.py
│   │   ├── test_url_safety.py
│   │   ├── test_process_safety.py
│   │   └── test_history_privacy.py
│   │
│   └── platform/
│       ├── test_instance_lock.py
│       └── test_platform_compatibility.py
│
└── .github/
    └── workflows/
        └── tests.yml
```

**Observação:** essa estrutura é uma referência arquitetural. Arquivos de testes e implementação serão criados conforme suas respectivas histórias e tarefas forem desenvolvidas.

# 3. Responsabilidade dos diretórios

## 3.1. `docs/`

Armazena a documentação oficial do projeto.

Os documentos deverão permanecer consistentes entre si. Alterações em requisitos, regras de negócio, arquitetura, segurança ou modelo de dados deverão ser avaliadas quanto aos seus impactos.

## 3.2. `src/odyssey_av/`

Contém o código-fonte principal.

Sua organização separa a interface de entrada, a coordenação dos casos de uso, o domínio, os módulos funcionais e a infraestrutura.

## 3.3. `cli/`

Responsável pela interface de linha de comando, utilizando Typer.

Responsabilidades:

- Registrar comandos.
- Receber argumentos.
- Validar parâmetros da interface.
- Encaminhar operações para a aplicação.
- Apresentar resultados.
- Apresentar erros e códigos de saída.

A CLI não deve implementar regras de negócio nem acessar diretamente o SQLite.

## 3.4. `application/`

Responsável por coordenar os casos de uso e controlar o fluxo de execução.

### `contracts/`

Define contratos utilizados pela aplicação para comunicação com outros componentes.

Os contratos deverão evitar dependência direta da aplicação em implementações concretas de infraestrutura.

### `services/`

Contém serviços de aplicação que coordenam operações transversais.

Responsabilidades previstas:

- Gerenciar o ciclo de execução.
- Coordenar registro de início e término.
- Controlar o ciclo de vida da instância.
- Coordenar a recuperação de execuções anteriores.

### `use_cases/`

Contém as operações disponibilizadas pela aplicação.

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
- `ShowHistory`
- `ExportHistory`

Cada caso de uso deverá possuir responsabilidade delimitada.

## 3.5. `domain/`

Contém as entidades, classificações e regras centrais do domínio.

### `entities/`

Entidades persistentes:

- `AnalysisRun`
- `AnalysisResult`

### `enums/`

Classificações:

- `ExecutionStatus`
- `ResultStatus`
- `Module`

Os estados de execução deverão contemplar:

- RUNNING
- SUCCESS
- PARTIAL
- FAILED
- INTERRUPTED

### `exceptions/`

Exceções específicas do domínio, quando necessárias.

O domínio não deverá depender da CLI, do SQLite ou de detalhes de infraestrutura.

## 3.6. `modules/`

Contém as sete ferramentas funcionais.

| Módulo | Responsabilidade |
|---|---|
| `file/` | Metadados, assinaturas e divergências de arquivos |
| `hash/` | Cálculo e comparação SHA-256 |
| `network/` | Diagnóstico de conectividade e DNS |
| `password/` | Geração e avaliação local de senhas |
| `url/` | Parsing, normalização e indicadores suspeitos |
| `process/` | Consulta de processos e métricas acessíveis |
| `history/` | Consulta e organização de registros históricos |

Os módulos deverão produzir resultados estruturados.

Não deverão acessar diretamente o SQLite ou assumir responsabilidades da camada de aplicação.

## 3.7. `infrastructure/`

Contém implementações técnicas dependentes de recursos externos ou do sistema operacional.

### `persistence/`

Responsável pela persistência local.

Componentes:

- Conexão SQLite.
- Repositórios de execução e resultado.
- Estrutura inicial do banco.
- Mecanismos de integridade e transação.

### `platform/`

Responsável por isolar diferenças entre Windows e Linux.

Inclui:

- Identificação e informações do sistema.
- Adaptador de processos.
- Mecanismo de bloqueio exclusivo da instância.

O mecanismo de bloqueio deverá utilizar recursos adequados de cada sistema operacional, mantendo um contrato comum para a aplicação.

### `network/`

Contém adaptadores para operações de rede.

Deverá respeitar os limites e timeouts definidos para o MVP.

## 3.8. `shared/`

Contém componentes transversais reutilizáveis.

| Diretório | Responsabilidade |
|---|---|
| `config/` | Carregamento e validação de configuração |
| `logging/` | Logs centralizados e sanitizados |
| `validation/` | Validações reutilizáveis |
| `errors/` | Tratamento compartilhado de erros |

Não deverão ser criadas abstrações genéricas sem necessidade comprovada.

# 4. Responsabilidade dos principais arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Inicialização da aplicação |
| `cli/app.py` | Configuração da CLI |
| `application/services/execution_service.py` | Coordenar ciclo de execução e resultados |
| `application/services/instance_service.py` | Coordenar ciclo de vida da instância |
| `domain/entities/analysis_run.py` | Representar uma execução |
| `domain/entities/analysis_result.py` | Representar um resultado |
| `infrastructure/persistence/database.py` | Gerenciar conexão SQLite |
| `analysis_run_repository.py` | Persistir e consultar execuções |
| `analysis_result_repository.py` | Persistir e consultar resultados |
| `infrastructure/platform/instance_lock.py` | Implementar bloqueio exclusivo |
| `shared/config/loader.py` | Carregar configuração |
| `shared/logging/logger.py` | Centralizar logs |

# 5. Fluxo arquitetural

O fluxo padrão de uma operação funcional será:

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
Resultado estruturado
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

A aplicação deverá coordenar a execução e a persistência.

O resultado funcional e o resultado da persistência deverão ser tratados separadamente.

Uma falha no SQLite não deverá transformar automaticamente uma operação funcional bem-sucedida em uma operação funcional com falha.

As operações de HISTORY deverão consultar e exportar registros sem criar novos `AnalysisRun`.

# 6. Ciclo de vida da aplicação

O ciclo de vida deverá seguir esta sequência:

```text
Inicialização
     |
     v
Gerar instance_id
     |
     v
Adquirir bloqueio exclusivo
     |
     +---- Falha ----> Impedir execução
     |
     v
Inicializar infraestrutura
     |
     v
Recuperar registros RUNNING anteriores
     |
     v
Marcar registros como INTERRUPTED
     |
     v
Disponibilizar comandos funcionais
     |
     v
Encerramento
     |
     v
Liberar bloqueio
```

O bloqueio deverá ser mantido enquanto a instância estiver ativa.

A identificação de uma instância não deverá depender exclusivamente do PID.

O fluxo deverá ser validado em Windows e Linux.

# 7. Organização dos testes

Os testes deverão acompanhar a organização funcional e arquitetural.

## 7.1. `tests/unit/`

Verifica componentes isoladamente.

Exemplos:

- Cálculo SHA-256.
- Parsing de URLs.
- Geração de senhas.
- Identificação de assinaturas.
- Validação de arquivos.
- Filtros de processos.

## 7.2. `tests/integration/`

Verifica a comunicação entre componentes.

Exemplos:

- Execução de casos de uso com persistência.
- Associação entre execução e resultado.
- Consulta e exportação de histórico.
- Recuperação de execuções interrompidas.
- Tratamento de falhas de persistência.

## 7.3. `tests/cli/`

Verifica comandos, argumentos, saídas e códigos de retorno.

## 7.4. `tests/security/`

Verifica os controles definidos em `SEGURANCA.md`.

## 7.5. `tests/platform/`

Verifica particularidades do sistema operacional.

Exemplos:

- Bloqueio exclusivo.
- Liberação de bloqueio.
- Recuperação após encerramento inesperado.
- Compatibilidade Windows/Linux.

## 7.6. `conftest.py`

Armazena fixtures compartilhadas:

- Banco SQLite temporário.
- Diretórios temporários.
- Arquivos de teste.
- Dados simulados.
- Dependências substituídas por mocks.

# 8. Configuração e arquivos auxiliares

## 8.1. `pyproject.toml`

Centraliza:

- Metadados do projeto.
- Dependências.
- Configuração do ambiente de desenvolvimento.
- Configuração do pytest.
- Configuração de cobertura.

## 8.2. `.gitignore`

Deverá impedir o versionamento de arquivos locais e temporários, como:

- Ambientes virtuais.
- Cache Python.
- Banco SQLite local.
- Logs.
- Arquivos temporários.
- Configurações locais com informações sensíveis.

## 8.3. Configuração TOML

O arquivo TOML será opcional.

A precedência será:

1. Padrões internos.
2. Configuração TOML.
3. Argumentos explícitos da CLI.

A ausência do arquivo deverá ser permitida.

Um arquivo inválido deverá gerar erro claro, sem ignorar silenciosamente configurações incorretas.

## 8.4. Banco de dados

O SQLite será armazenado localmente.

O banco real não deverá ser incluído no repositório.

A estrutura inicial será mantida em SQL versionado.

O histórico não deverá possuir exclusão automática no MVP.

# 9. Dependências entre camadas

As dependências deverão respeitar os seguintes princípios:

1. A CLI depende da aplicação.
2. A aplicação coordena os casos de uso.
3. Os módulos funcionais não dependem da CLI.
4. Os módulos funcionais não acessam diretamente o SQLite.
5. O domínio não depende da infraestrutura.
6. A infraestrutura implementa os contratos utilizados pela aplicação.
7. Os serviços compartilhados não concentram regras de negócio.
8. Não devem existir dependências circulares.

# 10. Convenções de nomenclatura

| Elemento | Convenção | Exemplo |
|---|---|---|
| Diretórios | snake_case | `application/` |
| Arquivos Python | snake_case | `analyze_file.py` |
| Classes | PascalCase | `AnalysisRun` |
| Funções | snake_case | `calculate_hash()` |
| Constantes | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| Testes | `test_` + nome | `test_hash_calculator.py` |

Os nomes deverão representar claramente a responsabilidade dos componentes.

# 11. Implementação incremental

A estrutura deverá ser criada progressivamente conforme o backlog.

| Sprint | Estrutura principal |
|---|---|
| Sprint 1 | `cli/`, `application/`, `shared/` e gerenciamento de instância |
| Sprint 2 | `domain/` e `infrastructure/persistence/` |
| Sprint 3 | `modules/file/` e `modules/hash/` |
| Sprint 4 | `modules/password/`, `modules/url/` e `modules/network/` |
| Sprint 5 | `modules/process/`, `modules/history/` e comandos de histórico |
| Sprint 6 | Ampliação de `tests/`, validação de segurança e compatibilidade |

A criação de diretórios e arquivos deverá acompanhar a implementação real.

Não criar arquivos vazios apenas para reproduzir o mapa.

# 12. Itens técnicos sujeitos a validação

| ID | Item | Situação |
|---|---|---|
| MAP-001 | Estratégia de migrations SQLite | Estrutura SQL inicial prevista; evolução do esquema deverá ser definida conforme necessidade |
| MAP-002 | Localização do TOML | Definir durante a implementação |
| MAP-003 | Contrato de execução | Estrutura geral definida; detalhes deverão seguir os contratos da aplicação |
| MAP-004 | Falha na persistência | Separação entre resultado funcional e histórico definida |
| MAP-005 | Bloqueio multiplataforma | Contrato previsto; implementação deverá ser validada em Windows e Linux |
| MAP-006 | Automação de testes | Workflow previsto; validar antes de torná-lo obrigatório |
| MAP-007 | Limites operacionais | Valores numéricos pendentes de testes e refinamento |

Esses pontos não autorizam a inclusão de funcionalidades novas no MVP.

# 13. Estado do documento

| Critério | Situação |
|---|---|
| Estrutura geral | Definida |
| Organização das camadas | Definida |
| Sete módulos funcionais | Definidos |
| Responsabilidades | Definidas |
| Entidades do domínio | Definidas |
| Persistência | Mapeada |
| Controle de instância | Mapeado |
| Recuperação de execuções | Mapeada |
| Organização dos testes | Definida |
| Configuração TOML | Definida |
| Dependências entre camadas | Definidas |
| Implementação incremental | Planejada |
| Revisão cruzada | Pendente |