# SEGURANCA.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Primeira versão

---

# 1. Objetivo

Este documento define os princípios e controles básicos de segurança do Odyssey AV.

O objetivo é proteger o sistema, os arquivos analisados, as informações do usuário e os resultados armazenados, reduzindo riscos durante a execução das ferramentas.

A segurança deverá ser considerada desde o desenvolvimento até a utilização da aplicação.

# 2. Princípios de segurança

O Odyssey AV deverá seguir os seguintes princípios:

- **Menor privilégio:** utilizar somente as permissões necessárias para executar cada operação.
- **Validação de entradas:** validar parâmetros e dados recebidos antes do processamento.
- **Privacidade:** evitar armazenar informações sensíveis sem necessidade.
- **Transparência:** informar quando uma operação realizar comunicação externa.
- **Não destrutividade:** não modificar, excluir ou colocar arquivos em quarentena automaticamente.
- **Isolamento:** uma falha em determinado módulo não deverá comprometer os demais.
- **Tratamento seguro de erros:** não expor informações sensíveis em mensagens ou logs.

# 3. Segurança por módulo

## 3.1. FILE — Análise de arquivos

Principais riscos:

- Acesso indevido a arquivos.
- Leitura de arquivos sem permissão.
- Consumo excessivo de memória durante a análise.
- Interpretação incorreta de formatos.

Controles:

- Validar caminhos recebidos.
- Respeitar as permissões do sistema operacional.
- Não executar arquivos analisados.
- Não modificar o conteúdo dos arquivos.
- Processar arquivos em blocos quando necessário.
- Identificar limitações de formatos não suportados.
- Tratar arquivos especiais e links simbólicos com cuidado.

## 3.2. HASH — Hash

Principais riscos:

- Comparações incorretas.
- Uso de referências não confiáveis.
- Leitura inadequada de arquivos.

Controles:

- Utilizar SHA-256.
- Calcular o hash a partir dos bytes reais do arquivo.
- Validar o formato dos hashes fornecidos.
- Não considerar uma correspondência como prova absoluta de segurança.
- Não modificar o arquivo original.

## 3.3. NETWORK — Diagnóstico de rede

Principais riscos:

- Comunicação externa não autorizada.
- Exposição de informações durante consultas externas.
- Indisponibilidade de serviços.
- Operações sem limite de tempo.

Controles:

- Executar verificações somente quando solicitadas pelo usuário.
- Informar quando houver comunicação externa.
- Aplicar timeout nas operações de rede.
- Tratar falhas e indisponibilidade de serviços.
- Não realizar varreduras de portas de terceiros.
- Não manter comunicação oculta em segundo plano.

A consulta de IP público deverá ser opcional e utilizar um serviço externo identificado na documentação da implementação.

## 3.4. PASSWORD — Ferramentas de senha

Principais riscos:

- Exposição de senhas em logs.
- Persistência acidental de senhas.
- Geração de valores previsíveis.
- Exposição de senhas em relatórios.

Controles:

- Utilizar o módulo `secrets` para geração.
- Não armazenar senhas geradas ou avaliadas.
- Não incluir senhas no histórico.
- Não registrar senhas nos logs.
- Não incluir senhas em relatórios exportados.
- Evitar exibir valores sensíveis em mensagens de erro.

## 3.5. URL — Análise de URL

Principais riscos:

- Acesso involuntário a destinos externos.
- Interpretação incorreta de endereços.
- Identificação equivocada de URLs suspeitas.

Controles:

- Realizar análise estrutural local.
- Normalizar e validar URLs.
- Não acessar automaticamente os endereços analisados.
- Não executar scripts ou conteúdo associado às URLs.
- Apresentar indicadores como suspeitas, não como confirmação de ameaça.

## 3.6. PROCESS — Monitoramento de processos

Principais riscos:

- Acesso a informações sem permissão.
- Exposição de informações de processos.
- Interferência indevida em processos do sistema.

Controles:

- Consultar somente informações acessíveis ao usuário.
- Respeitar as permissões do sistema operacional.
- Informar quando determinadas métricas não estiverem disponíveis.
- Não encerrar, suspender ou modificar processos.
- Não injetar código em processos.

## 3.7. HISTORY — Histórico e relatórios

Principais riscos:

- Exposição de informações sensíveis.
- Alteração ou perda de registros.
- Persistência acidental de dados que deveriam ser temporários.
- Exportação de informações inadequadas.

Controles:

- Utilizar consultas parametrizadas no SQLite.
- Não persistir senhas.
- Não armazenar conteúdo integral de arquivos.
- Sanitizar mensagens e resumos.
- Não registrar argumentos que contenham segredos.
- Exportar somente informações permitidas.
- Preservar a integridade dos relacionamentos entre execuções e resultados.

# 4. Proteção de dados

O Odyssey AV deverá armazenar somente os dados necessários para seu funcionamento.

## 4.1. Dados que podem ser armazenados

- Identificador da execução.
- Módulo utilizado.
- Nome do caso de uso ou comando normalizado.
- Estado da execução.
- Data e horário.
- Duração.
- Resultados das análises.
- Mensagens técnicas sem informações sensíveis.

## 4.2. Dados que não devem ser armazenados

- Senhas geradas.
- Senhas avaliadas.
- Conteúdo integral de arquivos analisados.
- Segredos presentes nos argumentos.
- Informações pessoais desnecessárias.
- Dados sensíveis que não sejam necessários ao histórico.

## 4.3. Logs

Os logs deverão registrar informações úteis para diagnóstico técnico.

Não deverão ser utilizados como substitutos do histórico de execuções.

Senhas, tokens e outros segredos não poderão aparecer nos registros.

# 5. Segurança da persistência

A aplicação utilizará SQLite para armazenar o histórico local.

Controles básicos:

- Utilizar consultas parametrizadas.
- Ativar e verificar as restrições de chave estrangeira.
- Utilizar transações nas operações de persistência.
- Tratar falhas de leitura e escrita.
- Evitar corrupção e inconsistência dos registros.
- Não expor diretamente os dados internos do banco pela CLI.

O acesso ao banco deverá permanecer centralizado na camada de infraestrutura.

# 6. Segurança de entradas e execução

Todas as entradas recebidas deverão ser tratadas como dados não confiáveis.

A aplicação deverá:

- Validar caminhos e parâmetros.
- Validar URLs antes de interpretá-las.
- Validar parâmetros de geração de senhas.
- Validar filtros de processos.
- Utilizar consultas SQL parametrizadas.
- Evitar execução de comandos do sistema operacional construídos a partir de entradas do usuário.
- Tratar exceções sem expor informações internas desnecessárias.

Arquivos analisados nunca deverão ser executados pelo Odyssey AV.

# 7. Permissões do sistema operacional

O Odyssey AV deverá funcionar com as permissões normais do usuário sempre que possível.

Não deverá solicitar privilégios administrativos automaticamente.

Quando uma operação depender de permissões adicionais, o sistema deverá informar a limitação.

A ausência de acesso a determinado arquivo ou processo não deverá ser interpretada como ausência de risco.

# 8. Matriz de ameaças

| ID | Ameaça | Impacto | Controle |
|---|---|---|---|
| SEC-001 | Exposição de senhas | Alto | Não persistir senhas ou registrá-las em logs |
| SEC-002 | Execução acidental de arquivo analisado | Alto | Nunca executar arquivos analisados |
| SEC-003 | Acesso indevido a arquivos | Alto | Validar caminhos e respeitar permissões |
| SEC-004 | SQL Injection | Alto | Utilizar consultas parametrizadas |
| SEC-005 | Comunicação externa inesperada | Médio | Operações externas explícitas |
| SEC-006 | Consumo excessivo de recursos | Médio | Processamento controlado e limites a definir |
| SEC-007 | Exposição de dados no histórico | Alto | Minimização e sanitização dos dados |
| SEC-008 | Interferência em processos | Alto | Permitir somente consulta e listagem |
| SEC-009 | Interpretação incorreta de ameaças | Médio | Apresentar limitações e indicadores como suspeitas |
| SEC-010 | Falha na persistência | Médio | Transações e tratamento de erros |

# 9. Tratamento de falhas de segurança

Quando uma operação apresentar falha relacionada à segurança, a aplicação deverá:

1. Interromper a operação quando necessário.
2. Evitar ações destrutivas ou efeitos colaterais.
3. Apresentar uma mensagem compreensível.
4. Registrar informações técnicas sem expor dados sensíveis.
5. Preservar os resultados que puderem ser armazenados com segurança.

# 10. Testes de segurança

O MVP deverá possuir testes para verificar os controles principais.

| ID | Teste | Resultado esperado |
|---|---|---|
| ST-001 | Analisar arquivo sem permissão | Erro tratado sem interromper a aplicação |
| ST-002 | Analisar arquivo suspeito | Arquivo não executado ou modificado |
| ST-003 | Informar entrada inválida | Entrada rejeitada |
| ST-004 | Gerar senha | Senha não aparece no histórico ou logs |
| ST-005 | Avaliar senha | Valor não é persistido |
| ST-006 | Analisar URL | Nenhuma requisição automática ao destino |
| ST-007 | Consultar processos | Nenhum processo é modificado |
| ST-008 | Consultar histórico | Dados persistidos sem exposição de segredos |
| ST-009 | Exportar histórico | Senhas e dados sensíveis são excluídos |
| ST-010 | Consultar SQLite | Entradas não alteram a estrutura das consultas |

# 11. Limites de segurança do MVP

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

A identificação de indicadores suspeitos não representa confirmação de malware.

# 12. Referências

- OWASP — princípios e boas práticas de segurança de aplicações.
- Python Documentation — `hashlib` e `secrets`.
- SQLite Documentation — consultas parametrizadas e transações.
- Regras de negócio do Odyssey AV.
- Requisitos funcionais e não funcionais do Odyssey AV.

---

# 13. Estado do documento

| Critério | Situação |
|---|---|
| Princípios de segurança | Definidos |
| Segurança por módulo | Definida |
| Proteção de dados | Definida |
| Proteção de entradas | Definida |
| Segurança da persistência | Definida |
| Permissões do sistema operacional | Definidas |
| Matriz de ameaças | Elaborada |
| Testes de segurança | Especificados |
| Revisão de consistência | Pendente |

