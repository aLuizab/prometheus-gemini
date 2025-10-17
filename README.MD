# Prometheus-GEMINI Alerter

Este é o projeto de demonstração para a palestra **"Do Prometheus ao GPT: Uma Nova Era de Observabilidade Inteligente"**, apresentada na Cloud Native Day São Paulo.

O objetivo deste projeto é demonstrar como a Inteligência Artificial Generativa pode ser integrada a uma stack de observabilidade tradicional (Prometheus + Alertmanager) para transformar alertas técnicos e crípticos em análises ricas, contextualizadas e acionáveis, enviadas diretamente para o Slack.

## Arquitetura

O fluxo da aplicação é simples e poderoso:

```
+-------------------+      +-----------------+      +------------------+
|  Aplicação Demo   |----->|   Prometheus    |----->|   Alertmanager   |
| (Python/Flask)    |      |(Coleta Métricas)|      | (Gatilho Alertas)|
+-------------------+      +-----------------+      +------------------+
                                                           | (Webhook)
                                                           v
                                                +---------------------+      +----------------+
                                                |  Gen AI Bridge      |----->|    Vertex AI   |
                                                | (Python/Flask)      |      | (Modelo Gemini)|
                                                +---------------------+      +----------------+
                                                           |
                                                           v
                                                +---------------------+
                                                | Canal do Slack      |
                                                |(Análise Inteligente)|
                                                +---------------------+
```

## Funcionalidades

  - **Aplicação Simples:** Um microserviço em Flask que expõe métricas customizadas para o Prometheus.
  - **Monitoramento Real:** Configuração funcional do Prometheus e Alertmanager para detectar problemas de latência e taxa de erros.
  - **Ponte Inteligente:** Um serviço intermediário que recebe webhooks do Alertmanager.
  - **Análise com Gen AI:** O serviço utiliza a SDK do Vertex AI para enviar os dados do alerta ao modelo Gemini, solicitando uma análise SRE.
  - **Notificações Ricas:** Publica a análise gerada pela IA em um canal do Slack de forma clara e bem formatada.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

  - [Docker](https://www.docker.com/get-started)
  - [Docker Compose](https://docs.docker.com/compose/install/)
  - Uma conta no [Google Cloud](https://cloud.google.com/)
  - Um workspace no [Slack](https://slack.com/) com permissões para criar aplicativos.

## ⚙️ Configuração

Siga estes passos cuidadosamente para configurar o ambiente.

### 1\. Google Cloud Platform (Vertex AI)

Esta é a etapa mais crítica. A autenticação com a API do Google Cloud requer uma configuração específica.

1.  **Crie um Projeto:** Se ainda não tiver um, crie um novo projeto no [Google Cloud Console](https://console.cloud.google.com/).
2.  **Ative o Faturamento:** A utilização das APIs de IA **exige** que seu projeto esteja vinculado a uma conta de faturamento ativa.
      - No menu, vá para `Faturamento` e siga as instruções.
3.  **Ative as APIs Necessárias:**
      - No menu, vá para `APIs e Serviços > Biblioteca`.
      - Procure e ative as seguintes APIs:
          - `Vertex AI API`
          - `Generative Language API` (para garantir compatibilidade)
4.  **Crie uma Conta de Serviço (Service Account):**
      - Vá para `IAM e admin > Contas de serviço`.
      - Crie uma nova conta de serviço (ex: `gemini-alerter-sa`).
      - Conceda a ela o papel de **"Usuário da Vertex AI" (Vertex AI User)**.
5.  **Gere uma Chave JSON:**
      - Após criar a conta de serviço, entre nela, vá na aba `CHAVES`.
      - Adicione uma nova chave do tipo **JSON**.
      - Um arquivo `.json` será baixado. **Renomeie este arquivo para `gcp-credentials.json`** e coloque-o na raiz deste projeto.
      - **Segurança:** Adicione `gcp-credentials.json` ao seu arquivo `.gitignore` para nunca cometer este segredo no repositório.

### 2\. Slack

1.  **Crie um App no Slack:** Vá para [api.slack.com/apps](https://api.slack.com/apps) e crie um novo aplicativo no seu workspace.
2.  **Ative Incoming Webhooks:** No menu do seu app, vá para `Incoming Webhooks` e ative-os.
3.  **Crie um Webhook:** Adicione um novo webhook, escolhendo o canal onde os alertas devem ser postados (ex: `#alertas-ia`).
4.  **Copie a URL do Webhook.** Ela se parecerá com `https://hooks.slack.com/services/...`.

### 3\. Arquivo de Ambiente (`.env`)

Na raiz do projeto, crie um arquivo chamado `.env` e preencha com as informações coletadas.

```
# .env

# Cole a URL do webhook do Slack aqui
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Cole o ID do seu projeto do Google Cloud aqui (ex: meu-projeto-12345)
GCP_PROJECT_ID=seu-id-de-projeto-aqui

# Região do Google Cloud para usar a API (us-east4 é uma boa opção)
GCP_REGION=us-east4
```

## 🚀 Executando o Projeto

Com todas as configurações no lugar, iniciar a stack é muito simples.

1.  Abra um terminal na raiz do projeto.
2.  Execute o comando:
    ```bash
    docker-compose up --build
    ```
3.  Aguarde enquanto o Docker baixa as imagens e constrói os containers.
4.  Após a inicialização, os seguintes serviços estarão disponíveis:
      - **Aplicação Demo:** `http://localhost:5000`
      - **Prometheus:** `http://localhost:9090`
      - **Alertmanager:** `http://localhost:9093`

## 🧪 Como Demonstrar

Para gerar os alertas, execute os seguintes comandos em um novo terminal.

**Para gerar um alerta de alta taxa de erros:**

```bash
# Gera 50 requests que resultarão em erro HTTP 500
hey -n 50 -c 10 http://localhost:5000/error
```

**Para gerar um alerta de alta latência:**

```bash
# Gera requests lentos
hey -n 20 -c 5 http://localhost:5000/slow
```

Após executar um dos comandos, observe o alerta aparecer primeiro no Prometheus (`Alerts`), depois no Alertmanager, e finalmente, a análise completa gerada pela IA chegará no seu canal do Slack\!

## ⚠️ Solução de Problemas

Durante o desenvolvimento, encontramos alguns erros comuns. Se algo der errado, verifique estes pontos:

  - **Alerta `PENDING` no Prometheus:** Se o alerta não passa para `FIRING`, verifique a cláusula `for` e a janela de tempo da `rate()` no arquivo `prometheus/alert.rules.yml`. Para demos, valores baixos (`for: 1s` e `rate([3m])`) funcionam melhor.
  - **Erro `404 model not found`:**
      - Verifique se o **faturamento** e as **APIs** (`Vertex AI` e `Generative Language`) estão ativos no seu projeto GCP.
      - Confirme se a **região** (`GCP_REGION`) no seu `.env` está correta.
      - **Crucial:** Verifique o nome do modelo no `gen-ai-bridge/bridge.py`. Descobrimos que o nome completo e versionado (`gemini-1.5-pro`) foi o que funcionou para o nosso projeto.
  - **Erro `401 Unauthorized` ou `CREDENTIALS_MISSING`:** Este erro indica que a autenticação via Chave de API não é aceita. A solução é usar uma **Service Account** com o arquivo JSON, conforme descrito no guia de configuração.
  - **Erro `403 SERVICE_DISABLED`:** Confirma que uma API específica (`Vertex AI` ou `Generative Language`) não está ativa no seu projeto. Use o link no erro para ativá-la.

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.