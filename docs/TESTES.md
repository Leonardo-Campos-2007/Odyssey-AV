# TESTES.md

**Projeto:** Odyssey AV  
**Versão:** 2.3<br>
**Escopo:** MVP  
**Status:** Consolidado após revisão cruzada

---

# 1. Objetivo

Este documento define a estratégia de testes do Odyssey AV.

Os testes deverão verificar se as funcionalidades implementadas atendem aos requisitos funcionais, às regras de negócio, aos requisitos não funcionais e aos controles de segurança definidos para o MVP.

A estratégia contempla:

- Testes unitários.
- Testes de integração.
- Testes funcionais da CLI.
- Testes de segurança.
- Testes de persistência e transações.
- Testes de instância e concorrência.
- Testes de configuração.
- Testes de compatibilidade Windows e Linux.
- Testes de regressão.

A ferramenta principal será `pytest`.

Os testes unitários deverão evitar dependências externas e utilizar simulações quando apropriado. Os testes de integração deverão utilizar recursos isolados e controlados.

# 2. Estratégia de testes

Os testes serão organizados de acordo com a responsabilidade e o nível de integração:

| Categoria | Objetivo |
|---|---|
| Unitários | Verificar funções, métodos e regras isoladamente |
| Integração | Verificar comunicação entre aplicação, módulos e infraestrutura |
| CLI | Verificar comandos, parâmetros, saídas e códigos de retorno |
| Segurança | Verificar os controles definidos em `SEGURANCA.md` |
| Persistência | Verificar integridade, transações e recuperação do histórico |
| Instância | Verificar bloqueio exclusivo e identificação das instâncias |
| Configuração | Verificar arquivo TOML, validação e precedência |
| Compatibilidade | Verificar comportamentos específicos de Windows e Linux |
| Regressão | Verificar se alterações não quebraram funcionalidades existentes |

# 3. Testes unitários

## 3.1. FILE — Análise de arquivos

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-FILE-001 | Analisar arquivo regular existente | Metadados apresentados corretamente |
| TU-FILE-002 | Analisar arquivo inexistente | Erro tratado |
| TU-FILE-003 | Informar caminho inválido | Entrada rejeitada |
| TU-FILE-004 | Analisar extensão incompatível com assinatura | Divergência identificada |
| TU-FILE-005 | Analisar formato não suportado | Limitação informada |
| TU-FILE-006 | Analisar arquivo sem permissão | Falha tratada |
| TU-FILE-007 | Analisar arquivo vazio | Resultado válido |
| TU-FILE-008 | Analisar diretório | Recurso rejeitado |
| TU-FILE-009 | Analisar link simbólico | Link não seguido automaticamente |
| TU-FILE-010 | Analisar dispositivo, socket ou pipe | Recurso rejeitado |
| TU-FILE-011 | Arquivo desaparece durante a leitura | Falha tratada |
| TU-FILE-012 | Arquivo é alterado durante a análise | Inconsistência detectada ou operação inconclusiva |
| TU-FILE-013 | Analisar assinatura PE | Identificação correspondente |
| TU-FILE-014 | Analisar assinatura ELF | Identificação correspondente |
| TU-FILE-015 | Analisar assinatura PDF | Identificação correspondente |
| TU-FILE-016 | Analisar assinatura PNG | Identificação correspondente |
| TU-FILE-017 | Analisar assinatura JPEG | Identificação correspondente |
| TU-FILE-018 | Analisar assinatura ZIP | Identificação correspondente |
| TU-FILE-019 | Analisar assinatura GZIP | Identificação correspondente |
| TU-FILE-020 | Analisar conteúdo desconhecido | Formato identificado como desconhecido |

A identificação de assinatura deverá ser testada separadamente da validação integral do formato. O reconhecimento de uma assinatura não deverá ser interpretado como garantia de segurança ou integridade do arquivo.

## 3.2. HASH — Hash

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-HASH-001 | Calcular SHA-256 | Hash correto retornado |
| TU-HASH-002 | Calcular hash de arquivo vazio | Hash válido retornado |
| TU-HASH-003 | Comparar hashes iguais | MATCH |
| TU-HASH-004 | Comparar hashes diferentes | MISMATCH |
| TU-HASH-005 | Comparar sem referência | NO_REFERENCE |
| TU-HASH-006 | Informar hash inválido | Entrada rejeitada |
| TU-HASH-007 | Calcular hash de arquivo em blocos | Resultado equivalente ao cálculo integral |
| TU-HASH-008 | Arquivo indisponível durante leitura | Erro tratado |

## 3.3. NETWORK — Diagnóstico de rede

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-NET-001 | Interpretar resultado de conectividade | Estado apresentado corretamente |
| TU-NET-002 | Interpretar resposta DNS válida | Resolução identificada |
| TU-NET-003 | Interpretar falha DNS | Falha identificada |
| TU-NET-004 | Operação excede timeout | Operação encerrada e erro tratado |
| TU-NET-005 | Serviço externo indisponível | Falha apresentada sem travar a aplicação |
| TU-NET-006 | Consulta de IP público desabilitada | Nenhuma consulta externa realizada |
| TU-NET-007 | Consulta de IP público habilitada | Serviço externo consultado e resultado tratado |
| TU-NET-008 | Falha de comunicação externa | Erro informado sem comprometer a aplicação |

Os testes unitários deverão utilizar respostas simuladas quando não for necessário realizar comunicação real.

## 3.4. PASSWORD — Ferramentas de senha

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-PASS-001 | Gerar senha com parâmetros válidos | Senha gerada |
| TU-PASS-002 | Informar comprimento inválido | Entrada rejeitada |
| TU-PASS-003 | Avaliar senha vazia | Resultado tratado |
| TU-PASS-004 | Avaliar senha com critérios diferentes | Avaliação coerente |
| TU-PASS-005 | Verificar fonte de aleatoriedade | Utilização de `secrets` |
| TU-PASS-006 | Verificar persistência após geração | Valor da senha não armazenado |
| TU-PASS-007 | Verificar persistência após avaliação | Valor da senha não armazenado |
| TU-PASS-008 | Verificar mensagens e logs | Nenhum valor secreto exposto |

## 3.5. URL — Análise de URL

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-URL-001 | Analisar URL válida | Componentes interpretados |
| TU-URL-002 | Analisar URL inválida | Entrada rejeitada ou sinalizada |
| TU-URL-003 | Normalizar URL | Representação normalizada |
| TU-URL-004 | Identificar indicador suspeito | Indicador apresentado |
| TU-URL-005 | Analisar URL sem esquema | Comportamento definido e consistente |
| TU-URL-006 | Analisar URL com caracteres especiais | Entrada tratada corretamente |
| TU-URL-007 | Analisar URL sem comunicação externa | Nenhuma requisição realizada |

## 3.6. PROCESS — Monitoramento de processos

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-PROC-001 | Listar processos | Lista apresentada |
| TU-PROC-002 | Consultar PID e nome | Informações corretas |
| TU-PROC-003 | Aplicar filtro | Somente resultados correspondentes |
| TU-PROC-004 | Processo inacessível | Limitação informada |
| TU-PROC-005 | Processo encerrado durante consulta | Falha tratada |
| TU-PROC-006 | Métrica indisponível | Ausência informada sem falha indevida do módulo |
| TU-PROC-007 | Verificar comportamento do módulo | Nenhum processo modificado |

## 3.7. HISTORY — Histórico e relatórios

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-HIST-001 | Criar registro de execução | Registro válido |
| TU-HIST-002 | Associar resultado à execução | Relacionamento correto |
| TU-HIST-003 | Consultar por módulo | Resultados filtrados |
| TU-HIST-004 | Consultar por período | Resultados filtrados |
| TU-HIST-005 | Consultar por estado | Resultados filtrados |
| TU-HIST-006 | Exportar JSON | Arquivo JSON válido |
| TU-HIST-007 | Exportar CSV | Arquivo CSV válido |
| TU-HIST-008 | Exportar execução com falha | Registro preservado |
| TU-HIST-009 | Consultar histórico | Nenhuma execução recursiva criada |
| TU-HIST-010 | Exportar histórico | Nenhuma execução recursiva criada |
| TU-HIST-011 | Registrar execução PASSWORD | Senha não persistida |
| TU-HIST-012 | Registrar execução parcial | Estado PARTIAL preservado |
| TU-HIST-013 | Registrar execução interrompida | Estado INTERRUPTED preservado |
| TU-HIST-014 | Registrar execução | `instance_id` associado corretamente |
| TU-HIST-015 | Sanitizar resumo e mensagem | Segredos não persistidos |
| TU-HIST-016 | Consultar HISTORY em modo degradado | Operação recusada |
| TU-HIST-017 | Exportar HISTORY em modo degradado | Operação recusada |
| TU-HIST-018 | Tentar gravar histórico em modo degradado | Nenhuma gravação realizada |

# 4. Testes de configuração

Os testes deverão verificar a configuração opcional por TOML, conforme a precedência definida em `REQUISITOS.md`.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-CONFIG-001 | Inicializar sem arquivo TOML | Padrões internos utilizados |
| TU-CONFIG-002 | Carregar arquivo TOML válido | Configurações reconhecidas |
| TU-CONFIG-003 | Carregar arquivo TOML inválido | Erro claro; configuração inválida não ignorada |
| TU-CONFIG-004 | Definir valor no padrão e no TOML | Valor do TOML prevalece |
| TU-CONFIG-005 | Definir valor no TOML e na CLI | Argumento explícito da CLI prevalece |
| TU-CONFIG-006 | Omitir parâmetro na CLI | Valor configurado ou padrão utilizado |
| TU-CONFIG-007 | Informar valor incompatível com o tipo esperado | Configuração rejeitada com mensagem clara |

# 5. Testes de integração

Os testes de integração verificarão o funcionamento conjunto das camadas e dos módulos.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TI-001 | Executar comando pela CLI | Caso de uso acionado corretamente |
| TI-002 | Executar análise e registrar resultado | Execução e resultado persistidos |
| TI-003 | Consultar histórico após execução | Dados recuperados corretamente |
| TI-004 | Exportar histórico persistido | Arquivo gerado com os dados esperados |
| TI-005 | Executar módulo com falha | Estado FAILED ou PARTIAL registrado conforme o resultado |
| TI-006 | Executar módulo sem resultados | Execução tratada corretamente |
| TI-007 | Consultar histórico sem registros | Resultado vazio apresentado corretamente |
| TI-008 | Executar módulo com falha de persistência | Resultado funcional preservado e falha de histórico comunicada |
| TI-009 | Executar módulo PASSWORD | Execução registrada sem persistir a senha |
| TI-010 | Executar operação funcional | Módulo não acessa diretamente o SQLite |
| TI-011 | Consultar histórico | Operação não cria novo AnalysisRun |
| TI-012 | Encerrar execução normalmente | Estado final e duração persistidos |
| TI-013 | Iniciar aplicação com registros RUNNING anteriores | Registros recuperados como INTERRUPTED |
| TI-014 | Falhar durante a recuperação do histórico | Aplicação entra em modo degradado |
| TI-015 | Executar FILE em modo degradado | Operação funcional permitida sem persistência |
| TI-016 | Executar HASH em modo degradado | Operação funcional permitida sem persistência |
| TI-017 | Executar NETWORK em modo degradado | Operação funcional permitida sem persistência |
| TI-018 | Executar PASSWORD em modo degradado | Operação funcional permitida sem persistência |
| TI-019 | Executar URL em modo degradado | Operação funcional permitida sem persistência |
| TI-020 | Executar PROCESS em modo degradado | Operação funcional permitida sem persistência |
| TI-021 | Executar HISTORY em modo degradado | Operação recusada com mensagem clara |
| TI-022 | Corrigir indisponibilidade e reiniciar | Nova inicialização tenta recuperar o histórico |
| TI-023 | Falhar durante transação de recuperação | Alterações incompletas revertidas quando aplicável |
| TI-024 | Executar operação funcional em modo degradado | Resultado não apresentado como persistido |
| TI-025 | Recuperar histórico com sucesso após inicialização anterior degradada | Aplicação retorna ao estado NORMAL após confirmação da recuperação |
| TI-026 | Falhar gravação inicial ou final em uma operação durante sessão NORMAL e executar outra operação | A operação funcional é executada e seu resultado preservado; a seguinte tenta persistir normalmente, sem transição para DEGRADED, fila em memória ou armazenamento alternativo |
| TI-027 | Falhar uma gravação após existirem registros confirmados | Registros anteriormente confirmados permanecem inalterados; dados não confirmados não são recuperados posteriormente |
| TI-028 | Consultar e exportar HISTORY com SQLite indisponível durante sessão NORMAL | Operação solicitada informa erro de persistência e não é apresentada como sucesso |

Os testes deverão confirmar que o modo degradado não altera as regras de segurança específicas dos módulos.

# 6. Testes da CLI

Os comandos deverão ser testados considerando entradas válidas, inválidas e situações de falha.

| ID | Comando ou operação | Verificação |
|---|---|---|
| TC-CLI-001 | `odyssey file analyze` | Análise de arquivo |
| TC-CLI-002 | `odyssey hash calculate` | Cálculo de hash |
| TC-CLI-003 | `odyssey hash compare` | Comparação com referência |
| TC-CLI-004 | `odyssey password generate` | Geração de senha |
| TC-CLI-005 | `odyssey password evaluate` | Avaliação local de senha |
| TC-CLI-006 | `odyssey url analyze` | Análise de URL |
| TC-CLI-007 | `odyssey network diagnose` | Diagnóstico de rede |
| TC-CLI-008 | `odyssey process list` | Listagem de processos |
| TC-CLI-009 | `odyssey history list` | Consulta de histórico |
| TC-CLI-010 | `odyssey history show` | Consulta de execução |
| TC-CLI-011 | `odyssey history export` | Exportação de histórico |
| TC-CLI-012 | Operação funcional com falha funcional | Código de saída `1` |
| TC-CLI-013 | Operação funcional bem-sucedida com falha de persistência em NORMAL | Resultado funcional preservado, falha de histórico informada e código `3` |
| TC-CLI-014 | Operação funcional com resultado parcial, inclusive com falha de persistência | Resultado parcial e código `4` |
| TC-CLI-015 | Consulta ou exportação HISTORY com SQLite indisponível | Erro da operação HISTORY e código `1`, não código `3` |
| TC-CLI-016 | Operação funcional bem-sucedida em DEGRADED | Histórico informado como indisponível, sem gravação, e código `3` |

Também deverão ser verificados:

- Mensagens de ajuda geral e por comando.
- Parâmetros obrigatórios.
- Parâmetros inválidos.
- Precedência das configurações.
- Código de saída dos comandos.
- Mensagens de erro.
- Formatação dos resultados.
- Saída textual e JSON.
- Ausência de segredos nas saídas e nos erros.
- Mensagens de inicialização em modo normal e degradado.
- Indisponibilidade de comandos HISTORY em modo degradado.
- Comunicação de que os resultados não serão persistidos.

Os códigos de saída deverão corresponder ao contrato definido em `API.md`, incluindo falhas funcionais, falhas de persistência, resultados parciais e falhas de consulta HISTORY.

# 7. Testes de segurança

Os testes de segurança deverão verificar os controles definidos em `SEGURANCA.md`.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TS-001 | Analisar arquivo suspeito | Arquivo não executado |
| TS-002 | Analisar arquivo | Conteúdo original não modificado |
| TS-003 | Gerar senha | Senha não persistida |
| TS-004 | Avaliar senha | Senha não aparece nos logs |
| TS-005 | Analisar URL | Nenhuma requisição automática ao destino |
| TS-006 | Consultar processos | Nenhum processo alterado |
| TS-007 | Informar entrada malformada | Entrada tratada com segurança |
| TS-008 | Consultar banco | Consultas parametrizadas |
| TS-009 | Exportar histórico | Nenhuma senha ou segredo exportado |
| TS-010 | Executar sem privilégios administrativos | Limitações informadas sem solicitar elevação automática |
| TS-011 | Analisar diretório | Recurso rejeitado |
| TS-012 | Analisar link simbólico | Link não seguido automaticamente |
| TS-013 | Analisar dispositivo, socket ou pipe | Recurso rejeitado |
| TS-014 | Informar segredo em argumento ou entrada | Segredo não aparece nos dados persistidos |
| TS-015 | Iniciar segunda instância | Operações funcionais impedidas |
| TS-016 | Encerrar instância inesperadamente | Execuções anteriores recuperadas como INTERRUPTED |
| TS-017 | Simular falha no SQLite durante operação | Resultado funcional preservado e falha de histórico comunicada |
| TS-018 | Verificar saída JSON e CSV | Dados sensíveis excluídos |
| TS-019 | Simular falha de recuperação do SQLite | Aplicação entra em modo degradado |
| TS-020 | Consultar HISTORY em modo degradado | Operação recusada |
| TS-021 | Executar módulo funcional em modo degradado | Nenhuma gravação no SQLite |
| TS-022 | Verificar mensagens do modo degradado | Indisponibilidade do histórico informada |
| TS-023 | Verificar tentativa de armazenamento alternativo | Nenhum armazenamento alternativo utilizado |
| TS-024 | Verificar registros antigos após falha de recuperação | Nenhum registro apresentado como recuperado sem confirmação |
| TS-025 | Verificar manutenção do bloqueio em modo degradado | Bloqueio exclusivo permanece ativo |

# 8. Testes de banco de dados

Os testes deverão verificar a integridade e o comportamento do SQLite.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TB-001 | Criar execução | Registro persistido |
| TB-002 | Criar resultado associado | Chave estrangeira válida |
| TB-003 | Criar resultado sem execução existente | Operação rejeitada |
| TB-004 | Consultar registros | Dados recuperados corretamente |
| TB-005 | Consultar módulo inexistente | Resultado vazio |
| TB-006 | Executar consulta inválida | Erro tratado |
| TB-007 | Verificar integridade referencial | Relacionamentos preservados |
| TB-008 | Criar execução sem `instance_id` | Operação rejeitada |
| TB-009 | Consultar execução por instância | Registros associados corretamente |
| TB-010 | Verificar estados permitidos | Estados inválidos rejeitados pela camada responsável |
| TB-011 | Verificar chave estrangeira | Restrição habilitada e aplicada |
| TB-012 | Verificar índices previstos | Índices disponíveis no banco |
| TB-013 | Verificar gravação em modo degradado | Nenhuma nova gravação realizada |
| TB-014 | Verificar estado de registros após rollback | Estado efetivamente confirmado preservado |
| TB-015 | Verificar acesso ao HISTORY em modo degradado | Consultas e exportações bloqueadas |

# 9. Testes de transação e rollback

A persistência deverá manter a consistência dos dados.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TR-001 | Inserção de execução e resultado concluída | Ambos persistidos |
| TR-002 | Falha durante operação transacional | Alterações revertidas quando aplicável |
| TR-003 | Falha na gravação de resultado | Estado da execução tratado corretamente |
| TR-004 | Falha de conexão com banco | Erro tratado sem perda silenciosa de dados |
| TR-005 | Falha ao finalizar execução | Estado e histórico tratados sem falsa confirmação |
| TR-006 | Falha de persistência após operação funcional bem-sucedida | Resultado funcional não convertido indevidamente em FAILED |
| TR-007 | Falha durante atualização de registros RUNNING | Transação de recuperação revertida quando aplicável |
| TR-008 | Falha ao confirmar transação de recuperação | Aplicação entra em modo degradado |
| TR-009 | Falha durante gravação em modo degradado | Nenhuma tentativa de gravação deverá ocorrer |
| TR-010 | Recuperação concluída com sucesso | Registros anteriores atualizados conforme as regras de recuperação |
| TR-011 | Falha isolada de gravação após registros previamente confirmados | Registros confirmados permanecem inalterados e dados não confirmados não são recuperados posteriormente |
| TR-012 | Falha de consulta ou exportação HISTORY por indisponibilidade do SQLite | Erro da operação HISTORY comunicado, sem ser tratado como sucesso com falha de gravação |

A estratégia deverá distinguir a transação de persistência do resultado da operação funcional. Uma falha de gravação não deverá alterar retroativamente o resultado funcional.

A recuperação deverá ser tratada como uma operação transacional. A aplicação somente poderá assumir o estado operacional `NORMAL` depois da confirmação de que a recuperação foi concluída.

# 10. Testes de instância e concorrência

O MVP permitirá somente uma instância ativa da aplicação.

Os testes deverão verificar:

- Aquisição do bloqueio exclusivo.
- Impedimento de inicialização funcional de uma segunda instância.
- Liberação do bloqueio após encerramento normal.
- Liberação do bloqueio após encerramento inesperado.
- Recuperação de registros `RUNNING`.
- Associação correta das execuções ao `instance_id`.
- Manutenção do bloqueio durante o modo degradado.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TCO-001 | Iniciar primeira instância | Bloqueio adquirido |
| TCO-002 | Iniciar segunda instância enquanto a primeira está ativa | Segunda instância impedida de executar operações |
| TCO-003 | Encerrar primeira instância normalmente | Bloqueio liberado |
| TCO-004 | Encerrar primeira instância inesperadamente | Bloqueio liberado pelo sistema operacional |
| TCO-005 | Reiniciar após encerramento inesperado | Registros RUNNING anteriores marcados INTERRUPTED |
| TCO-006 | Iniciar nova instância | Novo `instance_id` gerado |
| TCO-007 | Consultar registros de instâncias diferentes | Associação preservada |
| TCO-008 | Iniciar aplicação com falha na recuperação | Bloqueio permanece adquirido durante o modo degradado |
| TCO-009 | Tentar iniciar segunda instância durante modo degradado | Segunda instância impedida de executar operações |

Consultas e leituras concorrentes no SQLite poderão ser testadas isoladamente, sem violar a regra de instância única.

# 11. Testes de idempotência

No MVP, a idempotência será avaliada principalmente em operações de consulta e leitura.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TID-001 | Consultar histórico repetidamente | Mesmo conjunto de registros, sem novas execuções |
| TID-002 | Consultar processos repetidamente | Nenhuma alteração no sistema |
| TID-003 | Calcular hash do mesmo arquivo sem alterações | Mesmo resultado |
| TID-004 | Exportar o mesmo histórico sem alterações | Conteúdo equivalente |
| TID-005 | Consultar execução por identificador repetidamente | Mesmo registro retornado |
| TID-006 | Repetir consulta HISTORY em modo degradado | Consulta permanece indisponível, sem tentativa de gravação |

Não será exigida idempotência artificial para operações que geram uma nova execução a cada chamada.

# 12. Testes de compatibilidade entre plataformas

O Odyssey AV deverá funcionar em Windows e Linux.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TPL-001 | Inicializar aplicação no Windows | Inicialização conforme contrato |
| TPL-002 | Inicializar aplicação no Linux | Inicialização conforme contrato |
| TPL-003 | Resolver caminhos no Windows | Caminhos tratados corretamente |
| TPL-004 | Resolver caminhos no Linux | Caminhos tratados corretamente |
| TPL-005 | Identificar recursos especiais no Windows | Recursos não permitidos rejeitados quando identificáveis |
| TPL-006 | Identificar recursos especiais no Linux | Recursos não permitidos rejeitados |
| TPL-007 | Consultar processos no Windows | Informações disponíveis apresentadas |
| TPL-008 | Consultar processos no Linux | Informações disponíveis apresentadas |
| TPL-009 | Adquirir bloqueio exclusivo no Windows | Exclusividade garantida |
| TPL-010 | Adquirir bloqueio exclusivo no Linux | Exclusividade garantida |
| TPL-011 | Recuperar histórico no Windows | Recuperação conforme contrato |
| TPL-012 | Recuperar histórico no Linux | Recuperação conforme contrato |
| TPL-013 | Entrar em modo degradado no Windows | Regras do modo degradado respeitadas |
| TPL-014 | Entrar em modo degradado no Linux | Regras do modo degradado respeitadas |

Os testes deverão distinguir falhas da aplicação de limitações legítimas da plataforma ou das permissões do usuário.

# 13. Testes de regressão

Sempre que uma funcionalidade for alterada, os testes relacionados deverão ser executados novamente.

Os testes de regressão deverão priorizar:

- Cálculo e comparação de hashes.
- Geração e avaliação de senhas.
- Análise de arquivos.
- Identificação de assinaturas.
- Interpretação de URLs.
- Diagnóstico de rede.
- Listagem de processos.
- Persistência e exportação do histórico.
- Tratamento de erros.
- Proteção de dados sensíveis.
- Configuração TOML.
- Bloqueio de instância.
- Recuperação de execuções interrompidas.
- Separação entre resultado funcional e persistência.
- Entrada e saída do modo degradado.
- Compatibilidade entre Windows e Linux.

# 14. Dados de teste

Os testes deverão utilizar dados controlados e isolados.

| Tipo | Dados de teste |
|---|---|
| Arquivos | Arquivo de texto, arquivo vazio, arquivo binário e arquivo com extensão divergente |
| Assinaturas | Amostras controladas de PE, ELF, PDF, PNG, JPEG, ZIP e GZIP |
| Hash | Hashes conhecidos e hashes inválidos |
| URLs | URLs válidas, inválidas e com indicadores suspeitos |
| Senhas | Valores sintéticos de diferentes comprimentos e características |
| Rede | Respostas simuladas de sucesso, falha e timeout |
| Processos | Processos acessíveis e situações simuladas de indisponibilidade |
| Histórico | Execuções SUCCESS, PARTIAL, FAILED e INTERRUPTED |
| Recuperação | Bancos de teste com execuções RUNNING e cenários de falha transacional |
| Modo degradado | Banco indisponível, somente leitura ou com falha simulada de recuperação |
| Configuração | Arquivos TOML válidos, inválidos e combinações de precedência |

Não utilizar arquivos pessoais, senhas reais ou dados sensíveis nos testes.

As amostras de arquivos deverão ser inofensivas e não executáveis durante os testes.

# 15. Isolamento dos testes

Os testes deverão ser executados sem interferir no ambiente real do usuário.

Diretrizes:

- Utilizar diretórios temporários para arquivos.
- Utilizar banco SQLite exclusivo para testes.
- Não alterar o banco utilizado pela aplicação.
- Simular serviços externos sempre que possível.
- Não depender de conexão com a internet para testes unitários.
- Limpar arquivos temporários após a execução.
- Não executar testes que modifiquem processos reais do sistema operacional.
- Não utilizar senhas reais.
- Isolar arquivos de configuração e variáveis de ambiente.
- Evitar dependência da ordem de execução dos testes.
- Simular falhas de leitura, escrita e transação do SQLite.
- Garantir que testes de modo degradado não dependam de indisponibilidade real do banco de produção.

# 16. Cobertura de testes

A cobertura deverá ser acompanhada pelo `pytest-cov`.

Metas iniciais propostas:

- Cobrir todos os módulos funcionais com testes.
- Buscar pelo menos 80% de cobertura de código nas regras e serviços da aplicação.
- Testar integralmente as operações críticas de segurança e persistência.
- Evitar que linhas críticas de tratamento de erros permaneçam sem testes.
- Cobrir os caminhos de inicialização normal e degradada.
- Cobrir os caminhos de falha e rollback da recuperação.
- Cobrir a validação e a precedência da configuração TOML.

A porcentagem de cobertura não deverá ser utilizada isoladamente como indicador de qualidade. Os testes precisam verificar comportamentos e resultados relevantes.

Os limites definitivos poderão ser ajustados após a implementação da primeira versão executável.

# 17. Ferramentas

| Ferramenta | Finalidade |
|---|---|
| pytest | Execução dos testes |
| pytest-cov | Medição de cobertura |
| unittest.mock | Simulação de dependências e serviços externos |
| tempfile | Criação de arquivos e diretórios temporários |
| sqlite3 | Testes da persistência |

Não será necessário utilizar Docker, bancos externos ou ferramentas avançadas de testes no MVP.

# 18. Critérios de aprovação

Uma funcionalidade poderá ser considerada testada quando:

1. Seus testes unitários forem aprovados.
2. Seus testes de integração forem aprovados, quando aplicáveis.
3. Os critérios funcionais correspondentes forem atendidos.
4. Os controles de segurança relacionados forem verificados.
5. Os testes de persistência forem aprovados, quando aplicáveis.
6. Os testes de regressão relacionados forem aprovados.
7. As particularidades de Windows e Linux forem verificadas, quando aplicáveis.
8. Não houver falhas críticas conhecidas.
9. O comportamento em modo degradado for validado quando a funcionalidade depender do histórico.
10. A aplicação não apresentar resultados como persistidos sem confirmação efetiva do banco.

A conclusão de uma tarefa no backlog deverá considerar os critérios de aceitação e os testes correspondentes.

# 19. Rastreabilidade

| Área | Documentos relacionados |
|---|---|
| Requisitos funcionais | `REQUISITOS.md` |
| Regras de negócio | `REGRAS-DE-NEGOCIO.md` |
| Arquitetura e camadas | `ARQUITETURA.md` |
| Segurança e ameaças | `SEGURANCA.md` |
| Entidades e persistência | `MODELO-DE-DADOS.md` |
| Comandos e códigos de saída | `API.md` |
| Tarefas e critérios de aceitação | `BACKLOG.md` |

Os IDs dos testes deverão ser associados aos critérios de aceitação das tarefas correspondentes no backlog.

Referências a testes deverão utilizar identificadores existentes neste documento. Critérios de aceitação sem caso de teste específico deverão ser identificados como pendentes de rastreabilidade, não como testes já definidos.

# 20. Estado do documento

| Critério | Situação |
|---|---|
| Testes unitários | Definidos |
| Testes de integração | Definidos |
| Testes da CLI | Definidos |
| Testes de configuração | Definidos |
| Testes de segurança | Definidos |
| Testes de banco | Definidos |
| Transações e rollback | Definidos |
| Instância única e concorrência | Definidos |
| Recuperação de execuções | Definida |
| Modo degradado | Definido |
| Idempotência | Definida |
| Regressão | Definida |
| Dados e isolamento | Definidos |
| Compatibilidade Windows/Linux | Definida |
| Cobertura | Meta inicial proposta |
| Revisão cruzada | Concluída |

---

**Observação:** este documento especifica a estratégia de testes do MVP. A implementação dos testes será realizada após a consolidação documental e a autorização explícita para iniciar o desenvolvimento.
