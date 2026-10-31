# API.md — Contrato da Interface de Linha de Comando

**Projeto:** Odyssey AV  
**Versão:** 2.0  
**Escopo:** MVP  
**Status:** Consolidado para revisão cruzada  
**Tipo de interface:** CLI local

---

## 1. Objetivo

Este documento especifica o contrato de interação entre o usuário e o Odyssey AV por meio de sua interface de linha de comando (CLI).

O MVP não disponibiliza uma API REST ou serviço HTTP. A interface pública da aplicação será composta por comandos e subcomandos executados localmente.

O contrato define:

- Organização dos comandos.
- Parâmetros e opções.
- Comportamento esperado.
- Formato de apresentação dos resultados.
- Códigos de saída.
- Tratamento de erros.
- Operações registradas no histórico.
- Limites e restrições de segurança.

Os comandos descritos representam a interface planejada. Não significam que já estejam implementados.

## 2. Organização dos comandos

```text
odyssey
├── file
│   └── analyze
├── hash
│   ├── calculate
│   └── compare
├── network
│   └── diagnose
├── password
│   ├── generate
│   └── evaluate
├── url
│   └── analyze
├── process
│   └── list
└── history
    ├── list
    ├── show
    └── export
```

## 3. Convenções gerais

### 3.1. Execução

Os comandos deverão ser executados por meio do ponto de entrada `odyssey`.

Exemplo:

```bash
odyssey file analyze ./arquivo.bin
```

### 3.2. Ajuda

A CLI deverá disponibilizar ajuda geral e específica por comando.

Exemplos:

```bash
odyssey --help
odyssey file --help
odyssey hash calculate --help
```

### 3.3. Saída

A CLI deverá apresentar resultados de maneira legível no terminal.

Quando aplicável, poderá oferecer saída estruturada em JSON por meio de uma opção comum, como `--output json`.

A saída textual será o formato padrão.

A saída estruturada deverá preservar a distinção entre:

- Resultado da operação funcional.
- Situação da persistência do histórico.
- Resultados e avisos produzidos pelos módulos.

Uma falha de persistência não poderá ser representada como falha funcional quando a operação tiver sido concluída com sucesso.

### 3.4. Configuração

A CLI poderá receber opções explícitas e utilizar um arquivo TOML opcional.

A precedência será:

1. Padrões internos.
2. Configurações do arquivo TOML.
3. Argumentos e opções explícitos da CLI.

A ausência do arquivo TOML não deverá impedir a execução.

Um arquivo TOML inválido deverá produzir erro claro. A aplicação não deverá ignorar silenciosamente configurações inválidas.

## 4. Contrato dos módulos

### 4.1. FILE — Análise de arquivos

**Comando:**

```bash
odyssey file analyze <caminho>
```

**Entrada:**

- Caminho de um arquivo.

**Comportamento:**

- Identificar metadados disponíveis.
- Obter tamanho e extensão.
- Identificar assinaturas binárias reconhecidas.
- Comparar extensão declarada e formato identificado.
- Apresentar divergências e limitações.

**Restrições:**

- Não executar o arquivo.
- Não modificar seu conteúdo.
- Não analisar diretórios como se fossem arquivos.
- Não seguir links simbólicos automaticamente.
- Não processar dispositivos especiais, sockets ou pipes.
- Respeitar permissões do usuário.
- Tratar arquivos que desapareçam ou sejam modificados durante a análise.

**Assinaturas inicialmente previstas:**

| Formato | Identificação |
|---|---|
| PE | Executáveis Windows |
| ELF | Executáveis Linux e outros sistemas compatíveis |
| PDF | Documentos PDF |
| PNG | Imagens PNG |
| JPEG | Imagens JPEG |
| ZIP | Arquivos ZIP |
| GZIP | Arquivos GZIP |

A identificação por assinatura não representa validação integral do formato nem comprovação de segurança.

### 4.2. HASH — Cálculo e comparação

**Cálculo:**

```bash
odyssey hash calculate <caminho>
```

**Comparação:**

```bash
odyssey hash compare <caminho> --reference <sha256>
```

**Entrada:**

- Caminho de arquivo.
- Referência SHA-256 para comparação.

**Comportamento:**

- Calcular SHA-256 sobre os bytes reais do arquivo.
- Comparar o resultado com a referência fornecida.
- Validar o formato da referência.
- Informar o resultado da comparação.

**Classificações:**

| Estado | Significado |
|---|---|
| `MATCH` | Hash calculado igual à referência. |
| `MISMATCH` | Hash calculado diferente da referência. |
| `NO_REFERENCE` | Não foi fornecida referência para comparação. |

O cálculo de hash poderá ser executado sem referência. A classificação `NO_REFERENCE` representa ausência de comparação, não falha no cálculo.

O MVP não manterá uma base própria de hashes.

### 4.3. NETWORK — Diagnóstico de rede

**Comando:**

```bash
odyssey network diagnose
```

**Opções previstas:**

- Verificação de conectividade.
- Consulta DNS.
- Consulta opcional de IP público.

**Comportamento:**

- Executar somente verificações previstas e explicitamente solicitadas.
- Identificar operações que utilizam rede externa.
- Aplicar limites de tempo.
- Apresentar respostas, falhas e indisponibilidades.

A consulta de IP público dependerá de serviço externo e deverá ser opcional.

### 4.4. PASSWORD — Ferramentas de senha

**Geração:**

```bash
odyssey password generate
```

**Avaliação:**

```bash
odyssey password evaluate
```

**Comportamento:**

- Gerar senhas utilizando fonte aleatória criptograficamente segura.
- Permitir configurar comprimento e conjuntos de caracteres.
- Avaliar localmente características básicas de uma senha.

A senha avaliada deverá ser recebida de maneira que não seja exposta em argumentos visíveis do processo ou no histórico do terminal. O mecanismo de entrada deverá ser interativo e ocultar a digitação quando aplicável.

**Restrições obrigatórias:**

- Não persistir senhas.
- Não incluir senhas em logs.
- Não incluir senhas em mensagens de erro.
- Não incluir senhas em argumentos registrados.
- Não exportar senhas em relatórios.
- Não manter a senha em `AnalysisResult`.
- Não incluir a senha em resumos ou dados estruturados de saída que sejam destinados ao histórico.

A execução do módulo poderá ser registrada, mas somente com metadados operacionais e informações sanitizadas.

### 4.5. URL — Análise de endereços

**Comando:**

```bash
odyssey url analyze "<url>"
```

**Comportamento:**

- Interpretar a estrutura da URL.
- Normalizar sua representação.
- Identificar indicadores potencialmente suspeitos.
- Apresentar os componentes e indicadores encontrados.

**Restrições:**

- Não realizar requisições HTTP automaticamente.
- Não realizar consultas DNS automaticamente.
- Não acessar o destino.
- Não apresentar indicadores suspeitos como confirmação de malware.

### 4.6. PROCESS — Consulta de processos

**Comando:**

```bash
odyssey process list
```

**Filtros previstos:**

```bash
odyssey process list --pid <pid>
odyssey process list --name <nome>
```

**Comportamento:**

- Listar processos acessíveis ao usuário.
- Apresentar PID, nome e métricas disponíveis.
- Aplicar filtros solicitados.
- Comunicar limitações de acesso.

O módulo será exclusivamente informativo. Não poderá encerrar, suspender, retomar, alterar prioridade ou injetar código em processos.

### 4.7. HISTORY — Histórico e relatórios

**Listagem:**

```bash
odyssey history list
```

**Consulta de execução:**

```bash
odyssey history show <execution_id>
```

**Exportação:**

```bash
odyssey history export --format json
odyssey history export --format csv
```

**Filtros previstos:**

- Módulo.
- Período.
- Estado da execução.
- Identificador da execução.

**Comportamento:**

- Consultar execuções registradas.
- Consultar resultados associados.
- Exportar informações disponíveis.
- Respeitar as regras de privacidade e minimização de dados.

Consultas e exportações do módulo HISTORY não gerarão novos registros `AnalysisRun`.

Falhas na consulta ou exportação deverão ser comunicadas. A aplicação não deverá apresentar uma consulta incompleta ou uma exportação malsucedida como concluída.

## 5. Contrato de execução

As operações funcionais deverão possuir estados próprios:

- `RUNNING`
- `SUCCESS`
- `PARTIAL`
- `FAILED`
- `INTERRUPTED`

O estado da operação não deverá ser confundido com o estado de persistência do histórico.

### 5.1. Separação entre operação e histórico

O resultado funcional e o resultado da persistência deverão ser tratados separadamente.

Quando uma operação for concluída, mas não puder ser registrada no SQLite, a CLI deverá comunicar separadamente:

- Resultado funcional da operação.
- Situação do registro no histórico.

Exemplo conceitual:

```json
{
  "operation": {
    "status": "SUCCESS",
    "message": "Hash calculado com sucesso."
  },
  "history": {
    "status": "FAILED",
    "message": "Não foi possível persistir o histórico."
  }
}
```

Esse resultado não poderá ser apresentado como se a operação funcional tivesse falhado.

A aplicação também não poderá afirmar que o histórico foi salvo quando a persistência não tiver sido confirmada.

### 5.2. Execuções interrompidas

Execuções que permanecerem em `RUNNING` após encerramento inesperado deverão ser identificadas pelo mecanismo de recuperação da aplicação e atualizadas para `INTERRUPTED`, quando for possível determinar que pertencem a uma instância encerrada.

A identificação deverá utilizar o identificador lógico da instância. Não deverá depender exclusivamente do PID, devido à possibilidade de reutilização desse identificador pelo sistema operacional.

O MVP deverá permitir somente uma instância ativa por vez, utilizando mecanismo de bloqueio exclusivo compatível com Windows e Linux.

A recuperação deverá ocorrer após a aquisição do bloqueio exclusivo e antes da disponibilização de novas operações funcionais.

A política de inicialização diante de falha na recuperação do histórico permanece dependente de decisão arquitetural específica. Até que essa decisão seja consolidada, não se deverá presumir que a recuperação malsucedida equivale a uma recuperação concluída.

## 6. Códigos de saída

A CLI deverá utilizar códigos de saída consistentes para permitir automação por scripts.

| Código | Significado |
|---|---|
| `0` | Operação funcional concluída com sucesso e persistência confirmada quando aplicável. |
| `1` | Falha na operação funcional. |
| `2` | Uso inválido, argumento inválido ou entrada rejeitada antes da execução funcional. |
| `3` | Operação funcional concluída com sucesso, mas falha na persistência do histórico. |
| `4` | Operação funcional parcialmente concluída. |

### 6.1. Precedência dos códigos

Quando mais de uma condição ocorrer, a CLI deverá aplicar a seguinte precedência:

1. **Código 2 — Entrada ou uso inválido:** utilizado quando a operação não puder ser iniciada devido a argumentos ou entradas inválidas.
2. **Código 1 — Falha funcional:** utilizado quando a operação funcional falhar, mesmo que também ocorra falha na persistência do histórico.
3. **Código 4 — Resultado parcial:** utilizado quando a operação produzir resultado parcial, mesmo que também ocorra falha na persistência do histórico.
4. **Código 3 — Falha de persistência:** utilizado quando a operação funcional for concluída com sucesso, mas seu registro no histórico falhar.
5. **Código 0 — Sucesso:** utilizado quando a operação funcional for concluída com sucesso e a persistência for confirmada, quando aplicável.

### 6.2. Matriz de decisão

| Resultado funcional | Histórico | Código |
|---|---|---:|
| Sucesso | Persistido | `0` |
| Sucesso | Falha na persistência | `3` |
| Falha | Persistido ou não persistido | `1` |
| Parcial | Persistido ou não persistido | `4` |
| Entrada inválida antes da operação | Não aplicável | `2` |

Para comandos HISTORY, que não geram novos registros `AnalysisRun`, falhas de consulta ou exportação serão tratadas como falhas funcionais da operação solicitada.

A saída deverá preservar as informações sobre ambas as situações quando houver falha funcional e falha de persistência simultâneas.

Os códigos acima constituem o contrato proposto para o MVP e deverão ser verificados nos testes da CLI.

## 7. Tratamento de erros

A CLI deverá apresentar mensagens que:

- Identifiquem a operação que falhou.
- Informem a causa quando disponível.
- Não exponham stack traces por padrão.
- Não revelem senhas ou outros segredos.
- Diferenciem falhas de entrada, permissão, disponibilidade, rede e persistência.
- Não apresentem ausência de acesso como ausência de risco.
- Diferenciem resultado funcional de falha no histórico.

Detalhes técnicos poderão ser disponibilizados em modo de diagnóstico, desde que não exponham dados sensíveis.

## 8. Histórico das operações

As operações funcionais dos módulos FILE, HASH, NETWORK, PASSWORD, URL e PROCESS deverão ser registradas conforme as regras de histórico.

O registro deverá conter metadados operacionais, incluindo:

- Identificador da execução.
- Identificador da instância.
- Módulo.
- Comando normalizado.
- Estado.
- Horários disponíveis.
- Duração, quando disponível.
- Resumo sanitizado.

Não deverão ser armazenados argumentos secretos, senhas ou conteúdo integral de arquivos.

As consultas e exportações do HISTORY não gerarão novos registros de execução.

O histórico deverá preservar execuções concluídas, parciais, malsucedidas e interrompidas, conforme a disponibilidade dos dados.

## 9. Limites operacionais

Os módulos deverão respeitar limites de recursos e disponibilidade.

- FILE: processar arquivos em blocos e evitar carregamento integral desnecessário.
- HASH: calcular sobre os bytes reais, com leitura controlada.
- NETWORK: aplicar timeout às operações externas.
- PASSWORD: validar parâmetros de geração e evitar persistência da senha.
- URL: limitar-se à análise estrutural local.
- PROCESS: tratar processos inacessíveis ou encerrados durante a consulta.
- HISTORY: limitar consultas e evitar exportações excessivas.

Os valores numéricos dos limites serão definidos durante o refinamento técnico e validados por testes. Não serão presumidos sem justificativa.

## 10. Segurança e privacidade

A interface deverá respeitar as regras de `SEGURANCA.md` e `REGRAS-DE-NEGOCIO.md`.

Em especial:

- Não executar comandos de shell construídos a partir de entradas do usuário.
- Validar entradas e caminhos.
- Não executar arquivos analisados.
- Não realizar comunicação externa oculta.
- Não persistir senhas.
- Utilizar consultas parametrizadas no SQLite.
- Não realizar ações destrutivas sobre recursos do sistema.
- Não registrar argumentos que contenham segredos.
- Não apresentar informações não persistidas como se estivessem disponíveis no histórico.

## 11. Rastreabilidade

Este contrato está relacionado aos requisitos e regras de negócio do MVP.

**Requisitos funcionais:**

- RF-001 a RF-032.

**Requisitos não funcionais:**

- RNF-001 a RNF-018.

**Regras de negócio:**

- RN-001 a RN-013.

As referências acima indicam o conjunto documental relacionado ao contrato. Não significam que todos os requisitos e regras sejam implementados exclusivamente pela CLI.

A rastreabilidade específica entre requisitos, regras, critérios de aceitação, histórias e testes deverá ser mantida nos documentos:

- `REQUISITOS.md`
- `REGRAS-DE-NEGOCIO.md`
- `BACKLOG.md`
- `TESTES.md`

Os critérios de aceitação deverão receber identificadores próprios `CT-XXX` durante a consolidação do backlog.

## 12. Estado do documento

| Critério | Situação |
|---|---|
| Organização dos comandos | Definida |
| Contratos funcionais | Definidos |
| Saída textual e JSON | Definida em nível conceitual |
| Códigos de saída | Definidos como proposta documental |
| Precedência dos códigos | Definida como proposta documental |
| Tratamento de erros | Definido |
| Registro de execuções | Definido |
| Proteção de senhas | Definida |
| Limites operacionais | Política definida; valores pendentes |
| Rastreabilidade | Referências atualizadas; matriz global pendente |
| Revisão cruzada | Em andamento |

---

**Observação:** este documento especifica o contrato da interface CLI do MVP. Não representa uma API REST e não implica que os comandos estejam implementados.