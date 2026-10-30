# REGRAS-DE-NEGOCIO.md

**Projeto:** Odyssey AV  
**Versão:** 1.0  
**Escopo:** MVP  
**Status:** Em consolidação

---

# 1. Objetivo

Este documento define as regras de negócio que determinam como o Odyssey AV deverá se comportar durante suas operações de análise, diagnóstico, consulta e geração de relatórios.

As regras são independentes da tecnologia utilizada e devem ser respeitadas por todos os módulos do sistema.

---

# 2. Regras gerais de segurança e operação

## RN-001 — Ausência de ações destrutivas automáticas

O Odyssey AV não deverá executar ações destrutivas automaticamente.

No MVP, as ferramentas terão caráter de análise, diagnóstico e consulta. Não será permitido excluir, modificar, colocar em quarentena ou alterar arquivos e recursos do sistema.

**Aplicação:** todos os módulos.

**Consequência:** as operações disponíveis não deverão modificar os recursos analisados.

## RN-002 — Integridade do cálculo de hash

O cálculo de hash deverá ser realizado sobre os bytes reais do conteúdo do arquivo, independentemente de seu nome, extensão ou caminho.

**Aplicação:** módulo HASH.

**Consequência:** arquivos com conteúdos idênticos deverão produzir o mesmo hash utilizando o mesmo algoritmo, mesmo que possuam nomes ou extensões diferentes.

## RN-003 — Indicadores suspeitos não representam confirmação de malware

A identificação de características suspeitas não deverá ser apresentada como confirmação de que um arquivo, URL ou processo contém malware.

**Aplicação:** módulos FILE, HASH, URL e PROCESS.

**Consequência:** os resultados deverão distinguir indicadores, divergências e suspeitas de uma detecção efetivamente confirmada.

O Odyssey AV deverá informar limitações de análise e evitar classificações conclusivas sem evidências suficientes.

## RN-004 — Classificação de comparação de hashes

A comparação de hashes deverá apresentar resultados distintos para cada situação:

| Estado | Significado |
|---|---|
| MATCH | Hash correspondente à referência |
| MISMATCH | Hash diferente da referência |
| NO_REFERENCE | Nenhuma referência disponível para comparação |

**Aplicação:** módulo HASH.

**Consequência:** a ausência de uma referência não poderá ser interpretada como divergência ou como confirmação de integridade.

---

# 3. Regras de privacidade e dados

## RN-005 — Não persistência de senhas

Senhas geradas ou avaliadas pelo Odyssey AV não deverão ser armazenadas no histórico, nos logs ou nos relatórios exportados.

**Aplicação:** módulo PASSWORD.

**Consequência:** o resultado da avaliação poderá apresentar informações sobre a senha, mas nunca deverá revelar ou persistir seu conteúdo.

## RN-006 — Análise local de URLs

A análise de URLs deverá ocorrer localmente, considerando sua estrutura e características identificáveis sem acessar automaticamente o endereço informado.

**Aplicação:** módulo URL.

**Consequência:** o módulo não deverá realizar requisições HTTP, consultas DNS ou outras operações externas automaticamente para analisar uma URL.

A análise deverá se limitar às informações disponíveis no próprio endereço.

## RN-007 — Operações externas de rede identificáveis

Toda operação que envolva comunicação com recursos externos deverá ser identificável pelo usuário e decorrer de uma ação explícita.

**Aplicação:** módulo NETWORK e demais operações que eventualmente utilizem recursos externos.

**Consequência:**

- O diagnóstico de rede poderá executar verificações externas quando o usuário invocar explicitamente o comando correspondente.
- Consultas de DNS e conectividade deverão ser identificadas como operações de rede.
- A consulta de IP público deverá ser opcional.
- Nenhuma comunicação externa deverá ocorrer de maneira oculta ou como consequência inesperada de outro módulo.

---

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

---

# 5. Regras de histórico e relatórios

## RN-009 — Registro das execuções

As execuções dos módulos deverão ser registradas no histórico, incluindo operações concluídas com sucesso, parcialmente concluídas ou malsucedidas.

**Aplicação:** módulo HISTORY e persistência transversal.

**Consequência:**

- Execuções bem-sucedidas deverão ser registradas.
- Execuções parciais deverão preservar os resultados obtidos.
- Execuções com falhas deverão registrar as informações disponíveis sobre a falha.
- O histórico deverá permitir identificar o módulo, o comando e o estado da execução.

Uma execução interrompida inesperadamente não deverá permanecer indefinidamente apresentada como concluída ou bem-sucedida.

A recuperação dessas execuções deverá ser definida na implementação do mecanismo de persistência.

## RN-010 — Minimização de dados persistidos

O Odyssey AV deverá armazenar somente os dados necessários para manter o histórico e permitir a consulta dos resultados.

**Aplicação:** todos os módulos.

**Consequência:**

- Não armazenar o conteúdo integral dos arquivos analisados.
- Não armazenar senhas.
- Não armazenar informações sensíveis sem necessidade funcional.
- Evitar registrar argumentos de comandos que contenham segredos.
- Não incluir dados sensíveis desnecessários em resumos ou mensagens de erro.

---

# 6. Regras de exportação

## RN-011 — Exportação limitada aos dados disponíveis

Os relatórios exportados deverão conter somente informações efetivamente registradas e selecionadas para exportação.

**Aplicação:** módulo HISTORY.

**Consequência:**

- A exportação deverá respeitar os dados disponíveis no histórico.
- Informações inexistentes não poderão ser inventadas ou inferidas.
- Dados sensíveis deverão ser excluídos.
- Senhas nunca poderão aparecer em relatórios.
- Os formatos previstos para o MVP serão JSON e CSV.

---

# 7. Regras de confiabilidade

## RN-012 — Transparência sobre limitações de acesso

O Odyssey AV deverá informar quando não conseguir acessar, consultar ou analisar determinado recurso por limitações de permissão, plataforma ou disponibilidade.

**Aplicação:** todos os módulos.

**Consequência:**

- Falta de permissão não deverá ser interpretada como ausência de risco.
- Informações indisponíveis deverão ser identificadas como não verificadas.
- O sistema não deverá apresentar resultados incompletos como análises completas.
- Limitações específicas do Windows e Linux deverão ser comunicadas adequadamente.

---

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
| RN-009 | HISTORY | Preservar histórico das execuções |
| RN-010 | Todos | Minimizar dados persistidos |
| RN-011 | HISTORY | Controlar exportações |
| RN-012 | Todos | Comunicar limitações |

---

# 9. Observações para implementação

As regras acima definem o comportamento esperado do sistema. Os mecanismos técnicos para garanti-las serão detalhados nos documentos de arquitetura e segurança.

Exemplos:

| Regra | Mecanismo técnico relacionado |
|---|---|
| RN-002 | Biblioteca `hashlib` e leitura binária |
| RN-005 | Exclusão de senhas dos registros e relatórios |
| RN-006 | Separação entre parsing local e operações de rede |
| RN-007 | Controle explícito das operações externas |
| RN-009 | Persistência e recuperação de execuções |
| RN-010 | Sanitização de dados e logs |
| RN-011 | Seleção e filtragem dos campos exportados |
| RN-012 | Tratamento de exceções e mensagens de limitação |

Esses mecanismos não substituem as regras de negócio; são formas de implementá-las.

---

# 10. Estado do documento

| Critério | Situação |
|---|---|
| Regras gerais | Definidas |
| Regras de segurança | Definidas |
| Regras de privacidade | Definidas |
| Regras dos módulos | Definidas |
| Histórico e relatórios | Definidos |
| Exportação | Definida |
| Rastreabilidade | Estruturada |
| Revisão de consistência | Pendente |

**Total de regras:** 12.

