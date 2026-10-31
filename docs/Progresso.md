# PROGRESSO.md

**Projeto:** Odyssey AV
**Escopo:** MVP
**Atualizado em:** 31/10/2026

Este documento registra o que já foi implementado, testado e validado, e descreve as próximas fases. Ele é um guia de progresso, não um roteiro rígido. A documentação de `docs/` orienta o caminho, mas as decisões de implementação são tomadas durante o desenvolvimento.

---

## 1. Resumo do estado atual

| Área | Situação |
|---|---|
| Sprint 1: Fundação e ciclo de vida | Concluída |
| Sprint 2: Persistência e recuperação | Concluída |
| Fase A: Integração com `main.py` e `odyssey status` | Concluída |
| Fase B: `hash calculate` | Concluída |
| Fase C: `hash compare` e guarda de `HISTORY` em `DEGRADED` | Concluída |
| Fase D: PASSWORD, URL e FILE | Próxima (aguardando decisão D-01) |
| Fases E, F e G | Planejadas |

**Suíte de testes:** 86 casos coletados, 85 aprovados e 1 pulado (teste de link simbólico, que exige privilégio no Windows).

---

## 2. Ambiente e infraestrutura

| Item | Situação | Observações |
|---|---|---|
| Repositório no GitHub | Concluído | `Leonardo-Campos-2007/Odyssey-AV`, branch `main` |
| Ambiente local | Concluído | Windows, Python 3.13.2, instalação com `pip install -e ".[dev]"` |
| CI (GitHub Actions) | Concluído e verde | Matriz Ubuntu e Windows × Python 3.11 e 3.13 |
| Custo do CI | Verificado | Consumo dentro da cota gratuita, valor faturado em $0 |

**Pendências técnicas da infraestrutura:**

- Atualizar as actions `actions/checkout` e `actions/setup-python` para versões compatíveis com Node 24 (aviso do GitHub).
- Fixar `ubuntu-latest` em `ubuntu-24.04`, para evitar mudança de ambiente sem aviso (D-07).
- Empacotar os arquivos `.sql` no `pyproject.toml` (`package-data`). Necessário apenas para gerar um pacote distribuível.

---

## 3. Sprint 1: Fundação e ciclo de vida (concluída)

### 3.1. Arquivos implementados

| Arquivo | Função | Histórias e tarefas |
|---|---|---|
| `pyproject.toml` | Metadados, dependências, entry point `odyssey`, configuração do pytest e da cobertura | US-001 (TEC-001, TEC-002) |
| `.gitignore` | Impede versionar ambientes, caches, bancos locais, logs e configurações sensíveis | Política de repositório |
| `src/odyssey_av/main.py` | Ponto de entrada: lock, sessão, conversão de erros em mensagem segura e código de saída | US-001 (TEC-005, TEC-006) |
| `shared/errors/handlers.py` | `ExitCode` (0 a 4), exceções da aplicação e `report_error` | TEC-006, TEC-010, TEC-081 |
| `shared/config/loader.py` | Configuração em três camadas: padrões, TOML opcional e argumentos da CLI | US-002 (TEC-007, TEC-008, TEC-082) |
| `shared/logging/logger.py` | Logger em `stderr` com filtro que oculta segredos | US-002 (TEC-009, TEC-083) |
| `infrastructure/platform/instance_lock.py` | Bloqueio exclusivo: `fcntl.flock` no Linux e `msvcrt.locking` no Windows | US-017 Etapa A (TEC-085, TEC-087) |
| `application/services/instance_service.py` | Gera `instance_id` (UUID4) por inicialização e controla o bloqueio | US-017 Etapa A (TEC-084, TEC-086, TEC-089) |
| `cli/app.py` | Aplicação Typer com opções globais `--json` e `--log-level` | US-001 (TEC-003, TEC-080) |
| `.github/workflows/tests.yml` | Pipeline de testes em Windows e Linux | TEC-076, TEC-077 (antecipado) |

### 3.2. Testes da Sprint 1

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/conftest.py` | Fixtures | Isolamento de lock, configuração, ambiente e logger |
| `tests/unit/test_config_loader.py` | 11 | TU-CONFIG-001 a 007 e casos extras |
| `tests/platform/test_instance_lock.py` | 6 | TCO-001 a TCO-004, com encerramento forçado de processo real |
| `tests/unit/test_instance_service.py` | 9 | TCO-006 e integração do serviço com o bloqueio |

---

## 4. Sprint 2: Persistência e recuperação (concluída)

### 4.1. Arquivos implementados

| Arquivo | Função | Referência |
|---|---|---|
| `infrastructure/persistence/database.py` | Conexão SQLite com `PRAGMA foreign_keys = ON` verificado; migrations controladas por `user_version` | RNF-007, MODELO §11 e §12 |
| `infrastructure/persistence/migrations/001_initial_schema.sql` | Tabelas `analysis_runs` e `analysis_results`, com `CHECK` e índices | MODELO §11 |
| `domain/enums/` | `ExecutionStatus`, `ResultStatus`, `Module`, `OperationalState` e `ComparisonStatus` (`StrEnum`) | MODELO §4, RN-004 |
| `domain/entities/` | `AnalysisRun` e `AnalysisResult` (dataclasses, UUID gerado, datas com fuso) | MODELO §2 |
| `infrastructure/persistence/repositories/analysis_run_repository.py` | `add`, `update_status`, `get` e `interrupt_runs_from_other_instances` | TB-001, TR-005, TI-013 |
| `infrastructure/persistence/repositories/analysis_result_repository.py` | `add` e `list_by_run`, com `PersistenceError` para resultado órfão | TB-002, TB-003 |
| `application/services/recovery_service.py` | `start_session`: recuperação e definição de `NORMAL` ou `DEGRADED` | US-017 Etapa B, RF-030, RF-033 |
| `application/services/execution_service.py` | Ciclo de execução: registro, operação, resultado, estado final e separação entre resultado funcional e persistência | RN-013, RF-032 |
| `cli/context.py` | `AppContext`, que reúne configuração e sessão para os comandos | Fase A |
| `cli/commands/status.py` | Comando `odyssey status`, sem criação de registros | Fase A |

### 4.2. Testes da Sprint 2

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/integration/test_database.py` | 6 | Chaves estrangeiras, migration, reabertura, integridade e falha de caminho |
| `tests/integration/test_repositories.py` | 12 | TB-001 a TB-003, atualização de estado, cascata e consistência enum × `CHECK` |
| `tests/integration/test_recovery.py` | 5 | Interrupção de RUNNING anterior, falha com `TRIGGER` e recuperação na inicialização seguinte |
| `tests/cli/test_status.py` | 4 | Estados `NORMAL`, `DEGRADED` e saída JSON |

### 4.3. Decisões de arquitetura consolidadas

- O estado `DEGRADED` nasce somente de falha na recuperação durante a inicialização. Falha isolada de gravação em `NORMAL` não altera o estado.
- A recuperação é uma única instrução `UPDATE`, portanto atômica.
- Em `DEGRADED`, a conexão é fechada e não há gravação nem consulta HISTORY.
- Repositórios recebem a conexão e não controlam seu ciclo de vida.
- Violação de chave estrangeira e falhas de E/S são convertidas em `PersistenceError`.
- O lock e a sessão são adquiridos no `main.py`, antes do Typer. Consequência conhecida: `odyssey --help` também abre o banco e o bloqueio. Pode ser revisto se incomodar.

---

## 5. Fase A: Integração com a CLI (concluída)

- `main.py` adquire o lock, abre a sessão, executa a CLI e libera recursos no `finally`, mesmo em caso de erro.
- `odyssey status` mostra estado, `instance_id`, execuções recuperadas e disponibilidade do histórico. Com `--json`, a saída é estruturada.
- Aviso de `DEGRADED` é enviado para `stderr` em qualquer comando.

**Validações no terminal real:** `status` em `NORMAL` retorna código `0`; `--json status` retorna o JSON esperado; `--log-level verbose` retorna código `2`.

---

## 6. Fase B: `hash calculate` (concluída)

### 6.1. Arquivos implementados

| Arquivo | Função |
|---|---|
| `modules/hash/calculator.py` | SHA-256 em blocos de 1 MiB, com `O_NOFOLLOW` no Linux, verificação por `fstat` no descritor aberto e comparação com referência |
| `application/services/execution_service.py` | Registra `RUNNING`, executa a operação, grava resultado e estado final, e calcula o código de saída pela precedência do `API.md` |
| `application/use_cases/calculate_hash.py` | Caso de uso do HASH, com comando normalizado `hash calculate <nome do arquivo>` |
| `cli/commands/hash.py` | Comando `odyssey hash`, com saída textual e JSON |

### 6.2. Testes da Fase B

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/unit/test_hash_calculator.py` | 10 (1 pulado no Windows) | TU-HASH-001, 002, 003, 004, 005, 006, 007, 008, diretório e link simbólico |
| `tests/integration/test_hash_execution.py` | 7 | Sucesso, divergência com aviso, falha de arquivo, referência malformada, `DEGRADED`, falha de gravação inicial e precedência de falha |
| `tests/cli/test_hash_command.py` | 5 | Saída textual, JSON, código `3` em `DEGRADED`, código `1` para arquivo ausente e erro de referência |

---

## 7. Fase C: `hash compare` e guarda de `HISTORY` (concluída)

### 7.1. Arquivos implementados

| Arquivo | Função |
|---|---|
| `application/use_cases/calculate_hash.py` (ampliado) | Adiciona `compare_hash`, que exige referência |
| `cli/commands/hash.py` (ampliado) | Adiciona `odyssey hash compare --reference <sha256>` |
| `cli/commands/history.py` | Guarda de `HISTORY`: recusa em `DEGRADED` com código `1`, sem consultar o banco |

### 7.2. Testes da Fase C

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/cli/test_hash_compare.py` | 7 | `MATCH` com código `0`, `MISMATCH` com código `1`, referência ausente com código `2`, JSON e `DEGRADED` |
| `tests/cli/test_history_guard.py` | 4 | Recusa em `DEGRADED`, ausência de registros, sessão `NORMAL` sem criação de `AnalysisRun` e sessão ausente |

### 7.3. Validações no terminal real

| Comando | Resultado | Código |
|---|---|---|
| `hash compare` com hash correto | `MATCH` | `0` |
| `hash compare` com hash divergente | `MISMATCH` | `1` |
| `hash compare` sem `--reference` | Erro de uso | `2` |
| `hash calculate` com referência divergente | `MISMATCH` | `0` |
| `history list` em `NORMAL` | Não implementado | `1` |

---

## 8. Decisões tomadas

| ID | Decisão | Situação |
|---|---|---|
| D-04 | Campo `command` é normalizado, com nome do operação e nome do arquivo | Resolvido |
| D-05 | Só o nome do arquivo entra no `command`, sem diretórios, para não expor dados pessoais | Resolvido |
| D-06 | `hash compare` exige `--reference`. `NO_REFERENCE` existe somente no `calculate` | Resolvido |
| D-08 | Links simbólicos são recusados no HASH, como no FILE | Resolvido |
| D-09 | `hash compare` retorna `1` em divergência. `hash calculate` retorna `0` e informa a divergência na saída | Resolvido (opção A). Altera o contrato do `API.md`, seção 6 |

---

## 9. Pendências de documentação

| ID | Pendência | Destino |
|---|---|---|
| DOC-01 | Registrar a limitação de links simbólicos no Windows, porque `os.open` segue o link | `SEGURANCA.md` |
| DOC-02 | Registrar que a gravação do resultado e do estado final ocorre em duas operações, sem transação única. Se a segunda falhar, o registro permanece `RUNNING` até a próxima inicialização | `SEGURANCA.md` e `MODELO-DE-DADOS.md` |
| DOC-03 | Incluir o código `1` para divergência do `hash compare` na tabela de códigos de saída | `API.md`, seção 6 |
| DOC-04 | Registrar a efetivação do comportamento de `odyssey --help` abrir o banco e o lock | `ARQUITETURA.md` |

---

## 10. Decisões em aberto

| ID | Assunto | Quando decidir |
|---|---|---|
| D-01 | Sintaxe de PASSWORD: `generate` com `--length` e flags `--no-*`; `evaluate` com entrada oculta e recusa quando `stdin` não é terminal. Inclusão da senha gerada no JSON da saída | Antes da Fase D (aguardando resposta) |
| D-01b | Sintaxe de NETWORK e HISTORY (filtros, paginação, destino da exportação) | Antes das fases E e F |
| D-02 | Alvos de conectividade, domínio DNS padrão e serviço de IP público | Antes da Fase E |
| D-03 | Valores numéricos dos limites operacionais (RNF-015): tamanho de bloco, tempo de rede, quantidade de processos e de registros exportados | Ao implementar cada módulo |
| D-07 | Fixar `ubuntu-24.04` no CI e atualizar as actions | Quando for conveniente |
| D-12 | Lista de testes de `DEGRADED` para FILE, NETWORK, PASSWORD, URL e PROCESS (TI-015 a TI-020) | Junto de cada módulo |

---

## 11. Próximas fases do MVP

### Fase D: Ferramentas locais de baixo risco (próxima)

Ordem, do menor para o maior risco:

1. **PASSWORD**
   - `generate`: geração com `secrets`, parâmetros `--length` e `--no-*`, validação de parâmetros inválidos.
   - `evaluate`: avaliação local, com entrada oculta e recusa quando não há terminal interativo.
   - Restrições: nenhum valor de senha em histórico, logs, mensagens de erro ou `AnalysisResult`. Nenhuma aceitação de senha como argumento.
   - Testes: TU-PASS-001 a 008, TS-003 a 004, TI-009 e TI-018.
2. **URL**: parsing e normalização, sem nenhuma requisição automática. Testes TU-URL-001 a 007, ST-006 e TI-019.
3. **FILE**: assinaturas PE, ELF, PDF, PNG, JPEG, ZIP e GZIP, com tratamento de links simbólicos, arquivos especiais e alteração durante a leitura. Testes TU-FILE-001 a 020 e TI-015.

### Fase E: Ferramentas de rede e processos

1. **NETWORK**: DNS e conectividade com timeout. Depende de D-02. Testes com respostas simuladas, sem comunicação real no CI (TU-NET-001 a 008, TI-017).
2. **PROCESS**: listagem e filtros com `psutil`, em modo somente leitura, tratando processos inacessíveis ou encerrados durante a consulta (TU-PROC-001 a 007, TI-020).

### Fase F: HISTORY completo

1. Consulta com filtros por módulo, período e estado, paginação e consultas parametrizadas (TU-HIST-003 a 005).
2. `history show` para consultar os resultados de uma execução.
3. Exportação em JSON e CSV, sem senhas nem segredos, com limites de volume (TU-HIST-006 a 010).
4. Garantia de que consultas e exportações não criam `AnalysisRun` (TU-HIST-009, TU-HIST-010, TID-001).

### Fase G: Qualidade e segurança (Sprint 6)

1. Testes de segurança dos controles de `SEGURANCA.md` (TS-001 a 025).
2. Testes de compatibilidade Windows e Linux, incluindo o modo `DEGRADED` nas duas plataformas (TPL-001 a 014).
3. Revisão de cobertura, com meta de 80% nas regras e serviços.
4. Revisão final da rastreabilidade entre CT, testes e tarefas.

---

## 12. Princípios que guiam o desenvolvimento

- A documentação orienta, não engessa. Quando a implementação revelar um caminho melhor, o documento é ajustado.
- Cada arquivo é entregue, validado e testado antes do próximo.
- Testes de integração usam SQLite e lock reais, em diretórios temporários.
- Nenhum dado sensível aparece em logs, histórico ou mensagens de erro.
- Nenhuma funcionalidade fora do escopo do MVP é implementada.