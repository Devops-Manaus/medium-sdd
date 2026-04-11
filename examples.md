# Exemplos de Inputs — SDD Tech Writer

Cada exemplo tem versão **leigo** e **técnica**. Use a que fizer sentido pro seu nível.

---

## Container Runtime

### Docker vs Podman — comparação geral

**Versão leigo:**
```
Ferramentas: podman e docker
Contexto:    quero rodar containers no meu Linux pra desenvolvimento
Foco:        1 (comparação geral)

Perguntas:
  qual a diferença principal entre os dois?
  consigo usar meus arquivos docker-compose no podman?
  qual gasta menos memória e CPU parado?
  qual é mais seguro pra usar no dia a dia?

Critérios:
  explica a diferença sem assumir que eu sei o que é daemon
  tem comandos que eu possa copiar e colar
  não recomenda um sem explicar o porquê
```

**Versão técnica:**
```
Ferramentas: podman e docker
Contexto:    ambiente de desenvolvimento local no Linux para times de engenharia
Foco:        1 (comparação geral)

Perguntas:
  como configurar modo rootless em cada um?
  docker-compose funciona sem mudanças no podman?
  qual tem menor uso de RAM e CPU em idle?
  podman é daemonless e o que isso muda na prática?

Critérios:
  menciona que podman é daemonless e docker não
  explica rootless com comando real
  tem tabela comparativa com pelo menos 4 critérios
  não recomenda um sem justificativa técnica para o contexto
```

---

### Docker vs Podman — segurança

**Versão leigo:**
```
Ferramentas: podman e docker
Contexto:    quero rodar containers da forma mais segura possível em produção
Foco:        6 (segurança)

Perguntas:
  qual dos dois é mais seguro por padrão?
  o que é rodar sem root e por que isso importa?
  já tiveram problemas de segurança graves? quais?
  o que eu preciso configurar pra ficar seguro?

Critérios:
  explica rootless de forma simples
  menciona pelo menos um problema de segurança real
  tem passos concretos pra melhorar a segurança
  não diz que "basta seguir as boas práticas" sem dizer quais
```

**Versão técnica:**
```
Ferramentas: podman e docker
Contexto:    ambiente de produção com requisitos de compliance SOC2
Foco:        6 (segurança)

Perguntas:
  como rodar containers sem root em produção?
  quais CVEs recentes afetaram cada runtime?
  como configurar seccomp profiles customizados?
  qual suporta melhor namespaces de usuário?

Critérios:
  menciona rootless com impacto real em segurança
  tem pelo menos um CVE concreto referenciado
  não trata segurança como feature secundária
  tem comando real de configuração de seccomp
```

---

### Docker vs Podman — migração

**Versão leigo:**
```
Ferramentas: docker e podman
Contexto:    meu time usa docker mas queremos trocar pro podman sem quebrar tudo
Foco:        4 (migração)

Perguntas:
  é difícil trocar de docker pra podman?
  meus projetos atuais vão funcionar sem mudança?
  o que pode dar errado na troca?
  dá pra usar os dois ao mesmo tempo durante a transição?

Critérios:
  é honesto sobre o que funciona e o que quebra
  tem um plano passo a passo pra migração
  não diz que é só trocar o nome do comando
```

**Versão técnica:**
```
Ferramentas: docker e podman
Contexto:    migração gradual de docker para podman em CI/CD com GitHub Actions
Foco:        4 (migração)

Perguntas:
  quais comandos docker não têm equivalente direto no podman?
  como migrar docker-compose.yml para podman?
  como manter compatibilidade durante a transição?
  quais breaking changes esperar?

Critérios:
  lista comandos incompatíveis concretos
  tem exemplo de CI pipeline com podman
  menciona podman-docker como bridge de compatibilidade
  não assume que a migração é trivial
```

---

## Orquestração de Containers

### Kubernetes leve — k3s vs microk8s

**Versão leigo:**
```
Ferramentas: k3s e microk8s
Contexto:    quero aprender Kubernetes no meu notebook sem instalar algo pesado
Foco:        1 (comparação geral)

Perguntas:
  qual dos dois é mais leve e fácil de instalar?
  consigo rodar no meu notebook de 8GB?
  qual tem mais material de estudo em português?
  preciso saber Kubernetes antes ou ele ensina?

Critérios:
  tem comando de instalação que funciona de primeira
  diz quanto de RAM cada um consome
  não assume que eu já sei o que é kubectl
```

**Versão técnica:**
```
Ferramentas: k3s e microk8s
Contexto:    cluster Kubernetes single-node em servidor de desenvolvimento com 4GB RAM
Foco:        7 (hardware limitado / edge)

Perguntas:
  qual o consumo de RAM e CPU em idle de cada um?
  como desabilitar componentes desnecessários pra economizar recursos?
  qual suporta melhor storage local (local-path-provisioner vs hostpath)?
  como funciona o HA em cada um com 3 nós?

Critérios:
  tem números concretos de RAM idle
  mostra como desabilitar traefik/metrics-server no k3s
  mostra como desabilitar addons no microk8s
  tem comando real de instalação com flags de otimização
```

---

### Kubernetes local — kind vs minikube

**Versão leigo:**
```
Ferramentas: kind e minikube
Contexto:    preciso testar meus containers num Kubernetes local antes de mandar pra produção
Foco:        1 (comparação geral)

Perguntas:
  qual a diferença entre os dois?
  qual é mais rápido pra subir e derrubar?
  preciso de Docker instalado pra usar?
  qual se parece mais com um Kubernetes de verdade?

Critérios:
  explica pra que serve cada um sem jargão
  tem comando pra criar e destruir cluster
  diz qual funciona melhor pra CI/CD
```

**Versão técnica:**
```
Ferramentas: kind e minikube
Contexto:    ambiente de testes local para pipelines CI/CD com GitHub Actions
Foco:        2 (performance / throughput)

Perguntas:
  qual o tempo de startup de cada um com 1 nó e 3 nós?
  como cada um lida com LoadBalancer e Ingress local?
  qual funciona melhor dentro de GitHub Actions (Docker-in-Docker)?
  como persistir imagens entre recriações do cluster?

Critérios:
  tem benchmark de tempo de startup
  menciona limitações de kind com DinD
  tem exemplo de workflow GitHub Actions com cada um
  não ignora que kind não tem VM (roda em containers)
```

---

## Infrastructure as Code (IaC)

### Terraform vs OpenTofu

**Versão leigo:**
```
Ferramentas: terraform e opentofu
Contexto:    quero criar servidores e recursos na nuvem usando código
Foco:        1 (comparação geral)

Perguntas:
  qual a diferença se os dois fazem a mesma coisa?
  o opentofu é de graça mesmo? e o terraform?
  consigo migrar do terraform pro opentofu sem refazer tudo?
  qual tem mais exemplos e tutoriais disponíveis?

Critérios:
  explica o que é IaC de forma simples
  explica a mudança de licença do terraform
  não assume que eu sei o que é HCL ou provider
```

**Versão técnica:**
```
Ferramentas: terraform e opentofu
Contexto:    infraestrutura multi-cloud (AWS + GCP) com state remoto e módulos compartilhados
Foco:        4 (migração)

Perguntas:
  quais features do terraform 1.6+ não estão no opentofu?
  como migrar o state file sem downtime?
  os providers da hashicorp funcionam no opentofu sem mudança?
  como fica o suporte a terraform cloud vs backends open source?

Critérios:
  lista incompatibilidades concretas de versão
  tem exemplo de migração de state
  menciona a licença BSL do terraform
  referências incluem opentofu.org e github.com
```

---

### Ansible vs Salt

**Versão leigo:**
```
Ferramentas: ansible e salt
Contexto:    preciso configurar vários servidores Linux do mesmo jeito automaticamente
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de aprender do zero?
  preciso instalar algo nos servidores que vou configurar?
  qual funciona melhor com poucos servidores (5-10)?
  consigo testar antes de aplicar as mudanças?

Critérios:
  explica o que é gerenciamento de configuração
  menciona agentless (ansible) vs agent (salt)
  tem exemplo simples de como instalar um pacote em vários servidores
```

**Versão técnica:**
```
Ferramentas: ansible e salt
Contexto:    gerenciamento de configuração de 200+ servidores Linux com drift detection
Foco:        2 (performance / throughput)

Perguntas:
  qual escala melhor pra 500+ nós simultâneos?
  como funciona o modelo push (ansible) vs push/pull (salt)?
  qual tem melhor performance pra aplicar playbooks em paralelo?
  como detectar configuration drift em cada um?

Critérios:
  tem números de tempo de execução em escala
  menciona salt-minion vs agentless
  tem exemplo de detecção de drift
  não ignora que ansible é mais popular
```

---

### Pulumi vs Terraform

**Versão leigo:**
```
Ferramentas: pulumi e terraform
Contexto:    quero criar infraestrutura na nuvem mas prefiro usar Python do que aprender outra linguagem
Foco:        1 (comparação geral)

Perguntas:
  posso usar Python no pulumi mesmo?
  e no terraform, preciso aprender a linguagem HCL?
  qual tem mais exemplos prontos pra copiar?
  qual é mais fácil de manter quando o projeto cresce?

Critérios:
  mostra exemplo lado a lado em Python (pulumi) e HCL (terraform)
  não assume que eu sei o que é state file
  explica se pulumi é open source de verdade
```

**Versão técnica:**
```
Ferramentas: pulumi e terraform
Contexto:    IaC em Python para time que não quer aprender HCL, com state no S3
Foco:        1 (comparação geral)

Perguntas:
  como pulumi lida com state vs terraform state?
  qual tem melhor suporte a testes unitários da infraestrutura?
  como funciona import de recursos existentes em cada um?
  qual tem melhor integração com CI/CD (GitHub Actions, GitLab CI)?

Critérios:
  mostra exemplo Python real do pulumi (não pseudo-código)
  compara state backends (pulumi cloud vs s3)
  menciona o custo do pulumi cloud vs self-hosted
  tem exemplo de teste unitário de infra
```

---

## CI/CD

### Gitea Actions vs GitHub Actions (self-hosted)

**Versão leigo:**
```
Ferramentas: gitea e github actions
Contexto:    quero ter meu próprio git e CI/CD sem depender do GitHub
Foco:        1 (comparação geral)

Perguntas:
  o gitea tem CI/CD embutido?
  posso usar os mesmos workflows do github actions no gitea?
  quanto de servidor preciso pra rodar o gitea?
  é difícil de instalar e manter sozinho?

Critérios:
  explica o que é CI/CD sem jargão
  tem passo a passo de instalação do gitea
  é honesto sobre o que funciona e o que não funciona igual ao github
```

**Versão técnica:**
```
Ferramentas: gitea e github actions
Contexto:    plataforma git self-hosted com CI/CD para time de 10 devs em rede interna
Foco:        5 (integração)

Perguntas:
  quais actions do marketplace do github funcionam no gitea actions?
  como configurar runners self-hosted no gitea?
  como funciona o cache de dependências no gitea actions?
  qual o consumo de recursos do gitea com CI habilitado?

Critérios:
  lista incompatibilidades concretas com github actions
  tem exemplo de workflow .gitea/workflows real
  menciona act_runner
  tem números de consumo de RAM/CPU
```

---

### Woodpecker CI vs Drone CI

**Versão leigo:**
```
Ferramentas: woodpecker ci e drone ci
Contexto:    quero um CI/CD leve e open source pra meus projetos pessoais
Foco:        1 (comparação geral)

Perguntas:
  qual dos dois é realmente gratuito e open source?
  qual é mais fácil de instalar com docker?
  consigo fazer build e deploy automático com cada um?
  qual consome menos recursos no servidor?

Critérios:
  explica a relação entre drone e woodpecker (fork)
  tem docker-compose de instalação
  menciona a mudança de licença do drone
```

**Versão técnica:**
```
Ferramentas: woodpecker ci e drone ci
Contexto:    CI/CD self-hosted para monorepo com 5 serviços em Go
Foco:        1 (comparação geral)

Perguntas:
  qual suporta melhor pipelines matriciais e paralelismo?
  como funciona o sistema de plugins em cada um?
  qual tem melhor suporte a monorepo (path triggers)?
  como configurar cache entre builds?

Critérios:
  menciona que woodpecker é fork do drone
  tem exemplo de pipeline com build paralelo
  compara sistema de plugins
  referências incluem github.com/woodpecker-ci
```

---

## Observability

### Prometheus + Grafana — integração

**Versão leigo:**
```
Ferramentas: prometheus e grafana
Contexto:    quero monitorar minha aplicação web e ver gráficos bonitos
Foco:        5 (integração)

Perguntas:
  pra que serve cada um? são concorrentes ou trabalham juntos?
  como faço pra minha aplicação mandar dados pro prometheus?
  como criar um gráfico básico no grafana?
  é difícil de instalar e configurar?

Critérios:
  explica que são ferramentas complementares, não concorrentes
  tem passo a passo de instalação
  não assume que eu sei o que é scraping de métricas
```

**Versão técnica:**
```
Ferramentas: prometheus e grafana
Contexto:    observability em stack FastAPI com 3 serviços rodando em docker compose
Foco:        5 (integração)

Perguntas:
  como expor métricas do FastAPI para o prometheus?
  como configurar o grafana para usar o prometheus como datasource?
  qual o scrape interval recomendado para não sobrecarregar a aplicação?
  como criar um dashboard básico de latência e requisições por segundo?

Critérios:
  tem exemplo de scrape config do prometheus
  tem código Python real para expor métricas no FastAPI
  não trata prometheus e grafana como concorrentes
  menciona prometheus-client ou starlette-prometheus
```

---

### Loki vs Elasticsearch — logs

**Versão leigo:**
```
Ferramentas: loki e elasticsearch
Contexto:    quero guardar e pesquisar os logs da minha aplicação
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar e manter?
  qual gasta menos recursos no servidor?
  consigo pesquisar os logs de forma rápida nos dois?
  qual funciona melhor com o grafana?

Critérios:
  explica o que é um sistema de logs centralizado
  não assume que eu sei o que é índice invertido
  diz qual é melhor pra quem tá começando
```

**Versão técnica:**
```
Ferramentas: loki e elasticsearch
Contexto:    centralização de logs de 50 containers em docker compose com retenção de 30 dias
Foco:        2 (performance / throughput)

Perguntas:
  qual consome menos RAM e disco para o mesmo volume de logs?
  como cada um lida com ingestão de 10k logs/segundo?
  qual tem melhor query performance pra buscas por texto livre?
  como configurar retenção e rotação de logs em cada um?

Critérios:
  tem números concretos de consumo de recursos
  menciona que loki não indexa o conteúdo (só labels)
  tem exemplo de docker-compose com cada um
  compara LogQL vs KQL/Lucene
```

---

### Uptime Kuma vs Gatus

**Versão leigo:**
```
Ferramentas: uptime kuma e gatus
Contexto:    quero saber quando meu site cai e receber um alerta
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de configurar?
  consigo receber alerta no telegram ou discord?
  preciso de muito servidor pra rodar?
  qual tem interface mais bonita pra mostrar pro cliente?

Critérios:
  tem docker-compose de instalação pra cada um
  mostra a interface de status page
  não assume que eu sei configurar healthcheck
```

**Versão técnica:**
```
Ferramentas: uptime kuma e gatus
Contexto:    monitoramento de 200+ endpoints HTTP com status page pública
Foco:        2 (performance / throughput)

Perguntas:
  qual escala melhor pra 500+ monitores simultâneos?
  como configurar checks via código (config as code) no gatus?
  qual tem melhor integração com alertmanager e pagerduty?
  como cada um lida com SSL certificate monitoring?

Critérios:
  menciona que gatus é config-as-code e kuma é UI-first
  tem exemplo de gatus config.yaml
  compara consumo de recursos com muitos monitores
  referências incluem github.com
```

---

## Dados e Analytics

### SQLite vs DuckDB — performance

**Versão leigo:**
```
Ferramentas: sqlite e duckdb
Contexto:    preciso analisar planilhas e CSVs grandes (vários GB) no meu computador
Foco:        2 (performance / throughput)

Perguntas:
  qual é mais rápido pra analisar dados grandes?
  consigo abrir arquivos maiores que minha RAM?
  qual é mais fácil de usar com Python?
  preciso instalar um servidor de banco de dados?

Critérios:
  explica a diferença sem assumir que eu sei SQL avançado
  tem exemplo com arquivo CSV real
  diz qual usar pra cada situação
  não ignora que sqlite é mais conhecido
```

**Versão técnica:**
```
Ferramentas: sqlite e duckdb
Contexto:    análise de dados local com datasets de até 10GB em Python
Foco:        2 (performance / throughput)

Perguntas:
  qual é mais rápido para queries analíticas com aggregation?
  como cada um lida com datasets maiores que a RAM?
  qual o consumo de memória durante queries pesadas?
  duckdb substitui sqlite ou complementa?

Critérios:
  tem benchmark concreto com números
  menciona columnar vs row-based storage
  tem exemplo Python com pandas ou polars
  não ignora que sqlite é row-oriented
```

---

### Kafka + Flink — streaming

**Versão leigo:**
```
Ferramentas: kafka e flink
Contexto:    preciso processar logs da minha aplicação em tempo real
Foco:        5 (integração)

Perguntas:
  pra que serve cada um? são a mesma coisa?
  como eles trabalham juntos num pipeline?
  o que acontece se uma parte falhar no meio do processamento?
  preciso de muito hardware pra rodar os dois?

Critérios:
  explica o papel de cada um sem jargão pesado
  não trata kafka e flink como substitutos
  tem algum exemplo concreto do fluxo de dados
```

**Versão técnica:**
```
Ferramentas: kafka e flink
Contexto:    pipeline de ingestão de logs de aplicação em tempo real
Foco:        5 (integração)

Perguntas:
  como kafka e flink se encaixam no mesmo pipeline?
  qual a garantia de entrega padrão e como mudar para exactly-once?
  como lidar com backpressure quando o flink não acompanha o kafka?
  qual o mínimo de recursos para rodar os dois juntos em produção?

Critérios:
  explica o papel de cada um no pipeline (broker vs processador)
  menciona at-least-once ou exactly-once
  tem exemplo de job flink consumindo tópico kafka
  não trata kafka e flink como substitutos
```

---

### MinIO vs SeaweedFS — object storage

**Versão leigo:**
```
Ferramentas: minio e seaweedfs
Contexto:    quero guardar backups e arquivos grandes no meu próprio servidor tipo S3
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar?
  consigo usar com ferramentas que já funcionam com S3 da Amazon?
  qual aguenta mais dados sem ficar lento?
  qual gasta menos disco e memória?

Critérios:
  explica o que é object storage compatível com S3
  tem docker-compose de instalação
  não inventa funcionalidades
```

**Versão técnica:**
```
Ferramentas: minio e seaweedfs
Contexto:    object storage self-hosted para data lake com 50TB+ em bare metal
Foco:        2 (performance / throughput)

Perguntas:
  qual tem melhor throughput de escrita para objetos grandes (100MB+)?
  como cada um lida com erasure coding vs replicação?
  qual o overhead de metadados por objeto em cada um?
  como funciona o tiering (hot/cold) em cada um?

Critérios:
  tem benchmark de throughput com números
  compara modelos de redundância
  menciona a mudança de licença do minio (AGPL)
  tem exemplo de configuração com mc ou s3cmd
```

---

### Apache Superset vs Metabase

**Versão leigo:**
```
Ferramentas: superset e metabase
Contexto:    quero criar dashboards e gráficos dos dados da minha empresa sem pagar BI caro
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil pra quem não é programador?
  consigo conectar no meu banco PostgreSQL?
  qual tem gráficos mais bonitos?
  qual funciona melhor pra times pequenos (5-10 pessoas)?

Critérios:
  tem passo a passo de instalação com docker
  mostra exemplo de dashboard real
  diz qual é melhor pra cada perfil de usuário
  não assume que eu sei SQL
```

**Versão técnica:**
```
Ferramentas: superset e metabase
Contexto:    plataforma self-hosted de BI para equipe de dados com 20 usuários
Foco:        1 (comparação geral)

Perguntas:
  como cada um lida com row-level security?
  qual tem melhor suporte a SQL nativo e queries complexas?
  como funciona o caching de queries em cada um?
  qual escala melhor com muitos dashboards simultâneos?

Critérios:
  compara modelo de permissões
  tem exemplo de configuração de cache
  menciona embedded analytics
  referências incluem documentação oficial
```

---

## Nuvem e Self-Hosted

### Coolify vs CapRover — PaaS self-hosted

**Versão leigo:**
```
Ferramentas: coolify e caprover
Contexto:    quero fazer deploy das minhas aplicações no meu servidor sem usar Heroku ou Vercel
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar?
  consigo fazer deploy pelo git push?
  qual suporta mais linguagens e frameworks?
  quanto de servidor preciso?

Critérios:
  tem passo a passo pra instalar do zero num VPS
  mostra como fazer deploy de uma app real
  não assume que eu sei o que é reverse proxy
```

**Versão técnica:**
```
Ferramentas: coolify e caprover
Contexto:    PaaS self-hosted em VPS de 4GB RAM para deploy de 10 aplicações
Foco:        1 (comparação geral)

Perguntas:
  como cada um gerencia SSL automático (Let's Encrypt)?
  qual tem melhor suporte a docker-compose multi-service?
  como funciona o zero-downtime deployment em cada um?
  qual o consumo base de RAM com a plataforma idle?

Critérios:
  tem números de consumo de RAM base
  compara estratégia de deploy (rolling vs blue-green)
  menciona que coolify é o sucessor espiritual do heroku OSS
  tem exemplo de coolify.json ou captain-definition
```

---

### Proxmox vs XCP-ng — virtualização

**Versão leigo:**
```
Ferramentas: proxmox e xcp-ng
Contexto:    quero transformar um computador antigo num servidor de máquinas virtuais
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar e usar?
  consigo rodar Windows e Linux na mesma máquina?
  qual funciona melhor em hardware antigo?
  precisa de licença paga?

Critérios:
  tem passo a passo de instalação via USB
  explica o que é hypervisor sem jargão
  diz qual tem interface web mais amigável
```

**Versão técnica:**
```
Ferramentas: proxmox e xcp-ng
Contexto:    homelab com 3 nós para HA e migração live de VMs
Foco:        1 (comparação geral)

Perguntas:
  como funciona HA e live migration em cada um?
  qual tem melhor suporte a ZFS e storage distribuído (Ceph)?
  como cada um lida com passthrough de GPU?
  qual o overhead do hypervisor em RAM e CPU?

Critérios:
  compara KVM (proxmox) vs Xen (xcp-ng)
  tem exemplo de cluster com shared storage
  menciona Xen Orchestra como interface do xcp-ng
  tem números de overhead
```

---

### Cloudflare Tunnel vs Tailscale Funnel

**Versão leigo:**
```
Ferramentas: cloudflare tunnel e tailscale funnel
Contexto:    quero expor minha aplicação local pra internet sem abrir portas no roteador
Foco:        1 (comparação geral)

Perguntas:
  como funciona se eu não preciso abrir porta?
  qual é de graça?
  qual é mais fácil de configurar?
  é seguro usar isso?

Critérios:
  explica o conceito de tunnel sem jargão de rede
  tem comando pra funcionar em 5 minutos
  não assume que eu sei o que é NAT ou firewall
```

**Versão técnica:**
```
Ferramentas: cloudflare tunnel e tailscale funnel
Contexto:    exposição segura de serviços internos para acesso externo sem IP público
Foco:        6 (segurança)

Perguntas:
  como cada um lida com TLS termination?
  qual suporta melhor múltiplos serviços num mesmo tunnel?
  como funciona o controle de acesso (quem pode acessar)?
  qual tem menor latência adicionada ao request?

Critérios:
  compara modelo de segurança (zero trust)
  tem exemplo de configuração com múltiplos serviços
  menciona limitações do plano gratuito
  tem teste de latência com números
```

---

## IA Local

### Ollama — modelos pra notebook fraco

**Versão leigo:**
```
Ferramentas: ollama
Contexto:    notebook com 8GB de RAM sem placa de vídeo dedicada, quero rodar IA local
Foco:        8 (quantização / modelos locais)

Perguntas:
  quais modelos consigo rodar no meu notebook de 8GB?
  qual modelo tem melhor custo-benefício pra conversar e tirar dúvidas?
  meu notebook vai travar se eu rodar um modelo grande demais?
  como instalar o ollama e rodar meu primeiro modelo?
  a resposta demora muito sem placa de vídeo?
  tem como melhorar a velocidade sem trocar hardware?

Critérios:
  tem passo a passo de instalação do zero
  recomenda pelo menos 2 modelos que cabem em 8GB
  avisa claramente o que NÃO cabe em 8GB
  tem comando pra testar se tá funcionando
  não assume que o leitor sabe o que é quantização
```

**Versão técnica:**
```
Ferramentas: ollama
Contexto:    rodando LLMs localmente com 8GB a 16GB de RAM sem GPU dedicada no Ubuntu 22.04
Foco:        8 (quantização / modelos locais)

Perguntas:
  quanto de RAM usa o llama3.1:8b, qwen2.5:7b, gemma2:9b, phi3:3.8b e mistral:7b?
  qual o maior modelo que roda em 8GB sem swap e qual roda em 16GB?
  qual a perda real de qualidade entre Q4_K_M e Q8_0 no mesmo modelo?
  como ver RAM usada e tokens por segundo com ollama ps e ollama run --verbose?
  como configurar num_ctx e num_thread pra melhor performance em CPU only?
  o context length de 2048 vs 4096 vs 8192 muda quanto de RAM?

Critérios:
  lista pelo menos 5 modelos concretos com RAM estimada de cada
  separa claramente o que cabe em 8GB e o que precisa de 16GB
  mostra comando real ollama run --verbose com saída esperada
  tem tabela modelo vs RAM vs tokens/s
  menciona impacto do context length no consumo de RAM
```

---

### Ollama vs LM Studio

**Versão leigo:**
```
Ferramentas: ollama e lm studio
Contexto:    quero rodar IA local e não sei qual programa usar
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil pra quem nunca usou IA local?
  qual tem interface gráfica pra conversar?
  qual funciona melhor em notebook fraco?
  os dois são de graça?

Critérios:
  explica que ollama é terminal e lm studio é GUI
  tem passo a passo dos dois
  diz qual é melhor pra cada perfil de pessoa
```

**Versão técnica:**
```
Ferramentas: ollama e lm studio
Contexto:    servidor de inferência local para aplicações via API REST
Foco:        2 (performance / throughput)

Perguntas:
  qual tem melhor throughput servindo via API (requests/segundo)?
  como cada um lida com concorrência de múltiplos requests?
  qual suporta mais formatos de modelo (GGUF, safetensors)?
  como funciona o gerenciamento de modelos em cada um?

Critérios:
  tem benchmark de API throughput
  compara APIs compatíveis com OpenAI
  menciona que lm studio não é open source
  tem exemplo de chamada API com curl
```

---

### Open WebUI — interface pro Ollama

**Versão leigo:**
```
Ferramentas: open webui
Contexto:    quero uma interface tipo ChatGPT mas rodando no meu computador com ollama
Foco:        5 (integração)

Perguntas:
  como instalar o open webui junto com o ollama?
  fica parecido com o ChatGPT?
  consigo usar vários modelos diferentes?
  funciona no celular também?

Critérios:
  tem docker-compose que sobe ollama + open webui juntos
  mostra screenshot ou descrição da interface
  não assume que eu sei o que é API endpoint
```

**Versão técnica:**
```
Ferramentas: open webui
Contexto:    interface multi-usuário para ollama em rede local com autenticação
Foco:        5 (integração)

Perguntas:
  como configurar autenticação e múltiplos usuários?
  como conectar em um ollama rodando em outra máquina da rede?
  suporta RAG (upload de documentos)?
  como customizar system prompts por modelo?

Critérios:
  tem docker-compose com variáveis de ambiente reais
  mostra configuração de OLLAMA_BASE_URL remoto
  menciona funcionalidade de RAG
  tem exemplo de configuração multi-usuário
```

---

### Whisper — transcrição local

**Versão leigo:**
```
Ferramentas: whisper
Contexto:    quero transcrever áudio e vídeo em texto no meu computador sem mandar pra nuvem
Foco:        8 (quantização / modelos locais)

Perguntas:
  qual modelo do whisper roda no meu notebook de 8GB?
  quanto tempo demora pra transcrever 1 hora de áudio?
  funciona em português?
  a qualidade é boa mesmo sem internet?

Critérios:
  recomenda modelo específico pra 8GB
  tem comando pra transcrever um arquivo de áudio
  menciona suporte a português
  não assume que eu sei o que é modelo de speech-to-text
```

**Versão técnica:**
```
Ferramentas: whisper
Contexto:    pipeline de transcrição batch de reuniões em português com 8-16GB RAM
Foco:        2 (performance / throughput)

Perguntas:
  qual a diferença de WER entre whisper-small, medium e large-v3 em português?
  como rodar whisper.cpp pra melhor performance em CPU?
  qual o real-time factor (RTF) de cada modelo em CPU only?
  como fazer transcrição com timestamps e diarização?

Critérios:
  tem benchmark RTF por modelo
  compara whisper original vs whisper.cpp vs faster-whisper
  menciona WER em português especificamente
  tem exemplo de comando com output real
```

---

## Workflow e Orquestração

### Temporal vs Conductor

**Versão leigo:**
```
Ferramentas: temporal e conductor
Contexto:    tenho vários serviços que precisam executar tarefas em sequência sem perder dados
Foco:        1 (comparação geral)

Perguntas:
  pra que serve uma ferramenta de orquestração de workflows?
  o que acontece se um serviço cair no meio de uma tarefa?
  qual dos dois é mais fácil de começar a usar?
  preciso saber programar pra usar?

Critérios:
  explica o conceito de workflow sem jargão
  dá um exemplo concreto do tipo "pedido de compra"
  não assume que eu sei o que é durable execution
```

**Versão técnica:**
```
Ferramentas: temporal e conductor
Contexto:    orquestração de workflows em microsserviços com falhas parciais e retries
Foco:        1 (comparação geral)

Perguntas:
  o que é durable execution e como cada um implementa?
  como cada um lida com falha parcial no meio de um workflow?
  como funciona o mecanismo de retry e backoff?
  qual a diferença entre orquestração e coreografia?

Critérios:
  explica durable execution com clareza
  tem exemplo de workflow com pelo menos 2 steps
  não confunde orquestração com coreografia
  menciona compensação ou rollback em caso de falha
```

---

### n8n vs Apache Airflow

**Versão leigo:**
```
Ferramentas: n8n e airflow
Contexto:    quero automatizar tarefas repetitivas tipo "quando chegar email, salvar anexo no drive"
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de usar sem saber programar?
  qual tem mais integrações prontas (gmail, slack, drive)?
  consigo rodar no meu computador de graça?
  qual é melhor pra automações simples do dia a dia?

Critérios:
  explica que n8n é visual e airflow é código
  tem exemplo de automação simples em cada um
  diz qual é melhor pra quem não programa
  não assume que eu sei o que é DAG
```

**Versão técnica:**
```
Ferramentas: n8n e airflow
Contexto:    orquestração de pipelines de dados ETL com 50+ DAGs em produção
Foco:        2 (performance / throughput)

Perguntas:
  como airflow lida com paralelismo de tasks vs n8n?
  qual escala melhor pra 100+ workflows simultâneos?
  como cada um gerencia retry e alertas de falha?
  qual tem melhor suporte a custom operators/nodes?

Critérios:
  compara executor do airflow (celery/kubernetes) vs n8n workers
  tem exemplo de DAG real do airflow
  menciona que n8n tem licença fair-code (não é Apache 2.0)
  tem números de performance em escala
```

---

## Object Storage

### VersityGW vs Garage — ferramentas obscuras

**Versão leigo:**
```
Ferramentas: versitygw e garage
Contexto:    preciso guardar arquivos tipo S3 da Amazon mas no meu próprio servidor
Foco:        1 (comparação geral)

Perguntas:
  qual dos dois é mais fácil de instalar e manter?
  consigo usar as mesmas ferramentas que uso com S3 da Amazon?
  funciona sem internet depois de instalado?
  qual gasta menos espaço e memória?

Critérios:
  explica o que é compatibilidade S3 sem assumir conhecimento prévio
  tem exemplo prático de como subir e baixar um arquivo
  não inventa funcionalidades que não existem
```

**Versão técnica:**
```
Ferramentas: versitygw e garage
Contexto:    object storage self-hosted compatível com S3 em ambiente air-gapped
Foco:        1 (comparação geral)

Perguntas:
  quais operações da API S3 cada um suporta?
  como configurar replicação entre nós?
  funciona sem acesso à internet após instalado?
  qual o consumo de disco e RAM com 1TB de dados?

Critérios:
  menciona compatibilidade com API S3
  tem exemplo com aws-cli ou boto3
  não inventa features que não existem
  referências incluem github.com
```

---

## Custo — Cloud

### AWS Step Functions vs Temporal Cloud

**Versão leigo:**
```
Ferramentas: aws step functions e temporal cloud
Contexto:    preciso automatizar tarefas na nuvem e quero saber quanto vou gastar
Foco:        3 (custo)

Perguntas:
  quanto custa cada um por mês?
  qual fica mais caro quando uso muito?
  tem custos escondidos que eu não tô vendo?
  qual compensa mais pra quem tá começando?

Critérios:
  mostra preços reais, não só "depende"
  avisa sobre custos que não aparecem na página de pricing
  compara com um exemplo concreto de volume
  não assume que eu sei o que é egress
```

**Versão técnica:**
```
Ferramentas: aws step functions e temporal cloud
Contexto:    orquestração de 500k workflows/mês em produção
Foco:        3 (custo)

Perguntas:
  qual o modelo de pricing de cada um?
  como o custo escala com volume de execuções?
  existem custos ocultos (egress, storage, logging)?
  qual fica mais barato acima de 1M execuções/mês?

Critérios:
  tem números concretos de pricing
  menciona custos indiretos (compute, storage)
  não compara apenas o preço base
  tem estimativa para o volume do contexto
```

---

## Dados — Open Source

### DuckDB vs Polars

**Versão leigo:**
```
Ferramentas: duckdb e polars
Contexto:    quero analisar arquivos CSV grandes no meu computador sem ficar lento
Foco:        1 (comparação geral)

Perguntas:
  qual é mais rápido pra trabalhar com dados?
  qual usa menos memória?
  qual é mais fácil de aprender?
  dá pra usar em notebooks Python?

Critérios:
  explica sem assumir que conheço SQL
  tem exemplo prático com arquivo CSV
  compara performance com números reais
  mostra como instalar e começar em 5 minutos
```

**Versão técnica:**
```
Ferramentas: duckdb e polars
Contexto:    análise OLAP em arquivos Parquet com 10GB+ em notebooks Jupyter
Foco:        2 (performance / throughput)

Perguntas:
  qual executa queries mais rápido em Parquet?
  como cada um usa SIMD e paralelismo?
  qual suporta melhor pushdown predicates?
  como configurar memory pool otimizado?

Critérios:
  compara benchmark real com Parquet
  menciona SIMD vectorization em ambos
  tem exemplo de query com explain plan
  referencia benchmarks oficiais de ambos
```

---

### Apache Superset vs Metabase

**Versão leigo:**
```
Ferramentas: apache superset e metabase
Contexto:    quero criar dashboards que mostram dados de forma legal pra gerente
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de fazer gráficos bonitos?
  qual conecta melhor com banco de dados?
  preciso saber código pra usar?
  qual roda no meu servidor local?

Critérios:
  explica que ambas são BI tools
  tem exemplo de dashboard real
  não assume que sei Python ou SQL
  mostra como conectar num banco de dados simples
```

**Versão técnica:**
```
Ferramentas: apache superset vs metabase vs grafana
Contexto:    BI em múltiplas datasources (Postgres, BigQuery, S3)
Foco:        1 (comparação geral)

Perguntas:
  qual tem melhor suporte a diferentes datasources?
  qual oferece mais opções de visualização?
  como cada um lida com permissões e multi-tenancy?
  qual escala melhor com milhões de rows?

Critérios:
  compara tipos de visualização disponíveis
  explica arquitetura (Superset é mais extensível)
  tem exemplo de dashboard com múltiplos datasources
  menciona licensing (Superset é Apache 2.0, Metabase é SSPL)
```

---

### Airbyte vs Fivetran

**Versão leigo:**
```
Ferramentas: airbyte e fivetran
Contexto:    quero sincronizar dados entre vários sistemas automaticamente
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de configurar?
  qual sincroniza mais rápido?
  qual tem mais conectores prontos?
  qual é mais barato?

Critérios:
  explica o que é ELT sem jargão
  tem exemplo de pipeline simples
  não assume conhecimento de data pipelines
  mostra qual é gratuito e qual é pago
```

**Versão técnica:**
```
Ferramentas: airbyte vs fivetran vs stitch
Contexto:    pipeline ELT de 15+ datasources em data warehouse Postgres
Foco:        2 (performance / throughput)

Perguntas:
  qual suporta melhor incremental replication sem CDC?
  como cada um lida com schema evolution?
  qual tem menor latência fim-a-fim?
  como monitorar e alertar em caso de falha?

Critérios:
  compara incremental sync vs full sync
  menciona CDC (Change Data Capture)
  tem exemplo com postgres como destino
  não confunde ELT com ETL
```

---

## DevOps — Open Source

### Terraform vs Pulumi vs CDK

**Versão leigo:**
```
Ferramentas: terraform, pulumi, cdk
Contexto:    quero criar e manter servidores na nuvem sem clicar no console
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de começar?
  qual funciona em AWS, Azure e GCP?
  posso usar a mesma coisa pra todos os clouds?
  qual meu time consegue aprender rápido?

Critérios:
  explica o que é Infrastructure as Code sem jargão
  tem exemplo pequeno pra cada um
  não assume conhecimento de cloud
  menciona que o arquivo fica em version control
```

**Versão técnica:**
```
Ferramentas: terraform vs pulumi vs aws-cdk
Contexto:    multi-cloud infra em AWS/Azure/GCP com state management centralizado
Foco:        1 (comparação geral)

Perguntas:
  qual tem melhor suporte para modularity e code reuse?
  como cada um lida com state file em ambiente distribuído?
  qual integra melhor com Kubernetes?
  como fazer rollback seguro de infra changes?

Critérios:
  Terraform: declarativo (HCL), agnóstico de cloud
  Pulumi: programático (Python/TypeScript/Go), agnóstico
  CDK: programático (TypeScript/Python), AWS-only
  compara vantagens de declarativo vs imperativo
```

---

### Prometheus vs VictoriaMetrics

**Versão leigo:**
```
Ferramentas: prometheus e victoriametrics
Contexto:    quero monitorar meus servidores e saber quando algo está errado
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar?
  qual consome menos disco pra guardar dados?
  qual funciona melhor se tiver muitos servidores?
  qual é de graça?

Critérios:
  explica o que é time-series database sem jargão
  tem exemplo de métrica simples
  compara consumo de disco entre os dois
  não assume que sei Kubernetes
```

**Versão técnica:**
```
Ferramentas: prometheus vs victoriametrics vs influxdb
Contexto:    monitoramento em escala de 10k+ métricas/segundo
Foco:        2 (performance / throughput)

Perguntas:
  qual escala melhor horizontalmente?
  qual tem menor latência de escrita?
  como cada um implementa retenção de dados?
  qual suporta melhor federated scraping?

Critérios:
  menciona que VictoriaMetrics é drop-in replacement
  compara retention e compaction strategies
  tem benchmark real com k8s
  explica remote write vs federated scraping
```

---

### HashiCorp Vault vs Sealed Secrets (Kubernetes)

**Versão leigo:**
```
Ferramentas: hashicorp vault e sealed secrets
Contexto:    quero guardar senhas e chaves de forma segura no Kubernetes
Foco:        6 (segurança)

Perguntas:
  qual é mais seguro pra guardar secrets?
  qual é mais fácil de usar com Kubernetes?
  como recupero a senha se esquecer?
  qual é de graça?

Critérios:
  explica o que é secret management sem jargão
  tem exemplo de como usar no Kubernetes
  não assume conhecimento de criptografia
  avisa sobre armadilhas comuns
```

**Versão técnica:**
```
Ferramentas: hashicorp vault vs sealed-secrets vs external-secrets-operator
Contexto:    multi-cluster Kubernetes com gestão centralizada de secrets
Foco:        6 (segurança)

Perguntas:
  qual suporta melhor dynamic secrets?
  como cada um implementa auto-rotation?
  qual integra melhor com CI/CD pipelines?
  como fazer disaster recovery de master keys?

Critérios:
  menciona dynamic secrets vs static secrets
  explica HSM integration com Vault
  tem exemplo com external-secrets-operator
  não trata key rotation como opcional
```

---

## Backend — Open Source

### FastAPI vs Django vs Flask

**Versão leigo:**
```
Ferramentas: fastapi, django, flask
Contexto:    vou fazer uma API pra meu app mobile e quero escolher a melhor
Foco:        1 (comparação geral)

Perguntas:
  qual é mais rápida?
  qual é melhor pra quem tá começando?
  qual tem mais exemplos na internet?
  qual tem melhor documentação?

Critérios:
  explica sem assumir que sei Python
  tem exemplo pequenininho de cada um
  não diz que uma é "melhor" sem contexto
  mostra como fazer um GET e POST simples
```

**Versão técnica:**
```
Ferramentas: fastapi vs quart vs starlette
Contexto:    API assíncrona em produção com 10k req/s
Foco:        2 (performance / throughput)

Perguntas:
  qual executa requests mais rápido?
  como cada um implementa async/await?
  qual tem melhor suporte a OpenAPI/Swagger?
  qual escala melhor horizontalmente?

Critérios:
  compara throughput com benchmark real
  tem exemplo de async handler
  menciona que FastAPI é mais thin que Django
  não confunde framework throughput com DB bottleneck
```

---

### SQLAlchemy vs Tortoise ORM vs Pydantic

**Versão leigo:**
```
Ferramentas: sqlalchemy, tortoise orm, pydantic
Contexto:    quero trabalhar com banco de dados em Python sem escrever SQL
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de aprender?
  qual funciona com qualquer banco de dados?
  posso usar junto com FastAPI?
  qual é mais popular?

Critérios:
  explica ORM sem assumir conhecimento prévio
  tem exemplo de query simples
  diferencia Pydantic (validation) de ORM
  não assume que sei SQL
```

**Versão técnica:**
```
Ferramentas: sqlalchemy 2.0 vs tortoise-orm vs pony-orm
Contexto:    complex queries com múltiplos joins em PostgreSQL
Foco:        2 (performance / throughput)

Perguntas:
  qual gera melhor SQL pra joins complexos?
  como cada um implementa lazy vs eager loading?
  qual tem melhor query building API?
  como monitorar queries geradas?

Critérios:
  compara EXPLAIN ANALYZE de queries geradas
  menciona N+1 query problem
  tem exemplo com relationship loading
  não assume que todas são iguais
```

---

### Redis vs Dragonfly vs KeyDB (Cache)

**Versão leigo:**
```
Ferramentas: redis, dragonfly, keydb
Contexto:    quero cachear dados pra minha API ficar mais rápida
Foco:        1 (comparação geral)

Perguntas:
  qual é mais rápido?
  qual usa menos memória?
  qual é mais fácil de instalar?
  qual é de graça?

Critérios:
  explica o que é cache sem jargão
  tem exemplo de como usar
  compara consumo de RAM entre os três
  não assume conhecimento de Redis
```

**Versão técnica:**
```
Ferramentas: redis vs dragonfly vs keydb
Contexto:    cache em escala de 100GB+ com latência < 1ms
Foco:        2 (performance / throughput)

Perguntas:
  qual tem melhor throughput em set/get?
  qual escala melhor verticalmente?
  qual suporta melhor persistence (RDB/AOF)?
  como cada um implementa eviction policies?

Critérios:
  compara latência p99 entre os três
  menciona que Dragonfly é multi-threaded
  tem benchmark com redis-benchmark
  explica RESP3 vs RESP2
```

---

## Nuvem Local — Open Source

### Ceph vs MinIO vs SeaweedFS (Object Storage)

**Versão leigo:**
```
Ferramentas: ceph, minio, seaweedfs
Contexto:    quero guardar arquivos grandes no meu servidor sem pagar AWS
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de instalar em casa?
  qual funciona como o S3 da Amazon?
  qual consome menos energia?
  qual funciona em computador fraco?

Critérios:
  explica object storage sem jargão
  tem exemplo de como fazer upload/download
  não assume conhecimento de cloud
  menciona compatibilidade S3 claramente
```

**Versão técnica:**
```
Ferramentas: ceph vs minio vs seaweedfs vs garage
Contexto:    object storage self-hosted com 500TB em 10 nós
Foco:        1 (comparação geral)

Perguntas:
  qual tem melhor replicação?
  qual escala melhor horizontalmente?
  como cada um implementa erasure coding?
  qual tem melhor disaster recovery?

Critérios:
  compara replication factor vs overhead
  explica erasure coding de forma clara
  tem exemplo de multi-node setup
  não confunde replicação com backup
```

---

### Kubernetes vs Nomad vs Docker Swarm

**Versão leigo:**
```
Ferramentas: kubernetes, nomad, docker swarm
Contexto:    quero rodar containers no meu data center sem depender da AWS
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de aprender?
  qual funciona melhor em servidor fraco?
  qual posso rodar no meu laptop?
  qual tem mais documentação?

Critérios:
  explica container orchestration sem jargão
  tem exemplo pequeno de deployment
  não assume conhecimento de Docker
  avisa sobre curva de aprendizado
```

**Versão técnica:**
```
Ferramentas: kubernetes vs nomad vs docker swarm
Contexto:    orquestração de 100+ serviços em on-premise
Foco:        1 (comparação geral)

Perguntas:
  qual tem melhor service discovery?
  como cada um implementa networking?
  qual integra melhor com terraform?
  qual tem menor overhead de recursos?

Critérios:
  compara CNI plugins (K8s) vs Nomad agnóstico
  menciona que Docker Swarm é mais simples mas menos features
  tem exemplo real de deployment
  não trata Kubernetes como única opção
```

---

### OpenVPN vs WireGuard vs Tailscale

**Versão leigo:**
```
Ferramentas: openvpn, wireguard, tailscale
Contexto:    quero acessar meu servidor em casa de forma segura de qualquer lugar
Foco:        6 (segurança)

Perguntas:
  qual é mais fácil de configurar?
  qual é mais seguro?
  qual consome menos bateria?
  qual funciona através de proxy/firewall?

Critérios:
  explica VPN sem assumir conhecimento prévio
  tem exemplo de configuração básica
  não trata segurança como feature secundária
  avisa sobre armadilhas comuns
```

**Versão técnica:**
```
Ferramentas: openvpn vs wireguard vs zerotier
Contexto:    secure mesh network em 50+ nós geográficos distribuídos
Foco:        6 (segurança)

Perguntas:
  qual tem melhor latência e throughput?
  como cada um implementa encryption?
  qual suporta melhor key rotation?
  como configurar multi-hop routing?

Critérios:
  menciona que WireGuard usa Curve25519
  compara latência real entre os três
  tem exemplo de mesh network setup
  explica zero-trust principles
```

---

## Linux — Open Source

### systemd vs OpenRC vs s6 (Init System)

**Versão leigo:**
```
Ferramentas: systemd, openrc, s6
Contexto:    quero entender como meus serviços iniciam no Linux
Foco:        1 (comparação geral)

Perguntas:
  qual é o mais comum?
  qual é mais simples de usar?
  qual usa menos recursos?
  posso escolher qual usar?

Critérios:
  explica init system sem jargão
  tem exemplo de .service file
  não assume conhecimento prévio
  avisa sobre armadilhas do systemd
```

**Versão técnica:**
```
Ferramentas: systemd vs openrc vs runit
Contexto:    embarcado em imagem mínima com <50MB
Foco:        2 (performance / throughput)

Perguntas:
  qual tem menor footprint?
  qual inicia serviços mais rápido?
  como cada um lida com dependencies?
  qual tem melhor logging?

Critérios:
  compara tamanho binário entre os três
  tem exemplo de dependency ordering
  menciona que systemd é de facto padrão
  não assume que é melhor pra todos
```

---

### LUKS vs VeraCrypt vs dm-crypt (Disk Encryption)

**Versão leigo:**
```
Ferramentas: luks, veracrypt, dm-crypt
Contexto:    quero criptografar meu disco rígido pra ninguém roubá-lo
Foco:        6 (segurança)

Perguntas:
  qual é mais seguro?
  qual é mais fácil de usar?
  qual funciona melhor se eu esquecer a senha?
  qual desacelera menos o computador?

Critérios:
  explica criptografia de disco sem jargão
  tem exemplo de como ativar
  não assume conhecimento de criptografia
  avisa que perder a senha = dados perdidos
```

**Versão técnica:**
```
Ferramentas: luks2 vs tcplay vs dm-crypt vs fscrypt
Contexto:    full disk encryption em servidor de produção
Foco:        6 (segurança)

Perguntas:
  qual oferece melhor key derivation function (KDF)?
  como cada um implementa key recovery?
  qual suporta melhor TPM integration?
  qual tem menor performance impact?

Critérios:
  menciona que LUKS2 usa Argon2
  tem exemplo de key management
  explica hardware vs software encryption
  não confunde disk encryption com file encryption
```

---

### Btrfs vs ZFS vs LVM

**Versão leigo:**
```
Ferramentas: btrfs, zfs, lvm
Contexto:    tenho vários discos e quero gerenciar de forma mais inteligente
Foco:        1 (comparação geral)

Perguntas:
  qual é mais fácil de usar?
  qual é mais estável?
  qual oferece melhor proteção contra corrupção?
  qual é mais rápido?

Critérios:
  explica volume management sem jargão
  tem exemplo de criar pool/volume
  não assume conhecimento prévio
  avisa sobre estabilidade de cada um
```

**Versão técnica:**
```
Ferramentas: btrfs vs zfs vs lvm
Contexto:    NAS com 100TB armazenando dados críticos
Foco:         (comparação geral)

Perguntas:
  qual detecta e repara corrupção de dados?
  qual suporta melhor replicação e backup?
  qual tem overhead menor?
  qual é mais maduro em produção?

Critérios:
  explica checksum e COW (Copy on Write)
  compara recursos de snapshots
  menciona que ZFS é proprietário/CDDL
  tem exemplo real de setup
```

---

## Referência rápida — qual foco usar

| Situação | Foco recomendado |
|----------|-----------------|
| Duas ferramentas que fazem a mesma coisa | comparação geral |
| Preciso decidir qual adotar para o time | comparação geral |
| Ferramentas que trabalham juntas | integração |
| Hardware com pouca RAM ou CPU | hardware limitado / edge |
| Rodando modelos de IA localmente | quantização / modelos locais |
| Migrando de uma ferramenta para outra | migração |
| Custo é o critério principal | custo |
| Ambiente de produção com requisitos de segurança | segurança |
| Pipeline de dados com volume alto | performance / throughput |
| Analisar arquivos CSV/Parquet grandes | performance / throughput |
| Synchronizar dados entre systems | integração |
| Infra em múltiplos clouds | integração |
| Monitorar servidores e aplicações | performance / throughput |
| Rodar containers no próprio servidor | comparação geral |
| Guardar secrets de forma segura | segurança |
| Criar API rápida e moderna | performance / throughput |
| Cachear dados em memória | performance / throughput |
| Armazenar arquivos no próprio servidor | comparação geral |
| Gerenciar discos e volumes | comparação geral |
| Criptografar disco completo | segurança |
| VPN segura para equipe distribuída | segurança |