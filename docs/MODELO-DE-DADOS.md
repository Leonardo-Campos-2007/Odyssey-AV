# MODELO-DE-DADOS.md

**Projeto:** Odyssey AV  
**Versão:** 2.1  
**Escopo:** MVP  
**Status:** Consolidado para revisão cruzada

---

# 1. Visão geral

O modelo de dados do Odyssey AV foi projetado para manter a persistência simples, modular e compatível com os sete módulos definidos para o MVP.

O sistema será uma ferramenta local de análise e diagnóstico, sem necessidade de entidades relacionadas a usuários, contas, organizações ou autenticação.

O modelo utilizará inicialmente duas entidades persistentes:

- `AnalysisRun`
- `AnalysisResult`

A persistência será realizada em SQLite, utilizando relacionamentos, chaves estrangeiras e consultas parametrizadas.

O modelo deverá atender aos seguintes objetivos:

- Registrar execuções dos módulos.
- Armazenar resultados associados às execuções.
- Permitir consultas e exportações do histórico.
- Diferenciar estados de execução.
- Identificar execuções interrompidas.
- Preservar a privacidade dos dados.
- Evitar estruturas de persistência desnecessárias.
- Preservar a integridade do histórico durante a recuperação de execuções.

# 2. Entidades principais

## 2.1. AnalysisRun

Representa uma execução de uma ferramenta do Odyssey AV.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| id | UUID ou identificador textual | Sim | Identificador único da execução |
| instance_id | UUID | Sim | Identificador da instância responsável |
| module | String/Enum | Sim | Módulo executado |
| command | String | Sim | Nome normalizado do comando |
| status | Enum | Sim | Estado da execução |
| started_at | DateTime | Sim | Data e horário de início |
| finished_at | DateTime | Não | Data e horário de encerramento |
| duration_ms | Integer | Não | Duração em milissegundos |
| summary | String | Não | Resumo sanitizado da execução |

### Responsabilidades

- Identificar uma execução.
- Registrar o módulo utilizado.
- Identificar a instância responsável.
- Controlar o estado da execução.
- Registrar início, término e duração.
- Permitir consultas posteriores ao histórico.
- Possibilitar a identificação de execuções interrompidas.

### Regras

1. Cada execução deverá possuir um identificador único.
2. `instance_id` deverá identificar a instância que iniciou a execução.
3. `command` deverá armazenar o comando normalizado, sem argumentos que possam conter senhas ou outros segredos.
4. `summary` deverá ser sanitizado antes da persistência.
5. O estado deverá refletir o resultado da execução, e não exclusivamente a situação do armazenamento do histórico.

### Estados de execução

| Estado | Significado |
|---|---|
| `RUNNING` | Execução em andamento |
| `SUCCESS` | Execução concluída com sucesso |
| `PARTIAL` | Execução concluída parcialmente |
| `FAILED` | Execução que apresentou falha funcional |
| `INTERRUPTED` | Execução interrompida inesperadamente |

O estado `INTERRUPTED` será utilizado quando a aplicação identificar uma execução anterior que permaneceu em `RUNNING` após encerramento inesperado.

A interrupção não deverá ser classificada automaticamente como falha funcional.

## 2.2. AnalysisResult

Representa um resultado produzido durante uma execução.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| id | UUID ou identificador textual | Sim | Identificador único do resultado |
| analysis_run_id | UUID ou identificador textual | Sim | Referência à execução correspondente |
| result_type | String/Enum | Sim | Tipo de resultado produzido |
| status | Enum | Sim | Estado individual do resultado |
| data | JSON | Não | Dados estruturados específicos do módulo |
| message | String | Não | Mensagem descritiva sanitizada |
| created_at | DateTime | Sim | Data e horário de criação |

### Responsabilidades

- Armazenar resultados produzidos pelos módulos.
- Manter resultados associados à execução correspondente.
- Permitir informações específicas de cada módulo sem exigir tabelas próprias.
- Disponibilizar dados para consultas e exportações.
- Preservar as restrições de privacidade.

### Regras

1. Todo resultado persistido deverá pertencer a uma execução existente.
2. Os dados específicos de cada módulo deverão ser armazenados de forma estruturada.
3. O conteúdo de `data` deverá respeitar as regras de minimização e proteção de dados.
4. Mensagens deverão ser sanitizadas antes da persistência.
5. Resultados de operações PASSWORD não poderão conter o valor da senha, nem diretamente nem em estruturas derivadas que permitam recuperá-la.

### Estados de resultado

| Estado | Significado |
|---|---|
| `SUCCESS` | Resultado produzido com sucesso |
| `WARNING` | Resultado acompanhado de ressalva ou condição de atenção |
| `ERROR` | Resultado associado a uma falha específica |
| `INFO` | Informação complementar |

`ResultStatus` descreve um resultado individual, enquanto `ExecutionStatus` representa a execução completa.

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

Uma execução poderá produzir zero ou vários resultados.

Cada resultado pertencerá obrigatoriamente a uma única execução.

### Regras de integridade

- `AnalysisRun.id` será chave primária.
- `AnalysisResult.id` será chave primária.
- `AnalysisResult.analysis_run_id` será chave estrangeira.
- Um resultado não poderá existir sem uma execução correspondente.
- A exclusão de uma execução deverá remover seus resultados associados, caso uma exclusão seja realizada por mecanismo administrativo futuro.
- O MVP não deverá executar exclusões automáticas do histórico.
- Consultas e exportações do HISTORY não deverão criar novos registros de execução.

# 4. Enumerações

## 4.1. Module

| Valor | Módulo |
|---|---|
| `FILE` | Análise de arquivos |
| `HASH` | Hash |
| `NETWORK` | Diagnóstico de rede |
| `PASSWORD` | Ferramentas de senha |
| `URL` | Análise de URL |
| `PROCESS` | Monitoramento de processos |
| `HISTORY` | Histórico e relatórios |

## 4.2. ExecutionStatus

- `RUNNING`
- `SUCCESS`
- `PARTIAL`
- `FAILED`
- `INTERRUPTED`

## 4.3. ResultStatus

- `SUCCESS`
- `WARNING`
- `ERROR`
- `INFO`

# 5. Objetos internos dos módulos

Nem toda estrutura de dados precisa ser uma entidade persistente.

| Objeto | Módulo | Finalidade |
|---|---|---|
| `FileMetadata` | FILE | Representar metadados do arquivo |
| `HashReference` | HASH | Representar temporariamente a referência utilizada na comparação |
| `NetworkCheck` | NETWORK | Representar o resultado de uma verificação de rede |
| `PasswordEvaluation` | PASSWORD | Representar temporariamente a avaliação de uma senha |
| `UrlFinding` | URL | Representar indicadores encontrados na URL |
| `ProcessSnapshot` | PROCESS | Representar informações coletadas de processos |
| `SecurityFinding` | Transversal | Representar um achado estruturado |

Esses objetos existirão durante o processamento e não exigirão tabelas próprias no SQLite.

### Observação sobre HashReference

O MVP não manterá uma base própria de referências de hash.

A comparação utilizará uma referência fornecida pelo usuário. O objeto `HashReference` representará os dados necessários durante a operação, sem persistência ou gerenciamento de uma coleção local.

# 6. Regras de persistência

A persistência deverá respeitar as seguintes regras:

1. Cada execução deverá possuir um identificador único.
2. Cada execução deverá estar associada a uma instância identificável.
3. Os resultados deverão ser vinculados à execução correspondente.
4. Os dados específicos de cada módulo serão armazenados em JSON.
5. Senhas geradas ou avaliadas nunca serão persistidas.
6. Argumentos secretos não deverão ser armazenados em `command`.
7. O conteúdo integral dos arquivos analisados não deverá ser armazenado.
8. Dados sensíveis desnecessários não deverão entrar no histórico.
9. Execuções parciais, malsucedidas e interrompidas deverão permanecer consultáveis.
10. Datas deverão ser armazenadas em formato consistente, preferencialmente UTC.
11. O SQLite deverá utilizar chaves estrangeiras e consultas parametrizadas.
12. A exportação deverá respeitar os dados disponíveis e os limites de privacidade.
13. Falhas na persistência deverão ser comunicadas separadamente do resultado funcional.
14. A aplicação não deverá apresentar uma execução como persistida sem confirmação da gravação.
15. Durante o modo degradado, novas operações funcionais não deverão gerar registros no histórico.

# 7. Ciclo de vida das execuções

O ciclo de vida deverá respeitar os estados definidos em `ExecutionStatus`.

```text
          RUNNING
          /  |  \
         /   |   \
        v    v    v
   SUCCESS PARTIAL FAILED
         \
          \
       INTERRUPTED
```

`INTERRUPTED` representa uma execução que permaneceu em `RUNNING` após encerramento inesperado da instância responsável.

## 7.1. Identificação da instância

Cada inicialização deverá gerar um identificador único denominado `instance_id`.

Esse identificador será armazenado nos registros iniciados pela instância correspondente.

O identificador não deverá depender exclusivamente do PID do sistema operacional.

## 7.2. Instância única no MVP

O MVP adotará a política de uma única instância ativa do Odyssey AV por vez.

A aplicação deverá obter um bloqueio exclusivo antes de iniciar o processamento normal.

Esse mecanismo deverá:

- Impedir a execução simultânea de duas instâncias independentes.
- Ser liberado quando a aplicação encerrar normalmente.
- Ser liberado pelo sistema operacional quando o processo terminar inesperadamente, conforme o mecanismo utilizado.
- Impedir a recuperação enquanto outra instância válida estiver ativa.

A implementação deverá considerar as diferenças entre Windows e Linux.

## 7.3. Recuperação de execuções interrompidas

Após obter o bloqueio exclusivo e antes de aceitar novas operações, a aplicação deverá:

1. Gerar um novo `instance_id`.
2. Consultar execuções anteriores que ainda estejam em `RUNNING`.
3. Identificar registros pertencentes a instâncias anteriores.
4. Atualizar essas execuções para `INTERRUPTED`.
5. Registrar o horário de encerramento da recuperação.
6. Atualizar o resumo com justificativa sanitizada.
7. Prosseguir com a inicialização normal, caso a recuperação seja concluída.

O processo de recuperação não deverá alterar execuções pertencentes à instância atual.

A duração de uma execução interrompida deverá ser calculada a partir dos horários disponíveis, quando tecnicamente possível e confiável.

## 7.4. Limitações da recuperação

O estado `INTERRUPTED` não comprova que a operação funcional falhou.

Ele informa que a aplicação não conseguiu confirmar a conclusão normal da execução.

O sistema não deverá inventar resultados que não foram efetivamente produzidos ou persistidos.

# 8. Estado operacional e modo degradado

O estado operacional da aplicação será separado dos estados das entidades persistentes.

Serão utilizados dois estados operacionais:

| Estado | Significado |
|---|---|
| `NORMAL` | Recuperação concluída e persistência disponível |
| `DEGRADED` | Recuperação do histórico falhou e a persistência não está disponível durante a sessão |

Esses estados não serão armazenados como novos valores de `ExecutionStatus` ou `ResultStatus`.

## 8.1. Condições para entrar em modo degradado

A aplicação deverá entrar em modo degradado quando, após obter o bloqueio exclusivo, não conseguir concluir a recuperação das execuções anteriores.

Exemplos:

- Falha ao consultar registros `RUNNING`.
- Falha ao atualizar registros para `INTERRUPTED`.
- Erro de acesso ao banco.
- Indisponibilidade do SQLite que impeça a recuperação.

A aplicação deverá comunicar a condição ao usuário.

## 8.2. Comportamento durante o modo degradado

Enquanto estiver em modo degradado:

1. A aplicação poderá executar FILE, HASH, NETWORK, PASSWORD, URL e PROCESS.
2. Nenhuma nova execução deverá ser apresentada como persistida.
3. A aplicação não deverá realizar novas gravações no histórico.
4. O HISTORY deverá ficar indisponível para consultas e exportações.
5. A CLI deverá informar que os resultados da sessão não serão armazenados.
6. O resultado funcional deverá continuar separado da situação da persistência.
7. A aplicação não deverá ignorar silenciosamente execuções antigas em `RUNNING`.
8. A aplicação não deverá criar um mecanismo alternativo de armazenamento no MVP.

A falha de recuperação não deverá provocar a alteração artificial dos estados das execuções antigas.

Registros que não puderem ser atualizados deverão permanecer com os dados efetivamente armazenados, até que uma recuperação posterior possa ser concluída.

## 8.3. Retomada do modo normal

A recuperação será tentada novamente em uma inicialização posterior.

A aplicação somente deverá iniciar em modo `NORMAL` quando conseguir concluir a recuperação do histórico e confirmar a disponibilidade da persistência.

Não está prevista uma tentativa de recuperação em segundo plano durante a sessão degradada no MVP.

# 9. Separação entre resultado funcional e persistência

O resultado funcional de uma operação deverá ser tratado separadamente da situação de persistência do histórico.

Exemplo conceitual:

```json
{
  "operation": {
    "status": "SUCCESS",
    "message": "Hash calculado com sucesso."
  },
  "history": {
    "status": "FAILED",
    "message": "Não foi possível persistir o histórico."
  }
}
```

### Regras

- A falha de persistência não deverá alterar automaticamente o estado funcional.
- A aplicação deverá comunicar que o histórico não foi salvo.
- A CLI deverá utilizar o código de saída previsto para operação concluída com falha de persistência.
- Resultados não persistidos não poderão ser apresentados como disponíveis no histórico.
- A aplicação deverá evitar perda desnecessária de informações produzidas, dentro dos limites do mecanismo de execução.

No modo degradado, a situação do histórico deverá ser comunicada como indisponível, sem sugerir que houve tentativa de gravação bem-sucedida ou falha de uma gravação individual.

A situação da persistência não exige uma terceira entidade no modelo de dados. Ela será representada pelo contrato de execução da aplicação e pela resposta da CLI.

# 10. Tratamento específico do módulo PASSWORD

As execuções do módulo PASSWORD deverão seguir as regras gerais de histórico, com restrições adicionais.

Poderão ser persistidos:

- Identificador da execução.
- Módulo utilizado.
- Comando normalizado.
- Estado da operação.
- Horários.
- Duração.
- Resumo genérico e sanitizado.

Não poderão ser persistidos:

- Senha gerada.
- Senha avaliada.
- Argumentos contendo senhas.
- Conteúdo secreto em mensagens de erro.
- Valores de senha em `AnalysisResult.data`.
- Valores de senha em logs ou relatórios.

Exemplo de resumo permitido:

```text
Operação concluída. Saída sensível omitida.
```

O registro PASSWORD deverá comprovar que a operação ocorreu, sem armazenar o conteúdo da senha.

No modo degradado, a operação poderá ser executada, mas não haverá registro persistido.

# 11. Estrutura conceitual do banco

O banco terá inicialmente duas tabelas.

```sql
CREATE TABLE analysis_runs (
    id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
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

CREATE INDEX idx_analysis_runs_status
    ON analysis_runs(status);

CREATE INDEX idx_analysis_runs_instance_id
    ON analysis_runs(instance_id);

CREATE INDEX idx_analysis_results_run_id
    ON analysis_results(analysis_run_id);
```

> **Nota:** este é um esquema conceitual. Ainda não representa uma migration ou implementação executada.

Os valores de enumeração deverão ser validados pela aplicação. Restrições adicionais no banco poderão ser adotadas durante a implementação, desde que mantenham compatibilidade com o modelo documentado.

# 12. Estratégia de integridade e transações

A persistência deverá utilizar transações para manter a consistência entre execuções e resultados.

Regras:

1. As operações de gravação deverão utilizar transações.
2. Falhas durante a gravação deverão provocar rollback quando aplicável.
3. Chaves estrangeiras deverão estar habilitadas na conexão SQLite.
4. Consultas deverão utilizar parâmetros, sem interpolação insegura de entradas.
5. A atualização do estado de uma execução deverá preservar a consistência dos horários e resultados.
6. A recuperação deverá ser executada de maneira controlada, antes de novas operações.
7. A atualização das execuções antigas deverá utilizar transação, evitando recuperação parcialmente confirmada.
8. Se a transação de recuperação falhar, a aplicação deverá entrar em modo degradado.
9. A aplicação não deverá iniciar gravações funcionais enquanto a recuperação não estiver concluída.

A persistência deverá evitar que resultados sejam associados a execuções inexistentes.

# 13. Decisões de modelagem

| Identificador | Decisão | Justificativa |
|---|---|---|
| DOM-001 | Duas entidades persistentes | Evitar complexidade desnecessária |
| DOM-002 | Relacionamento 1:N | Uma execução pode gerar vários resultados |
| DOM-003 | Dados específicos em JSON | Evitar tabelas diferentes para cada módulo |
| DOM-004 | Objetos internos não persistentes | Separar processamento de armazenamento |
| DOM-005 | Histórico local no SQLite | Simplicidade e independência de servidores |
| DOM-006 | Identificador de instância em AnalysisRun | Identificar a origem das execuções |
| DOM-007 | Estado INTERRUPTED | Diferenciar interrupção inesperada de falha funcional |
| DOM-008 | Instância única ativa no MVP | Simplificar a recuperação segura |
| DOM-009 | Referências de hash não persistentes | Evitar base própria de hashes |
| DOM-010 | Separação entre operação e histórico | Preservar o resultado funcional quando a persistência falhar |
| DOM-011 | Modo degradado após falha de recuperação | Preservar disponibilidade sem declarar o histórico consistente |

# 14. Rastreabilidade

| Elemento do modelo | Requisitos e regras relacionados |
|---|---|
| `AnalysisRun` | RF-025, RN-009, RN-010 |
| `AnalysisResult` | RF-027, RF-028, RN-010, RN-011 |
| `ExecutionStatus` | RF-025, RN-009, RN-012 |
| `ResultStatus` | RF-004, RF-012 |
| `instance_id` | RN-009 |
| Proteção de PASSWORD | RF-016, RN-005 |
| Separação da persistência | RNF-007, RNF-010, RN-013 |
| Dados em JSON | RNF-011, RNF-012 |
| Modo degradado | RN-014, RNF-019 |

# 15. Estado do documento

| Critério | Situação |
|---|---|
| Entidades | Definidas |
| Atributos | Definidos |
| Relacionamentos | Definidos |
| Cardinalidades | Definidas |
| Estados de execução | Definidos |
| Estado INTERRUPTED | Incorporado |
| Identificação de instância | Definida |
| Recuperação de execuções | Definida conceitualmente |
| Modo degradado | Definido |
| Proteção de senhas | Definida |
| Separação entre operação e histórico | Definida |
| Persistência SQLite | Estruturada conceitualmente |
| Rastreabilidade | Mapeada |
| Revisão cruzada | Em andamento |

---

**Observação final:** este documento especifica o modelo de dados do MVP. A implementação física do banco, das migrations, do bloqueio exclusivo, da recuperação e do modo degradado será realizada conforme o backlog, após a aprovação da documentação e autorização para iniciar o desenvolvimento.