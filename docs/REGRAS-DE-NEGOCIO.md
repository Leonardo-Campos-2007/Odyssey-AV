# REGRAS-DE-NEGOCIO.md

**Projeto:** Odyssey AV  
**Versão:** 2.0  
**Escopo:** MVP  
**Status:** Consolidado para revisão

---

# 1. Objetivo

Este documento define as regras de negócio que determinam como o Odyssey AV deverá se comportar durante suas operações de análise, diagnóstico, consulta e geração de relatórios.

As regras são independentes da tecnologia utilizada e deverão ser respeitadas por todos os módulos do sistema.

O MVP contempla sete módulos:

- FILE — Análise de arquivos.
- HASH — Cálculo e comparação de hashes.
- NETWORK — Diagnóstico de rede.
- PASSWORD — Ferramentas de senha.
- URL — Análise de URLs.
- PROCESS — Monitoramento de processos.
- HISTORY — Histórico e relatórios.

# 2. Regras gerais de segurança e operação

## RN-001 — Ausência de ações destrutivas automáticas

O Odyssey AV não deverá executar ações destrutivas automaticamente.

No MVP, as ferramentas terão caráter de análise, diagnóstico e consulta. Não será permitido excluir, modificar, colocar em quarentena ou alterar arquivos e recursos do sistema.

**Aplicação:** todos os módulos.

**Consequência:**

- As operações disponíveis não deverão modificar os recursos analisados.
- O sistema não deverá executar ações corretivas automaticamente.
- A análise de um recurso não deverá provocar sua alteração ou exclusão.
- O monitoramento de processos deverá permanecer exclusivamente informativo.

## RN-002 — Integridade do cálculo de hash

O cálculo de hash deverá ser realizado sobre os bytes reais do conteúdo do arquivo, independentemente de seu nome, extensão ou caminho.

**Aplicação:** módulo HASH.

**Consequência:**

- Arquivos com conteúdos idênticos deverão produzir o mesmo hash utilizando o mesmo algoritmo.
- Alterações no conteúdo deverão refletir-se no resultado do cálculo.
- A extensão ou o nome do arquivo não deverão interferir no cálculo.
- O algoritmo previsto para o MVP será SHA-256.

## RN-003 — Indicadores suspeitos não representam confirmação de malware

A identificação de características suspeitas não deverá ser apresentada como confirmação de que um arquivo, URL ou processo contém malware.

**Aplicação:** módulos FILE, HASH, URL e PROCESS.

**Consequência:**

- Os resultados deverão distinguir indicadores, divergências e suspeitas de uma detecção efetivamente confirmada.
- O Odyssey AV deverá informar limitações de análise.
- O sistema deverá evitar classificações conclusivas sem evidências suficientes.
- A identificação de uma assinatura ou divergência de extensão não deverá ser apresentada como comprovação de segurança ou infecção.

## RN-004 — Classificação de comparação de hashes

A comparação de hashes deverá apresentar resultados distintos para cada situação:

| Estado | Significado |
|---|---|
| `MATCH` | Hash correspondente à referência |
| `MISMATCH` | Hash diferente da referência |
| `NO_REFERENCE` | Nenhuma referência fornecida para comparação |

**Aplicação:** módulo HASH.

**Consequência:**

- A ausência de uma referência não poderá ser interpretada como divergência.
- A correspondência de hashes não deverá ser apresentada como prova absoluta de segurança.
- A referência utilizada deverá ser informada pelo usuário.
- O MVP não manterá uma base própria de hashes.

# 3. Regras de privacidade e dados

## RN-005 — Não persistência de senhas

Senhas geradas ou avaliadas pelo Odyssey AV não deverão ser armazenadas no histórico, nos logs ou nos relatórios exportados.

**Aplicação:** módulo PASSWORD.

**Consequência:**

- O resultado da avaliação poderá apresentar informações sobre características da senha, sem revelar seu conteúdo.
- Senhas geradas não deverão ser persistidas.
- Senhas avaliadas não deverão ser persistidas.
- Senhas não deverão aparecer em argumentos registrados.
- Senhas não deverão aparecer em mensagens de erro, resumos ou logs.
- Senhas não deverão ser incluídas em `AnalysisResult.data`.
- Senhas não deverão ser incluídas em relatórios exportados.
- A execução do módulo poderá ser registrada, desde que sejam armazenados somente metadados operacionais e informações sanitizadas.

O histórico deverá permitir identificar que uma operação PASSWORD ocorreu, sem armazenar o valor da senha.

## RN-006 — Análise local de URLs

A análise de URLs deverá ocorrer localmente, considerando sua estrutura e características identificáveis sem acessar automaticamente o endereço informado.

**Aplicação:** módulo URL.

**Consequência:**

- O módulo não deverá realizar requisições HTTP automaticamente.
- O módulo não deverá realizar consultas DNS automaticamente.
- O módulo não deverá acessar o destino informado.
- A análise deverá limitar-se às informações disponíveis no próprio endereço.
- Indicadores suspeitos deverão ser apresentados como sinais de atenção, não como confirmação de ameaça.

## RN-007 — Operações externas de rede identificáveis

Toda operação que envolva comunicação com recursos externos deverá ser identificável pelo usuário e decorrer de uma ação explícita.

**Aplicação:** módulo NETWORK e demais operações que eventualmente utilizem recursos externos.

**Consequência:**

- O diagnóstico de rede poderá executar verificações externas quando o usuário invocar explicitamente o comando correspondente.
- Consultas DNS e conectividade deverão ser identificadas como operações de rede.
- A consulta de IP público deverá ser opcional.
- Nenhuma comunicação externa deverá ocorrer de maneira oculta.
- A análise local de arquivos, hashes, senhas e URLs não deverá iniciar operações externas inesperadas.
- Falhas de comunicação deverão ser apresentadas como limitações ou falhas da operação de rede.

# 4. Regras dos módulos

## RN-008 — Monitoramento de processos somente para consulta

O módulo de processos deverá limitar-se à listagem e consulta de informações dos processos acessíveis ao usuário.

**Aplicação:** módulo PROCESS.

**Consequência:** o Odyssey AV não poderá:

- Encerrar processos.
- Suspender ou retomar processos.
- Alterar prioridades.
- Injetar código.
- Modificar a execução de processos.

O módulo terá finalidade exclusivamente informativa no MVP.

A impossibilidade de consultar determinado processo por falta de permissão ou indisponibilidade deverá ser comunicada ao usuário.

# 5. Regras de histórico e relatórios

## RN-009 — Registro e recuperação das execuções

As execuções funcionais dos módulos deverão ser registradas no histórico, incluindo operações concluídas com sucesso, parcialmente concluídas ou malsucedidas.

**Aplicação:** persistência transversal e módulo HISTORY.

**Consequência:**

- Execuções bem-sucedidas deverão ser registradas.
- Execuções parciais deverão preservar os resultados efetivamente obtidos.
- Execuções com falhas deverão registrar as informações disponíveis e sanitizadas sobre a falha.
- O histórico deverá permitir identificar o módulo, o comando normalizado e o estado da execução.
- Execuções PASSWORD deverão ser registradas sem persistir o conteúdo das senhas.
- Consultas e exportações do módulo HISTORY não deverão gerar novos registros `AnalysisRun`.

### Estados de execução

O histórico deverá reconhecer os seguintes estados:

- `RUNNING`
- `SUCCESS`
- `PARTIAL`
- `FAILED`
- `INTERRUPTED`

### Recuperação de execuções

Uma execução interrompida inesperadamente não deverá permanecer indefinidamente apresentada como concluída ou bem-sucedida.

A aplicação deverá identificar execuções anteriores que permaneceram em `RUNNING` após encerramento inesperado e atualizá-las para `INTERRUPTED`, quando for possível determinar que pertencem a uma instância encerrada.

O MVP adotará uma única instância ativa do Odyssey AV por vez, utilizando mecanismo de bloqueio exclusivo compatível com Windows e Linux.

O identificador lógico da instância deverá ser utilizado para associar as execuções à inicialização correspondente. A recuperação não deverá depender exclusivamente do PID do sistema operacional.

O estado `INTERRUPTED` não deverá ser interpretado automaticamente como falha funcional.

## RN-010 — Minimização e proteção de dados persistidos

O Odyssey AV deverá armazenar somente os dados necessários para manter o histórico e permitir a consulta dos resultados.

**Aplicação:** todos os módulos.

**Consequência:**

- Não armazenar o conteúdo integral dos arquivos analisados.
- Não armazenar senhas.
- Não armazenar argumentos que contenham segredos.
- Não armazenar informações sensíveis sem necessidade funcional.
- Não incluir dados sensíveis desnecessários em resumos ou mensagens de erro.
- Sanitizar mensagens antes da persistência.
- Evitar dados que permitam recuperar indiretamente informações que deveriam ser protegidas.
- Não armazenar conteúdo desnecessário de processos, arquivos ou recursos analisados.

Os registros deverão utilizar comandos normalizados, evitando armazenar argumentos potencialmente sensíveis.

## RN-013 — Separação entre resultado funcional e persistência

O resultado funcional de uma operação deverá ser tratado separadamente da situação de persistência do histórico.

**Aplicação:** aplicação, infraestrutura de persistência e CLI.

**Consequência:**

- Uma operação poderá ser concluída com sucesso mesmo quando o SQLite estiver indisponível para registrar seu resultado.
- A falha de persistência não deverá transformar automaticamente uma operação funcional bem-sucedida em uma falha funcional.
- A aplicação deverá comunicar separadamente o resultado da operação e a situação do histórico.
- O sistema não deverá afirmar que o histórico foi salvo quando a persistência não tiver sido confirmada.
- A CLI deverá utilizar o código de saída previsto para operação concluída com falha de persistência.
- Informações não persistidas não poderão ser apresentadas como se estivessem disponíveis no histórico.

A separação deverá ser preservada tanto na saída textual quanto na saída estruturada em JSON.

# 6. Regras de exportação

## RN-011 — Exportação limitada aos dados disponíveis

Os relatórios exportados deverão conter somente informações efetivamente registradas e selecionadas para exportação.

**Aplicação:** módulo HISTORY.

**Consequência:**

- A exportação deverá respeitar os dados disponíveis no histórico.
- Informações inexistentes não poderão ser inventadas ou inferidas.
- Dados sensíveis deverão ser excluídos.
- Senhas nunca poderão aparecer em relatórios.
- Argumentos secretos não deverão ser exportados.
- Os formatos previstos para o MVP serão JSON e CSV.
- A exportação deverá respeitar os filtros solicitados pelo usuário.
- Falhas na exportação deverão ser comunicadas sem apresentar arquivos incompletos como relatórios concluídos.

# 7. Regras de confiabilidade

## RN-012 — Transparência sobre limitações de acesso

O Odyssey AV deverá informar quando não conseguir acessar, consultar ou analisar determinado recurso por limitações de permissão, plataforma ou disponibilidade.

**Aplicação:** todos os módulos.

**Consequência:**

- Falta de permissão não deverá ser interpretada como ausência de risco.
- Informações indisponíveis deverão ser identificadas como não verificadas.
- O sistema não deverá apresentar resultados incompletos como análises completas.
- Limitações específicas do Windows e Linux deverão ser comunicadas adequadamente.
- Processos que encerrarem durante a consulta deverão ser tratados como dados indisponíveis.
- Falhas de acesso a arquivos deverão ser diferenciadas de resultados negativos de análise.

# 8. Matriz de rastreabilidade

| Regra | Módulo relacionado | Objetivo principal |
|---|---|---|
| RN-001 | Todos | Evitar ações destrutivas |
| RN-002 | HASH | Garantir cálculo correto |
| RN-003 | FILE, HASH, URL, PROCESS | Evitar conclusões indevidas |
| RN-004 | HASH | Diferenciar estados de comparação |
| RN-005 | PASSWORD | Proteger senhas |
| RN-006 | URL | Evitar acessos externos automáticos |
| RN-007 | NETWORK | Controlar operações externas |
| RN-008 | PROCESS | Restringir operações a consultas |
| RN-009 | Todos, HISTORY | Preservar e recuperar histórico |
| RN-010 | Todos | Minimizar dados persistidos |
| RN-011 | HISTORY | Controlar exportações |
| RN-012 | Todos | Comunicar limitações |
| RN-013 | Aplicação e infraestrutura | Separar operação e persistência |

# 9. Observações para implementação

As regras acima definem o comportamento esperado do sistema. Os mecanismos técnicos para garanti-las serão detalhados nos documentos de arquitetura, segurança e testes.

| Regra | Mecanismo técnico relacionado |
|---|---|
| RN-002 | `hashlib` e leitura binária |
| RN-005 | Exclusão de senhas dos registros e relatórios |
| RN-006 | Separação entre parsing local e operações de rede |
| RN-007 | Controle explícito das operações externas |
| RN-009 | Identificação de instância, bloqueio exclusivo e recuperação de execuções |
| RN-010 | Sanitização de dados e logs |
| RN-011 | Seleção e filtragem dos campos exportados |
| RN-012 | Tratamento de exceções e mensagens de limitação |
| RN-013 | Separação entre resultado funcional e persistência do histórico |

Esses mecanismos não substituem as regras de negócio; são formas de implementá-las.

# 10. Estado do documento

| Critério | Situação |
|---|---|
| Regras gerais | Definidas |
| Regras de segurança | Definidas |
| Regras de privacidade | Definidas |
| Regras dos módulos | Definidas |
| Histórico e relatórios | Definidos |
| Recuperação de execuções | Definida conceitualmente |
| Proteção de senhas | Definida |
| Separação entre operação e histórico | Definida |
| Exportação | Definida |
| Rastreabilidade | Estruturada |
| Revisão cruzada | Pendente |

**Total de regras:** 13.