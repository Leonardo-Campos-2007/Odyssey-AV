# PROGRESSO.md

**Projeto:** Odyssey AV
**Escopo:** MVP
**Atualizado em:** 31/10/2026

Este documento registra o que já foi implementado, testado e validado, e descreve as próximas fases. Ele serve como guia de progresso, não como roteiro rígido. A documentação de `docs/` orienta o caminho, mas as decisões de implementação são tomadas durante o desenvolvimento.

---

## 1. Ambiente e infraestrutura

| Item | Situação | Observações |
|---|---|---|
| Repositório no GitHub | Concluído | `Leonardo-Campos-2007/Odyssey-AV`, branch `main` |
| Ambiente local | Concluído | Windows, Python 3.13.2, instalação editável com `pip install -e ".[dev]"` |
| CI (GitHub Actions) | Concluído e verde | Matriz Ubuntu e Windows × Python 3.11 e 3.13 |
| Custo do CI | Verificado | Consumo dentro da cota gratuita, com valor faturado em $0 |

**Pendências técnicas da infraestrutura:**

- Atualizar as actions para versões compatíveis com Node 24 (`checkout` e `setup-python`).
- Fixar `ubuntu-latest` em `ubuntu-24.04`, para evitar mudança de ambiente sem aviso.
- Empacotar os arquivos `.sql` no `pyproject.toml` (`package-data`), necessário apenas para gerar um pacote distribuível.

---

## 2. Sprint 1: Fundação e ciclo de vida (concluída)

### 2.1. Arquivos implementados

| Arquivo | Função | Histórias e tarefas |
|---|---|---|
| `pyproject.toml` | Metadados, dependências, entry point `odyssey`, configuração do pytest e da cobertura | US-001 (TEC-001, TEC-002) |
| `.gitignore` | Impede versionar ambientes, caches, bancos locais, logs e configurações sensíveis | Política de repositório |
| `src/odyssey_av/main.py` | Ponto de entrada; converte erros em mensagem segura e código de saída | US-001 (TEC-005, TEC-006) |
| `shared/errors/handlers.py` | `ExitCode` (0 a 4), exceções da aplicação e `report_error` | TEC-006, TEC-010, TEC-081 |
| `shared/config/loader.py` | Configuração em três camadas: padrões, TOML opcional e argumentos da CLI | US-002 (TEC-007, TEC-008, TEC-082) |
| `shared/logging/logger.py` | Logger em `stderr` com filtro que oculta segredos | US-002 (TEC-009, TEC-083) |
| `infrastructure/platform/instance_lock.py` | Bloqueio exclusivo: `fcntl.flock` no Linux e `msvcrt.locking` no Windows | US-017 Etapa A (TEC-085, TEC-087) |
| `application/services/instance_service.py` | Gera `instance_id` (UUID4) por inicialização e controla o bloqueio | US-017 Etapa A (TEC-084, TEC-086, TEC-089) |
| `cli/app.py` | Aplicação Typer com opções globais `--json` e `--log-level` | US-001 (TEC-003, TEC-080) |
| `.github/workflows/tests.yml` | Pipeline de testes em Windows e Linux | TEC-076, TEC-077 (antecipado) |

### 2.2. Testes da Sprint 1

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/conftest.py` | Fixtures | Isolamento de lock, configuração, ambiente e logger |
| `tests/unit/test_config_loader.py` | 11 | TU-CONFIG-001 a 007 e casos extras |
| `tests/platform/test_instance_lock.py` | 6 | TCO-001 a TCO-004, com encerramento forçado de processo real |
| `tests/unit/test_instance_service.py` | 9 | TCO-006 e integração do serviço com o bloqueio |

### 2.3. Validações realizadas

- Ajuda da CLI exibida corretamente, com `--json` e `--log-level`.
- `odyssey --log-level verbose` retorna mensagem de erro e código de saída `2`.
- `odyssey` sem argumentos exibe a ajuda e retorna código `0`.
- Logs ocultam valores de `senha` e `token`.
- Lock impede uma segunda instância e é liberado após o `release`.

---

## 3. Sprint 2: Persistência e recuperação (em andamento)

### 3.1. Arquivos implementados

| Arquivo | Função | Referência |
|---|---|---|
| `infrastructure/persistence/database.py` | Conexão SQLite com `PRAGMA foreign_keys = ON` verificado; migrations controladas por `user_version` | RNF-007, MODELO §11 e §12 |
| `infrastructure/persistence/migrations/001_initial_schema.sql` | Tabelas `analysis_runs` e `analysis_results`, com `CHECK` e índices | MODELO §11 |
| `domain/enums/` | `ExecutionStatus`, `ResultStatus`, `Module` e `OperationalState` (`StrEnum`) | MODELO §4 |
| `domain/entities/` | `AnalysisRun` e `AnalysisResult` (dataclasses, UUID gerado, datas com fuso) | MODELO §2 |
| `infrastructure/persistence/repositories/analysis_run_repository.py` | `add`, `update_status`, `get` e `interrupt_runs_from_other_instances` | TB-001, TR-005, TI-013 |
| `infrastructure/persistence/repositories/analysis_result_repository.py` | `add` e `list_by_run`, com `PersistenceError` para resultado órfão | TB-002, TB-003 |
| `application/services/recovery_service.py` | `start_session`: recuperação e definição de `NORMAL` ou `DEGRADED` | US-017 Etapa B, RF-030, RF-033 |
| `shared/errors/handlers.py` (ampliado) | Acrescentada `PersistenceError` | Tratamento de erros |

### 3.2. Testes da Sprint 2 até o momento

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/integration/test_database.py` | 6 | Chaves estrangeiras, migration, reabertura, integridade e falha de caminho |
| `tests/integration/test_repositories.py` | 12 | TB-001 a TB-003, atualização de estado, cascata e consistência enum × `CHECK` |
| `tests/integration/test_recovery.py` | 5 | Interrupção de RUNNING anterior, falha com `TRIGGER` e recuperação na inicialização seguinte |

**Resultado total:** 49 testes passando em `pytest`, incluindo os 26 da Sprint 1.

### 3.3. Decisões de arquitetura consolidadas

- Estado `DEGRADED` nasce somente de falha na recuperação durante a inicialização. Falha isolada de gravação em `NORMAL` não altera o estado.
- A recuperação é uma única instrução `UPDATE`, portanto atômica.
- Em `DEGRADED`, a conexão é fechada e não há gravação nem consulta HISTORY.
- Repositórios recebem a conexão e não controlam seu ciclo de vida.
- Violação de chave estrangeira e falhas de E/S são convertidas em `PersistenceError`.

### 3.4. Pendências da Sprint 2

- Ligar o `main.py` à sessão: adquirir o lock, chamar `start_session`, disponibilizar a sessão no contexto da CLI e liberar recursos ao sair.
- Comando `odyssey status` para exibir estado, `instance_id` e execuções recuperadas.
- Tratar a condição `DEGRADED` na CLI, com aviso ao usuário.
- Teste de integração ponta a ponta do `main.py`.

---

## 4. Próximas fases do MVP

### Fase A: Fechar a Sprint 2 (próximo passo)

1. Integrar o `main.py` com o lock e com `start_session`.
2. Criar `odyssey status`, que não gera registros de execução.
3. Testar o fluxo completo: lock, recuperação, estado e liberação.
4. Validar no terminal real e no CI.

### Fase B: Primeiro fluxo funcional completo (`hash calculate`)

1. Implementar `modules/hash/calculator.py`, com SHA-256 em blocos (RNF-008).
2. Criar `application/use_cases/calculate_hash.py`, que orquestra a operação.
3. Implementar `application/services/execution_service.py`, que:
   - registra `RUNNING` antes da operação;
   - persiste o resultado e o estado final;
   - separa o resultado funcional da falha de persistência (código `3` quando aplicável).
4. Criar o comando `cli/commands/hash.py`.
5. Testes: TU-HASH-001 a 008, TI-002, TI-008 e TI-026, além dos cenários de código de saída (TC-CLI-002, TC-CLI-013).

### Fase C: Comparação de hashes e modo `DEGRADED` na CLI

1. Implementar `hash compare` com `MATCH`, `MISMATCH` e `NO_REFERENCE` (TU-HASH-003 a 006).
2. Na CLI, operar em `DEGRADED` com aviso claro e código `3` (TC-CLI-016, TI-015 a TI-020).
3. Confirmar que `HISTORY` é recusado em `DEGRADED` (TI-021, TU-HIST-016 a 018).

### Fase D: Ferramentas locais de baixo risco

Ordem sugerida, do menor para o maior risco:

1. **PASSWORD** (geração com `secrets` e avaliação local, com entrada oculta). Restrições: nunca persistir senha e nunca aceitar senha como argumento.
2. **URL** (parsing e normalização, sem nenhuma requisição automática).
3. **FILE** (assinaturas PE, ELF, PDF, PNG, JPEG, ZIP e GZIP, com tratamento de links simbólicos e arquivos especiais). Atenção ao TOCTOU: abrir o arquivo e verificar o descritor com `fstat`, usando `O_NOFOLLOW` quando disponível.

### Fase E: Ferramentas de rede e processos

1. **NETWORK**: DNS e conectividade com timeout. Definir antes os alvos padrão e o serviço de IP público, que ainda estão em aberto no `API.md`. Testar com respostas simuladas, sem comunicação real no CI.
2. **PROCESS**: listagem e filtros com `psutil`, em modo somente leitura, tratando processos inacessíveis e encerrados durante a consulta.

### Fase F: HISTORY

1. Consulta com filtros por módulo, período e estado, com paginação e consultas parametrizadas (TU-HIST-003 a 005).
2. `history show` para consultar resultados de uma execução.
3. Exportação em JSON e CSV, sem senhas nem segredos, com limites de volume (TU-HIST-006 a 010).
4. Garantia de que consultas e exportações não criam `AnalysisRun` (TU-HIST-009, TU-HIST-010, TID-001).

### Fase G: Qualidade e segurança (Sprint 6)

1. Testes de segurança dos controles de `SEGURANCA.md` (TS-001 a 025).
2. Testes de compatibilidade Windows e Linux, incluindo o modo `DEGRADED` nas duas plataformas.
3. Revisão de cobertura, com meta de 80% nas regras e serviços.
4. Revisão final da rastreabilidade entre CT, testes e tarefas.

---

## 5. Decisões em aberto

| ID | Assunto | Quando decidir |
|---|---|---|
| D-01 | Sintaxe de opções de NETWORK, PASSWORD e HISTORY | Antes da Fase D |
| D-02 | Alvos de conectividade, domínio DNS padrão e serviço de IP público | Antes da Fase E |
| D-03 | Valores numéricos dos limites operacionais (RNF-015) | Ao implementar cada módulo |
| D-04 | Regra de normalização do campo `command` | Antes da Fase B |
| D-05 | Caminho do arquivo no `command`: completo, relativo ou omitido | Antes da Fase B |
| D-06 | `hash compare` sem `--reference`: erro de uso ou `NO_REFERENCE` | Antes da Fase C |
| D-07 | Fixar `ubuntu-24.04` no CI e atualizar actions | Quando for conveniente |

---

## 6. Princípios que guiam o desenvolvimento

- Documentação orienta, não engessa. Quando a implementação revelar um caminho melhor, o documento é ajustado.
- Cada arquivo é entregue, validado e testado antes do próximo.
- Testes de integração usam SQLite e lock reais, em diretórios temporários.
- Nenhum dado sensível aparece em logs, histórico ou mensagens de erro.
- Nenhuma funcionalidade fora do escopo do MVP é implementada.