# BACKLOG.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Primeira versão

---

# 1. Objetivo

Este documento organiza o desenvolvimento do MVP do Odyssey AV em épicos, histórias de usuário e tarefas técnicas.

O backlog estabelece uma sequência de implementação baseada nas dependências entre funcionalidades, na arquitetura definida e nos requisitos documentados.

O objetivo é permitir que o desenvolvimento aconteça de forma incremental, mantendo a rastreabilidade entre requisitos, regras de negócio, segurança e testes.

# 2. Escopo do MVP

O MVP será composto por sete módulos funcionais:

1. FILE — Análise de arquivos.
2. HASH — Cálculo e comparação de hashes.
3. NETWORK — Diagnóstico de rede.
4. PASSWORD — Ferramentas de senha.
5. URL — Análise de URLs.
6. PROCESS — Monitoramento de processos.
7. HISTORY — Histórico e relatórios.

Também fazem parte do MVP:

- Interface de linha de comando (CLI).
- Arquitetura modular em camadas.
- Persistência local com SQLite.
- Configuração local.
- Logs centralizados.
- Tratamento padronizado de erros.
- Testes automatizados.

# 3. Critérios de prioridade

| Prioridade | Significado |
|---|---|
| P0 | Crítica — necessária para viabilizar o MVP ou proteger sua operação |
| P1 | Alta — necessária para completar funcionalidades importantes |
| P2 | Média — importante, mas pode ser implementada após os componentes essenciais |
| P3 | Futura — fora do escopo atual |

A prioridade representa a importância da entrega, não a ordem de dependência.

# 4. Épicos

| ID | Épico | Objetivo | Prioridade |
|---|---|---|---|
| EP-001 | Fundação e arquitetura | Preparar estrutura técnica e execução da aplicação | P0 |
| EP-002 | Persistência e histórico | Registrar e consultar execuções e resultados | P0 |
| EP-003 | Análise de arquivos e hashes | Implementar análise estrutural e integridade | P0 |
| EP-004 | Ferramentas de senha e URL | Implementar funcionalidades locais de análise | P1 |
| EP-005 | Diagnóstico de rede | Implementar verificações de conectividade e DNS | P1 |
| EP-006 | Monitoramento de processos | Consultar processos do sistema operacional | P1 |
| EP-007 | Qualidade e segurança | Validar integração, segurança e estabilidade do MVP | P0 |

# 5. Histórias de usuário

## EP-001 — Fundação e arquitetura

### US-001 — Preparar estrutura da aplicação

- **Épico:** EP-001
- **Prioridade:** P0
- **Sprint:** 1
- **Dependências:** Nenhuma

**História:**

Como usuário, quero executar o Odyssey AV por uma interface de linha de comando para acessar suas ferramentas de diagnóstico.

**Critérios de aceitação:**

- A aplicação deve iniciar pela CLI.
- Os comandos devem possuir uma estrutura organizada.
- A CLI deve encaminhar operações para a camada de aplicação.
- Erros devem ser apresentados de maneira compreensível.
- A estrutura deve respeitar a arquitetura modular definida.

**Tarefas técnicas:**

- TEC-001 — Configurar projeto Python.
- TEC-002 — Configurar dependências do projeto.
- TEC-003 — Configurar Typer.
- TEC-004 — Criar estrutura inicial de diretórios.
- TEC-005 — Implementar ponto de entrada da aplicação.
- TEC-006 — Implementar tratamento centralizado de erros.

### US-002 — Configurar serviços transversais

- **Épico:** EP-001
- **Prioridade:** P0
- **Sprint:** 1
- **Dependências:** US-001

**História:**

Como desenvolvedor, quero serviços compartilhados de configuração, validação e logs para manter o comportamento da aplicação consistente.

**Critérios de aceitação:**

- A configuração deve ser local e validada.
- Os logs devem seguir um padrão centralizado.
- Informações sensíveis não podem aparecer nos logs.
- Os serviços não devem depender diretamente da CLI.
- As configurações devem possuir valores padrão seguros.

**Tarefas técnicas:**

- TEC-007 — Implementar carregamento de configuração TOML.
- TEC-008 — Implementar validação de configurações.
- TEC-009 — Implementar serviço centralizado de logs.
- TEC-010 — Definir contratos de erro e resultado.
- TEC-011 — Implementar identificador de execução.

## EP-002 — Persistência e histórico

### US-003 — Registrar execuções

- **Épico:** EP-002
- **Prioridade:** P0
- **Sprint:** 2
- **Dependências:** US-001, US-002

**História:**

Como usuário, quero que as execuções das ferramentas sejam registradas para consultar posteriormente o que foi executado.

**Critérios de aceitação:**

- Cada execução deve possuir identificador único.
- O módulo executado deve ser identificado.
- O estado da execução deve ser registrado.
- Os horários de início e término devem ser armazenados.
- A duração deve ser registrada quando disponível.
- Os registros devem utilizar os estados definidos no domínio.
- Informações sensíveis não devem ser persistidas.

**Tarefas técnicas:**

- TEC-012 — Configurar conexão SQLite.
- TEC-013 — Criar estrutura da tabela AnalysisRun.
- TEC-014 — Implementar repositório de execuções.
- TEC-015 — Implementar registro de início e término.
- TEC-016 — Implementar persistência de estados de execução.

### US-004 — Registrar resultados

- **Épico:** EP-002
- **Prioridade:** P0
- **Sprint:** 2
- **Dependências:** US-003

**História:**

Como usuário, quero que os resultados das análises sejam associados às suas execuções para manter o histórico organizado.

**Critérios de aceitação:**

- Cada resultado deve pertencer a uma execução existente.
- Uma execução pode possuir vários resultados.
- Os resultados devem possuir tipo e estado.
- Os dados específicos do módulo devem ser armazenados em JSON.
- A integridade referencial deve ser respeitada.

**Tarefas técnicas:**

- TEC-017 — Criar estrutura da tabela AnalysisResult.
- TEC-018 — Implementar relacionamento entre execução e resultado.
- TEC-019 — Implementar repositório de resultados.
- TEC-020 — Implementar transações de persistência.
- TEC-021 — Testar integridade referencial e rollback.

### US-005 — Consultar histórico

- **Épico:** EP-002
- **Prioridade:** P1
- **Sprint:** 5
- **Dependências:** US-003, US-004

**História:**

Como usuário, quero consultar o histórico de execuções para visualizar análises anteriores.

**Critérios de aceitação:**

- Deve ser possível consultar por módulo.
- Deve ser possível consultar por período.
- Deve ser possível consultar por estado.
- Os resultados associados devem poder ser consultados.
- Consultas não devem criar novas execuções.
- Consultas vazias devem apresentar uma resposta adequada.

**Tarefas técnicas:**

- TEC-022 — Implementar filtros de histórico.
- TEC-023 — Implementar consulta de resultados associados.
- TEC-024 — Implementar comandos de consulta na CLI.

### US-006 — Exportar relatórios

- **Épico:** EP-002
- **Prioridade:** P1
- **Sprint:** 5
- **Dependências:** US-005

**História:**

Como usuário, quero exportar os resultados do histórico para arquivos JSON e CSV para utilizar os dados externamente.

**Critérios de aceitação:**

- Deve ser possível exportar em JSON.
- Deve ser possível exportar em CSV.
- Os arquivos devem possuir estrutura válida.
- Apenas informações disponíveis devem ser exportadas.
- Senhas e outros segredos não podem ser exportados.

**Tarefas técnicas:**

- TEC-025 — Implementar exportador JSON.
- TEC-026 — Implementar exportador CSV.
- TEC-027 — Implementar validação dos dados exportados.
- TEC-028 — Testar exportações e proteção de dados sensíveis.

## EP-003 — Análise de arquivos e hashes

### US-007 — Analisar arquivos

- **Épico:** EP-003
- **Prioridade:** P0
- **Sprint:** 3
- **Dependências:** US-001, US-002, US-003, US-004

**História:**

Como usuário, quero analisar arquivos para identificar metadados e possíveis divergências entre extensão e formato real.

**Critérios de aceitação:**

- Deve apresentar nome, extensão e tamanho.
- Deve identificar assinaturas dos formatos suportados.
- Deve identificar divergências entre extensão e assinatura.
- Deve apresentar indicadores encontrados.
- Deve informar quando um formato não for suportado.
- Não deve executar nem modificar o arquivo analisado.
- A análise deve respeitar as permissões do sistema operacional.

**Tarefas técnicas:**

- TEC-029 — Implementar leitura segura de arquivos.
- TEC-030 — Implementar extração de metadados.
- TEC-031 — Definir assinaturas dos formatos suportados.
- TEC-032 — Implementar identificação de assinaturas.
- TEC-033 — Implementar comparação entre extensão e assinatura.
- TEC-034 — Implementar apresentação dos resultados na CLI.
- TEC-035 — Criar testes com arquivos controlados.

### US-008 — Calcular e comparar hashes

- **Épico:** EP-003
- **Prioridade:** P0
- **Sprint:** 3
- **Dependências:** US-001, US-002, US-003, US-004

**História:**

Como usuário, quero calcular e comparar hashes SHA-256 para verificar a integridade de arquivos.

**Critérios de aceitação:**

- Deve calcular SHA-256 sobre os bytes reais do arquivo.
- Deve permitir comparação com uma referência.
- Deve retornar MATCH quando os hashes forem iguais.
- Deve retornar MISMATCH quando forem diferentes.
- Deve retornar NO_REFERENCE quando não existir referência.
- Não deve modificar o arquivo analisado.

**Tarefas técnicas:**

- TEC-036 — Implementar cálculo SHA-256.
- TEC-037 — Implementar processamento em blocos.
- TEC-038 — Implementar comparação de hashes.
- TEC-039 — Implementar validação de referências.
- TEC-040 — Criar testes com hashes conhecidos.

## EP-004 — Ferramentas de senha e URL

### US-009 — Gerar senhas seguras

- **Épico:** EP-004
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001, US-002

**História:**

Como usuário, quero gerar senhas com parâmetros configuráveis para criar credenciais seguras.

**Critérios de aceitação:**

- Deve permitir definir comprimento.
- Deve permitir selecionar conjuntos de caracteres.
- Deve utilizar fonte criptograficamente segura de aleatoriedade.
- Deve validar parâmetros inválidos.
- A senha gerada não deve ser armazenada no histórico ou nos logs.

**Tarefas técnicas:**

- TEC-041 — Implementar geração com `secrets`.
- TEC-042 — Implementar parâmetros de geração.
- TEC-043 — Implementar validações.
- TEC-044 — Criar testes de geração.

### US-010 — Avaliar senhas

- **Épico:** EP-004
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001, US-002

**História:**

Como usuário, quero avaliar características de uma senha para entender sua qualidade estimada.

**Critérios de aceitação:**

- Deve avaliar características básicas de composição.
- Deve apresentar uma avaliação compreensível.
- Não deve transmitir a senha para serviços externos.
- Não deve persistir a senha.
- A avaliação não deve ser apresentada como garantia de segurança absoluta.

**Tarefas técnicas:**

- TEC-045 — Implementar avaliação local.
- TEC-046 — Definir critérios básicos de avaliação.
- TEC-047 — Implementar proteção contra exposição da senha.
- TEC-048 — Criar testes de avaliação.

### US-011 — Analisar URLs

- **Épico:** EP-004
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001, US-002, US-003, US-004

**História:**

Como usuário, quero analisar URLs para identificar características estruturais e indicadores potencialmente suspeitos.

**Critérios de aceitação:**

- Deve decompor os componentes da URL.
- Deve realizar normalização.
- Deve identificar indicadores potencialmente suspeitos.
- Deve tratar entradas inválidas.
- Não deve realizar requisições automáticas ao destino.
- Não deve executar conteúdo encontrado na URL.

**Tarefas técnicas:**

- TEC-049 — Implementar parsing de URL.
- TEC-050 — Implementar normalização.
- TEC-051 — Implementar identificação de indicadores.
- TEC-052 — Implementar apresentação dos resultados.
- TEC-053 — Criar testes com URLs controladas.

## EP-005 — Diagnóstico de rede

### US-012 — Diagnosticar conectividade e DNS

- **Épico:** EP-005
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001, US-002, US-003, US-004

**História:**

Como usuário, quero verificar conectividade e resolução DNS para identificar problemas básicos de rede.

**Critérios de aceitação:**

- Deve permitir executar diagnóstico por comando explícito.
- Deve realizar consulta DNS.
- Deve apresentar falhas de resolução.
- Deve utilizar timeout nas operações.
- Deve informar operações incompletas.
- Não deve executar comunicação externa oculta.

**Tarefas técnicas:**

- TEC-054 — Implementar adaptador de rede.
- TEC-055 — Implementar consulta DNS.
- TEC-056 — Implementar verificação de conectividade.
- TEC-057 — Implementar tratamento de timeout.
- TEC-058 — Implementar consulta opcional de IP público.
- TEC-059 — Criar testes com respostas simuladas.

## EP-006 — Monitoramento de processos

### US-013 — Listar processos do sistema

- **Épico:** EP-006
- **Prioridade:** P1
- **Sprint:** 5
- **Dependências:** US-001, US-002, US-003, US-004

**História:**

Como usuário, quero listar processos em execução para consultar informações básicas do sistema.

**Critérios de aceitação:**

- Deve listar processos acessíveis.
- Deve apresentar PID e nome.
- Deve apresentar métricas disponíveis.
- Deve permitir filtros por PID e nome.
- Deve tratar processos inacessíveis ou encerrados.
- Não deve encerrar, suspender ou modificar processos.

**Tarefas técnicas:**

- TEC-060 — Implementar integração com psutil.
- TEC-061 — Implementar listagem de processos.
- TEC-062 — Implementar filtros.
- TEC-063 — Implementar tratamento de permissões.
- TEC-064 — Criar testes controlados.

## EP-007 — Qualidade e segurança

### US-014 — Validar segurança das funcionalidades

- **Épico:** EP-007
- **Prioridade:** P0
- **Sprint:** 6
- **Dependências:** US-007, US-008, US-009, US-010, US-011, US-012, US-013

**História:**

Como usuário, quero que as ferramentas respeitem os controles de segurança definidos para evitar ações inesperadas e exposição de informações.

**Critérios de aceitação:**

- Arquivos analisados não podem ser executados ou modificados.
- Senhas não podem ser persistidas.
- URLs não podem gerar requisições automáticas.
- Processos não podem ser alterados.
- Consultas SQLite devem ser parametrizadas.
- Dados sensíveis não podem aparecer em logs ou relatórios.
- A aplicação não deve solicitar elevação automática de privilégios.

**Tarefas técnicas:**

- TEC-065 — Executar testes de segurança.
- TEC-066 — Revisar persistência de dados sensíveis.
- TEC-067 — Revisar validação de entradas.
- TEC-068 — Revisar permissões de arquivos e processos.
- TEC-069 — Corrigir falhas identificadas.

### US-015 — Validar integração e regressão

- **Épico:** EP-007
- **Prioridade:** P0
- **Sprint:** 6
- **Dependências:** US-003, US-004, US-007, US-008, US-009, US-010, US-011, US-012, US-013

**História:**

Como desenvolvedor, quero validar os fluxos completos da aplicação para garantir que os módulos funcionem em conjunto.

**Critérios de aceitação:**

- Os módulos devem funcionar pela CLI.
- As execuções devem ser registradas corretamente.
- Os resultados devem estar associados às execuções.
- O histórico deve permitir consulta e exportação.
- Os testes de regressão devem ser aprovados.
- Falhas de um módulo não devem comprometer indevidamente os demais.

**Tarefas técnicas:**

- TEC-070 — Executar testes de integração.
- TEC-071 — Executar testes de regressão.
- TEC-072 — Validar persistência e transações.
- TEC-073 — Validar concorrência.
- TEC-074 — Verificar cobertura de testes.
- TEC-075 — Corrigir falhas de integração.

### US-016 — Validar compatibilidade Windows e Linux

- **Épico:** EP-007
- **Prioridade:** P1
- **Sprint:** 6
- **Dependências:** US-007, US-012, US-013, US-015

**História:**

Como usuário, quero executar o Odyssey AV em Windows e Linux para utilizar as ferramentas em diferentes sistemas operacionais.

**Critérios de aceitação:**

- A aplicação deve iniciar nos dois sistemas.
- Os caminhos devem ser tratados corretamente.
- Particularidades do sistema operacional devem ser isoladas.
- Limitações de permissões devem ser comunicadas.
- Os módulos devem manter comportamento consistente quando as funcionalidades forem suportadas.

**Tarefas técnicas:**

- TEC-076 — Validar execução no Windows.
- TEC-077 — Validar execução no Linux.
- TEC-078 — Revisar adaptadores de plataforma.
- TEC-079 — Corrigir incompatibilidades encontradas.

# 6. Planejamento das Sprints

As Sprints terão duração aproximada de duas semanas. A distribuição representa uma sequência inicial de implementação, não uma estimativa fechada de esforço.

## Sprint 1 — Fundação

**Objetivo:** preparar a estrutura da aplicação.

**Histórias:**
- US-001 — Preparar estrutura da aplicação.
- US-002 — Configurar serviços transversais.

**Incremento esperado:**
- Projeto Python inicializado.
- CLI funcional.
- Estrutura modular criada.
- Configuração e logs centralizados.

## Sprint 2 — Persistência

**Objetivo:** implementar a base de armazenamento e rastreabilidade.

**Histórias:**
- US-003 — Registrar execuções.
- US-004 — Registrar resultados.

**Incremento esperado:**
- SQLite configurado.
- Entidades persistidas.
- Relacionamento entre execução e resultado.
- Transações e integridade referencial testadas.

## Sprint 3 — Arquivos e integridade

**Objetivo:** entregar as primeiras ferramentas de análise.

**Histórias:**
- US-007 — Analisar arquivos.
- US-008 — Calcular e comparar hashes.

**Incremento esperado:**
- Análise estrutural de arquivos.
- Identificação de assinaturas suportadas.
- Cálculo SHA-256.
- Comparação de hashes.
- Resultados registrados no histórico.

## Sprint 4 — Ferramentas locais e rede

**Objetivo:** implementar ferramentas de senha, URL e diagnóstico de rede.

**Histórias:**
- US-009 — Gerar senhas seguras.
- US-010 — Avaliar senhas.
- US-011 — Analisar URLs.
- US-012 — Diagnosticar conectividade e DNS.

**Incremento esperado:**
- Geração e avaliação local de senhas.
- Análise estrutural de URLs.
- Diagnóstico de conectividade e DNS.
- Tratamento de operações externas explícitas.

## Sprint 5 — Processos e histórico

**Objetivo:** completar as ferramentas restantes e disponibilizar consultas e relatórios.

**Histórias:**
- US-013 — Listar processos do sistema.
- US-005 — Consultar histórico.
- US-006 — Exportar relatórios.

**Incremento esperado:**
- Listagem e filtros de processos.
- Consulta do histórico.
- Exportação JSON e CSV.
- Sete módulos funcionais disponíveis.

## Sprint 6 — Qualidade e estabilização

**Objetivo:** validar a aplicação completa antes de considerar o MVP concluído.

**Histórias:**
- US-014 — Validar segurança.
- US-015 — Validar integração e regressão.
- US-016 — Validar compatibilidade Windows e Linux.

**Incremento esperado:**
- Testes de segurança aprovados.
- Testes de integração e regressão aprovados.
- Compatibilidade verificada.
- Correções críticas concluídas.

# 7. Matriz de rastreabilidade

| Épico | Requisitos relacionados | Regras relacionadas |
|---|---|---|
| EP-001 | RNF-001, RNF-002, RNF-010, RNF-011, RNF-012, RNF-013 | RN-007, RN-010, RN-012 |
| EP-002 | RF-025 a RF-028, RNF-007 | RN-009, RN-010, RN-011 |
| EP-003 | RF-001 a RF-008, RNF-003, RNF-004, RNF-008 | RN-001, RN-002, RN-003, RN-004, RN-010 |
| EP-004 | RF-013 a RF-020, RNF-004, RNF-005 | RN-005, RN-006 |
| EP-005 | RF-009 a RF-012, RNF-006, RNF-009 | RN-007 |
| EP-006 | RF-021 a RF-024, RNF-001, RNF-002 | RN-008, RN-012 |
| EP-007 | RNF-001 a RNF-014 | RN-001 a RN-012 |

# 8. Definition of Ready

Uma história poderá iniciar seu desenvolvimento quando:

- Seu objetivo estiver compreendido.
- Seus critérios de aceitação estiverem definidos.
- Seus requisitos relacionados estiverem identificados.
- Suas dependências estiverem resolvidas.
- As regras de negócio aplicáveis estiverem documentadas.
- Os riscos de segurança relevantes estiverem identificados.

# 9. Definition of Done

Uma história será considerada concluída quando:

- A funcionalidade atender aos critérios de aceitação.
- Os testes unitários aplicáveis forem aprovados.
- Os testes de integração aplicáveis forem aprovados.
- Os controles de segurança relacionados forem verificados.
- Os erros forem tratados adequadamente.
- Não houver exposição indevida de dados sensíveis.
- A documentação relacionada estiver consistente.
- Não houver falhas críticas conhecidas.

# 10. Dependências e sequência de implementação

A sequência principal de dependências é:

1. US-001 e US-002 estabelecem a fundação.
2. US-003 e US-004 estabelecem a persistência.
3. Os módulos funcionais passam a utilizar os contratos de execução e resultado.
4. US-005 e US-006 utilizam os registros persistidos.
5. US-014, US-015 e US-016 validam o conjunto implementado.

Não existem dependências circulares planejadas.

A implementação dos módulos funcionais depende dos contratos de execução e resultado, mas não deve criar dependência direta entre os módulos.

# 11. Itens fora do backlog do MVP

Os seguintes itens não fazem parte deste backlog:

- Agente de IA.
- Integração com modelos de IA.
- Memória de IA.
- Antivírus em tempo real.
- Quarentena automática.
- Exclusão automática de arquivos.
- Análise comportamental.
- Execução controlada de malware.
- Drivers de kernel.
- Varredura e exploração de portas de terceiros.
- Telemetria remota obrigatória.
- Contas e infraestrutura em nuvem.

Essas funcionalidades não devem ser adicionadas às Sprints atuais.

# 12. Estado do backlog

| Critério | Situação |
|---|---|
| Épicos | Definidos |
| Histórias de usuário | Definidas |
| Prioridades | Definidas |
| Dependências | Mapeadas |
| Tarefas técnicas | Definidas |
| Critérios de aceitação | Definidos |
| Planejamento de Sprints | Proposto |
| Rastreabilidade | Definida |
| Revisão de consistência | Pendente |

