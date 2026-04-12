# Exemplos de Inputs — SDD Tech Writer

Curadoria focada em **benchmark e comparação técnica**.
Cada exemplo tem versão **leigo** e **técnica**.

---

## MiniStack

### MiniStack — setup inicial e operação

**Versão leigo:**
```
Ferramentas: ministack
Contexto:    quero subir um ambiente local simples para testar aplicações
Foco:        1 (comparação geral)

Perguntas:
  o que o ministack resolve na prática?
  quais são os requisitos mínimos de máquina?
  qual o passo a passo mais simples para instalar?
  quais erros mais comuns aparecem no primeiro uso?

Critérios:
  tem comandos reais de instalação e verificação
  explica os erros sem linguagem complexa
  inclui checklist de pós-instalação
  usa https://ministack.org/ como referência principal
```

**Versão técnica:**
```
Ferramentas: ministack
Contexto:    ambiente de desenvolvimento local para times com Docker e CI/CD
Foco:        5 (integração)

Perguntas:
  quais componentes do ministack são obrigatórios e quais são opcionais?
  como integrar com docker compose sem quebrar serviços já existentes?
  como configurar logs e healthchecks para troubleshooting rápido?
  quais parâmetros impactam consumo de RAM/CPU em idle?

Critérios:
  inclui arquitetura resumida com fluxo entre componentes
  tem comandos de diagnóstico e troubleshooting
  cita limitações conhecidas e trade-offs
  referências incluem https://ministack.org/ e repositório GitHub oficial
```

---

## Container Runtime

### Docker vs Podman — benchmark de consumo e operação

**Versão leigo:**
```
Ferramentas: docker e podman
Contexto:    quero rodar containers no Linux com baixo consumo de recursos
Foco:        1 (comparação geral)

Perguntas:
  qual usa menos RAM e CPU parado?
  qual inicia container mais rápido?
  qual é mais simples para quem está começando?
  o que muda na prática entre daemon e daemonless?

Critérios:
  traz tabela com memória, CPU idle e tempo de start
  inclui comandos reproduzíveis
  explica diferenças sem jargão excessivo
  não recomenda sem justificar pelo contexto
```

**Versão técnica:**
```
Ferramentas: docker e podman
Contexto:    workstations Linux e runners de CI self-hosted
Foco:        2 (performance / throughput)

Perguntas:
  qual latência média de start para N containers curtos?
  qual overhead por container em idle?
  como rootless afeta performance e segurança?
  qual impacto no build cache e I/O de imagens?

Critérios:
  benchmark com metodologia clara (máquina, versão, comandos)
  inclui p50/p95 para start time
  separa resultado de runtime e build
  lista limitações do teste
```

---

## Orquestração de Containers

### k3s vs microk8s — Kubernetes leve

**Versão leigo:**
```
Ferramentas: k3s e microk8s
Contexto:    quero Kubernetes leve para laboratório local
Foco:        1 (comparação geral)

Perguntas:
  qual instala mais rápido?
  qual usa menos memória em idle?
  qual tem menos dor de cabeça para manutenção?
  qual funciona melhor em máquina simples?

Critérios:
  compara recursos mínimos de hardware
  inclui passos de instalação e teste
  mostra quando escolher cada um
  evita respostas genéricas
```

**Versão técnica:**
```
Ferramentas: k3s e microk8s
Contexto:    clusters pequenos para edge e ambientes de homologação
Foco:        2 (performance / throughput)

Perguntas:
  qual tempo de bootstrap até cluster ficar pronto?
  qual consumo de RAM/CPU em idle com addons mínimos?
  qual latência de deploy de workload simples?
  qual overhead de upgrades e gestão de addons?

Critérios:
  inclui comandos e métricas objetivas
  compara bootstrap, idle e deploy time
  explicita trade-offs operacionais
  referencia documentação oficial
```

---

## Dados e Analytics

### SQLite vs DuckDB — analytics local

**Versão leigo:**
```
Ferramentas: sqlite e duckdb
Contexto:    quero analisar arquivos grandes CSV/Parquet no notebook
Foco:        2 (performance / throughput)

Perguntas:
  qual consulta dados maiores mais rápido?
  qual é mais fácil de usar no dia a dia?
  qual funciona melhor para relatórios locais?
  quando vale migrar de sqlite para duckdb?

Critérios:
  inclui benchmark de leitura e agregação
  usa exemplos com dados reais
  compara tempo e consumo de memória
  explica limitações de cada engine
```

**Versão técnica:**
```
Ferramentas: sqlite e duckdb
Contexto:    analytics embarcado em aplicação Python
Foco:        2 (performance / throughput)

Perguntas:
  qual throughput em scans e joins com dados colunares?
  qual impacto de formatos (CSV vs Parquet)?
  como cada engine se comporta em concorrência local?
  qual estratégia para cache e compactação?

Critérios:
  traz queries de benchmark reproduzíveis
  reporta tempo, memória e versão das ferramentas
  separa cenários OLTP e OLAP
  apresenta conclusão com cenário de uso
```

---

### DuckDB vs Polars — engine SQL vs DataFrame

**Versão leigo:**
```
Ferramentas: duckdb e polars
Contexto:    preciso decidir ferramenta para análises de dados no time
Foco:        1 (comparação geral)

Perguntas:
  qual é melhor para quem já conhece SQL?
  qual costuma ser mais rápido em agregações grandes?
  qual integra melhor com Python?
  quando usar os dois juntos?

Critérios:
  compara curva de aprendizado e performance
  inclui exemplos práticos simples
  mostra cenários de uso complementar
  evita recomendação absoluta
```

**Versão técnica:**
```
Ferramentas: duckdb e polars
Contexto:    pipeline analítico em Python com arquivos Parquet particionados
Foco:        2 (performance / throughput)

Perguntas:
  benchmark de groupby, join e filtros seletivos em datasets grandes
  diferença de consumo de memória em lazy/eager execution
  custo de conversão entre DataFrame e tabelas SQL
  quando combinar Polars para ETL e DuckDB para serving SQL?

Critérios:
  inclui scripts/queries reprodutíveis
  apresenta p50/p95 e memória pico
  traz recomendação por tipo de workload
  documenta limitações do benchmark
```

---

### PySpark vs Trino — ETL e SQL distribuído

**Versão leigo:**
```
Ferramentas: pyspark e trino
Contexto:    preciso processar muitos dados e também consultar rápido para BI
Foco:        1 (comparação geral)

Perguntas:
  quando usar pyspark em vez de trino?
  qual costuma responder dashboards mais rápido?
  qual é mais simples para o time operar?
  como os dois podem trabalhar juntos?

Critérios:
  explica processamento vs consulta de forma clara
  inclui fluxo simples de ponta a ponta
  compara custo operacional básico
  não recomenda sem contexto
```

**Versão técnica:**
```
Ferramentas: pyspark e trino
Contexto:    lakehouse com S3/MinIO + BI em produção
Foco:        5 (integração)

Perguntas:
  qual estratégia para ETL pesado (joins, deduplicação, janelas)?
  como otimizar tabelas Iceberg/Delta para leitura no Trino?
  quais parâmetros afetam throughput no Spark e latência no Trino?
  como instrumentar SLA de jobs e queries ponta a ponta?

Critérios:
  inclui arquitetura Spark (transform) + Trino (serving)
  tem comandos reais e queries de validação
  cobre particionamento, compactação e small files
  lista gargalos típicos e mitigação
```

---

### Kafka + Flink — streaming de alto volume

**Versão leigo:**
```
Ferramentas: kafka e flink
Contexto:    preciso processar eventos em tempo real sem perder mensagens
Foco:        2 (performance / throughput)

Perguntas:
  como garantir que mensagens não se percam?
  qual volume por segundo é realista em ambiente médio?
  quais erros aparecem com mais frequência?
  como monitorar se o pipeline está atrasando?

Critérios:
  explica conceitos de forma simples
  tem exemplo de pipeline mínimo reproduzível
  traz métricas de throughput e atraso
  inclui troubleshooting de produção
```

**Versão técnica:**
```
Ferramentas: kafka e flink
Contexto:    processamento de eventos críticos com SLA de baixa latência
Foco:        2 (performance / throughput)

Perguntas:
  throughput máximo por partição e por cluster em cenário controlado
  latência end-to-end p50/p95/p99 com janelas e estado
  impacto de exactly-once e checkpointing no desempenho
  tuning de paralelismo, backpressure e retention

Critérios:
  metodologia de benchmark explícita
  métricas de latência e throughput por estágio
  inclui comandos/configs reais
  mostra gargalos e trade-offs de consistência
```

---

## Observability

### Prometheus vs VictoriaMetrics — métricas em escala

**Versão leigo:**
```
Ferramentas: prometheus e victoriametrics
Contexto:    quero monitorar muitos serviços sem gastar recursos demais
Foco:        2 (performance / throughput)

Perguntas:
  qual aguenta mais métricas com menos custo?
  qual é mais fácil de operar no dia a dia?
  como fica retenção de dados e consultas longas?
  quando trocar Prometheus puro por VictoriaMetrics?

Critérios:
  compara ingestão, armazenamento e consulta
  inclui benchmark simples e reproduzível
  traz custo operacional estimado
  explica trade-offs sem viés
```

**Versão técnica:**
```
Ferramentas: prometheus e victoriametrics
Contexto:    plataforma com alta cardinalidade e retenção longa
Foco:        2 (performance / throughput)

Perguntas:
  ingestão sustentada (samples/s) com cardinalidade alta
  latência de query em range curto e longo
  compressão e uso de disco por série
  impacto de federation/remote_write na arquitetura

Critérios:
  inclui dataset, carga e hardware do teste
  reporta ingestão, latência, RAM e disco
  separa cenário single-node e cluster
  recomenda por perfil de uso
```

---

### Loki vs Elasticsearch — logs

**Versão leigo:**
```
Ferramentas: loki e elasticsearch
Contexto:    quero centralizar logs de aplicações e servidores
Foco:        2 (performance / throughput)

Perguntas:
  qual usa menos recurso para armazenar logs?
  qual é melhor para buscar erros rapidamente?
  qual é mais simples para manter?
  qual escala melhor com aumento de volume?

Critérios:
  compara ingestão e busca
  mede custo de armazenamento
  mostra limites e riscos operacionais
  inclui comandos de consulta reais
```

**Versão técnica:**
```
Ferramentas: loki e elasticsearch
Contexto:    observabilidade com alto volume de logs e retenção de 30+ dias
Foco:        2 (performance / throughput)

Perguntas:
  throughput de ingestão com diferentes tamanhos de linha
  latência de busca em índices frios e quentes
  custo de storage por GB ingerido
  efeito de parsing/indexação no desempenho

Critérios:
  benchmark com dataset e queries definidos
  p50/p95 de ingestão e busca
  custo operacional por cenário
  conclusão orientada ao contexto
```

---

## IA Local

### Ollama vs LM Studio — inferência local

**Versão leigo:**
```
Ferramentas: ollama e lm studio
Contexto:    quero rodar IA local no notebook para uso diário
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil para instalar e começar?
  qual funciona melhor sem placa de vídeo forte?
  qual responde mais rápido no uso comum?
  qual oferece interface mais amigável?

Critérios:
  compara facilidade, desempenho e consumo
  inclui comandos reais de instalação
  mostra limitações por hardware
  não usa placeholders
```

**Versão técnica:**
```
Ferramentas: ollama e lm studio
Contexto:    uso local para desenvolvimento com modelos 7B/13B
Foco:        2 (performance / throughput)

Perguntas:
  tokens/s por modelo e quantização em CPU/GPU
  tempo de warmup e latência da primeira resposta
  uso de RAM/VRAM em idle e carga
  como cada ferramenta lida com concorrência local?

Critérios:
  benchmark reproduzível com mesma máquina/modelo
  reporta tokens/s, p95 e memória
  diferencia UX de operação e API de automação
  recomenda por perfil de workload
```

---

## Backend e Cache

### FastAPI vs Django vs Flask — API web

**Versão leigo:**
```
Ferramentas: fastapi, django e flask
Contexto:    preciso construir API para produto novo
Foco:        1 (comparação geral)

Perguntas:
  qual é mais rápido para começar?
  qual aguenta mais requisições com menos esforço?
  qual tem mais recursos prontos?
  qual facilita manutenção a longo prazo?

Critérios:
  compara produtividade e performance
  inclui benchmark básico de requests/s
  mostra curva de aprendizado
  indica quando cada um faz sentido
```

**Versão técnica:**
```
Ferramentas: fastapi, django e flask
Contexto:    API de produção com autenticação, observabilidade e scaling horizontal
Foco:        2 (performance / throughput)

Perguntas:
  latência p50/p95/p99 sob carga concorrente
  throughput por worker e impacto de async/sync
  overhead de middleware e validação
  custo de operação e manutenção por framework

Critérios:
  benchmark com mesmas rotas e mesmas regras de negócio
  métricas claras de latência e throughput
  inclui análise de ergonomia de desenvolvimento
  conclusão por cenário de produto
```

---

### Redis vs Dragonfly vs KeyDB — cache

**Versão leigo:**
```
Ferramentas: redis, dragonfly e keydb
Contexto:    preciso acelerar aplicação com cache em memória
Foco:        2 (performance / throughput)

Perguntas:
  qual entrega mais desempenho com menos RAM?
  qual é mais estável para produção?
  qual é mais simples de operar?
  qual tem melhor custo-benefício?

Critérios:
  compara operações de leitura/escrita
  mede consumo de memória e CPU
  inclui cenário realista de uso
  evita recomendação sem dados
```

**Versão técnica:**
```
Ferramentas: redis, dragonfly e keydb
Contexto:    cache distribuído para APIs com alto tráfego
Foco:        2 (performance / throughput)

Perguntas:
  throughput em GET/SET com concorrência alta
  latência p95/p99 em carga mista
  impacto de persistência (AOF/RDB) no desempenho
  comportamento em failover e replicação

Critérios:
  benchmark reproduzível com workload definido
  reporta latência, throughput e memória pico
  inclui tuning mínimo necessário
  mostra riscos operacionais de cada opção
```

---

## Object Storage

### Ceph vs MinIO vs SeaweedFS — storage distribuído

**Versão leigo:**
```
Ferramentas: ceph, minio e seaweedfs
Contexto:    quero armazenar arquivos em infraestrutura própria
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar e manter?
  qual costuma ser mais rápido para upload/download?
  qual escala melhor quando cresce o volume?
  qual tem melhor custo operacional?

Critérios:
  compara instalação, operação e desempenho
  inclui benchmark básico de leitura/escrita
  aponta limitações de cada solução
  recomenda conforme contexto
```

**Versão técnica:**
```
Ferramentas: ceph, minio e seaweedfs
Contexto:    object storage self-hosted para dados críticos e tráfego alto
Foco:        2 (performance / throughput)

Perguntas:
  throughput de leitura/escrita em objetos pequenos e grandes
  latência p95/p99 em carga concorrente
  custo de replicação/erasure coding no desempenho
  complexidade operacional e MTTR de incidentes

Critérios:
  benchmark com hardware e topologia descritos
  métricas por tipo de objeto
  inclui custo operacional estimado
  conclusão baseada em trade-offs reais
```

---

## Banco de Dados Analítico

### PostgreSQL vs ClickHouse — OLTP vs OLAP

**Versão leigo:**
```
Ferramentas: postgresql e clickhouse
Contexto:    tenho dados transacionais e também preciso de relatórios rápidos
Foco:        1 (comparação geral)

Perguntas:
  qual é melhor para sistema operacional do dia a dia?
  qual é melhor para consultas analíticas grandes?
  dá para usar os dois juntos?
  qual tende a custar menos para manter?

Critérios:
  compara escrita transacional e leitura analítica
  inclui benchmark simples de insert e query
  explica quando combinar ambos
  não recomenda sem contexto
```

**Versão técnica:**
```
Ferramentas: postgresql e clickhouse
Contexto:    plataforma com workload misto (transações + BI)
Foco:        2 (performance / throughput)

Perguntas:
  throughput de inserts/updates no PostgreSQL vs ingestão em lote no ClickHouse
  latência p50/p95 de agregações em tabelas grandes
  impacto de particionamento, índices e compressão
  estratégia de replicação/CDC entre OLTP e OLAP

Critérios:
  metodologia de benchmark reproduzível
  métricas de throughput, latência e custo
  separa claramente cenários OLTP e OLAP
  conclusão por tipo de carga
```

---

## Streaming Engine

### Spark Structured Streaming vs Flink — stream processing

**Versão leigo:**
```
Ferramentas: spark structured streaming e flink
Contexto:    quero processar eventos em tempo real com confiabilidade
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil para começar?
  qual lida melhor com atraso de eventos?
  qual costuma ter menor latência?
  qual é mais simples de operar em produção?

Critérios:
  explica conceitos sem jargão excessivo
  inclui exemplo mínimo de pipeline
  compara latência e estabilidade
  mostra trade-offs operacionais
```

**Versão técnica:**
```
Ferramentas: spark structured streaming e flink
Contexto:    processamento contínuo com SLA de baixa latência
Foco:        2 (performance / throughput)

Perguntas:
  latência p50/p95/p99 com stateful operations
  impacto de watermark/checkpoint no throughput
  comportamento sob backpressure
  recuperação após falha e tempo de retomada

Critérios:
  benchmark com carga sintética e real
  métricas de latência, throughput e recovery time
  inclui tuning de paralelismo e state backend
  traz limitações do experimento
```

---

## Transformação SQL

### dbt Core vs SQLMesh — engenharia analítica

**Versão leigo:**
```
Ferramentas: dbt core e sqlmesh
Contexto:    quero organizar transformações SQL com menos retrabalho
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de adotar no time?
  qual ajuda mais na qualidade dos dados?
  qual é melhor para versionar mudanças?
  qual reduz mais erros em produção?

Critérios:
  compara curva de aprendizado e fluxo de trabalho
  inclui exemplo de pipeline com testes
  mostra ganhos reais de governança
  evita recomendação vaga
```

**Versão técnica:**
```
Ferramentas: dbt core e sqlmesh
Contexto:    transformação SQL em ambiente com múltiplos domínios de dados
Foco:        2 (performance / throughput)

Perguntas:
  tempo de build incremental vs full refresh
  overhead de testes e validações
  impacto em custo computacional por execução
  observabilidade de lineage e deploy seguro

Critérios:
  benchmark por volume de modelos e dados
  reporta tempo, custo e falhas detectadas
  inclui estratégia de CI para transformação
  conclusão por maturidade de equipe
```

---

## Orquestração de Dados

### Airflow vs Dagster — orquestração de pipelines

**Versão leigo:**
```
Ferramentas: airflow e dagster
Contexto:    preciso agendar e monitorar pipelines de dados
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil para manter no dia a dia?
  qual tem melhor visibilidade dos erros?
  qual é mais simples para o time evoluir?
  qual é mais estável em produção?

Critérios:
  compara usabilidade, operação e manutenção
  inclui exemplo de DAG/job simples
  mostra diferenças de observabilidade
  recomenda por contexto
```

**Versão técnica:**
```
Ferramentas: airflow e dagster
Contexto:    orquestração de pipelines críticos com dependências complexas
Foco:        2 (performance / throughput)

Perguntas:
  overhead do scheduler com muitos jobs
  latência entre tarefas encadeadas
  comportamento de retries e backfills
  impacto operacional de upgrades/migrações

Critérios:
  benchmark com volume crescente de DAGs/jobs
  métricas de scheduling delay e taxa de falha
  inclui estratégia de observabilidade
  detalha trade-offs de operação
```

---

## Mensageria

### NATS JetStream vs Kafka — pub/sub e streams

**Versão leigo:**
```
Ferramentas: nats jetstream e kafka
Contexto:    preciso trocar mensagens entre serviços com confiabilidade
Foco:        1 (comparação geral)

Perguntas:
  qual é mais simples de subir e operar?
  qual aguenta mais volume?
  qual tem menor latência?
  qual é melhor para equipe pequena?

Critérios:
  compara complexidade operacional e desempenho
  inclui cenário de uso realista
  mostra custos de manutenção
  evita resposta absolutista
```

**Versão técnica:**
```
Ferramentas: nats jetstream e kafka
Contexto:    arquitetura event-driven com múltiplos consumidores
Foco:        2 (performance / throughput)

Perguntas:
  throughput sustentado por tópico/subject
  latência p95/p99 em carga alta
  garantias de entrega e replay
  impacto de retenção e replicação

Critérios:
  benchmark reproduzível com payloads distintos
  métricas de latência, throughput e durabilidade
  inclui tuning mínimo necessário
  conclusão por perfil de workload
```

---

## Busca e Logs

### OpenSearch vs Elasticsearch — indexação e consulta

**Versão leigo:**
```
Ferramentas: opensearch e elasticsearch
Contexto:    quero buscar logs e documentos com boa performance
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de administrar?
  qual consulta mais rápido em volume alto?
  qual custa menos para manter?
  qual integra melhor com dashboards?

Critérios:
  compara custo, desempenho e operação
  inclui benchmark básico de indexação e busca
  mostra trade-offs de ecossistema
  recomenda por contexto
```

**Versão técnica:**
```
Ferramentas: opensearch e elasticsearch
Contexto:    plataforma de observabilidade e busca com alta ingestão
Foco:        2 (performance / throughput)

Perguntas:
  throughput de indexação com shards equivalentes
  latência p50/p95 de queries complexas
  custo de storage e retenção
  impacto de tuning de refresh e merge

Critérios:
  benchmark com mesma topologia de cluster
  reporta ingestão, busca e consumo de recursos
  inclui custos operacionais estimados
  detalha limitações metodológicas
```

---

## LLM

### GPT-4.1 vs Claude 3.7 Sonnet vs Gemini 2.0 Flash — qualidade e custo

**Versão leigo:**
```
Ferramentas: gpt-4.1, claude 3.7 sonnet e gemini 2.0 flash
Contexto:    quero escolher um modelo para assistente do time
Foco:        1 (comparação geral)

Perguntas:
  qual entrega melhor resposta com menos erro?
  qual responde mais rápido?
  qual tende a custar menos por uso?
  qual é melhor para tarefas do dia a dia?

Critérios:
  compara qualidade, velocidade e custo
  usa conjunto de prompts representativo
  inclui limitações e riscos
  evita viés por um único caso
```

**Versão técnica:**
```
Ferramentas: gpt-4.1, claude 3.7 sonnet e gemini 2.0 flash
Contexto:    plataforma com RAG, automação e análise de documentos
Foco:        2 (performance / throughput)

Perguntas:
  latência p50/p95 por tamanho de prompt/resposta
  taxa de acerto em benchmark interno de tarefas
  custo por 1k requests em cenários reais
  robustez a prompt injection e alucinação

Critérios:
  benchmark com dataset interno e avaliação cega
  métricas de qualidade, latência e custo
  separa tasks simples e complexas
  conclusão por risco e ROI
```

---

## NLP

### spaCy vs Stanza vs Hugging Face Transformers — pipeline de NLP

**Versão leigo:**
```
Ferramentas: spacy, stanza e hugging face transformers
Contexto:    preciso extrair entidades e classificar textos
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil para iniciar?
  qual funciona melhor em português?
  qual é mais rápido em CPU?
  qual tem melhor qualidade para produção?

Critérios:
  compara qualidade e velocidade
  inclui exemplos de tarefas comuns de NLP
  mostra quando cada opção é melhor
  evita resposta genérica
```

**Versão técnica:**
```
Ferramentas: spacy, stanza e hugging face transformers
Contexto:    processamento de alto volume de textos multilíngues
Foco:        2 (performance / throughput)

Perguntas:
  throughput de NER e classificação por segundo
  latência por documento em CPU e GPU
  impacto de batch size e quantização
  precisão/recall por domínio textual

Critérios:
  benchmark com corpus representativo
  reporta f1, precisão, recall e latência
  inclui custo operacional por hardware
  conclusão por cenário de negócio
```

---

## Banco Vetorial

### pgvector vs Qdrant vs Weaviate — busca semântica

**Versão leigo:**
```
Ferramentas: pgvector, qdrant e weaviate
Contexto:    quero implementar busca semântica no meu produto
Foco:        1 (comparação geral)

Perguntas:
  qual é mais simples de colocar no ar?
  qual busca mais rápido em base grande?
  qual dá menos trabalho para manter?
  qual integra melhor com pipeline de embeddings?

Critérios:
  compara simplicidade, desempenho e operação
  inclui exemplo de ingestão e consulta
  mostra trade-offs de custo e escalabilidade
  recomenda por contexto
```

**Versão técnica:**
```
Ferramentas: pgvector, qdrant e weaviate
Contexto:    RAG em produção com alto volume de documentos
Foco:        2 (performance / throughput)

Perguntas:
  recall@k e latência p95 em ANN sob carga
  impacto de index types e parâmetros de busca
  custo de atualização/reindexação em produção
  comportamento com filtros híbridos (vetor + metadata)

Critérios:
  benchmark com dataset e embeddings fixos
  reporta recall, latência, throughput e custo
  inclui estratégia de particionamento/sharding
  conclusão por perfil de escala
```

---

## Referência rápida — foco para benchmark

| Situação | Foco recomendado |
|----------|-----------------|
| Comparar duas ferramentas de mesma categoria | comparação geral |
| Medir latência, throughput e consumo | performance / throughput |
| Integrar engines no mesmo pipeline | integração |
| Hardware limitado (edge/notebook) | hardware limitado / edge |
| Avaliar impacto financeiro da arquitetura | custo |
| Ambientes de produção com compliance | segurança |
| Migração entre stacks existentes | migração |
