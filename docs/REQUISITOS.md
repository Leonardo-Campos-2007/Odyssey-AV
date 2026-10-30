# REQUISITOS.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Primeira versão consolidada

---

# 1. Objetivo

Este documento especifica os requisitos funcionais e não funcionais do Odyssey AV.

Os requisitos estabelecem as funcionalidades que o sistema deverá oferecer e as condições de qualidade, segurança, confiabilidade e compatibilidade que deverão ser respeitadas durante seu desenvolvimento.

O escopo está limitado às sete ferramentas definidas para o MVP.

---

# 2. Escopo funcional

O MVP será composto pelos seguintes módulos:

| Código | Módulo | Descrição |
|---|---|---|
| FILE | Análise de arquivos | Inspeção de metadados e características de arquivos |
| HASH | Hash | Cálculo e comparação de hashes |
| NETWORK | Diagnóstico de rede | Verificações de conectividade e DNS |
| PASSWORD | Ferramentas de senha | Geração e avaliação local de senhas |
| URL | Análise de URL | Análise estrutural e identificação de indicadores suspeitos |
| PROCESS | Monitoramento de processos | Listagem e consulta de processos |
| HISTORY | Histórico e relatórios | Consulta e exportação de execuções |

---

# 3. Requisitos funcionais

## 3.1. Análise de arquivos — FILE

### RF-001 — Leitura de metadados

O sistema deverá permitir a leitura de metadados de arquivos, incluindo nome, extensão, tamanho e informações disponíveis sobre o formato.

### RF-002 — Identificação de formato

O sistema deverá identificar assinaturas de formatos de arquivos selecionados, quando houver suporte para o formato analisado.

### RF-003 — Identificação de divergências

O sistema deverá identificar possíveis divergências entre a extensão declarada e a assinatura identificada do arquivo.

### RF-004 — Apresentação dos resultados

O sistema deverá apresentar as informações coletadas e os indicadores identificados durante a análise do arquivo.

---

## 3.2. Hash — HASH

### RF-005 — Cálculo de hash

O sistema deverá calcular o hash de arquivos utilizando o algoritmo SHA-256.

### RF-006 — Comparação de hashes

O sistema deverá permitir a comparação do hash calculado com uma referência fornecida ou disponível localmente.

### RF-007 — Classificação da comparação

O sistema deverá classificar o resultado da comparação como:

- `MATCH`: hash correspondente.
- `MISMATCH`: hash divergente.
- `NO_REFERENCE`: referência indisponível.

### RF-008 — Verificação de integridade

O sistema deverá permitir verificar a integridade de um arquivo por meio da comparação entre seu hash atual e uma referência previamente definida.

---

## 3.3. Diagnóstico de rede — NETWORK

### RF-009 — Verificação de conectividade

O sistema deverá permitir verificar a conectividade de rede mediante comandos explícitos do usuário.

### RF-010 — Consulta DNS

O sistema deverá permitir realizar consultas DNS para verificar a resolução de nomes de domínio.

### RF-011 — Consulta de IP público

O sistema deverá disponibilizar uma consulta opcional de IP público por meio de um serviço externo.

### RF-012 — Apresentação do diagnóstico

O sistema deverá apresentar os resultados das verificações de rede, identificando falhas, respostas obtidas e operações que não puderam ser concluídas.

---

## 3.4. Ferramentas de senha — PASSWORD

### RF-013 — Geração de senhas

O sistema deverá permitir gerar senhas utilizando geração aleatória segura.

### RF-014 — Configuração da geração

O sistema deverá permitir configurar parâmetros da senha gerada, como comprimento e utilização de diferentes conjuntos de caracteres.

### RF-015 — Avaliação de senhas

O sistema deverá permitir avaliar localmente características básicas de uma senha, apresentando indicadores relacionados à sua composição e qualidade estimada.

### RF-016 — Proteção dos dados de senha

O sistema deverá impedir que senhas geradas ou avaliadas sejam armazenadas no histórico, nos logs ou nos relatórios exportados.

---

## 3.5. Análise de URL — URL

### RF-017 — Interpretação de URLs

O sistema deverá permitir interpretar e decompor URLs em seus componentes estruturais.

### RF-018 — Normalização de URLs

O sistema deverá permitir normalizar a representação de URLs para facilitar sua análise.

### RF-019 — Identificação de indicadores suspeitos

O sistema deverá identificar características potencialmente suspeitas em URLs, apresentando os indicadores encontrados.

### RF-020 — Análise sem acesso automático ao destino

O sistema deverá realizar a análise estrutural da URL sem executar requisições automáticas ao endereço informado.

---

## 3.6. Monitoramento de processos — PROCESS

### RF-021 — Listagem de processos

O sistema deverá permitir listar os processos em execução que estejam acessíveis ao usuário.

### RF-022 — Consulta de informações

O sistema deverá apresentar informações disponíveis sobre os processos, incluindo PID, nome e métricas acessíveis.

### RF-023 — Filtragem de processos

O sistema deverá permitir filtrar processos utilizando critérios disponíveis, como PID e nome.

### RF-024 — Respeito às permissões do sistema operacional

O sistema deverá identificar e comunicar limitações de acesso às informações dos processos.

---

## 3.7. Histórico e relatórios — HISTORY

### RF-025 — Registro de execuções

O sistema deverá registrar as execuções dos módulos, incluindo identificador, módulo utilizado, comando, estado e informações temporais disponíveis.

### RF-026 — Consulta do histórico

O sistema deverá permitir consultar execuções anteriores, utilizando filtros como módulo, período e estado.

### RF-027 — Consulta dos resultados

O sistema deverá permitir consultar os resultados associados a uma execução específica.

### RF-028 — Exportação de relatórios

O sistema deverá permitir exportar informações do histórico e de seus resultados nos formatos JSON e CSV, respeitando as regras de privacidade.

---

# 4. Requisitos não funcionais

## 4.1. Compatibilidade

### RNF-001 — Compatibilidade multiplataforma

O sistema deverá funcionar em ambientes Windows e Linux, respeitando as diferenças existentes entre os sistemas operacionais.

### RNF-002 — Isolamento de particularidades da plataforma

As operações dependentes do sistema operacional deverão ser organizadas de forma que suas particularidades não comprometam a estrutura geral dos módulos.

---

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

---

## 4.3. Desempenho e utilização de recursos

### RNF-008 — Uso eficiente de memória

A análise de arquivos deverá evitar carregar integralmente arquivos grandes na memória quando o processamento em blocos for aplicável.

### RNF-009 — Controle de operações externas

As operações de rede deverão considerar limites de tempo de execução e tratamento de indisponibilidade, evitando bloqueios indefinidos.

### RNF-010 — Controle de falhas

O sistema deverá tratar falhas de execução sem comprometer desnecessariamente os demais módulos ou a integridade dos dados já registrados.

---

## 4.4. Arquitetura e manutenção

### RNF-011 — Modularidade

O sistema deverá manter separação entre os módulos funcionais, permitindo manutenção e evolução independentes sempre que possível.

### RNF-012 — Testabilidade

O sistema deverá possuir estrutura que permita a execução de testes unitários, de integração, segurança e compatibilidade.

### RNF-013 — Gerenciamento de dependências

As dependências externas deverão ser identificadas, justificadas e revisadas quanto à necessidade e aos riscos de segurança.

### RNF-014 — Persistência e configuração local

O sistema deverá utilizar persistência local e configuração adequada ao ambiente do usuário, sem exigir obrigatoriamente infraestrutura remota para seu funcionamento.

---

# 5. Matriz de rastreabilidade

## 5.1. Requisitos funcionais e regras de negócio

| Requisito | Regra relacionada |
|---|---|
| RF-001 a RF-004 | RN-001, RN-003, RN-010, RN-012 |
| RF-005 a RF-008 | RN-002, RN-004, RN-010 |
| RF-009 a RF-012 | RN-007, RN-012 |
| RF-013 a RF-016 | RN-005, RN-010 |
| RF-017 a RF-020 | RN-003, RN-006 |
| RF-021 a RF-024 | RN-008, RN-012 |
| RF-025 a RF-027 | RN-009, RN-010 |
| RF-028 | RN-005, RN-010, RN-011 |

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

---

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

---

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

---

# 8. Critérios gerais de aceitação

O conjunto de requisitos será considerado atendido quando:

- Os sete módulos estiverem implementados e acessíveis pela CLI.
- Cada módulo executar as operações previstas.
- Os resultados forem apresentados de forma compreensível.
- As regras de negócio forem respeitadas.
- O histórico registrar adequadamente as execuções.
- A exportação JSON e CSV funcionar.
- Nenhum dado de senha for persistido.
- Operações externas ocorrerem somente quando solicitadas.
- O sistema funcionar nos ambientes Windows e Linux suportados.
- Os testes previstos forem executados e aprovados.
- As falhas e limitações forem comunicadas sem produzir resultados enganosos.

---

# 9. Estado do documento

| Critério | Situação |
|---|---|
| Escopo funcional | Definido |
| Requisitos funcionais | 28 definidos |
| Requisitos não funcionais | 14 definidos |
| Regras de negócio relacionadas | Mapeadas |
| Limitações do MVP | Definidas |
| Premissas e restrições | Definidas |
| Critérios gerais de aceitação | Definidos |
| Revisão de consistência | Pendente |

**Total:** 42 requisitos documentados.

