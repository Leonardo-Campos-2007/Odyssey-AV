# PROGRESSO.md

**Projeto:** Odyssey AV
**Escopo:** MVP
**Atualizado em:** 01/11/2026

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
| Fase D: PASSWORD (`generate` e `evaluate`) | Concluída e com privacidade verificada |
| Fase D: URL (`analyze`) | Concluída e com privacidade verificada. Commit e CI pendentes |
| Fase D: FILE | Próxima (aguardando decisões D-17, D-18 e D-19) |
| Fase E: NETWORK e PROCESS | Planejada |
| Fases F e G | Planejadas |

**Suíte de testes:** 177 casos coletados, 176 aprovados e 1 pulado (teste de link simbólico, que exige privilégio no Windows).

---

## 2. Ambiente e infraestrutura

| Item | Situação | Observações |
|---|---|---|
| Repositório no GitHub | Concluído | `Leonardo-Campos-2007/Odyssey-AV`, branch `main` |
| Ambiente local | Concluído | Windows, Python 3.13.2, instalação com `pip install -e ".[dev]"` |
| CI (GitHub Actions) | Concluído e verde | Matriz Ubuntu 24.04 e Windows × Python 3.11 e 3.13 |
| Custo do CI | Verificado | Consumo dentro da cota gratuita, valor faturado em $0 |

**Pendências técnicas da infraestrutura:**

- Atualizar as actions `actions/checkout` e `actions/setup-python` para versões compatíveis com Node 24 (aviso do GitHub).
- Empacotar os arquivos `.sql` no `pyproject.toml` (`package-data`). Necessário apenas para gerar um pacote distribuível.
- Fixar `ubuntu-latest` em `ubuntu-24.04` (D-07). O workflow já usa a versão fixa na matriz de Linux.

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
| `modules/hash/calculator.py` | SHA-256 em blocos de 1 MiB, com `O_NOFOLLOW` no Linux, verificação de tipo por `fstat` no descritor aberto antes de qualquer leitura, e comparação com referência |
| `application/services/execution_service.py` | Registra `RUNNING`, executa a operação, grava resultado e estado final, e calcula o código de saída pela precedência do `API.md` |
| `application/use_cases/calculate_hash.py` | Caso de uso do HASH, com comando normalizado `hash calculate <nome do arquivo>` |
| `cli/commands/hash.py` | Comando `odyssey hash`, com saída textual e JSON |

### 6.2. Testes da Fase B

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/unit/test_hash_calculator.py` | 10 (1 pulado no Windows) | TU-HASH-001 a 008, diretório e link simbólico |
| `tests/integration/test_hash_execution.py` | 7 | Sucesso, divergência com aviso, falha de arquivo, referência malformada, `DEGRADED`, falha de gravação inicial e precedência de falha |
| `tests/cli/test_hash_command.py` | 5 | Saída textual, JSON, código `3` em `DEGRADED`, código `1` para arquivo ausente e erro de referência |

**Observação:** o CI em Linux revelou que o teste de diretório dependia da plataforma. A correção verifica o tipo com `fstat` antes de criar o objeto de arquivo. Ambos os sistemas passaram.

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

## 8. Fase D: PASSWORD e URL

### 8.1. Arquivos de PASSWORD

| Arquivo | Função |
|---|---|
| `modules/password/generator.py` | Geração com `secrets`, comprimento de 8 a 128 (provisório) e um caractere de cada conjunto habilitado garantido |
| `modules/password/evaluator.py` | Avaliação local por pontuação, com classificação em quatro níveis; o resultado não contém a senha |
| `application/use_cases/generate_password.py` | Caso de uso de geração. Registra apenas comprimento e conjuntos |
| `application/use_cases/evaluate_password.py` | Caso de uso de avaliação. Registra apenas indicadores |
| `cli/commands/password.py` | `generate` com `--length` e `--no-*`; `evaluate` com entrada oculta, recusado sem terminal interativo |
| `cli/formatting.py` | Rotulagem compartilhada do histórico, usada por todos os comandos |

### 8.2. Arquivos de URL

| Arquivo | Função |
|---|---|
| `modules/url/analyzer.py` | Decomposição com `urllib.parse`, normalização, indicadores de atenção e `to_record`, que define o que é persistido |
| `application/use_cases/analyze_url.py` | Caso de uso. Registra apenas componentes e códigos de indicadores |
| `cli/commands/url.py` | Comando `odyssey url analyze`, com aviso de que indicadores não são confirmação de ameaça |

### 8.3. Testes da Fase D

| Arquivo de teste | Casos | Cobertura |
|---|---|---|
| `tests/unit/test_password_generator.py` | 13 | TU-PASS-001, 002 e 005, conjuntos, limites e aleatoriedade |
| `tests/unit/test_password_evaluator.py` | 14 | TU-PASS-003, 004 e 008, classificação, repetições e ausência da senha nos indicadores |
| `tests/integration/test_password_execution.py` | 5 | Geração: senha fora do histórico, apenas metadados gravados, `DEGRADED` |
| `tests/integration/test_password_evaluate.py` | 7 | Avaliação: senha fora do histórico, apenas indicadores, senha vazia, `DEGRADED` |
| `tests/cli/test_password_generate.py` | 5 | Saída textual, JSON com aviso em `stderr`, `--no-symbols`, erro de comprimento e `DEGRADED` |
| `tests/cli/test_password_evaluate.py` | 5 | Saída sem a senha, JSON, recusa sem terminal sem leitura da senha, senha vazia e `DEGRADED` |
| `tests/unit/test_url_analyzer.py` | 30 | TU-URL-001 a 008, normalização, indicadores, credenciais, limite de tamanho e ausência de rede |
| `tests/integration/test_url_execution.py` | 6 | Registro como `url analyze`, credenciais e query fora do histórico, status de resultado, entrada inválida e `DEGRADED` |
| `tests/cli/test_url_analyze.py` | 6 | Saída textual, JSON, aviso de indicador, credenciais omitidas, entrada inválida e `DEGRADED` |

**Total da Fase D:** 91 testes novos (49 de PASSWORD e 42 de URL).

### 8.4. Validações no terminal real

**PASSWORD**

| Comando | Resultado | Código |
|---|---|---|
| `password generate` | Senha de 16 caracteres, histórico registrado | `0` |
| `password generate --length 24 --no-symbols` | Senha sem símbolos | `0` |
| `--json password generate` | JSON com aviso em `stderr` | `0` |
| `password generate --length 3` | Comprimento inválido | `2` |
| `password evaluate` (digitação oculta) | Força, pontuação e indicadores, sem a senha | `0` |
| `"Senha123" \| password evaluate` | Recusa por falta de terminal interativo | `2` |

**URL**

| Comando | Resultado | Código |
|---|---|---|
| `url analyze "https://exemplo.com/caminho?x=1"` | URL normalizada, sem indicadores | `0` |
| `url analyze "http://192.168.0.1/"` | Indicador de endereço IP | `0` |
| `url analyze "https://usuario:SenhaTeste@exemplo.com/"` | Credenciais presentes, valores omitidos | `0` |
| `url analyze "exemplo.com"` | Esquema ausente | `2` |

### 8.5. Verificação de privacidade no banco real (concluída)

Foi feita verificação manual no arquivo `%LOCALAPPDATA%\odyssey-av\history.db`, com consultas no DB Browser for SQLite:

- **PASSWORD:** a senha de teste não aparece em `analysis_runs` nem em `analysis_results`. A execução `password evaluate` foi confirmada no histórico, o que torna o resultado vazio válido.
- **URL:** o termo de teste das credenciais (`SenhaTeste`) não aparece em nenhuma das duas tabelas, mesmo com a execução `url analyze` registrada.

Consulta usada, com o termo trocado a cada teste:

```sql
SELECT 'analysis_runs' AS tabela, id, command, summary
FROM analysis_runs
WHERE command LIKE '%TERMO%' OR summary LIKE '%TERMO%'
UNION ALL
SELECT 'analysis_results', id, result_type, message
FROM analysis_results
WHERE data LIKE '%TERMO%' OR message LIKE '%TERMO%';
```

### 8.6. Pendências desta fase

- Commit e push de PASSWORD e URL, com CI verde nos quatro jobs.
- Os limites provisórios de URL (`MAX_URL_LENGTH` = 2048, `MAX_HOST_LABELS` = 4 e `MAX_HYPHENS_IN_HOST` = 3) e de senha (8 a 128) entram na revisão do D-03.

---

## 9. Decisões tomadas

| ID | Decisão | Situação |
|---|---|---|
| D-01 | Sintaxe de PASSWORD: `generate` com `--length` (padrão 16) e flags `--no-*`, com todos os conjuntos incluídos por padrão. `evaluate` com entrada oculta, recusada quando `stdin` não é terminal. A senha gerada aparece no JSON, com aviso no `stderr` de que não é armazenada | Resolvido. `API.md`, seção 4.4, atualizado |
| D-04 | Campo `command` é normalizado, com nome da operação e nome do arquivo | Resolvido |
| D-05 | Só o nome do arquivo entra no `command`, sem diretórios, para não expor dados pessoais | Resolvido |
| D-06 | `hash compare` exige `--reference`. `NO_REFERENCE` existe somente no `calculate` | Resolvido |
| D-08 | Links simbólicos são recusados no HASH, como no FILE | Resolvido |
| D-09 | `hash compare` retorna `1` em divergência. `hash calculate` retorna `0` e informa a divergência na saída | Resolvido (opção A). `API.md`, seção 6, atualizado |
| D-14 | Critérios de `password evaluate`: pontuação por comprimento (0 a 2), por conjuntos presentes (0 a 4) e penalidade de 1 ponto para repetições ou sequências simples. Classificação em quatro níveis: muito fraca, fraca, razoável e forte | Resolvido. Penalidade de repetição equivale a descer um nível |
| D-15 | URL: o histórico guarda somente componentes (esquema, host, porta, caminho, presença de query e fragmento, presença de credenciais e códigos de indicadores). Credenciais, valores de query e fragmento não são gravados. O `command` é `url analyze`, sem a URL | Resolvido |
| D-16 | URL sem esquema ou sem host é rejeitada com código `2`. Esquemas como `javascript:` e `mailto:` não são analisados | Resolvido |

---

## 10. Pendências de documentação

### 10.1. Concluídas

| ID | Pendência | Destino |
|---|---|---|
| DOC-03 | Código `1` para divergência do `hash compare` na tabela de códigos de saída | `API.md`, seção 6 (concluída) |

### 10.2. Abertas

| ID | Pendência | Destino |
|---|---|---|
| DOC-01 | Registrar a limitação de links simbólicos no Windows, porque `os.open` segue o link | `SEGURANCA.md` |
| DOC-02 | Registrar que a gravação do resultado e do estado final ocorre em duas operações, sem transação única. Se a segunda falhar, o registro permanece `RUNNING` até a próxima inicialização | `SEGURANCA.md` e `MODELO-DE-DADOS.md` |
| DOC-04 | Registrar que `odyssey --help` abre o banco e o bloqueio, por consequência da inicialização no `main.py` | `ARQUITETURA.md` |
| DOC-05 | Registrar que a senha permanece em memória até o coletor de lixo liberar a string, pois Python não permite apagá-la de forma garantida | `SEGURANCA.md` |
| DOC-06 | Registrar que caracteres fora dos quatro conjuntos (espaços, acentos) não pontuam na avaliação de senha | `SEGURANCA.md` e `API.md` |
| DOC-07 | Registrar que `password evaluate` depende de terminal interativo, e que os testes simulam o terminal, sem cobrir a digitação oculta real | `TESTES.md` |
| DOC-08 | Registrar a política de persistência de URL (D-15) | `SEGURANCA.md` |
| DOC-09 | Registrar a lista de indicadores, a regra de rejeição (D-16) e a limitação de não decodificar percent-encoding | `API.md`, seção 4.5 |
| DOC-10 | Registrar que o caminho da URL é gravado e pode conter identificadores, como limitação conhecida | `SEGURANCA.md` |

---

## 11. Decisões em aberto

| ID | Assunto | Quando decidir |
|---|---|---|
| D-02 | Alvos de conectividade, domínio DNS padrão e serviço de IP público | Antes da Fase E |
| D-03 | Valores numéricos dos limites operacionais (RNF-015): tamanho de bloco, tempo de rede, quantidade de processos e de registros exportados. Já definidos de forma provisória: comprimento de senha (8 a 128), tamanho de URL (2048), níveis de subdomínio (4) e hífens no domínio (3) | Ao implementar cada módulo |
| D-07 | Fixar `ubuntu-24.04` no CI e atualizar as actions | Quando for conveniente |
| D-12 | Lista de testes de `DEGRADED` para FILE, NETWORK, PASSWORD, URL e PROCESS (TI-015 a TI-020). Concluídos para HASH, HISTORY, PASSWORD e URL | Junto de cada módulo restante |
| D-13 | Sintaxe de NETWORK e HISTORY (filtros, paginação, destino da exportação) | Antes das fases E e F |
| D-17 | FILE: formatos e profundidade da verificação. Proposta: PE verifica `MZ` e a assinatura `PE\0\0` apontada pelo offset `0x3C`; ELF, PDF, PNG, JPEG, ZIP e GZIP por assinatura de cabeçalho | Antes da implementação de FILE |
| D-18 | FILE: regra de divergência. Proposta: só avaliar quando a extensão pertence a uma família conhecida (por exemplo, `.exe` para PE, `.pdf` para PDF). Extensão desconhecida não gera divergência | Antes da implementação de FILE |
| D-19 | FILE: nome do arquivo no histórico. Proposta: gravar extensão, tamanho e formato identificado, sem o nome, para não expor informação pessoal. `command` como `file analyze` | Antes da implementação de FILE |

---

## 12. Próximas fases do MVP

### Fase D: FILE (próxima)

1. **FILE**
   - Leitura apenas do cabeçalho, com tamanho obtido por `fstat`.
   - Aceitar somente arquivos regulares, sem seguir links simbólicos, com verificação de tipo pelo descritor aberto, como no HASH.
   - Assinaturas PE, ELF, PDF, PNG, JPEG, ZIP e GZIP, conforme RF-002.
   - Divergência entre extensão e formato, conforme D-17 e D-18.
   - Histórico conforme D-19.
   - Testes com cabeçalhos sintéticos em diretório temporário, sem binários reais: TU-FILE-001 a 020 e TI-015.

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
3. Revisão de cobertura, com meta de 80% nas regras e serviços. O relatório atual aponta `main.py` em 0% e `database.py` e `instance_lock.py` abaixo de 75%.
4. Revisão final da rastreabilidade entre CT, testes e tarefas.

---

## 13. Princípios que guiam o desenvolvimento

- A documentação orienta, não engessa. Quando a implementação revelar um caminho melhor, o documento é ajustado.
- Cada arquivo é entregue, validado e testado antes do próximo.
- Alterações que tocam arquivos, processos, bloqueio ou caminhos passam pelo CI em Windows e Linux antes de serem consideradas concluídas.
- Testes de integração usam SQLite e lock reais, em diretórios temporários.
- Nenhum dado sensível aparece em logs, histórico ou mensagens de erro. A privacidade é verificada também no arquivo real do banco.
- Nenhuma funcionalidade fora do escopo do MVP é implementada.

---

## 14. Histórico de alterações

| Data | Alteração |
|---|---|
| 31/10/2026 | Sprint 2 concluída; Fases A, B e C concluídas; `hash compare` e guarda de HISTORY em `DEGRADED` |
| 01/11/2026 | Fase D: PASSWORD e URL concluídos e verificados no banco real. Correção da numeração de decisões (D-14 restaurado e DOC-03 movido para concluídas). Inclusão de D-17 a D-19 para FILE |