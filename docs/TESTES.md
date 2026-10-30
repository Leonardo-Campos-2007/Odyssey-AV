# TESTES.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Primeira versão

---

# 1. Objetivo

Este documento define a estratégia de testes do Odyssey AV.

O objetivo é verificar se as funcionalidades implementadas atendem aos requisitos funcionais, às regras de negócio e aos requisitos de segurança definidos para o MVP.

Os testes deverão identificar falhas antes que uma funcionalidade seja considerada concluída.

# 2. Estratégia de testes

O projeto utilizará principalmente:

- **Testes unitários:** verificam funções, métodos e regras isoladamente.
- **Testes de integração:** verificam a comunicação entre módulos, aplicação e infraestrutura.
- **Testes funcionais da CLI:** verificam os comandos e suas respostas.
- **Testes de segurança:** verificam se os controles definidos em `SEGURANCA.md` estão funcionando.
- **Testes de regressão:** verificam se alterações não quebraram funcionalidades existentes.

A ferramenta principal será o `pytest`.

# 3. Testes unitários

Os testes unitários deverão validar o comportamento individual das funcionalidades, sem depender de serviços externos ou de um banco de dados real.

## 3.1. FILE — Análise de arquivos

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-FILE-001 | Analisar arquivo existente | Metadados apresentados corretamente |
| TU-FILE-002 | Analisar arquivo inexistente | Erro tratado |
| TU-FILE-003 | Informar caminho inválido | Entrada rejeitada |
| TU-FILE-004 | Analisar extensão incompatível com assinatura | Divergência identificada |
| TU-FILE-005 | Analisar formato não suportado | Limitação informada |
| TU-FILE-006 | Analisar arquivo sem permissão | Falha tratada sem interromper a aplicação |

## 3.2. HASH — Hash

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-HASH-001 | Calcular SHA-256 | Hash correto retornado |
| TU-HASH-002 | Calcular hash de arquivo vazio | Hash válido retornado |
| TU-HASH-003 | Comparar hashes iguais | MATCH |
| TU-HASH-004 | Comparar hashes diferentes | MISMATCH |
| TU-HASH-005 | Comparar sem referência | NO_REFERENCE |
| TU-HASH-006 | Informar hash inválido | Entrada rejeitada |

## 3.3. NETWORK — Diagnóstico de rede

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-NET-001 | Interpretar resultado de conectividade | Estado apresentado corretamente |
| TU-NET-002 | Interpretar resposta DNS válida | Resolução identificada |
| TU-NET-003 | Interpretar falha DNS | Falha identificada |
| TU-NET-004 | Operação excede timeout | Operação encerrada e erro tratado |
| TU-NET-005 | Serviço externo indisponível | Falha apresentada sem travar a aplicação |

Os testes unitários deverão utilizar respostas simuladas quando não for necessário realizar comunicação real.

## 3.4. PASSWORD — Ferramentas de senha

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-PASS-001 | Gerar senha | Senha gerada com parâmetros válidos |
| TU-PASS-002 | Informar comprimento inválido | Entrada rejeitada |
| TU-PASS-003 | Avaliar senha vazia | Resultado tratado |
| TU-PASS-004 | Avaliar senha com critérios diferentes | Avaliação coerente |
| TU-PASS-005 | Verificar fonte de aleatoriedade | Utilização de `secrets` |

## 3.5. URL — Análise de URL

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-URL-001 | Analisar URL válida | Componentes interpretados |
| TU-URL-002 | Analisar URL inválida | Entrada rejeitada ou sinalizada |
| TU-URL-003 | Normalizar URL | Representação normalizada |
| TU-URL-004 | Identificar indicador suspeito | Indicador apresentado |
| TU-URL-005 | Analisar URL sem esquema | Comportamento definido e consistente |
| TU-URL-006 | Analisar URL com caracteres especiais | Entrada tratada corretamente |

## 3.6. PROCESS — Monitoramento de processos

| ID | Cenário | Resultado esperado |
|---|---|---|
| TU-PROC-001 | Listar processos | Lista apresentada |
| TU-PROC-002 | Consultar PID e nome | Informações corretas |
| TU-PROC-003 | Aplicar filtro | Somente resultados correspondentes |
| TU-PROC-004 | Processo inacessível | Limitação informada |
| TU-PROC-005 | Processo encerrado durante consulta | Falha tratada |

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

# 4. Testes de integração

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

# 5. Testes da CLI

Os comandos deverão ser testados considerando entradas válidas, inválidas e situações de falha.

| ID | Comando ou operação | Verificação |
|---|---|---|
| TC-CLI-001 | `odyssey file analyze` | Análise de arquivo |
| TC-CLI-002 | `odyssey hash calculate` | Cálculo de hash |
| TC-CLI-003 | `odyssey password generate` | Geração de senha |
| TC-CLI-004 | `odyssey url analyze` | Análise de URL |
| TC-CLI-005 | `odyssey network diagnose` | Diagnóstico de rede |
| TC-CLI-006 | `odyssey process list` | Listagem de processos |
| TC-CLI-007 | `odyssey history list` | Consulta de histórico |

Também deverão ser verificados:

- Mensagens de ajuda.
- Parâmetros obrigatórios.
- Parâmetros inválidos.
- Código de saída dos comandos.
- Mensagens de erro.
- Formatação dos resultados.

# 6. Testes de segurança

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
| TS-010 | Executar sem privilégios administrativos | Aplicação informa limitações sem solicitar elevação automática |

# 7. Testes de banco de dados

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

# 8. Testes de transação e rollback

A persistência deverá manter a consistência dos dados.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TR-001 | Inserção de execução e resultado concluída | Ambos persistidos |
| TR-002 | Falha durante operação transacional | Alterações revertidas quando aplicável |
| TR-003 | Falha na gravação de resultado | Estado da execução tratado corretamente |
| TR-004 | Falha de conexão com banco | Erro tratado sem perda silenciosa de dados |

# 9. Testes de concorrência

Embora o MVP seja local, poderão ocorrer operações simultâneas.

Os testes deverão verificar:

- Duas execuções registradas simultaneamente.
- Consultas simultâneas ao histórico.
- Escritas concorrentes no SQLite.
- Integridade dos registros após operações simultâneas.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TCO-001 | Duas execuções simultâneas | Registros independentes |
| TCO-002 | Consulta durante gravação | Dados consistentes |
| TCO-003 | Duas gravações simultâneas | Sem corrupção do banco |
| TCO-004 | Conflito de escrita | Erro tratado e operação recuperável quando possível |

# 10. Testes de idempotência

No MVP, a idempotência será avaliada principalmente em operações de consulta e leitura.

| ID | Cenário | Resultado esperado |
|---|---|---|
| TID-001 | Consultar histórico repetidamente | Mesmo conjunto de registros, sem novas execuções |
| TID-002 | Consultar processos repetidamente | Nenhuma alteração no sistema |
| TID-003 | Calcular hash do mesmo arquivo sem alterações | Mesmo resultado |
| TID-004 | Exportar o mesmo histórico sem alterações | Conteúdo equivalente |

Não será exigida idempotência artificial para operações que geram uma nova execução a cada chamada.

# 11. Testes de regressão

Sempre que uma funcionalidade for alterada, os testes relacionados deverão ser executados novamente.

Os testes de regressão deverão priorizar:

- Cálculo e comparação de hashes.
- Geração e avaliação de senhas.
- Análise de arquivos.
- Interpretação de URLs.
- Diagnóstico de rede.
- Listagem de processos.
- Persistência e exportação do histórico.
- Tratamento de erros.
- Controles de segurança.

# 12. Dados de teste

Os testes deverão utilizar dados controlados e isolados.

Exemplos:

| Tipo | Dados de teste |
|---|---|
| Arquivos | Arquivo de texto, arquivo vazio, arquivo binário e arquivo com extensão divergente |
| Hash | Hashes conhecidos e hashes inválidos |
| URLs | URLs válidas, inválidas e com indicadores suspeitos |
| Senhas | Senhas de diferentes comprimentos e complexidades |
| Rede | Respostas simuladas de sucesso, falha e timeout |
| Processos | Processos acessíveis e situações simuladas de indisponibilidade |
| Histórico | Execuções SUCCESS, PARTIAL e FAILED |

Não utilizar arquivos pessoais, senhas reais ou dados sensíveis nos testes.

# 13. Isolamento dos testes

Os testes deverão ser executados sem interferir no ambiente real do usuário.

Diretrizes:

- Utilizar diretórios temporários para arquivos.
- Utilizar banco SQLite exclusivo para testes.
- Não alterar o banco utilizado pela aplicação.
- Simular serviços externos sempre que possível.
- Não depender de conexão com a internet para testes unitários.
- Limpar arquivos temporários após a execução.
- Não executar testes que modifiquem processos reais do sistema operacional.

# 14. Cobertura de testes

A cobertura deverá ser acompanhada pelo `pytest-cov`.

Meta inicial proposta:

- Cobrir 100% dos módulos funcionais com testes.
- Buscar pelo menos 80% de cobertura de código nas regras e serviços da aplicação.
- Testar integralmente as operações críticas de segurança e persistência.

A porcentagem de cobertura não deverá ser utilizada isoladamente como indicador de qualidade. Os testes precisam verificar comportamentos e resultados relevantes.

# 15. Critérios de aprovação

Uma funcionalidade poderá ser considerada testada quando:

1. Seus testes unitários forem aprovados.
2. Seus testes de integração forem aprovados, quando aplicáveis.
3. Os critérios funcionais correspondentes forem atendidos.
4. Os controles de segurança relacionados forem verificados.
5. Não houver falhas críticas conhecidas.
6. Os testes de regressão relacionados forem aprovados.

# 16. Ferramentas

| Ferramenta | Finalidade |
|---|---|
| pytest | Execução dos testes |
| pytest-cov | Medição de cobertura |
| unittest.mock | Simulação de dependências e serviços externos |
| tempfile | Criação de arquivos e diretórios temporários |
| sqlite3 | Testes da persistência |

Não será necessário utilizar Docker, bancos externos ou ferramentas avançadas de testes no MVP.

# 17. Estado do documento

| Critério | Situação |
|---|---|
| Testes unitários | Definidos |
| Testes de integração | Definidos |
| Testes da CLI | Definidos |
| Testes de segurança | Definidos |
| Testes de banco | Definidos |
| Transações e rollback | Definidos |
| Concorrência | Definida |
| Idempotência | Definida |
| Regressão | Definida |
| Cobertura | Meta inicial proposta |
| Revisão de consistência | Pendente |

