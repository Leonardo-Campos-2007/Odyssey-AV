# SEGURANCA.md

**Projeto:** Odyssey AV  
**Versão:** 2.3<br>
**Escopo:** MVP  
**Status:** Consolidado após revisão cruzada

---

# 1. Objetivo

Este documento define os princípios, ameaças e controles de segurança do Odyssey AV.

O objetivo é proteger a aplicação, os arquivos analisados, as informações do usuário e os resultados armazenados, reduzindo riscos durante a execução das ferramentas.

A segurança deverá ser considerada desde o desenvolvimento até a utilização da aplicação, respeitando os limites funcionais definidos para o MVP.

# 2. Escopo de segurança

O Odyssey AV será uma ferramenta local de análise e diagnóstico, executada por linha de comando.

A segurança deverá contemplar os sete módulos:

| Módulo | Área de proteção |
|---|---|
| FILE | Acesso e leitura segura de arquivos |
| HASH | Integridade e comparação de hashes |
| NETWORK | Comunicação externa controlada |
| PASSWORD | Geração segura e proteção de senhas |
| URL | Análise estrutural sem acesso automático ao destino |
| PROCESS | Consulta sem interferência nos processos |
| HISTORY | Proteção e integridade dos registros |

O MVP não será considerado um antivírus ou uma solução completa de proteção de endpoints.

# 3. Princípios de segurança

O Odyssey AV deverá seguir os seguintes princípios:

- **Menor privilégio:** utilizar somente as permissões necessárias.
- **Validação de entradas:** validar parâmetros e dados recebidos.
- **Privacidade:** evitar armazenar informações sensíveis sem necessidade.
- **Transparência:** informar quando uma operação realizar comunicação externa.
- **Não destrutividade:** não modificar, excluir ou colocar arquivos em quarentena automaticamente.
- **Isolamento:** uma falha em determinado módulo não deverá comprometer desnecessariamente os demais.
- **Tratamento seguro de erros:** não expor informações sensíveis em mensagens ou logs.
- **Integridade:** preservar a consistência dos dados e resultados armazenados.
- **Previsibilidade:** executar somente operações correspondentes à solicitação explícita do usuário.
- **Disponibilidade controlada:** permitir operações funcionais em modo degradado sem ocultar a indisponibilidade do histórico.

# 4. Segurança por módulo

## 4.1. FILE — Análise de arquivos

**Principais riscos:**

- Acesso indevido a arquivos.
- Leitura de arquivos sem permissão.
- Consumo excessivo de memória.
- Interpretação incorreta de formatos.
- Acesso involuntário a recursos especiais do sistema de arquivos.
- Alteração ou desaparecimento do arquivo durante a análise.

**Controles:**

- Validar os caminhos recebidos.
- Respeitar as permissões do sistema operacional.
- Aceitar somente arquivos regulares.
- Rejeitar diretórios.
- Não seguir links simbólicos automaticamente.
- Rejeitar dispositivos, sockets e pipes.
- Tratar arquivos que desapareçam ou sejam modificados durante a análise.
- Processar arquivos em blocos quando necessário.
- Não executar arquivos analisados.
- Não modificar o conteúdo dos arquivos.
- Identificar limitações de formatos não suportados.
- Não apresentar identificação de assinatura como prova de segurança.
- Abrir o arquivo somente para leitura, sem nenhum modo de escrita.
- Verificar o tipo do arquivo pelo descritor aberto (`os.fstat`) antes de qualquer leitura de conteúdo.
- Comparar o número de bytes lidos com o tamanho informado pelo `fstat`. Divergência gera erro de alteração durante a leitura, sem resultado enganoso.
- Ler apenas o cabeçalho necessário para identificar o formato, com limite de bytes definido na implementação.

As proteções contra alteração e exclusão de arquivos estão detalhadas na seção 4.8.

A análise deverá trabalhar sobre o conteúdo do arquivo, sem executar seu código ou conteúdo incorporado.

## 4.2. HASH — Hash

**Principais riscos:**

- Comparações incorretas.
- Uso de referências não confiáveis.
- Leitura inadequada de arquivos.
- Interpretação equivocada de correspondência como garantia de segurança.

**Controles:**

- Utilizar SHA-256.
- Calcular o hash a partir dos bytes reais do arquivo.
- Validar o formato da referência fornecida.
- Utilizar exclusivamente a referência informada pelo usuário.
- Não manter base própria de hashes no MVP.
- Não considerar correspondência como prova absoluta de segurança.
- Não modificar o arquivo original.

A comparação deverá distinguir `MATCH`, `MISMATCH` e `NO_REFERENCE`.

## 4.3. NETWORK — Diagnóstico de rede

**Principais riscos:**

- Comunicação externa não autorizada.
- Exposição de informações durante consultas externas.
- Indisponibilidade de serviços.
- Operações sem limite de tempo.
- Comunicação oculta em segundo plano.

**Controles:**

- Executar verificações somente quando solicitadas.
- Informar quando houver comunicação externa.
- Aplicar timeout nas operações de rede.
- Tratar falhas e indisponibilidade de serviços.
- Não realizar varreduras de portas de terceiros.
- Não manter comunicação oculta em segundo plano.
- Tornar opcional a consulta de IP público.
- Identificar o serviço externo utilizado na consulta de IP público na documentação da implementação.

Operações locais não deverão iniciar comunicações externas implícitas.

## 4.4. PASSWORD — Ferramentas de senha

**Principais riscos:**

- Exposição de senhas em logs.
- Persistência acidental de senhas.
- Geração de valores previsíveis.
- Exposição de senhas em relatórios.
- Vazamento por argumentos ou mensagens de erro.

**Controles:**

- Utilizar o módulo `secrets` para geração.
- Não armazenar senhas geradas ou avaliadas.
- Não incluir senhas no histórico.
- Não registrar senhas nos logs.
- Não incluir senhas em relatórios exportados.
- Não persistir senhas em argumentos de comandos.
- Não incluir senhas em mensagens de erro, resumos ou resultados estruturados.
- Evitar exibir valores sensíveis desnecessariamente.
- Realizar a avaliação localmente, sem envio a serviços externos.

A execução do módulo poderá ser registrada, desde que sejam armazenados somente metadados operacionais e informações sanitizadas.

A proteção deverá abranger também dados que permitam recuperar indiretamente o valor da senha.

Em modo degradado, o módulo poderá executar normalmente, mas não deverá tentar persistir dados da operação.

## 4.5. URL — Análise de URL

**Principais riscos:**

- Acesso involuntário a destinos externos.
- Interpretação incorreta de endereços.
- Identificação equivocada de URLs suspeitas.
- Execução de conteúdo associado a endereços analisados.

**Controles:**

- Realizar análise estrutural local.
- Normalizar e validar URLs.
- Não acessar automaticamente os endereços analisados.
- Não executar scripts ou conteúdo associado às URLs.
- Não realizar consultas DNS implícitas.
- Apresentar indicadores como suspeitas, não como confirmação de ameaça.

## 4.6. PROCESS — Monitoramento de processos

**Principais riscos:**

- Acesso a informações sem permissão.
- Exposição de informações de processos.
- Interferência indevida em processos do sistema.
- Indisponibilidade de processos durante a consulta.

**Controles:**

- Consultar somente informações acessíveis ao usuário.
- Respeitar as permissões do sistema operacional.
- Informar quando determinadas métricas não estiverem disponíveis.
- Tratar processos encerrados durante a consulta.
- Não encerrar, suspender ou modificar processos.
- Não injetar código em processos.
- Não solicitar privilégios administrativos automaticamente.

## 4.7. HISTORY — Histórico e relatórios

**Principais riscos:**

- Exposição de informações sensíveis.
- Alteração ou perda de registros.
- Persistência acidental de dados temporários.
- Exportação de informações inadequadas.
- Inconsistência entre execuções e resultados.
- Registros indefinidamente no estado `RUNNING`.
- Recuperação incompleta de registros antigos.
- Apresentação enganosa da disponibilidade do histórico.

**Controles:**

- Utilizar consultas parametrizadas no SQLite.
- Não persistir senhas.
- Não armazenar conteúdo integral de arquivos.
- Sanitizar mensagens e resumos.
- Não registrar argumentos que contenham segredos.
- Exportar somente informações permitidas.
- Preservar a integridade dos relacionamentos entre execuções e resultados.
- Utilizar transações nas operações de persistência.
- Identificar cada instância por UUID.
- Recuperar execuções anteriores em `RUNNING`, utilizando `INTERRUPTED`.
- Não gerar registros recursivos durante consultas e exportações.
- Não disponibilizar consultas ou exportações quando a recuperação do histórico falhar.
- Não realizar novas gravações no banco enquanto a aplicação estiver em modo degradado.
- Informar explicitamente a indisponibilidade do histórico.

## 4.8. Proteção contra alteração e exclusão de arquivos

**Princípio:** a análise de arquivos é somente leitura. Nenhum módulo do Odyssey AV pode modificar ou excluir o arquivo analisado, nem o diretório que o contém (RN-001, RF-029).

**Principais riscos:**

- Alteração acidental do conteúdo por abertura em modo de escrita.
- Exclusão acidental por chamada indevida de remoção de arquivos.
- Leitura de um arquivo diferente do pretendido, por meio de link simbólico.
- Alteração do arquivo durante a leitura, por outro processo.
- Análise de bancos ou arquivos internos do próprio aplicativo.

**Controles obrigatórios:**

- Abrir o arquivo somente para leitura, sem nenhum modo de escrita (`O_RDONLY` ou `"rb"`).
- Verificar o tipo do arquivo pelo descritor aberto (`os.fstat`) antes de qualquer leitura de conteúdo.
- Rejeitar links simbólicos e tratar a abertura sem seguir o link, quando a plataforma permitir (`O_NOFOLLOW`).
- Comparar o número de bytes lidos com o tamanho informado pelo `fstat`. Divergência gera erro de alteração durante a leitura, sem resultado enganoso.
- Não utilizar, no pacote de análise, chamadas de exclusão (`os.remove`, `os.unlink`, `os.rmdir`, `shutil.rmtree`) nem abertura em modo de escrita.
- Recusar caminhos localizados no diretório de dados do próprio aplicativo, que contém o banco de histórico e o arquivo de bloqueio.

**Verificação:**

- Teste de integridade (ST-026): hash, tamanho e data de modificação do arquivo são iguais antes e depois da análise.
- Teste de varredura estática (ST-027): o código de `modules/` não contém chamadas de exclusão nem modos de escrita sobre o arquivo analisado.
- Teste de caminho sensível (ST-028): a análise do banco de histórico é recusada antes de qualquer leitura de conteúdo.

**Limitações conhecidas:**

- O horário de último acesso (`atime`) pode ser atualizado pelo sistema operacional durante a leitura. Esse comportamento não altera o conteúdo do arquivo e não é controlado pelo aplicativo.
- No Windows, `os.open` segue links simbólicos. A proteção depende da verificação de tipo pelo descritor, registrada em DOC-01.

# 5. Proteção de dados

O Odyssey AV deverá armazenar somente os dados necessários para seu funcionamento e para a consulta do histórico.

## 5.1. Dados que podem ser armazenados

- Identificador da execução.
- Identificador da instância.
- Módulo utilizado.
- Comando normalizado.
- Estado da execução.
- Data e horário.
- Duração, quando disponível.
- Resultados estruturados das análises.
- Mensagens técnicas sanitizadas.

## 5.2. Dados que não devem ser armazenados

- Senhas geradas.
- Senhas avaliadas.
- Conteúdo integral de arquivos analisados.
- Segredos presentes nos argumentos.
- Informações pessoais desnecessárias.
- Dados sensíveis desnecessários ao histórico.
- Informações que permitam reconstruir indiretamente valores protegidos.

## 5.3. Sanitização

Antes da persistência, os dados deverão ser avaliados para impedir a exposição de informações sensíveis.

A sanitização deverá contemplar:

- Comandos e argumentos.
- Mensagens de erro.
- Resumos das execuções.
- Dados estruturados dos resultados.
- Informações utilizadas em relatórios.

A sanitização não deverá substituir a minimização de dados: informações desnecessárias não deverão ser coletadas ou encaminhadas à persistência.

## 5.4. Logs

Os logs deverão registrar informações úteis para diagnóstico técnico.

Não deverão ser utilizados como substitutos do histórico de execuções.

Senhas, tokens, segredos e outros dados sensíveis não poderão aparecer nos registros.

# 6. Segurança da persistência

A aplicação utilizará SQLite para armazenar o histórico local.

**Controles obrigatórios:**

- Utilizar consultas parametrizadas.
- Ativar e verificar as restrições de chave estrangeira.
- Utilizar transações nas operações de persistência.
- Tratar falhas de leitura e escrita.
- Evitar corrupção e inconsistência dos registros.
- Não expor diretamente os dados internos do banco pela CLI.
- Centralizar o acesso ao banco na camada de infraestrutura.
- Respeitar o relacionamento entre `AnalysisRun` e `AnalysisResult`.
- Evitar persistência de informações sensíveis.

## 6.1. Falha de persistência durante uma operação

A falha ao registrar uma operação não deverá ser confundida com falha funcional.

A aplicação deverá distinguir:

- Resultado da operação solicitada.
- Resultado da tentativa de persistência.

Exemplo:

```text
Operação HASH:
    Resultado funcional: SUCCESS

Persistência:
    Resultado do histórico: FAILED

Comunicação:
    Operação concluída, mas não foi possível registrar o histórico.
```

A CLI deverá informar claramente as duas situações.

O sistema não deverá afirmar que os dados foram registrados quando a persistência não tiver sido confirmada.

Durante uma sessão iniciada em `NORMAL`, a falha será tratada por operação e não provocará transição automática para `DEGRADED`. As operações funcionais subsequentes permanecerão disponíveis e deverão tentar persistir normalmente. Não haverá fila em memória nem armazenamento alternativo; dados cuja gravação falhou não serão recuperados posteriormente, e registros anteriormente confirmados permanecerão inalterados.

Consultas e exportações `HISTORY` dependem da disponibilidade do SQLite. Se uma consulta ou exportação falhar, a aplicação deverá informar erro da operação solicitada. Essa falha não deverá ser confundida com uma operação funcional bem-sucedida cuja gravação falhou.

## 6.2. Falha durante a recuperação do histórico

A recuperação do histórico é uma condição necessária para iniciar o funcionamento normal da aplicação.

Se o SQLite estiver indisponível ou ocorrer falha que impeça a conclusão da recuperação, a aplicação deverá entrar em modo degradado.

O modo degradado deverá obedecer aos seguintes controles:

1. O bloqueio exclusivo da aplicação deverá permanecer ativo.
2. A falha deverá ser comunicada claramente ao usuário.
3. As ferramentas FILE, HASH, NETWORK, PASSWORD, URL e PROCESS poderão continuar disponíveis.
4. Nenhuma nova gravação no histórico deverá ser realizada durante a sessão.
5. O HISTORY deverá ficar indisponível para consultas e exportações.
6. Nenhuma execução deverá ser apresentada como persistida.
7. A aplicação deverá informar que os resultados da sessão não serão armazenados.
8. A falha de recuperação não deverá ser ocultada ou tratada como recuperação bem-sucedida.
9. A aplicação não deverá utilizar armazenamento alternativo no MVP.
10. A recuperação deverá ser tentada novamente em uma inicialização posterior.

A aplicação não deverá tentar corrigir parcialmente o histórico e prosseguir como se a recuperação tivesse sido concluída.

A transação de recuperação deverá garantir que alterações incompletas sejam revertidas quando aplicável.

Se a transação falhar, os registros deverão permanecer conforme o estado efetivamente confirmado pelo banco.

O modo degradado representa uma condição operacional limitada, e não uma garantia de integridade do histórico.

# 7. Segurança de entradas e execução

Todas as entradas recebidas deverão ser tratadas como dados não confiáveis.

A aplicação deverá:

- Validar caminhos e parâmetros.
- Validar URLs antes de interpretá-las.
- Validar parâmetros de geração de senhas.
- Validar filtros de processos.
- Utilizar consultas SQL parametrizadas.
- Evitar execução de comandos do sistema operacional construídos a partir de entradas do usuário.
- Tratar exceções sem expor informações internas desnecessárias.
- Evitar que entradas inválidas provoquem operações inesperadas.
- Impedir que arquivos analisados sejam executados.

A validação deverá ocorrer nas fronteiras adequadas da aplicação, sem concentrar todas as regras na interface CLI.

# 8. Permissões do sistema operacional

O Odyssey AV deverá funcionar com as permissões normais do usuário sempre que possível.

Não deverá solicitar privilégios administrativos automaticamente.

Quando uma operação depender de permissões adicionais, o sistema deverá informar a limitação.

A ausência de acesso a determinado arquivo ou processo não deverá ser interpretada como ausência de risco.

As diferenças entre Windows e Linux deverão ser consideradas na implementação dos adaptadores de plataforma.

# 9. Segurança da instância e concorrência

## 9.1. Instância única

O MVP deverá permitir somente uma instância ativa do Odyssey AV por vez.

A aplicação deverá utilizar um mecanismo de bloqueio exclusivo compatível com Windows e Linux.

Uma nova inicialização não deverá executar operações funcionais enquanto outra instância mantiver o bloqueio.

## 9.2. Identificação da instância

Cada inicialização válida deverá receber um UUID próprio (`instance_id`).

As execuções deverão estar associadas à instância responsável por sua criação.

O identificador deverá permitir distinguir registros de inicializações diferentes, sem depender exclusivamente do PID.

## 9.3. Recuperação de execuções interrompidas

Após obter o bloqueio exclusivo, a aplicação deverá verificar execuções anteriores que permaneceram em `RUNNING`.

As execuções pertencentes a instâncias anteriores deverão ser atualizadas para `INTERRUPTED`.

O mecanismo deverá evitar que uma execução de outra instância ativa seja marcada incorretamente como interrompida.

A recuperação deverá ser transacional.

## 9.4. Liberação do bloqueio

O bloqueio deverá ser liberado no encerramento normal da aplicação.

Em encerramentos inesperados, deverá ser utilizado um mecanismo do sistema operacional que permita liberar o bloqueio quando o processo responsável deixar de existir.

O bloqueio não deverá depender de um arquivo de estado permanente que impeça a inicialização após uma falha.

# 10. Estado operacional da aplicação

O estado operacional da aplicação deverá ser separado dos estados de execução armazenados no banco.

| Estado | Significado |
|---|---|
| `NORMAL` | Recuperação transacional inicial concluída; operações funcionais e tentativas de persistência habilitadas |
| `DEGRADED` | Recuperação transacional falhou durante a inicialização; novas gravações e operações HISTORY desabilitadas durante a sessão |

Esses estados não substituem `RUNNING`, `SUCCESS`, `PARTIAL`, `FAILED` ou `INTERRUPTED`.

## 10.1. Regras de segurança do modo degradado

- O modo degradado deverá ser informado antes da execução dos comandos funcionais.
- O usuário deverá saber que o histórico está indisponível.
- As operações funcionais permitidas não poderão tentar gravar no SQLite.
- O HISTORY deverá recusar consultas e exportações.
- Os resultados não poderão ser apresentados como armazenados.
- O bloqueio exclusivo deverá continuar ativo.
- A aplicação não deverá tentar recuperar o banco em segundo plano no MVP.
- A próxima inicialização deverá tentar novamente a recuperação.

A execução funcional em modo degradado não deverá reduzir os controles de segurança próprios de cada módulo.

# 11. Matriz de ameaças

| ID | Ameaça | Impacto | Controle |
|---|---|---|---|
| SEC-001 | Exposição de senhas | Alto | Não persistir senhas nem registrá-las em logs, argumentos ou relatórios |
| SEC-002 | Execução acidental de arquivo analisado | Alto | Nunca executar arquivos analisados |
| SEC-003 | Acesso indevido a arquivos | Alto | Validar caminhos, rejeitar recursos especiais e respeitar permissões |
| SEC-004 | SQL Injection | Alto | Utilizar consultas parametrizadas |
| SEC-005 | Comunicação externa inesperada | Médio | Operações externas explícitas e identificáveis |
| SEC-006 | Consumo excessivo de recursos | Médio | Processamento controlado e limites operacionais |
| SEC-007 | Exposição de dados no histórico | Alto | Minimização e sanitização dos dados |
| SEC-008 | Interferência em processos | Alto | Permitir somente consulta e listagem |
| SEC-009 | Interpretação incorreta de ameaças | Médio | Apresentar limitações e indicadores como suspeitas |
| SEC-010 | Falha na persistência | Médio | Transações, tratamento de erros e separação do resultado funcional |
| SEC-011 | Recuperação incompleta do histórico | Alto | Transação de recuperação e modo degradado |
| SEC-012 | Histórico apresentado como disponível sem consistência | Alto | Bloquear HISTORY e novas gravações enquanto degradado |
| SEC-013 | Alteração acidental do arquivo analisado | Alto | Abertura somente leitura, verificação de tipo pelo descritor e teste de integridade (ST-026) |
| SEC-014 | Exclusão acidental de arquivos pelo aplicativo | Alto | Proibição de chamadas de remoção no pacote de análise, verificada por varredura estática (ST-027) |
| SEC-015 | Análise de arquivos internos do aplicativo | Médio | Recusa de caminhos no diretório de dados (ST-028) |

# 12. Tratamento de falhas de segurança

Quando uma operação apresentar falha relacionada à segurança, a aplicação deverá:

1. Interromper a operação quando necessário.
2. Evitar ações destrutivas ou efeitos colaterais.
3. Apresentar uma mensagem compreensível.
4. Registrar informações técnicas sem expor dados sensíveis, quando a persistência estiver disponível.
5. Preservar os resultados que puderem ser armazenados com segurança.
6. Distinguir limitações de acesso de resultados negativos de análise.
7. Informar separadamente falhas funcionais e falhas de persistência.
8. Comunicar o modo degradado quando a recuperação do histórico falhar.

A aplicação não deverá apresentar uma análise incompleta como se tivesse sido concluída integralmente.

# 13. Testes de segurança

O MVP deverá possuir testes para verificar os controles principais.

| ID | Teste | Resultado esperado |
|---|---|---|
| ST-001 | Analisar arquivo sem permissão | Erro tratado sem interromper indevidamente a aplicação |
| ST-002 | Analisar arquivo suspeito | Arquivo não executado ou modificado |
| ST-003 | Informar entrada inválida | Entrada rejeitada |
| ST-004 | Gerar senha | Senha não aparece no histórico ou logs |
| ST-005 | Avaliar senha | Valor não é persistido |
| ST-006 | Analisar URL | Nenhuma requisição automática ao destino |
| ST-007 | Consultar processos | Nenhum processo é modificado |
| ST-008 | Consultar histórico | Dados consultados sem exposição de segredos |
| ST-009 | Exportar histórico | Senhas e dados sensíveis são excluídos |
| ST-010 | Consultar SQLite | Entradas não alteram a estrutura das consultas |
| ST-011 | Analisar diretório | Recurso rejeitado |
| ST-012 | Analisar link simbólico | Link não seguido automaticamente |
| ST-013 | Analisar dispositivo, socket ou pipe | Recurso rejeitado |
| ST-014 | Modificar ou remover arquivo durante leitura | Situação tratada sem resultado enganoso |
| ST-015 | Iniciar segunda instância | Nova instância impedida de executar operações |
| ST-016 | Encerrar instância inesperadamente | Execuções anteriores em `RUNNING` recuperadas como `INTERRUPTED` |
| ST-017 | Simular falha no SQLite durante operação | Resultado funcional preservado e falha de histórico comunicada |
| ST-018 | Informar segredo em argumento ou entrada | Segredo não aparece em histórico, logs ou mensagens persistidas |
| ST-019 | Simular falha de leitura durante recuperação | Aplicação inicia em modo degradado |
| ST-020 | Simular falha ao atualizar `RUNNING` para `INTERRUPTED` | Transação revertida quando aplicável e aplicação em modo degradado |
| ST-021 | Executar módulo funcional em modo degradado | Operação permitida sem tentativa de persistência |
| ST-022 | Consultar HISTORY em modo degradado | Operação recusada com mensagem clara |
| ST-023 | Inicializar novamente após corrigir o SQLite | Recuperação executada antes do funcionamento normal |
| ST-024 | Verificar registros após falha de recuperação | Nenhum registro apresentado como recuperado sem confirmação |
| ST-026 | Analisar arquivo e comparar estado antes e depois | Hash, tamanho e data de modificação iguais; nenhuma alteração do arquivo |
| ST-027 | Varrer o código de `modules/` em busca de chamadas de exclusão e modos de escrita | Nenhuma ocorrência fora de contextos permitidos |
| ST-028 | Analisar o arquivo de histórico do próprio aplicativo | Operação recusada antes de qualquer leitura de conteúdo |

Os testes deverão ser executados em ambientes Windows e Linux sempre que o comportamento depender de particularidades da plataforma.

# 14. Limites de segurança do MVP

O Odyssey AV não deverá ser considerado um antivírus ou uma solução completa de proteção de endpoints.

O MVP não implementará:

- Proteção em tempo real.
- Quarentena automática.
- Exclusão automática de arquivos.
- Análise comportamental.
- Execução controlada de malware.
- Drivers de kernel.
- Monitoramento remoto obrigatório.
- Inteligência artificial para classificação de ameaças.
- Varredura ou exploração de portas de terceiros.
- Comunicação oculta em segundo plano.
- Alteração do horário de último acesso (`atime`) pelo sistema operacional durante a leitura.
- Garantia de integridade de arquivos modificados por outros processos durante a análise. O aplicativo detecta divergência de tamanho, mas não impede a alteração.

A identificação de indicadores suspeitos não representa confirmação de malware.

A identificação de uma assinatura de arquivo também não representa validação integral de seu conteúdo ou garantia de segurança.

# 15. Referências técnicas

As seguintes fontes deverão orientar a implementação e a revisão dos controles:

- OWASP — princípios e boas práticas de segurança de aplicações.
- Python Documentation — `hashlib`, `secrets` e tratamento de arquivos.
- SQLite Documentation — consultas parametrizadas, transações e chaves estrangeiras.
- Typer Documentation — interface de linha de comando.
- psutil Documentation — consulta de processos.
- Regras de negócio do Odyssey AV.
- Requisitos funcionais e não funcionais do Odyssey AV.
- Arquitetura do Odyssey AV.
- Modelo de dados do Odyssey AV.

As referências deverão ser complementadas com links e versões específicas durante a implementação, quando as dependências e APIs utilizadas forem definidas.

# 16. Rastreabilidade

| Elemento | Referências relacionadas |
|---|---|
| Proteção de senhas | RF-016, RN-005 |
| Recuperação de execuções | RN-009 |
| Separação entre operação e persistência | RN-013 |
| Modo degradado após falha de recuperação na inicialização | RF-033, RN-009, DOM-011, ARC-013 |
| Bloqueio de consultas HISTORY em modo degradado | RF-033, DOM-011, ARC-013 |
| Falha de persistência durante sessão NORMAL | RF-032, RN-013 |

# 17. Estado do documento

| Critério | Situação |
|---|---|
| Princípios de segurança | Definidos |
| Segurança por módulo | Definida |
| Proteção de dados | Definida |
| Sanitização | Definida conceitualmente |
| Proteção de entradas | Definida |
| Segurança da persistência | Definida |
| Falha de persistência | Tratamento definido |
| Falha de recuperação | Tratamento definido |
| Modo degradado | Definido |
| Permissões do sistema operacional | Definidas |
| Instância única | Definida |
| Recuperação de execuções | Definida |
| Matriz de ameaças | Atualizada |
| Testes de segurança | Especificados |
| Limites do MVP | Definidos |
| Revisão cruzada | Concluída |
| Proteção contra alteração e exclusão de arquivos | Definida (seção 4.8) |

---

**Observação final:** este documento especifica os controles de segurança do MVP. A implementação física dos mecanismos de persistência, bloqueio exclusivo, recuperação e modo degradado será realizada conforme o backlog, após a aprovação da documentação e autorização para iniciar o desenvolvimento.
