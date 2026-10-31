# Odyssey AV

**Ferramenta modular de diagnóstico e análise de segurança para Windows e Linux.**

O **Odyssey AV** é um projeto de segurança da informação desenvolvido em Python, com interface de linha de comando (CLI). Seu objetivo é reunir ferramentas locais de diagnóstico, análise e verificação em uma aplicação modular, com foco em segurança, integridade e organização dos resultados.

O projeto está sendo desenvolvido de forma incremental, começando por um MVP com sete módulos funcionais. Sua arquitetura deverá permitir evolução futura, sem antecipar funcionalidades que não fazem parte do escopo atual.

> **Status:** Fase 1 documental consolidada; a implementação do MVP ainda não foi iniciada. As funcionalidades descritas representam o escopo planejado e não devem ser consideradas implementadas.

---

## 1. Objetivos

- Reunir ferramentas de diagnóstico e análise de segurança em uma única aplicação.
- Oferecer operações acessíveis por linha de comando.
- Permitir análises locais sem modificar arquivos ou processos do sistema.
- Registrar execuções e resultados em histórico local.
- Manter uma arquitetura modular, organizada e testável.
- Oferecer compatibilidade com Windows e Linux.

## 2. Funcionalidades do MVP

O MVP contempla sete módulos:

| Módulo | Funcionalidade |
|---|---|
| FILE | Análise de metadados, assinaturas e divergências entre extensão e formato identificado |
| HASH | Cálculo SHA-256 e comparação com uma referência fornecida pelo usuário |
| NETWORK | Diagnóstico de conectividade, DNS e consulta opcional de IP público |
| PASSWORD | Geração segura e avaliação local básica de senhas |
| URL | Parsing, normalização e identificação de indicadores suspeitos em URLs |
| PROCESS | Listagem e monitoramento informativo de processos acessíveis |
| HISTORY | Consulta, organização e exportação do histórico de execuções |

### Limites funcionais

O MVP não contempla:

- Antivírus em tempo real.
- Execução ou análise comportamental de malware.
- Exclusão automática ou quarentena de arquivos.
- Encerramento ou modificação de processos.
- Varredura de portas de terceiros.
- Requisições automáticas aos destinos analisados pelo módulo URL.
- Serviço remoto obrigatório, conta de usuário ou telemetria.
- Agente de inteligência artificial integrado.

Essas limitações preservam o escopo inicial e permitem validar os fundamentos da aplicação antes de sua evolução.

## 3. Exemplos de utilização planejada

Os comandos abaixo representam a interface CLI prevista para o MVP:

```bash
# Análise de arquivo
odyssey file analyze ./arquivo.bin

# Cálculo de hash
odyssey hash calculate ./arquivo.bin

# Comparação de hash
odyssey hash compare ./arquivo.bin --reference HASH_ESPERADO

# Diagnóstico de rede
odyssey network diagnose

# Geração de senha
odyssey password generate

# Avaliação de senha
odyssey password evaluate

# Análise de URL
odyssey url analyze "https://example.com"

# Listagem de processos
odyssey process list

# Consulta do histórico
odyssey history list

# Exportação do histórico
odyssey history export --format json
```

Os comandos representam o contrato planejado. Sua disponibilidade dependerá da implementação correspondente.

## 4. Arquitetura e tecnologias

O projeto adota uma arquitetura modular em camadas, buscando separar responsabilidades e reduzir o acoplamento entre os componentes.

### Tecnologias previstas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal |
| Typer | Interface de linha de comando |
| SQLite | Persistência local |
| psutil | Consulta de processos e informações do sistema |
| hashlib | Cálculo de hashes |
| secrets | Geração segura de senhas |
| pytest | Testes automatizados |
| TOML | Configuração opcional |

### Organização arquitetural

A aplicação será organizada nas seguintes camadas:

- **CLI:** recebe comandos e apresenta resultados.
- **Application:** coordena casos de uso e fluxo de execução.
- **Domain:** concentra entidades e regras centrais.
- **Modules:** implementa as sete ferramentas funcionais.
- **Infrastructure:** implementa persistência e integração com recursos do sistema.
- **Shared:** reúne componentes transversais.

A persistência será local, utilizando SQLite. O histórico será composto pelas entidades `AnalysisRun` e `AnalysisResult`.

## 5. Segurança e privacidade

A segurança é um requisito transversal do projeto.

Entre os princípios definidos para o MVP:

- Não executar arquivos analisados.
- Não modificar arquivos durante a análise.
- Não encerrar ou alterar processos.
- Não armazenar senhas geradas ou avaliadas.
- Não incluir valores secretos em logs, histórico ou relatórios.
- Utilizar SHA-256 para verificação de integridade.
- Utilizar consultas parametrizadas no SQLite.
- Respeitar permissões e limites do sistema operacional.
- Não realizar requisições automáticas durante a análise de URLs.

A identificação de uma assinatura de arquivo não representa validação integral do formato nem comprovação de que o arquivo é seguro.

## 6. Histórico e persistência

O Odyssey AV deverá manter um histórico local das operações funcionais.

O modelo de dados prevê duas entidades:

- `AnalysisRun`: representa uma execução.
- `AnalysisResult`: representa os resultados associados à execução.

Os estados de execução previstos são:

- `RUNNING`
- `SUCCESS`
- `PARTIAL`
- `FAILED`
- `INTERRUPTED`

O sistema deverá controlar a execução de uma única instância ativa no MVP e recuperar registros que tenham permanecido em estado `RUNNING` após uma interrupção inesperada.

As consultas e exportações do histórico não deverão gerar novas execuções registradas.

O histórico local utilizará SQLite para registrar as operações funcionais e recuperar execuções que permanecerem em `RUNNING` após uma interrupção inesperada. Se a recuperação transacional falhar durante a inicialização, a aplicação deverá operar em modo `DEGRADED`: as ferramentas funcionais permanecerão disponíveis, enquanto novas gravações e operações `HISTORY` ficarão indisponíveis.

O resultado funcional será informado separadamente da situação do histórico. Uma falha isolada de gravação durante uma sessão `NORMAL` não provocará transição automática para `DEGRADED`; operações posteriores continuarão tentando persistir normalmente.

## 7. Compatibilidade

A aplicação será planejada para:

- Windows.
- Linux.

As diferenças entre sistemas operacionais deverão ser isoladas por adaptadores de infraestrutura.

A compatibilidade deverá ser verificada por testes automatizados nos ambientes correspondentes.

## 8. Estrutura da documentação

A documentação do projeto está organizada em `docs/`:

| Documento | Conteúdo |
|---|---|
| `REQUISITOS.md` | Requisitos funcionais e não funcionais |
| `REGRAS-DE-NEGOCIO.md` | Regras que orientam o comportamento da aplicação |
| `ARQUITETURA.md` | Organização arquitetural e responsabilidades |
| `SEGURANCA.md` | Controles, ameaças e restrições de segurança |
| `MODELO-DE-DADOS.md` | Entidades, relacionamentos e persistência |
| `API.md` | Contrato da interface CLI |
| `TESTES.md` | Estratégia e cenários de testes |
| `BACKLOG.md` | Épicos, histórias, tarefas e sprints |
| `MAPA-FASE-1.md` | Estrutura prevista de diretórios e arquivos |

## 9. Desenvolvimento

O desenvolvimento será organizado em etapas incrementais, seguindo o backlog do projeto.

A implementação deverá respeitar:

- Requisitos e regras de negócio aprovados.
- Separação de responsabilidades.
- Testes unitários e de integração.
- Controles de segurança.
- Compatibilidade entre Windows e Linux.
- Revisão da documentação quando houver mudanças relevantes.

Não serão criados arquivos vazios apenas para reproduzir a estrutura planejada.

## 10. Evolução futura

O Odyssey AV possui uma visão de evolução para ferramentas mais avançadas de proteção e análise de ameaças.

Entretanto, funcionalidades como mecanismos antimalware avançados e integração com agentes de inteligência artificial serão avaliadas em fases posteriores.

A prioridade atual é construir uma base funcional, segura, testável e bem documentada.

---

**Odyssey AV — uma base modular para diagnóstico, análise e evolução em segurança da informação.**
