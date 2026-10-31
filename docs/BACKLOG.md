# BACKLOG.md

**Projeto:** Odyssey AV  
**Versão:** 2.4<br>
**Escopo:** MVP  
**Status:** Revisado após auditoria documental

---

# 1. Objetivo

Este documento organiza o desenvolvimento do MVP do Odyssey AV em épicos, histórias de usuário e tarefas técnicas.

O backlog estabelece uma sequência de implementação baseada nas dependências entre funcionalidades, na arquitetura definida e nos requisitos documentados.

Seu objetivo é manter a rastreabilidade entre requisitos, regras de negócio, segurança, testes e entregas.

Os itens deste documento representam o escopo do MVP. Funcionalidades futuras não deverão ser incorporadas sem decisão explícita.

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
- Configuração local opcional por TOML.
- Logs centralizados e sanitizados.
- Tratamento padronizado de erros.
- Controle de instância única.
- Recuperação de execuções interrompidas.
- Modo degradado quando a recuperação do histórico falhar.
- Testes automatizados.
- Compatibilidade com Windows e Linux.

# 3. Critérios de prioridade

| Prioridade | Significado |
|---|---|
| P0 | Crítica — necessária para viabilizar o MVP ou proteger sua operação |
| P1 | Alta — necessária para completar funcionalidades importantes |
| P2 | Média — importante, mas pode ser implementada após os componentes essenciais |
| P3 | Futura — fora do escopo atual |

A prioridade representa a importância da entrega, não necessariamente sua ordem de implementação.

# 4. Épicos

| ID | Épico | Objetivo | Prioridade |
|---|---|---|---|
| EP-001 | Fundação e arquitetura | Preparar estrutura técnica, configuração e ciclo de vida da aplicação | P0 |
| EP-002 | Persistência e histórico | Registrar, consultar e exportar execuções e resultados | P0 |
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
- Os comandos devem possuir estrutura organizada.
- A CLI deve encaminhar operações para a camada de aplicação.
- Erros devem ser apresentados de maneira compreensível.
- A estrutura deve respeitar a arquitetura modular definida.
- A interface deve possuir comandos de ajuda.
- A aplicação deve funcionar sem exigir privilégios administrativos.
- A CLI deverá apresentar saídas textuais e JSON conforme o contrato definido.
- Os códigos de saída deverão seguir o contrato documentado.

**Tarefas técnicas:**

- TEC-001 — Configurar projeto Python.
- TEC-002 — Configurar dependências do projeto.
- TEC-003 — Configurar Typer.
- TEC-004 — Criar estrutura inicial de diretórios.
- TEC-005 — Implementar ponto de entrada da aplicação.
- TEC-006 — Implementar tratamento centralizado de erros.
- TEC-080 — Implementar contratos de saída textual e JSON.
- TEC-081 — Implementar códigos de saída definidos em `API.md`.

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
- O TOML deverá ser opcional.
- A precedência deverá ser padrões internos, TOML e argumentos explícitos da CLI.
- Arquivos TOML inválidos deverão produzir erro claro.

**Tarefas técnicas:**

- TEC-007 — Implementar carregamento de configuração TOML.
- TEC-008 — Implementar validação de configurações.
- TEC-009 — Implementar serviço centralizado de logs.
- TEC-010 — Definir contratos de erro e resultado.
- TEC-011 — Implementar identificador de execução.
- TEC-082 — Implementar precedência entre padrões, TOML e argumentos CLI.
- TEC-083 — Implementar sanitização de logs, mensagens e dados de execução.

### US-017 — Controlar ciclo de vida e instância da aplicação

- **Épico:** EP-001
- **Prioridade:** P0
- **Sprint:** 1 e 2, conforme as tarefas
- **Dependências gerais:** US-001 e US-002
- **Dependência específica da recuperação:** US-003 e US-004

**História:**

Como usuário, quero que somente uma instância do Odyssey AV execute operações por vez, garantindo consistência no acesso aos recursos e ao histórico.

**Critérios de aceitação:**

- A aplicação deverá adquirir um bloqueio exclusivo do sistema operacional durante sua execução.
- Uma segunda instância não deverá executar operações funcionais enquanto a primeira estiver ativa.
- Cada inicialização deverá gerar um `instance_id` UUID.
- O bloqueio deverá ser liberado após encerramento normal.
- O bloqueio deverá ser liberado pelo sistema operacional após encerramento inesperado.
- A recuperação do histórico deverá ocorrer após a aquisição do bloqueio.
- Registros `RUNNING` de instâncias anteriores deverão ser marcados como `INTERRUPTED`, quando a recuperação for concluída.
- A identificação da instância não deverá depender exclusivamente do PID.
- Se a recuperação falhar, a aplicação deverá entrar em modo degradado.
- O bloqueio exclusivo deverá permanecer ativo durante o modo degradado.
- O comportamento deverá ser validado em Windows e Linux.

**Tarefas técnicas:**

- TEC-084 — Definir contrato de gerenciamento de instância.
- TEC-085 — Implementar mecanismo de bloqueio exclusivo para Windows e Linux.
- TEC-086 — Gerar UUID por inicialização.
- TEC-087 — Implementar liberação do bloqueio no encerramento normal.
- TEC-088 — Implementar recuperação de registros RUNNING anteriores após a disponibilidade da persistência.
- TEC-089 — Implementar tratamento de falha na aquisição do bloqueio.
- TEC-090 — Criar testes de ciclo de vida e recuperação.
- TEC-109 — Implementar estado operacional NORMAL e DEGRADED.
- TEC-110 — Implementar transição para modo degradado diante de falha na recuperação.
- TEC-111 — Impedir gravações no SQLite enquanto degradado.
- TEC-112 — Bloquear consultas e exportações do HISTORY enquanto degradado.
- TEC-113 — Informar ao usuário a indisponibilidade do histórico e a não persistência das operações.
- TEC-114 — Garantir nova tentativa de recuperação em inicialização posterior.

**Separação de execução:**

- Na Sprint 1 serão implementados o bloqueio exclusivo, o identificador da instância e seu ciclo de vida.
- Na Sprint 2 serão implementadas a recuperação do histórico e a transição para modo degradado, pois essas operações dependem do SQLite.
- A recuperação deverá depender da conclusão das estruturas de persistência e dos contratos necessários de `AnalysisRun`.
- A dependência da recuperação não deverá bloquear a implementação anterior do controle de instância.

## EP-002 — Persistência e histórico

### US-003 — Registrar execuções

- **Épico:** EP-002
- **Prioridade:** P0
- **Sprint:** 2
- **Dependências:** US-001, US-002 e conclusão das tarefas TEC-085 e TEC-086 de US-017.

**História:**

Como usuário, quero que as execuções das ferramentas sejam registradas para consultar posteriormente o que foi executado.

**Critérios de aceitação:**

- Cada execução deve possuir identificador único.
- O módulo executado deve ser identificado.
- O estado da execução deve ser registrado.
- Os horários de início e término devem ser armazenados.
- A duração deve ser registrada quando disponível.
- Os registros devem utilizar os estados definidos no domínio.
- Cada execução deverá possuir `instance_id`.
- Informações sensíveis não devem ser persistidas.
- Execuções funcionais deverão ser registradas mesmo quando terminarem com falha, desde que a persistência esteja disponível.
- Falhas de persistência deverão ser comunicadas separadamente do resultado funcional.
- Nenhuma gravação deverá ser realizada em modo degradado.
- Durante uma sessão iniciada em `NORMAL`, uma falha de gravação não deverá alterar o resultado funcional nem mudar automaticamente o estado para `DEGRADED`.
- A falha ao registrar inicialmente `RUNNING` não deverá impedir a execução da operação funcional.
- Cada operação funcional posterior deverá realizar sua própria tentativa normal de persistência; não haverá fila em memória ou armazenamento alternativo.
- Registros anteriormente confirmados deverão permanecer inalterados; dados não confirmados não serão recuperados posteriormente.

**Tarefas técnicas:**

- TEC-012 — Configurar conexão SQLite.
- TEC-013 — Criar estrutura da tabela AnalysisRun.
- TEC-014 — Implementar repositório de execuções.
- TEC-015 — Implementar registro de início e término.
- TEC-016 — Implementar persistência de estados de execução.
- TEC-091 — Implementar persistência de `instance_id`.
- TEC-092 — Implementar estados RUNNING, SUCCESS, PARTIAL, FAILED e INTERRUPTED.
- TEC-093 — Implementar separação entre resultado funcional e estado da persistência, com falha tratada por operação, sem transição automática para `DEGRADED` e com novas tentativas normais em operações posteriores.

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
- Mensagens e dados persistidos deverão ser sanitizados.
- Resultados de operações PASSWORD não poderão conter valores de senha.
- Uma falha ao persistir resultados não deverá alterar o resultado funcional nem os registros anteriormente confirmados.

**Tarefas técnicas:**

- TEC-017 — Criar estrutura da tabela AnalysisResult.
- TEC-018 — Implementar relacionamento entre execução e resultado.
- TEC-019 — Implementar repositório de resultados.
- TEC-020 — Implementar transações de persistência.
- TEC-021 — Testar integridade referencial e rollback.
- TEC-094 — Implementar sanitização de resultados e mensagens.
- TEC-095 — Validar restrições de persistência de dados sensíveis.

### US-005 — Consultar histórico

- **Épico:** EP-002
- **Prioridade:** P1
- **Sprint:** 5
- **Dependências:** US-003, US-004 e estado operacional NORMAL

**História:**

Como usuário, quero consultar o histórico de execuções para visualizar análises anteriores.

**Critérios de aceitação:**

- Deve ser possível consultar por módulo.
- Deve ser possível consultar por período.
- Deve ser possível consultar por estado.
- Os resultados associados devem poder ser consultados.
- Consultas não devem criar novas execuções.
- Consultas vazias devem apresentar resposta adequada.
- A consulta deverá respeitar limites e paginação.
- Os filtros deverão utilizar consultas parametrizadas.
- Consultas deverão ser recusadas em modo degradado.
- Se o SQLite estiver indisponível durante uma sessão `NORMAL`, a falha da consulta deverá ser comunicada como erro da operação `HISTORY`.

**Tarefas técnicas:**

- TEC-022 — Implementar filtros de histórico.
- TEC-023 — Implementar consulta de resultados associados.
- TEC-024 — Implementar comandos de consulta na CLI.
- TEC-096 — Implementar paginação e limites de consulta.
- TEC-097 — Testar ausência de recursão no histórico.

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
- Exportações não devem criar novas execuções.
- A exportação deverá respeitar limites operacionais.
- Exportações deverão ser recusadas em modo degradado.
- Se o SQLite estiver indisponível durante uma sessão `NORMAL`, a falha da exportação deverá ser comunicada como erro da operação `HISTORY`.

**Tarefas técnicas:**

- TEC-025 — Implementar exportador JSON.
- TEC-026 — Implementar exportador CSV.
- TEC-027 — Implementar validação dos dados exportados.
- TEC-028 — Testar exportações e proteção de dados sensíveis.
- TEC-098 — Implementar limites de exportação.
- TEC-099 — Validar ausência de recursão nas operações de exportação.

## EP-003 — Análise de arquivos e hashes

### US-007 — Analisar arquivos

- **Épico:** EP-003
- **Prioridade:** P0
- **Sprint:** 3
- **Dependências:** US-001, US-002, US-003 e US-004

**História:**

Como usuário, quero analisar arquivos para identificar metadados e possíveis divergências entre extensão e formato real.

**Critérios de aceitação:**

- Deve apresentar nome, extensão e tamanho.
- Deve identificar assinaturas dos formatos suportados.
- Deve identificar divergências entre extensão e assinatura.
- Deve apresentar indicadores encontrados.
- Deve informar quando um formato não for suportado.
- Não deve executar nem modificar o arquivo analisado.
- Deve aceitar somente arquivos regulares.
- Deve rejeitar diretórios, dispositivos, sockets e pipes.
- Não deve seguir links simbólicos automaticamente.
- Deve tratar arquivos removidos, alterados ou sem permissão durante a leitura.
- A leitura deverá utilizar blocos.
- A análise deverá respeitar as permissões do sistema operacional.

**Tarefas técnicas:**

- TEC-029 — Implementar leitura segura de arquivos.
- TEC-030 — Implementar extração de metadados.
- TEC-031 — Definir assinaturas dos formatos suportados.
- TEC-032 — Implementar identificação de assinaturas.
- TEC-033 — Implementar comparação entre extensão e assinatura.
- TEC-034 — Implementar apresentação dos resultados na CLI.
- TEC-035 — Criar testes com arquivos controlados.
- TEC-100 — Implementar validação de arquivos regulares e rejeição de arquivos especiais.
- TEC-101 — Implementar tratamento de links simbólicos.
- TEC-102 — Implementar tratamento de alterações e desaparecimento durante leitura.
- TEC-103 — Validar identificação PE, ELF, PDF, PNG, JPEG, ZIP e GZIP.

### US-008 — Calcular e comparar hashes

- **Épico:** EP-003
- **Prioridade:** P0
- **Sprint:** 3
- **Dependências:** US-001, US-002, US-003 e US-004

**História:**

Como usuário, quero calcular e comparar hashes SHA-256 para verificar a integridade de arquivos.

**Critérios de aceitação:**

- Deve calcular SHA-256 sobre os bytes reais do arquivo.
- Deve permitir comparação com uma referência fornecida pelo usuário.
- Deve retornar MATCH quando os hashes forem iguais.
- Deve retornar MISMATCH quando forem diferentes.
- Deve retornar NO_REFERENCE quando não existir referência.
- Não deve utilizar uma base própria de hashes no MVP.
- Não deve modificar o arquivo analisado.
- A leitura deverá utilizar blocos.

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
- **Dependências:** US-001 e US-002

**História:**

Como usuário, quero gerar senhas com parâmetros configuráveis para criar credenciais seguras.

**Critérios de aceitação:**

- Deve permitir definir comprimento.
- Deve permitir selecionar conjuntos de caracteres.
- Deve utilizar fonte criptograficamente segura de aleatoriedade.
- Deve validar parâmetros inválidos.
- A senha gerada não deve ser armazenada no histórico ou nos logs.
- A senha não deverá ser incluída em mensagens, argumentos persistidos ou relatórios.

**Tarefas técnicas:**

- TEC-041 — Implementar geração com `secrets`.
- TEC-042 — Implementar parâmetros de geração.
- TEC-043 — Implementar validações.
- TEC-044 — Criar testes de geração.

### US-010 — Avaliar senhas

- **Épico:** EP-004
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001 e US-002

**História:**

Como usuário, quero avaliar características de uma senha para entender sua qualidade estimada.

**Critérios de aceitação:**

- Deve avaliar características básicas de composição.
- Deve apresentar uma avaliação compreensível.
- Não deve transmitir a senha para serviços externos.
- Não deve persistir a senha.
- A avaliação não deve ser apresentada como garantia de segurança absoluta.
- A entrada da senha deverá evitar exposição desnecessária no terminal.

**Tarefas técnicas:**

- TEC-045 — Implementar avaliação local.
- TEC-046 — Definir critérios básicos de avaliação.
- TEC-047 — Implementar proteção contra exposição da senha.
- TEC-048 — Criar testes de avaliação.

### US-011 — Analisar URLs

- **Épico:** EP-004
- **Prioridade:** P1
- **Sprint:** 4
- **Dependências:** US-001, US-002, US-003 e US-004

**História:**

Como usuário, quero analisar URLs para identificar características estruturais e indicadores potencialmente suspeitos.

**Critérios de aceitação:**

- Deve decompor os componentes da URL.
- Deve realizar normalização.
- Deve identificar indicadores potencialmente suspeitos.
- Deve tratar entradas inválidas.
- Não deve realizar requisições automáticas ao destino.
- Não deve executar conteúdo encontrado na URL.
- A análise deverá ser local.

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
- **Dependências:** US-001, US-002, US-003 e US-004

**História:**

Como usuário, quero verificar conectividade e resolução DNS para identificar problemas básicos de rede.

**Critérios de aceitação:**

- Deve permitir executar diagnóstico por comando explícito.
- Deve realizar consulta DNS.
- Deve apresentar falhas de resolução.
- Deve utilizar timeout nas operações.
- Deve informar operações incompletas.
- Não deve executar comunicação externa oculta.
- A consulta de IP público deverá ser opcional.

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
- **Dependências:** US-001, US-002, US-003 e US-004

**História:**

Como usuário, quero listar processos em execução para consultar informações básicas do sistema.

**Critérios de aceitação:**

- Deve listar processos acessíveis.
- Deve apresentar PID e nome.
- Deve apresentar métricas disponíveis.
- Deve permitir filtros por PID e nome.
- Deve tratar processos inacessíveis ou encerrados.
- Não deve encerrar, suspender ou modificar processos.
- A consulta deverá respeitar as permissões do usuário.

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
- **Dependências:** US-007, US-008, US-009, US-010, US-011, US-012, US-013 e US-017

**História:**

Como usuário, quero que as ferramentas respeitem os controles de segurança definidos para evitar ações inesperadas e exposição de informações.

**Critérios de aceitação:**

- Arquivos analisados não podem ser executados ou modificados.
- Arquivos especiais devem ser rejeitados.
- Links simbólicos não devem ser seguidos automaticamente.
- Senhas não podem ser persistidas.
- URLs não podem gerar requisições automáticas.
- Processos não podem ser alterados.
- Consultas SQLite devem ser parametrizadas.
- Dados sensíveis não podem aparecer em logs ou relatórios.
- A aplicação não deve solicitar elevação automática de privilégios.
- O controle de instância única deverá funcionar.
- Falhas de persistência deverão ser comunicadas sem alterar indevidamente o resultado funcional.
- A recuperação do histórico deverá ser validada.
- O modo degradado deverá impedir operações HISTORY e novas gravações.
- O bloqueio exclusivo deverá permanecer ativo durante o modo degradado.

**Tarefas técnicas:**

- TEC-065 — Executar testes de segurança.
- TEC-066 — Revisar persistência de dados sensíveis.
- TEC-067 — Revisar validação de entradas.
- TEC-068 — Revisar permissões de arquivos e processos.
- TEC-069 — Corrigir falhas identificadas.
- TEC-104 — Validar proteção de senhas em todos os fluxos.
- TEC-105 — Validar bloqueio de instância e recuperação.
- TEC-106 — Validar tratamento de falhas de persistência.
- TEC-115 — Validar entrada e permanência em modo degradado.
- TEC-116 — Validar bloqueio de HISTORY e ausência de gravações durante modo degradado.
- TEC-117 — Validar nova tentativa de recuperação após reinicialização.

### US-015 — Validar integração e regressão

- **Épico:** EP-007
- **Prioridade:** P0
- **Sprint:** 6
- **Dependências:** US-003, US-004, US-007, US-008, US-009, US-010, US-011, US-012, US-013 e US-017

**História:**

Como desenvolvedor, quero validar os fluxos completos da aplicação para garantir que os módulos funcionem em conjunto.

**Critérios de aceitação:**

- Os módulos devem funcionar pela CLI.
- As execuções devem ser registradas corretamente quando a persistência estiver disponível.
- Os resultados devem estar associados às execuções.
- O histórico deve permitir consulta e exportação quando disponível.
- Os testes de regressão devem ser aprovados.
- Falhas de um módulo não devem comprometer indevidamente os demais.
- A recuperação de execuções interrompidas deverá funcionar.
- A separação entre operação funcional e persistência deverá ser validada.
- Os fluxos de modo normal e degradado deverão ser validados.

**Tarefas técnicas:**

- TEC-070 — Executar testes de integração.
- TEC-071 — Executar testes de regressão.
- TEC-072 — Validar persistência e transações.
- TEC-073 — Validar controle de instância única e acesso ao SQLite.
- TEC-074 — Verificar cobertura de testes.
- TEC-075 — Corrigir falhas de integração.
- TEC-118 — Validar os fluxos completos de operação em modo degradado.

### US-016 — Validar compatibilidade Windows e Linux

- **Épico:** EP-007
- **Prioridade:** P1
- **Sprint:** 6
- **Dependências:** US-007, US-012, US-013, US-015 e US-017

**História:**

Como usuário, quero executar o Odyssey AV em Windows e Linux para utilizar as ferramentas em diferentes sistemas operacionais.

**Critérios de aceitação:**

- A aplicação deve iniciar nos dois sistemas.
- Os caminhos devem ser tratados corretamente.
- Particularidades do sistema operacional devem ser isoladas.
- Limitações de permissões devem ser comunicadas.
- Os módulos devem manter comportamento consistente quando as funcionalidades forem suportadas.
- O bloqueio exclusivo deverá funcionar nos dois sistemas.
- O encerramento e a recuperação deverão ser testados nas duas plataformas.
- O modo degradado deverá manter o comportamento definido nas duas plataformas.

**Tarefas técnicas:**

- TEC-076 — Validar execução no Windows.
- TEC-077 — Validar execução no Linux.
- TEC-078 — Revisar adaptadores de plataforma.
- TEC-079 — Corrigir incompatibilidades encontradas.
- TEC-107 — Validar mecanismo de bloqueio no Windows.
- TEC-108 — Validar mecanismo de bloqueio no Linux.
- TEC-119 — Validar modo degradado no Windows e Linux.

# 6. Planejamento das Sprints

As Sprints terão duração aproximada de duas semanas. A distribuição representa uma sequência inicial de implementação, não uma estimativa fechada de esforço.

## Sprint 1 — Fundação e ciclo de vida

**Objetivo:** preparar a estrutura da aplicação e seu controle de execução.

**Histórias:**

- US-001 — Preparar estrutura da aplicação.
- US-002 — Configurar serviços transversais.
- US-017 — Controlar ciclo de vida e instância da aplicação, limitado à aquisição e liberação do bloqueio e identificação da instância.

**Incremento esperado:**

- Projeto Python inicializado.
- CLI funcional.
- Estrutura modular criada.
- Configuração e logs centralizados.
- Controle de instância única.
- Identificador UUID por inicialização.
- Bloqueio exclusivo validado em Windows e Linux.

## Sprint 2 — Persistência e recuperação

**Objetivo:** implementar o armazenamento, a integridade dos registros e a recuperação de execuções anteriores.

**Histórias:**

- US-003 — Registrar execuções.
- US-004 — Registrar resultados.
- US-017 — Concluir ciclo de vida e recuperação do histórico.

**Incremento esperado:**

- SQLite configurado.
- Entidades persistidas.
- Relacionamento entre execução e resultado.
- Estados de execução definidos.
- Transações e integridade referencial testadas.
- Separação entre resultado funcional e persistência.
- Recuperação de registros RUNNING anteriores.
- Estado operacional NORMAL e DEGRADED.
- Bloqueio de novas gravações e HISTORY durante modo degradado.

**Ordem técnica obrigatória:**

1. Confirmar que o bloqueio exclusivo e o `instance_id` estão implementados.
2. Implementar a persistência de `AnalysisRun`.
3. Implementar a persistência de `AnalysisResult`.
4. Garantir transações e integridade referencial.
5. Implementar a recuperação de execuções anteriores.
6. Implementar o modo degradado e seus controles.
7. Validar recuperação bem-sucedida, falha de recuperação e nova tentativa em inicialização posterior.

A recuperação não poderá ser implementada como dependência circular da persistência: ela deverá consumir os contratos e repositórios já disponibilizados por US-003 e US-004.

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
- Resultados registrados no histórico quando a persistência estiver disponível.

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
- HISTORY respeitando o estado operacional da aplicação.

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
- Recuperação de execuções interrompidas validada.
- Modo degradado validado.
- Correções críticas concluídas.

# 7. Matriz de rastreabilidade

A matriz relaciona os épicos aos requisitos e regras de negócio.

| Épico | Requisitos relacionados | Regras relacionadas |
|---|---|---|
| EP-001 | RF-030 (recuperação), RF-031 (instância), RF-032 (separação), RF-033 (modo degradado); RNF-001, RNF-002, RNF-010 a RNF-013, RNF-016 a RNF-018 | RN-007, RN-009, RN-010, RN-012 |
| EP-002 | RF-025 a RF-028, RF-032 a RF-033; RNF-007, RNF-015, RNF-018 | RN-009, RN-010, RN-011, RN-013 |
| EP-003 | RF-001 a RF-008, RF-029; RNF-003, RNF-004, RNF-008, RNF-015 | RN-001, RN-002, RN-003, RN-004, RN-010 |
| EP-004 | RF-013 a RF-020; RNF-004, RNF-005, RNF-015 | RN-005, RN-006 |
| EP-005 | RF-009 a RF-012; RNF-006, RNF-009, RNF-015 | RN-007 |
| EP-006 | RF-021 a RF-024; RNF-001, RNF-002, RNF-015 | RN-008, RN-012 |
| EP-007 | Requisitos funcionais e não funcionais aplicáveis ao MVP | Regras de negócio aplicáveis ao MVP |

**Observação:** as referências RF/RNF/RN foram conferidas nos documentos correspondentes. A rastreabilidade do modo degradado aponta para o requisito e as decisões existentes que descrevem a falha de recuperação durante a inicialização.

Esta matriz não autoriza criar requisitos ou regras que não estejam documentados.

# 8. Matriz de rastreabilidade dos critérios de aceitação e testes

Os identificadores CT representam critérios verificáveis de aceitação. Os IDs de teste apontam para casos documentados em `TESTES.md` versão 2.3.

| ID | História | Critério verificável | Testes relacionados |
|---|---|---|---|
| CT-001 | US-001 | Inicialização, organização dos comandos e ajuda da CLI | TC-CLI-001 a TC-CLI-011 |
| CT-002 | US-002 | Configuração opcional, validação e precedência TOML | TU-CONFIG-001 a TU-CONFIG-007 |
| CT-003 | US-017 | Aquisição e exclusividade do bloqueio | TCO-001, TCO-002 |
| CT-004 | US-017 | Liberação do bloqueio em encerramento normal e inesperado | TCO-003, TCO-004 |
| CT-005 | US-017 | UUID distinto por inicialização e associação correta | TCO-006, TCO-007 |
| CT-006 | US-003 | Registro de execução, estados e horários | TU-HIST-001, TI-002, TB-001 |
| CT-007 | US-004 | Associação de resultados e integridade referencial | TU-HIST-002, TB-002, TB-003, TB-007 |
| CT-008 | US-003, US-004 | Separação entre resultado funcional e persistência | TI-008, TR-006, TS-017 |
| CT-009 | US-003, US-004 | Proteção contra persistência de segredos | TU-HIST-011, TU-HIST-015, TS-014 |
| CT-010 | US-005 | Consultas por módulo, período e estado | TU-HIST-003 a TU-HIST-005 |
| CT-011 | US-005 | Consultas sem recursão e com paginação | TU-HIST-009, TID-001, TU-HIST-003 a TU-HIST-005 |
| CT-012 | US-006 | Exportação JSON e CSV válida | TU-HIST-006, TU-HIST-007, TI-004 |
| CT-013 | US-006 | Exportação sem senhas ou segredos | TU-HIST-010, TS-009, TS-018 |
| CT-014 | US-007 | Análise de metadados e assinaturas | TU-FILE-001, TU-FILE-013 a TU-FILE-020 |
| CT-015 | US-007 | Rejeição de arquivos especiais e tratamento de links | TU-FILE-008 a TU-FILE-010, TS-011 a TS-013 |
| CT-016 | US-007 | Tratamento de alteração ou desaparecimento de arquivo | TU-FILE-011, TU-FILE-012 |
| CT-017 | US-008 | Cálculo SHA-256 e processamento em blocos | TU-HASH-001, TU-HASH-002, TU-HASH-007 |
| CT-018 | US-008 | Comparação de referência fornecida pelo usuário | TU-HASH-003 a TU-HASH-006 |
| CT-019 | US-009 | Geração segura e validação de parâmetros | TU-PASS-001, TU-PASS-002, TU-PASS-005 |
| CT-020 | US-010 | Avaliação local sem persistência ou exposição | TU-PASS-003, TU-PASS-004, TU-PASS-007, TU-PASS-008 |
| CT-021 | US-011 | Análise estrutural local sem requisições automáticas | TU-URL-001 a TU-URL-007 |
| CT-022 | US-012 | Diagnóstico DNS, conectividade e timeout | TU-NET-001 a TU-NET-008 |
| CT-023 | US-013 | Listagem e filtros de processos sem modificação | TU-PROC-001 a TU-PROC-007 |
| CT-024 | US-017 | Recuperação de registros RUNNING anteriores | TI-013, TS-016, TCO-005 |
| CT-025 | US-017 | Falha de recuperação resulta em modo degradado | TI-014, TS-019, TR-008 |
| CT-026 | US-017 | Modo degradado impede novas gravações | TU-HIST-018, TS-021, TB-013 |
| CT-027 | US-005, US-006, US-017 | HISTORY indisponível em modo degradado | TU-HIST-016, TU-HIST-017, TI-021, TS-020 |
| CT-028 | US-017 | Ferramentas funcionais permanecem disponíveis em modo degradado | TI-015 a TI-020, TI-024 |
| CT-029 | US-017 | Bloqueio exclusivo permanece ativo em modo degradado | TCO-008, TCO-009, TS-025 |
| CT-030 | US-017 | Nova inicialização tenta recuperar o histórico | TI-022 |
| CT-031 | US-017 | Falha de recuperação não altera indevidamente registros antigos | TI-023, TR-007, TS-024 |
| CT-032 | US-014 | Controles de segurança aplicados aos módulos | TS-001 a TS-025 |
| CT-033 | US-015 | Fluxos completos e regressão aprovados | TI-001 a TI-025 e suíte de regressão |
| CT-034 | US-016 | Compatibilidade Windows/Linux | TPL-001 a TPL-014 |
| CT-035 | US-017 | Modo degradado validado em Windows/Linux | TPL-013, TPL-014, TCO-008, TCO-009 |
| CT-036 | US-003, US-004 | Falha isolada de persistência preserva o resultado funcional e não altera o estado operacional | TI-008, TI-026, TR-006, TC-CLI-013 |
| CT-037 | US-003 | Operação subsequente tenta persistir normalmente, sem fila ou armazenamento alternativo | TI-026 |
| CT-038 | US-003, US-004 | Registros confirmados permanecem inalterados após falha de gravação | TI-027, TR-011 |
| CT-039 | US-005, US-006 | Falha de consulta ou exportação HISTORY é comunicada como erro da operação | TI-028, TR-012, TC-CLI-015 |
| CT-040 | US-001, US-003, US-005 | Códigos de saída distinguem falha funcional, falha de persistência, resultado parcial e falha HISTORY | TC-CLI-012 a TC-CLI-016 |

**Regras de rastreabilidade:**

- Um CT deverá apontar somente para casos de teste existentes.
- Um teste deverá verificar o comportamento descrito pelo critério.
- Referências a tarefas TEC não substituem referências a casos de teste.
- Um caso de teste definido não significa que o teste já foi implementado ou aprovado.
- Critérios sem teste específico deverão ser identificados como pendentes de rastreabilidade.
- A matriz deverá ser atualizada sempre que os IDs de `TESTES.md` forem alterados.
- A correspondência semântica entre cada critério e seus testes deverá ser validada na revisão cruzada final.

# 9. Definition of Ready

Uma história poderá iniciar seu desenvolvimento quando:

- Seu objetivo estiver compreendido.
- Seus critérios de aceitação estiverem definidos.
- Seus requisitos relacionados estiverem identificados.
- Suas dependências estiverem resolvidas.
- As regras de negócio aplicáveis estiverem documentadas.
- Os riscos de segurança relevantes estiverem identificados.
- Os testes necessários puderem ser definidos.
- Os critérios de aceitação possuírem rastreabilidade por CT quando aplicável.

# 10. Definition of Done

Uma história será considerada concluída quando:

- A funcionalidade atender aos critérios de aceitação.
- Os testes unitários aplicáveis forem aprovados.
- Os testes de integração aplicáveis forem aprovados.
- Os controles de segurança relacionados forem verificados.
- Os erros forem tratados adequadamente.
- Não houver exposição indevida de dados sensíveis.
- A documentação relacionada estiver consistente.
- Não houver falhas críticas conhecidas.
- Os critérios de compatibilidade aplicáveis forem atendidos.
- Os casos de teste relacionados estiverem associados aos critérios de aceitação.
- O comportamento em modo degradado estiver validado quando aplicável.

# 11. Dependências e sequência de implementação

A sequência principal de dependências é:

1. US-001 estabelece a estrutura de execução.
2. US-002 estabelece os serviços transversais.
3. US-017 implementa o bloqueio exclusivo e a identificação da instância.
4. US-003 e US-004 estabelecem a persistência.
5. US-017 conclui a recuperação do histórico e o modo degradado com a persistência disponível.
6. Os módulos funcionais utilizam os contratos de execução e resultado.
7. US-005 e US-006 utilizam os registros persistidos e exigem estado operacional NORMAL.
8. US-014, US-015 e US-016 validam o conjunto implementado.

### 11.1. Dependências técnicas de US-017

Para evitar dependência circular, a história US-017 deverá ser acompanhada em duas etapas:

**Etapa A — Controle de instância (Sprint 1):**

- TEC-084 — Definir contrato de gerenciamento de instância.
- TEC-085 — Implementar mecanismo de bloqueio exclusivo.
- TEC-086 — Gerar UUID por inicialização.
- TEC-087 — Implementar liberação do bloqueio.
- TEC-089 — Implementar tratamento de falha na aquisição do bloqueio.

Essas tarefas não dependem da persistência SQLite.

**Etapa B — Recuperação e modo degradado (Sprint 2):**

- TEC-088 — Implementar recuperação de registros RUNNING anteriores.
- TEC-090 — Criar testes de ciclo de vida e recuperação.
- TEC-109 — Implementar estado operacional NORMAL e DEGRADED.
- TEC-110 — Implementar transição para modo degradado diante de falha na recuperação.
- TEC-111 — Impedir gravações no SQLite enquanto degradado.
- TEC-112 — Bloquear consultas e exportações do HISTORY enquanto degradado.
- TEC-113 — Informar indisponibilidade do histórico e não persistência.
- TEC-114 — Garantir nova tentativa de recuperação em inicialização posterior.

A Etapa B depende da conclusão dos contratos e mecanismos de persistência de US-003 e US-004.

### 11.2. Regras gerais de dependência

- Os módulos funcionais não deverão acessar diretamente o SQLite.
- As operações de HISTORY não deverão criar novos registros de execução.
- A execução funcional deverá permanecer separada da persistência do histórico.
- Em modo degradado, os módulos funcionais poderão operar sem persistência, mas não poderão realizar gravações alternativas.
- O controle de instância não deverá depender da conclusão da recuperação para ser implementado.
- A recuperação não poderá ser considerada concluída antes da confirmação da transação.
- A falha de recuperação deverá manter o estado persistido anterior.
- Não existem dependências circulares planejadas no grafo de implementação.

Durante uma sessão iniciada em `NORMAL`, uma falha de gravação é tratada por operação, sem transição automática para `DEGRADED`. Operações posteriores fazem suas próprias tentativas de persistência. Não há fila em memória nem armazenamento alternativo; dados não confirmados não são recuperados posteriormente e registros confirmados permanecem inalterados. Falhas de consulta ou exportação `HISTORY` por indisponibilidade do SQLite são comunicadas como erro da operação solicitada.

# 12. Itens fora do backlog do MVP

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

Essas funcionalidades não deverão ser adicionadas às Sprints atuais.

# 13. Estado do backlog

| Critério | Situação |
|---|---|
| Épicos | 7 definidos |
| Histórias de usuário | 17 definidas |
| Prioridades | Definidas |
| Dependências | Mapeadas e revisadas |
| Tarefas técnicas | 119 definidas |
| Critérios de aceitação | Definidos |
| Identificadores CT | 40 estruturados |
| Planejamento de Sprints | 6 Sprints propostas |
| Controle de instância | Incluído |
| Recuperação de execuções | Incluída |
| Modo degradado | Incluído |
| Separação entre operação e persistência | Incluída |
| Rastreabilidade de testes | Referências existentes e correspondência semântica validada |
| Rastreabilidade RF/RNF | Referências existentes e revisão cruzada concluída |
| Rastreabilidade RN | Modo degradado relacionado às regras existentes |
| Dependência circular | Corrigida na estrutura de dependências |
| Revisão cruzada | Concluída |

---

**Observação:** este backlog especifica o planejamento do MVP. A implementação das tarefas deverá ocorrer somente após a consolidação documental e a autorização explícita para iniciar o desenvolvimento.
