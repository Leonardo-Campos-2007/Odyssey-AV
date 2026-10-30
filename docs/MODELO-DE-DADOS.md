# MODELO-DE-DADOS.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP

---

# 1. Visão geral

O modelo de domínio do Odyssey AV foi projetado para manter a persistência simples, modular e compatível com os sete módulos definidos para o MVP.

Como o sistema é uma ferramenta local de diagnóstico e análise de segurança, não serão necessárias entidades de usuários, contas, permissões comerciais ou organizações.

O modelo utilizará inicialmente duas entidades persistentes:

- `AnalysisRun`
- `AnalysisResult`

---

# 2. Entidades principais

## 2.1. AnalysisRun

Representa uma execução de uma ferramenta do Odyssey AV.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| id | UUID ou identificador textual | Sim | Identificador único da execução |
| module | String/Enum | Sim | Módulo executado |
| command | String | Sim | Comando utilizado |
| status | Enum | Sim | Estado da execução |
| started_at | DateTime | Sim | Início da execução |
| finished_at | DateTime | Não | Encerramento da execução |
| duration_ms | Integer | Não | Duração em milissegundos |
| summary | String | Não | Resumo do resultado |

### Responsabilidades

- Identificar uma execução.
- Registrar qual módulo foi utilizado.
- Controlar o estado da execução.
- Registrar início, término e duração.
- Permitir consultas posteriores ao histórico.

### Estados

| Estado | Significado |
|---|---|
| RUNNING | Execução em andamento |
| SUCCESS | Execução concluída |
| PARTIAL | Execução concluída parcialmente |
| FAILED | Execução com falha |

## 2.2. AnalysisResult

Representa um resultado produzido durante uma execução.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| id | UUID ou identificador textual | Sim | Identificador único do resultado |
| analysis_run_id | UUID ou identificador textual | Sim | Referência à execução |
| result_type | String/Enum | Sim | Tipo de resultado |
| status | Enum | Sim | Estado do resultado |
| data | JSON | Não | Dados específicos do módulo |
| message | String | Não | Mensagem descritiva |
| created_at | DateTime | Sim | Data de criação |

### Responsabilidades

- Armazenar resultados produzidos pelos módulos.
- Manter os resultados associados à execução correspondente.
- Permitir que cada módulo produza informações diferentes sem exigir novas tabelas.
- Disponibilizar os dados para consultas e exportações.

O campo `data` armazenará dados estruturados em JSON, respeitando os limites de privacidade do projeto.

---

# 3. Relacionamento entre entidades

O modelo possui um relacionamento de um para muitos (1:N).

```text
AnalysisRun (1)
      |
      | 1:N
      |
      v
AnalysisResult (N)
```

Uma execução pode produzir vários resultados.

Cada resultado pertence obrigatoriamente a uma única execução.

### Regras de integridade

- `AnalysisRun.id` será chave primária.
- `AnalysisResult.id` será chave primária.
- `AnalysisResult.analysis_run_id` será chave estrangeira.
- Um resultado não poderá existir sem uma execução correspondente.
- A exclusão de uma execução deverá remover seus resultados associados, caso a exclusão seja necessária.
- O histórico não terá exclusão automática no MVP.

---

# 4. Enumerações

Para manter consistência entre os módulos, serão utilizados valores controlados.

## 4.1. Module

| Valor | Módulo |
|---|---|
| FILE | Análise de arquivos |
| HASH | Hash |
| NETWORK | Diagnóstico de rede |
| PASSWORD | Ferramentas de senha |
| URL | Análise de URL |
| PROCESS | Monitoramento de processos |
| HISTORY | Histórico e relatórios |

## 4.2. ExecutionStatus

- `RUNNING`
- `SUCCESS`
- `PARTIAL`
- `FAILED`

## 4.3. ResultStatus

- `SUCCESS`
- `WARNING`
- `ERROR`
- `INFO`

O `ResultStatus` descreve cada resultado individualmente, enquanto `ExecutionStatus` representa a execução completa.

---

# 5. Objetos internos dos módulos

Nem toda estrutura de dados precisa ser uma entidade persistente.

Para evitar tabelas desnecessárias, serão utilizados objetos internos específicos.

| Objeto | Módulo | Finalidade |
|---|---|---|
| FileMetadata | FILE | Metadados do arquivo |
| HashReference | HASH | Referência local para comparação de hashes |
| NetworkCheck | NETWORK | Resultado de verificações de rede |
| PasswordEvaluation | PASSWORD | Avaliação temporária de senha |
| UrlFinding | URL | Indicadores encontrados na URL |
| ProcessSnapshot | PROCESS | Informações coletadas de processos |
| SecurityFinding | Transversal | Representação estruturada de um achado |

Esses objetos existirão durante o processamento e não exigirão tabelas próprias no SQLite.

**Observação:** referências de hash poderão ser armazenadas localmente em uma estrutura simples, caso o gerenciamento dessas referências exija persistência. Uma tabela adicional somente será criada se houver necessidade comprovada.

---

# 6. Regras de persistência

1. Cada execução deverá possuir um identificador único.
2. Os resultados deverão ser vinculados à execução correspondente.
3. Os dados específicos de cada módulo serão armazenados em JSON.
4. Senhas geradas ou avaliadas nunca serão persistidas.
5. O conteúdo integral dos arquivos analisados não será armazenado.
6. Dados sensíveis desnecessários não deverão entrar no histórico.
7. Execuções parciais e malsucedidas também poderão ser consultadas.
8. Datas deverão ser armazenadas em formato consistente, preferencialmente UTC.
9. O SQLite utilizará chaves estrangeiras e consultas parametrizadas.
10. A exportação deverá respeitar os dados efetivamente disponíveis e os limites de privacidade.

---

# 7. Estrutura conceitual do banco

O banco terá inicialmente duas tabelas.

```sql
CREATE TABLE analysis_runs (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    command TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    duration_ms INTEGER,
    summary TEXT
);

CREATE TABLE analysis_results (
    id TEXT PRIMARY KEY,
    analysis_run_id TEXT NOT NULL,
    result_type TEXT NOT NULL,
    status TEXT NOT NULL,
    data TEXT,
    message TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (analysis_run_id)
        REFERENCES analysis_runs(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_analysis_runs_module
    ON analysis_runs(module);

CREATE INDEX idx_analysis_runs_started_at
    ON analysis_runs(started_at);

CREATE INDEX idx_analysis_results_run_id
    ON analysis_results(analysis_run_id);
```

> **Nota:** este é um esquema conceitual inicial. Ainda não representa uma migration ou implementação executada.

---

# 8. Decisões de modelagem

| Identificador | Decisão | Justificativa |
|---|---|---|
| DOM-001 | Duas entidades persistentes | Evitar complexidade desnecessária |
| DOM-002 | Relacionamento 1:N | Uma execução pode gerar vários resultados |
| DOM-003 | Dados específicos em JSON | Evitar tabelas diferentes para cada módulo |
| DOM-004 | Objetos internos não persistentes | Separar processamento de armazenamento |
| DOM-005 | Histórico local no SQLite | Simplicidade e independência de servidores |

---

# 9. Estado do documento

| Critério | Situação |
|---|---|
| Entidades | Definidas |
| Atributos | Definidos |
| Relacionamentos | Definidos |
| Cardinalidades | Definidas |
| Estados | Definidos |
| Responsabilidades | Definidas |
| Regras de unicidade | Definidas |
| Persistência | Estruturada conceitualmente |

O modelo deverá ser confrontado com os requisitos funcionais e com os casos de uso dos sete módulos antes da implementação.

