# REQUISITOS.md

**Projeto:** Odyssey AV  
**Versão:** 2.2<br>
**Escopo:** MVP  
**Status:** Consolidado após revisão cruzada

---

# 1. Objetivo

Este documento especifica os requisitos funcionais e não funcionais do Odyssey AV.

Os requisitos estabelecem as funcionalidades que o sistema deverá oferecer e as condições de qualidade, segurança, confiabilidade, desempenho e compatibilidade que deverão ser respeitadas durante seu desenvolvimento.

O escopo está limitado às sete ferramentas definidas para o MVP.

# 2. Escopo funcional

| Código | Módulo | Descrição |
|---|---|---|
| FILE | Análise de arquivos | Inspeção de metadados, assinaturas e características de arquivos |
| HASH | Hash | Cálculo e comparação de hashes |
| NETWORK | Diagnóstico de rede | Verificações de conectividade, DNS e IP público opcional |
| PASSWORD | Ferramentas de senha | Geração segura e avaliação local de senhas |
| URL | Análise de URL | Análise estrutural e identificação de indicadores suspeitos |
| PROCESS | Monitoramento de processos | Listagem, consulta e filtragem de processos |
| HISTORY | Histórico e relatórios | Consulta e exportação das execuções registradas |

# 3. Requisitos funcionais

## 3.1. Análise de arquivos — FILE

### RF-001 — Leitura de metadados

O sistema deverá permitir a leitura de metadados de arquivos, incluindo nome, extensão, tamanho e informações disponíveis sobre o formato.

### RF-002 — Identificação de formato

O sistema deverá identificar assinaturas de formatos de arquivos selecionados, quando houver suporte para o formato analisado.

Os formatos iniciais contemplados serão:

- PE — Portable Executable.
- ELF — Executable and Linkable Format.
- PDF — Portable Document Format.
- PNG — Portable Network Graphics.
- JPEG — Joint Photographic Experts Group.
- ZIP — formato de arquivo ZIP.
- GZIP — formato de compressão GZIP.
- Desconhecido — quando nenhuma assinatura suportada for identificada.

A identificação de assinatura não deverá ser interpretada como validação integral do arquivo ou confirmação de segurança.

### RF-003 — Identificação de divergências

O sistema deverá identificar possíveis divergências entre a extensão declarada e a assinatura identificada do arquivo.

### RF-004 — Apresentação dos resultados

O sistema deverá apresentar as informações coletadas e os indicadores identificados durante a análise do arquivo.

### RF-029 — Validação do tipo de recurso

O sistema deverá aceitar somente arquivos regulares para análise.

Deverá:

- Rejeitar diretórios.
- Não seguir links simbólicos automaticamente.
- Rejeitar dispositivos, sockets e pipes.
- Tratar arquivos que desapareçam ou sejam modificados durante a análise.
- Respeitar as permissões do sistema operacional.
- Não modificar o arquivo analisado.

## 3.2. Hash — HASH

### RF-005 — Cálculo de hash

O sistema deverá calcular o hash de arquivos utilizando o algoritmo SHA-256.

### RF-006 — Comparação de hashes

O sistema deverá permitir comparar o hash calculado com uma referência fornecida explicitamente pelo usuário.

O MVP não deverá utilizar uma base própria de hashes para essa comparação.

### RF-007 — Classificação da comparação

O sistema deverá classificar o resultado da comparação como:

- `MATCH`: hash correspondente à referência.
- `MISMATCH`: hash diferente da referência.
- `NO_REFERENCE`: nenhuma referência fornecida.

### RF-008 — Verificação de integridade

O sistema deverá permitir verificar a integridade de um arquivo por meio da comparação entre seu hash atual e uma referência previamente fornecida pelo usuário.

A correspondência deverá indicar igualdade entre os valores comparados, sem representar garantia absoluta de segurança do arquivo.

## 3.3. Diagnóstico de rede — NETWORK

### RF-009 — Verificação de conectividade

O sistema deverá permitir verificar a conectividade de rede mediante comandos explícitos do usuário.

### RF-010 — Consulta DNS

O sistema deverá permitir realizar consultas DNS para verificar a resolução de nomes de domínio.

### RF-011 — Consulta de IP público

O sistema deverá disponibilizar uma consulta opcional de IP público por meio de um serviço externo.

A consulta deverá depender de solicitação explícita do usuário.

### RF-012 — Apresentação do diagnóstico

O sistema deverá apresentar os resultados das verificações de rede, identificando falhas, respostas obtidas e operações que não puderam ser concluídas.

## 3.4. Ferramentas de senha — PASSWORD

### RF-013 — Geração de senhas

O sistema deverá permitir gerar senhas utilizando geração aleatória segura.

### RF-014 — Configuração da geração

O sistema deverá permitir configurar parâmetros da senha gerada, como comprimento e utilização de diferentes conjuntos de caracteres.

### RF-015 — Avaliação de senhas

O sistema deverá permitir avaliar localmente características básicas de uma senha, apresentando indicadores relacionados à sua composição e qualidade estimada.

A avaliação deverá ocorrer localmente, sem envio da senha a serviços externos.

### RF-016 — Proteção dos dados de senha

O sistema deverá impedir que senhas geradas ou avaliadas sejam armazenadas:

- No histórico.
- Nos logs.
- Nos relatórios exportados.
- Nos argumentos persistidos dos comandos.
- Nas mensagens de erro.
- Nos resumos e resultados estruturados.

O sistema poderá registrar a execução do módulo, desde que armazene somente metadados operacionais e informações sanitizadas.

## 3.5. Análise de URL — URL

### RF-017 — Interpretação de URLs

O sistema deverá permitir interpretar e decompor URLs em seus componentes estruturais.

### RF-018 — Normalização de URLs

O sistema deverá permitir normalizar a representação de URLs para facilitar sua análise.

### RF-019 — Identificação de indicadores suspeitos

O sistema deverá identificar características potencialmente suspeitas em URLs, apresentando os indicadores encontrados.

### RF-020 — Análise sem acesso automático ao destino

O sistema deverá realizar a análise estrutural da URL sem executar requisições automáticas ao endereço informado.

A análise deverá ocorrer localmente, sem consultas DNS ou outras operações externas implícitas.

## 3.6. Monitoramento de processos — PROCESS

### RF-021 — Listagem de processos

O sistema deverá permitir listar os processos em execução que estejam acessíveis ao usuário.

### RF-022 — Consulta de informações

O sistema deverá apresentar informações disponíveis sobre os processos, incluindo:

- PID.
- Nome.
- Métricas acessíveis do processo.

### RF-023 — Filtragem de processos

O sistema deverá permitir filtrar processos utilizando critérios disponíveis, como PID e nome.

### RF-024 — Respeito às permissões do sistema operacional

O sistema deverá identificar e comunicar limitações de acesso às informações dos processos.

Processos encerrados durante a consulta ou inacessíveis por limitações de permissão deverão ser tratados como informações indisponíveis, sem comprometer indevidamente a operação completa.

## 3.7. Histórico e relatórios — HISTORY

### RF-025 — Registro de execuções

O sistema deverá registrar as execuções dos módulos funcionais, incluindo:

- Identificador da execução.
- Identificador da instância da aplicação.
- Módulo utilizado.
- Comando normalizado.
- Estado da execução.
- Data e hora de início.
- Data e hora de término, quando disponíveis.
- Duração, quando disponível.
- Resumo sanitizado.
- Resultados associados.

As execuções dos módulos FILE, HASH, NETWORK, PASSWORD, URL e PROCESS deverão ser registradas.

Consultas e exportações do próprio módulo HISTORY não deverão gerar novos registros de execução.

### RF-026 — Consulta do histórico

O sistema deverá permitir consultar execuções anteriores, utilizando filtros como:

- Módulo.
- Período.
- Estado da execução.

A consulta deverá permitir paginação ou limitação de resultados para evitar retornos excessivos.

### RF-027 — Consulta dos resultados

O sistema deverá permitir consultar os resultados associados a uma execução específica.

Os resultados deverão preservar a associação com a execução correspondente e apresentar informações estruturadas de acordo com o módulo responsável.

### RF-028 — Exportação de relatórios

O sistema deverá permitir exportar informações do histórico e de seus resultados nos formatos JSON e CSV, respeitando as regras de privacidade.

A exportação deverá permitir limitar os registros e campos selecionados, evitando geração de arquivos excessivamente grandes.

### RF-030 — Recuperação de execuções interrompidas

O sistema deverá identificar execuções que permaneceram no estado `RUNNING` após o encerramento inesperado de uma instância anterior.

A recuperação deverá:

- Ocorrer somente após a obtenção do bloqueio exclusivo da aplicação.
- Identificar registros pertencentes a instâncias anteriores.
- Atualizar para `INTERRUPTED` as execuções que permaneceram em `RUNNING`.
- Utilizar o identificador da instância da aplicação, sem depender exclusivamente do PID do sistema operacional.
- Ser realizada de maneira transacional.

A aplicação não deverá considerar a recuperação concluída antes da confirmação da transação.

Caso a transação de recuperação falhe, os registros deverão permanecer no estado efetivamente persistido, sem atualização parcial apresentada como recuperação concluída.

### RF-031 — Identificação e exclusividade da instância

Cada inicialização válida do Odyssey AV deverá possuir um identificador único de instância (`instance_id`).

As execuções registradas deverão estar associadas à instância responsável por sua execução.

O sistema deverá impedir a operação simultânea de múltiplas instâncias ativas no MVP, utilizando mecanismo de bloqueio exclusivo compatível com Windows e Linux.

O bloqueio deverá permanecer ativo durante toda a operação da instância, inclusive quando a aplicação estiver em modo degradado.

### RF-032 — Separação entre resultado funcional e histórico

O sistema deverá apresentar separadamente:

- O resultado funcional da operação solicitada.
- A situação de persistência do histórico.

Uma falha de persistência não deverá transformar automaticamente uma operação funcional bem-sucedida em falha funcional.

Quando não for possível registrar uma execução ou seus resultados, a CLI deverá informar claramente essa condição.

O sistema não deverá afirmar que os resultados foram registrados quando a persistência não tiver sido confirmada.

Durante uma sessão iniciada em `NORMAL`, a falha de persistência será tratada por operação e não alterará o resultado funcional. A aplicação não deverá mudar automaticamente para `DEGRADED`; operações posteriores permanecerão disponíveis e farão suas próprias tentativas normais de persistência. Não haverá fila de gravações pendentes nem armazenamento alternativo, e dados cuja gravação falhou não serão recuperados posteriormente. Registros anteriormente confirmados permanecerão inalterados.

Consultas `HISTORY` dependem da disponibilidade do SQLite. Se uma consulta ou exportação falhar por indisponibilidade do banco, a aplicação deverá comunicar a falha da operação solicitada, separadamente dos resultados de operações funcionais.

### RF-033 — Operação em modo degradado

Caso a recuperação transacional do histórico falhe durante a inicialização, o sistema deverá entrar em modo operacional degradado.

Nesse estado:

- O bloqueio exclusivo deverá permanecer ativo.
- A falha de recuperação deverá ser comunicada claramente.
- Os módulos FILE, HASH, NETWORK, PASSWORD, URL e PROCESS deverão continuar disponíveis.
- Novas gravações no histórico deverão permanecer desabilitadas.
- O módulo HISTORY deverá ficar indisponível para consultas e exportações.
- A aplicação não deverá afirmar que resultados foram registrados.
- A falha de persistência deverá permanecer separada do resultado funcional das operações.
- Não deverá ser utilizado mecanismo alternativo de armazenamento.
- Registros antigos `RUNNING` não deverão ser marcados como `INTERRUPTED` quando a transação de recuperação não tiver sido concluída.

Uma nova tentativa de recuperação deverá ocorrer em uma inicialização posterior.

O modo degradado deverá ser distinguido dos estados individuais das execuções.

O estado operacional `DEGRADED` decorre exclusivamente da falha da recuperação transacional durante a inicialização. Uma falha de persistência isolada em uma sessão `NORMAL` não provoca essa transição.

# 4. Requisitos não funcionais

## 4.1. Compatibilidade

### RNF-001 — Compatibilidade multiplataforma

O sistema deverá funcionar em ambientes Windows e Linux, respeitando as diferenças existentes entre os sistemas operacionais.

### RNF-002 — Isolamento de particularidades da plataforma

As operações dependentes do sistema operacional deverão ser organizadas de forma que suas particularidades não comprometam a estrutura geral dos módulos.

## 4.2. Segurança

### RNF-003 — Execução segura de operações

O sistema não deverá executar arquivos analisados nem utilizar mecanismos de execução de comandos do sistema operacional de maneira insegura.

### RNF-004 — Validação de entradas

O sistema deverá validar caminhos, parâmetros, argumentos e demais entradas fornecidas pelo usuário antes de processá-los.

### RNF-005 — Proteção de dados sensíveis

O sistema deverá impedir que senhas, segredos e informações sensíveis desnecessárias sejam expostos em logs, histórico e relatórios.

### RNF-006 — Comunicação externa controlada

As operações que envolvam comunicação externa deverão ser explícitas, identificáveis e limitadas às funcionalidades solicitadas pelo usuário.

### RNF-007 — Integridade da persistência

Os dados persistidos deverão manter integridade e consistência, evitando corrupção e associações inválidas entre execuções e resultados.

O sistema deverá utilizar mecanismos adequados de integridade referencial e transações no banco de dados local.

## 4.3. Desempenho e utilização de recursos

### RNF-008 — Uso eficiente de memória

A análise de arquivos deverá evitar carregar integralmente arquivos grandes na memória quando o processamento em blocos for aplicável.

### RNF-009 — Controle de operações externas

As operações de rede deverão considerar limites de tempo de execução e tratamento de indisponibilidade, evitando bloqueios indefinidos.

### RNF-010 — Controle de falhas

O sistema deverá tratar falhas de execução sem comprometer desnecessariamente os demais módulos ou a integridade dos dados já registrados.

### RNF-015 — Limitação de operações e resultados

O sistema deverá estabelecer limites operacionais adequados para:

- Leitura e processamento de arquivos.
- Tempo de execução de operações externas.
- Quantidade de processos consultados e resultados apresentados.
- Quantidade de registros retornados pelo histórico.
- Quantidade de registros e volume de dados exportados.

Os valores numéricos deverão ser definidos durante o refinamento técnico e validados por testes. Não serão estabelecidos limites arbitrários nesta etapa documental.

## 4.4. Arquitetura e manutenção

### RNF-011 — Modularidade

O sistema deverá manter separação entre os módulos funcionais, permitindo manutenção e evolução independentes sempre que possível.

### RNF-012 — Testabilidade

O sistema deverá possuir estrutura que permita a execução de testes unitários, de integração, segurança e compatibilidade.

### RNF-013 — Gerenciamento de dependências

As dependências externas deverão ser identificadas, justificadas e revisadas quanto à necessidade e aos riscos de segurança.

### RNF-014 — Persistência e configuração local

O sistema deverá utilizar persistência local e configuração adequada ao ambiente do usuário, sem exigir obrigatoriamente infraestrutura remota para seu funcionamento.

### RNF-016 — Separação de responsabilidades

A arquitetura deverá manter responsabilidades distintas entre:

- Interface de linha de comando.
- Camada de aplicação.
- Módulos funcionais.
- Domínio.
- Infraestrutura.

Os módulos funcionais não deverão acessar diretamente o banco de dados SQLite.

### RNF-017 — Configuração previsível

O sistema deverá permitir configuração local opcional por arquivo TOML.

A configuração deverá respeitar a seguinte precedência:

1. Padrões internos.
2. Valores definidos no arquivo TOML.
3. Argumentos explicitamente fornecidos na CLI.

A ausência do arquivo de configuração deverá ser permitida. Arquivos TOML inválidos deverão gerar mensagens claras de erro, sem que configurações inválidas sejam ignoradas silenciosamente.

### RNF-018 — Consistência temporal e identificação

As datas persistidas deverão utilizar UTC e formato consistente.

Os registros de execução deverão manter associação inequívoca com o identificador da instância responsável por sua criação.

# 5. Matriz de rastreabilidade

## 5.1. Requisitos funcionais e regras de negócio

| Requisito | Regra relacionada |
|---|---|
| RF-001 a RF-004 | RN-001, RN-003, RN-010, RN-012 |
| RF-005 a RF-008 | RN-002, RN-003, RN-004 |
| RF-009 a RF-012 | RN-007, RN-012 |
| RF-013 a RF-016 | RN-005, RN-010 |
| RF-017 a RF-020 | RN-003, RN-006 |
| RF-021 a RF-024 | RN-008, RN-012 |
| RF-025 a RF-028 | RN-009, RN-010, RN-011 |
| RF-029 | RN-001, RN-010, RN-012 |
| RF-030 a RF-031 | RN-009 |
| RF-032 | RN-013 |
| RF-033 | RN-009 |

## 5.2. Requisitos não funcionais e áreas relacionadas

| Requisito | Área |
|---|---|
| RNF-001 | Compatibilidade |
| RNF-002 | Arquitetura multiplataforma |
| RNF-003 | Segurança operacional |
| RNF-004 | Validação de entradas |
| RNF-005 | Privacidade |
| RNF-006 | Segurança de rede |
| RNF-007 | Integridade de dados |
| RNF-008 | Desempenho |
| RNF-009 | Confiabilidade de rede |
| RNF-010 | Tratamento de falhas |
| RNF-011 | Arquitetura |
| RNF-012 | Testabilidade |
| RNF-013 | Dependências |
| RNF-014 | Persistência e configuração |
| RNF-015 | Limites operacionais |
| RNF-016 | Separação de responsabilidades |
| RNF-017 | Configuração |
| RNF-018 | Consistência temporal e identificação |

# 6. Limitações do MVP

Os requisitos deste documento não incluem:

- Antivírus em tempo real.
- Quarentena ou exclusão automática de arquivos.
- Análise comportamental de malware.
- Execução controlada de arquivos suspeitos.
- Drivers ou componentes em modo kernel.
- Varredura ou exploração de portas de terceiros.
- Classificação de ameaças por inteligência artificial.
- Agente de IA integrado.
- Integração obrigatória com serviços remotos.
- Contas de usuário, autenticação ou sincronização em nuvem.

Essas funcionalidades não fazem parte dos requisitos da primeira versão.

# 7. Premissas e restrições

1. O Odyssey AV será uma ferramenta local, operada por linha de comando.
2. O usuário deverá iniciar explicitamente as operações.
3. O sistema deverá respeitar as permissões disponíveis no ambiente.
4. A ausência de acesso a determinado recurso deverá ser comunicada.
5. A análise de arquivos não deverá modificar os arquivos analisados.
6. A análise de URLs não deverá acessar automaticamente os destinos.
7. Senhas não deverão ser persistidas.
8. O histórico deverá armazenar somente informações necessárias.
9. Os resultados deverão distinguir falhas, avisos e conclusões bem-sucedidas.
10. O MVP deverá permanecer limitado aos sete módulos definidos.
11. O sistema deverá permitir somente uma instância ativa por vez.
12. A consulta e exportação do histórico não deverão gerar registros recursivos.
13. O sistema deverá funcionar sem dependência obrigatória de serviços remotos, exceto nas operações externas explicitamente solicitadas.
14. A falha na recuperação transacional do histórico deverá resultar em modo degradado, sem desabilitar as ferramentas funcionais.
15. O modo degradado não deverá permitir novas gravações ou operações de HISTORY.

# 8. Critérios gerais de aceitação

O conjunto de requisitos será considerado atendido quando:

- Os sete módulos estiverem implementados e acessíveis pela CLI.
- Cada módulo executar as operações previstas.
- Os resultados forem apresentados de forma compreensível e estruturada.
- As regras de negócio forem respeitadas.
- Os formatos de assinatura definidos para FILE forem reconhecidos conforme o escopo.
- A comparação de hashes utilizar referência fornecida pelo usuário.
- Arquivos especiais não permitidos forem rejeitados.
- Operações externas ocorrerem somente quando solicitadas.
- Nenhum dado de senha for persistido.
- O histórico registrar adequadamente as execuções funcionais quando disponível.
- Execuções interrompidas forem recuperadas conforme o mecanismo definido.
- A recuperação do histórico ocorrer transacionalmente.
- A aplicação impedir múltiplas instâncias ativas.
- A falha de persistência for comunicada separadamente do resultado funcional.
- Em uma sessão `NORMAL`, uma falha isolada de gravação não alterar o resultado funcional nem provocar transição automática para `DEGRADED`; uma operação posterior tentar persistir normalmente, sem fila ou armazenamento alternativo, e registros confirmados permanecerem inalterados.
- Dados cuja gravação falhou durante uma sessão `NORMAL` não serem recuperados posteriormente.
- Uma consulta ou exportação `HISTORY` comunicar erro quando o SQLite estiver indisponível.
- O modo degradado preservar a disponibilidade dos módulos funcionais.
- O modo degradado impedir novas gravações e operações de HISTORY.
- Registros antigos não forem alterados quando a transação de recuperação falhar.
- A aplicação tentar novamente a recuperação em inicialização posterior.
- A exportação JSON e CSV funcionar quando o histórico estiver disponível.
- Os limites operacionais forem aplicados e testados.
- A configuração TOML respeitar a precedência definida.
- O sistema funcionar nos ambientes Windows e Linux suportados.
- Os testes previstos forem executados e aprovados.
- As falhas e limitações forem comunicadas sem produzir resultados enganosos.

# 9. Estado do documento

| Critério | Situação |
|---|---|
| Escopo funcional | Definido |
| Requisitos funcionais | 33 definidos |
| Requisitos não funcionais | 18 definidos |
| Regras de negócio relacionadas | Mapeadas |
| Recuperação de execuções | Definida transacionalmente |
| Identificação de instância | Definida |
| Proteção de dados sensíveis | Definida |
| Modo degradado | Definido |
| Limites operacionais | Definidos conceitualmente |
| Configuração TOML | Definida |
| Limitações do MVP | Definidas |
| Premissas e restrições | Definidas |
| Critérios gerais de aceitação | Definidos |
| Revisão cruzada | Concluída |

**Total: 51 requisitos documentados.**
