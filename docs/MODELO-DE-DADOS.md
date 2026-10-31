# MODELO-DE-DADOS.md

**Projeto:** Odyssey AV  
**Versão:** 2.3<br>
**Escopo:** MVP  
**Status:** Consolidado após revisão cruzada

---

# 1. Visão geral

O modelo de dados do Odyssey AV foi projetado para oferecer persistência local, simples e modular, compatível com os sete módulos definidos para o MVP.

O sistema utilizará SQLite e terá duas entidades persistentes:

- `AnalysisRun`
- `AnalysisResult`

Não serão criadas entidades para usuários, contas, organizações ou autenticação, pois esses recursos não fazem parte do MVP.

O modelo deverá permitir:

- Registrar execuções dos módulos funcionais.
- Armazenar resultados associados às execuções.
- Consultar e exportar o histórico.
- Diferenciar sucesso, execução parcial, falha e interrupção.
- Identificar a instância responsável por cada execução.
- Recuperar registros deixados em estado `RUNNING`.
- Preservar a integridade dos dados durante a recuperação.
- Proteger informações sensíveis e minimizar os dados persistidos.

**Importante:** o módulo `HISTORY` faz parte do sistema, mas suas operações de consulta e exportação não geram registros próprios de `AnalysisRun`.

# 2. Entidades principais

## 2.1. AnalysisRun

Representa uma execução de uma ferramenta funcional do Odyssey AV.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| `id` | UUID textual | Sim | Identificador único da execução |
| `instance_id` | UUID textual | Sim | Identificador da instância responsável |
| `module` | Enum/String | Sim | Módulo executado |
| `command` | String | Sim | Comando normalizado, sem argumentos secretos |
| `status` | Enum/String | Sim | Estado da execução |
| `started_at` | DateTime | Sim | Data e horário de início |
| `finished_at` | DateTime | Não | Data e horário de encerramento |
| `duration_ms` | Integer | Não | Duração em milissegundos |
| `summary` | String | Não | Resumo sanitizado da execução |

### Responsabilidades

- Identificar uma execução.
- Registrar o módulo e o comando utilizado.
- Identificar a instância responsável.
- Controlar o estado da execução.
- Registrar início, término e duração.
- Disponibilizar informações para consultas posteriores.
- Permitir a identificação de execuções interrompidas.

### Regras

1. Cada execução persistida deverá possuir identificador único.
2. `instance_id` deverá identificar a instância que iniciou a execução.
3. `command` deverá armazenar o comando normalizado, sem argumentos que possam conter senhas ou outros segredos.
4. `summary` deverá ser sanitizado antes da persistência.
5. O estado deverá representar o resultado funcional da execução, não exclusivamente a situação do armazenamento do histórico.
6. A aplicação deverá tentar registrar uma execução antes do processamento. Durante uma sessão iniciada em `NORMAL`, se essa gravação falhar, a operação funcional ainda deverá ser executada, sem afirmar que o registro existe.
7. Operações do módulo `HISTORY` não deverão criar registros de execução.
8. Operações executadas durante o modo degradado não deverão ser apresentadas como persistidas.

### Estados de execução

| Estado | Significado |
|---|---|
| `RUNNING` | Execução em andamento |
| `SUCCESS` | Execução concluída com sucesso |
| `PARTIAL` | Execução concluída parcialmente |
| `FAILED` | Execução que apresentou falha funcional |
| `INTERRUPTED` | Execução interrompida inesperadamente |

O estado `INTERRUPTED` será utilizado quando uma execução anterior permanecer em `RUNNING` após encerramento inesperado da instância responsável.

A interrupção não deverá ser classificada automaticamente como falha funcional. Ela indica que a aplicação não conseguiu confirmar a conclusão normal da execução.

## 2.2. AnalysisResult

Representa um resultado produzido durante uma execução.

| Atributo | Tipo lógico | Obrigatório | Descrição |
|---|---|---|---|
| `id` | UUID textual | Sim | Identificador único do resultado |
| `analysis_run_id` | UUID textual | Sim | Referência à execução correspondente |
| `result_type` | String/Enum | Sim | Tipo de resultado produzido |
| `status` | Enum/String | Sim | Estado individual do resultado |
| `data` | JSON | Não | Dados estruturados específicos do módulo |
| `message` | String | Não | Mensagem descritiva sanitizada |
| `created_at` | DateTime | Sim | Data e horário de criação |

### Responsabilidades

- Armazenar resultados produzidos pelos módulos.
- Associar resultados à execução correspondente.
- Permitir informações específicas de cada módulo sem exigir tabelas próprias.
- Disponibilizar dados para consultas e exportações.
- Respeitar as regras de privacidade e minimização de dados.

### Regras

1. Todo resultado persistido deverá pertencer a uma execução existente.
2. Os dados específicos de cada módulo deverão ser armazenados de forma estruturada.
3. O conteúdo de `data` deverá respeitar as regras de minimização e proteção de dados.
4. Mensagens deverão ser sanitizadas antes da persistência.
5. Resultados de operações `PASSWORD` não poderão conter a senha, diretamente ou em estruturas derivadas que permitam recuperá-la.
6. Resultados não produzidos ou não confirmados não deverão ser inventados para completar um registro.

### Estados de resultado

| Estado | Significado |
|---|---|
| `SUCCESS` | Resultado produzido com sucesso |
| `WARNING` | Resultado acompanhado de ressalva ou condição de atenção |
| `ERROR` | Resultado associado a uma falha específica |
| `INFO` | Informação complementar |

`ResultStatus` descreve um resultado individual. `ExecutionStatus` representa a execução completa. Portanto, os dois estados não são intercambiáveis.

# 3. Relacionamento entre entidades

O modelo possui relacionamento de um para muitos (1:N).

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
- A exclusão de uma execução, caso venha a ser disponibilizada por mecanismo administrativo futuro, deverá remover seus resultados associados por meio de `ON DELETE CASCADE`.
- O MVP não deverá executar exclusões automáticas do histórico.
- Consultas e exportações do `HISTORY` não deverão criar novos registros de execução.

A exclusão em cascata define o comportamento referencial do banco caso uma exclusão explícita seja implementada futuramente. Ela não autoriza exclusões automáticas no MVP.

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

`HISTORY` identifica o módulo funcional na interface e na organização do sistema. Suas consultas e exportações não geram `AnalysisRun`.

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

Os valores deverão ser validados pela aplicação. Restrições adicionais no SQLite poderão ser adotadas durante a implementação, desde que mantenham compatibilidade com este modelo.

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

### 5.1. HashReference

O MVP não manterá uma base própria de referências de hash.

A comparação utilizará uma referência fornecida pelo usuário. O objeto `HashReference` representará os dados necessários durante a operação, sem persistência ou gerenciamento de uma coleção local.

### 5.2. PasswordEvaluation

Representará os dados necessários para a avaliação local de uma senha.

Seu conteúdo deverá permanecer em memória durante o processamento, sem persistir a senha avaliada, a senha gerada ou informações que permitam recuperá-la.

# 6. Regras gerais de persistência

A persistência deverá respeitar as seguintes regras:

1. Cada execução funcional registrada deverá possuir identificador único.
2. Cada execução deverá estar associada a uma instância identificável.
3. Os resultados deverão ser vinculados à execução correspondente.
4. Os dados específicos de cada módulo serão armazenados em JSON.
5. Senhas geradas ou avaliadas nunca serão persistidas.
6. Argumentos secretos não deverão ser armazenados em `command`.
7. O conteúdo integral dos arquivos analisados não deverá ser armazenado.
8. Dados sensíveis desnecessários não deverão entrar no histórico.
9. Execuções parciais, malsucedidas e interrompidas deverão permanecer consultáveis quando persistidas.
10. Datas deverão ser armazenadas em UTC, utilizando formato consistente.
11. O SQLite deverá utilizar chaves estrangeiras habilitadas e consultas parametrizadas.
12. Exportações deverão respeitar os dados disponíveis e os limites de privacidade.
13. Falhas na persistência deverão ser comunicadas separadamente do resultado funcional.
14. A aplicação não deverá apresentar uma execução como persistida sem confirmação da gravação.
15. Durante o modo degradado, novas operações funcionais não deverão gerar registros no histórico.
16. A aplicação não deverá utilizar armazenamento alternativo para substituir o SQLite no MVP.
17. O histórico não deverá conter dados que não tenham sido efetivamente produzidos ou confirmados.
18. Durante uma sessão iniciada em `NORMAL`, cada falha de gravação afetará somente a persistência da operação correspondente; não provocará transição automática para `DEGRADED`.
19. Operações funcionais posteriores deverão realizar sua própria tentativa normal de persistência. Não haverá fila em memória ou armazenamento alternativo, e dados cuja gravação falhou não serão recuperados posteriormente.
20. Registros anteriormente confirmados deverão permanecer inalterados quando uma gravação posterior falhar.
21. Consultas e exportações `HISTORY` dependerão da disponibilidade do SQLite e deverão comunicar erro se a operação falhar.

# 7. Ciclo de vida das execuções

O ciclo de vida deverá respeitar os estados definidos em `ExecutionStatus`.

```text
                 RUNNING
                /   |   \
               /    |    \
              v     v     v
          SUCCESS PARTIAL FAILED

                 RUNNING
                    |
                    | interrupção inesperada
                    v
               INTERRUPTED
```

`INTERRUPTED` representa uma execução que permaneceu em `RUNNING` após encerramento inesperado da instância responsável.

## 7.1. Identificação da instância

Cada inicialização deverá gerar um identificador único denominado `instance_id`.

Esse identificador será armazenado nos registros iniciados pela instância correspondente.

O identificador não deverá depender exclusivamente do PID do sistema operacional, pois PIDs podem ser reutilizados.

## 7.2. Instância única no MVP

O MVP adotará a política de uma única instância ativa do Odyssey AV por vez.

A aplicação deverá obter um bloqueio exclusivo antes de iniciar o processamento normal.

Esse mecanismo deverá:

- Impedir a execução simultânea de duas instâncias independentes.
- Ser liberado quando a aplicação encerrar normalmente.
- Ser liberado pelo sistema operacional quando o processo terminar inesperadamente, conforme o mecanismo utilizado.
- Impedir a recuperação enquanto outra instância válida estiver ativa.
- Considerar as diferenças de implementação entre Windows e Linux.

## 7.3. Recuperação de execuções interrompidas

Após obter o bloqueio exclusivo e antes de aceitar novas operações, a aplicação deverá:

1. Gerar um novo `instance_id`.
2. Iniciar uma transação de recuperação.
3. Consultar execuções anteriores que ainda estejam em `RUNNING`.
4. Identificar registros pertencentes a instâncias anteriores.
5. Atualizar essas execuções para `INTERRUPTED`.
6. Registrar o horário de encerramento da recuperação.
7. Atualizar o resumo com justificativa sanitizada.
8. Confirmar a transação.
9. Prosseguir com a inicialização normal somente após a recuperação ser concluída e confirmada.

O processo de recuperação não deverá alterar execuções pertencentes à instância atual.

A duração de uma execução interrompida deverá ser calculada a partir dos horários disponíveis, quando tecnicamente possível e confiável.

## 7.4. Atomicidade da recuperação

A recuperação deverá ser transacional.

Isso significa que as alterações realizadas durante a recuperação deverão ser confirmadas como uma única operação lógica.

Se a transação falhar:

- A aplicação deverá executar rollback quando aplicável.
- Não deverá considerar a recuperação concluída.
- Não deverá assumir que os registros antigos foram atualizados.
- Deverá entrar em modo degradado.
- Deverá preservar o estado efetivamente persistido no banco.

Não será permitido marcar registros antigos como `INTERRUPTED` quando a transação de recuperação não tiver sido concluída.

## 7.5. Limitações da recuperação

O estado `INTERRUPTED` não comprova que a operação funcional falhou.

Ele informa que a aplicação não conseguiu confirmar a conclusão normal da execução.

O sistema não deverá inventar resultados que não foram efetivamente produzidos ou persistidos.

# 8. Estado operacional e modo degradado

O estado operacional da aplicação será separado dos estados das entidades persistentes.

Serão utilizados dois estados operacionais:

| Estado | Significado |
|---|---|
| `NORMAL` | Recuperação transacional inicial concluída; operações funcionais e tentativas de persistência habilitadas |
| `DEGRADED` | Recuperação transacional falhou durante a inicialização; novas gravações e operações HISTORY desabilitadas durante a sessão |

Esses estados não serão armazenados como novos valores de `ExecutionStatus` ou `ResultStatus`.

## 8.1. Condições para entrar em modo degradado

A aplicação deverá entrar em modo degradado quando, após obter o bloqueio exclusivo, não conseguir concluir a recuperação das execuções anteriores.

Exemplos:

- Falha ao consultar registros `RUNNING`.
- Falha ao atualizar registros para `INTERRUPTED`.
- Falha na confirmação da transação.
- Erro de acesso ao banco.
- Indisponibilidade do SQLite que impeça a recuperação.

A aplicação deverá comunicar claramente a condição ao usuário.

## 8.2. Comportamento durante o modo degradado

Enquanto estiver em modo degradado:

1. A aplicação poderá executar `FILE`, `HASH`, `NETWORK`, `PASSWORD`, `URL` e `PROCESS`.
2. Nenhuma nova gravação deverá ser realizada no histórico.
3. Nenhuma execução deverá ser apresentada como persistida.
4. O módulo `HISTORY` deverá ficar indisponível para consultas e exportações.
5. A CLI deverá informar que os resultados da sessão não serão armazenados.
6. O resultado funcional deverá continuar separado da situação da persistência.
7. A aplicação não deverá ignorar silenciosamente execuções antigas em `RUNNING`.
8. A aplicação não deverá criar mecanismo alternativo de armazenamento no MVP.
9. A falha de recuperação não deverá provocar alteração artificial dos estados das execuções antigas.

Registros que não puderem ser atualizados deverão permanecer com os dados efetivamente armazenados, até que uma recuperação posterior possa ser concluída.

## 8.3. Retomada do modo normal

A recuperação será tentada novamente em uma inicialização posterior.

A aplicação somente deverá iniciar em modo `NORMAL` quando conseguir concluir a recuperação do histórico e confirmar a disponibilidade da persistência.

Não está prevista uma tentativa de recuperação em segundo plano durante a sessão degradada no MVP.

## 8.4. Falha de persistência durante uma sessão NORMAL

O modelo mantém a separação entre resultado funcional e persistência.

Se uma operação funcional for concluída, mas sua gravação no histórico falhar, a operação não deverá ser convertida automaticamente em falha funcional.

A aplicação deverá comunicar separadamente os dois resultados.

Durante uma sessão iniciada em `NORMAL`, a falha de persistência será tratada por operação. O resultado funcional deverá ser preservado e comunicado separadamente da situação do histórico. Uma falha de gravação não provocará transição automática para `DEGRADED`; as operações funcionais subsequentes continuarão disponíveis e farão suas próprias tentativas normais de persistência.

Não haverá fila em memória para gravações pendentes nem armazenamento alternativo. Dados cuja gravação falhou não serão recuperados posteriormente, e registros anteriormente confirmados permanecerão inalterados. Consultas e exportações `HISTORY` dependerão da disponibilidade do SQLite e deverão comunicar erro quando falharem.

O estado `DEGRADED` continuará reservado à falha da recuperação transacional durante a inicialização. Essa falha exige manter o bloqueio exclusivo, não realizar novas gravações e indisponibilizar consultas e exportações `HISTORY`, conforme as seções 8.1 e 8.2.

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
- O resultado funcional produzido deverá ser apresentado ao usuário mesmo quando sua persistência falhar; isso não autoriza manter uma fila de gravações ou recuperar posteriormente dados não confirmados.
- No modo degradado, a situação do histórico deverá ser comunicada como indisponível, sem sugerir que houve gravação bem-sucedida ou tentativa de gravação individual.

A situação da persistência não exige uma terceira entidade no modelo de dados. Ela será representada pelo contrato de execução da aplicação e pela resposta da CLI.

# 10. Tratamento específico do módulo PASSWORD

As execuções do módulo `PASSWORD` deverão seguir as regras gerais de histórico, com restrições adicionais.

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

O registro `PASSWORD` deverá comprovar que a operação ocorreu, sem armazenar o conteúdo da senha.

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

### Considerações de implementação

- UUIDs serão armazenados como texto no SQLite.
- Datas serão armazenadas em UTC, com representação consistente.
- `data` será armazenado como texto JSON válido.
- A aplicação deverá validar os valores de enumeração.
- A conexão SQLite deverá habilitar explicitamente o suporte a chaves estrangeiras.
- Consultas deverão utilizar parâmetros.
- Restrições adicionais poderão ser implementadas durante o desenvolvimento, desde que mantenham compatibilidade com o modelo.

# 12. Estratégia de integridade e transações

A persistência deverá utilizar transações para manter a consistência entre execuções e resultados.

Regras:

1. Operações de gravação deverão utilizar transações quando envolverem múltiplas alterações relacionadas.
2. Falhas durante a gravação deverão provocar rollback quando aplicável.
3. Chaves estrangeiras deverão estar habilitadas na conexão SQLite.
4. Consultas deverão utilizar parâmetros, sem interpolação insegura de entradas.
5. A atualização do estado de uma execução deverá preservar a consistência dos horários e resultados.
6. A recuperação deverá ser executada de maneira controlada, antes de novas operações.
7. A atualização das execuções antigas deverá utilizar uma única transação lógica.
8. Se a transação de recuperação falhar, a aplicação deverá entrar em modo degradado.
9. A aplicação não deverá iniciar gravações funcionais enquanto a recuperação não estiver concluída.
10. Resultados não poderão ser associados a execuções inexistentes.

# 13. Decisões de modelagem

| Identificador | Decisão | Justificativa |
|---|---|---|
| DOM-001 | Duas entidades persistentes | Evitar complexidade desnecessária |
| DOM-002 | Relacionamento 1:N | Uma execução pode gerar vários resultados |
| DOM-003 | Dados específicos em JSON | Evitar tabelas diferentes para cada módulo |
| DOM-004 | Objetos internos não persistentes | Separar processamento de armazenamento |
| DOM-005 | Histórico local no SQLite | Simplicidade e independência de servidores |
| DOM-006 | Identificador de instância em `AnalysisRun` | Identificar a origem das execuções |
| DOM-007 | Estado `INTERRUPTED` | Diferenciar interrupção inesperada de falha funcional |
| DOM-008 | Instância única ativa no MVP | Simplificar a recuperação segura |
| DOM-009 | Referências de hash não persistentes | Evitar base própria de hashes |
| DOM-010 | Separação entre operação e histórico | Preservar o resultado funcional quando a persistência falhar |
| DOM-011 | Modo degradado após falha de recuperação | Preservar disponibilidade sem declarar o histórico consistente |
| DOM-012 | Recuperação transacional | Impedir confirmação parcial da recuperação |
| DOM-013 | Estado operacional independente | Não misturar disponibilidade da aplicação com estado das execuções |
| DOM-014 | HISTORY sem registro próprio | Evitar histórico recursivo |

# 14. Rastreabilidade

| Elemento do modelo | Requisitos e regras relacionados |
|---|---|
| `AnalysisRun` | RF-025, RN-009, RN-010 |
| `AnalysisResult` | RF-027, RF-028, RN-010, RN-011 |
| `ExecutionStatus` | RF-025, RN-009, RN-012 |
| `ResultStatus` | RF-004, RF-012 |
| `instance_id` | RN-009 |
| Proteção de PASSWORD | RF-016, RN-005 |
| Separação da persistência | RNF-007, RNF-010, RNF-013 |
| Dados em JSON | RNF-011, RNF-012 |
| Modo degradado após falha de recuperação na inicialização | RF-033, RN-009, DOM-011, ARC-013 |
| Recuperação transacional | RF-030, RN-009, DOM-012, ARC-014 |
| HISTORY sem registro próprio | RF-025, RN-009, DOM-014 |
| Separação entre resultado funcional e persistência | RF-032, RN-013, DOM-010, ARC-012 |
| Falha de persistência durante sessão NORMAL | RF-032, RN-013, DOM-010, ARC-012 |

Os identificadores foram conferidos na revisão cruzada dos documentos. As referências inexistentes ou divergentes foram corrigidas.

# 15. Estado do documento

| Critério | Situação |
|---|---|
| Entidades | Definidas |
| Atributos | Definidos |
| Relacionamentos | Definidos |
| Cardinalidades | Definidas |
| Estados de execução | Definidos |
| Estado `INTERRUPTED` | Incorporado |
| Identificação de instância | Definida |
| Instância única | Definida conceitualmente |
| Recuperação de execuções | Definida conceitualmente |
| Atomicidade da recuperação | Definida |
| Modo degradado | Definido |
| Proteção de senhas | Definida |
| Separação entre operação e histórico | Definida |
| Persistência SQLite | Estruturada conceitualmente |
| HISTORY sem registro próprio | Definido |
| Falha de persistência durante sessão NORMAL | Definida |
| Rastreabilidade | Validada |
| Revisão cruzada | Concluída |

---

**Observação final:** este documento especifica o modelo de dados do MVP. A implementação física do banco, das migrations, do bloqueio exclusivo, da recuperação e do modo degradado será realizada conforme o backlog, após a aprovação da documentação e autorização explícita para iniciar o desenvolvimento.
