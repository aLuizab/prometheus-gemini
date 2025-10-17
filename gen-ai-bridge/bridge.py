# gen-ai-bridge/bridge.py
from flask import Flask, request, jsonify
import os
import requests
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# --- Configuração ---
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")  # Padrão para us-central1 se não for definido

if not SLACK_WEBHOOK_URL or not GCP_PROJECT_ID:
    raise ValueError("As variáveis de ambiente SLACK_WEBHOOK_URL e GCP_PROJECT_ID devem ser definidas.")

# Inicializa o cliente do Vertex AI. Ele usa a autenticação do Service Account automaticamente.
vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)

# Carrega o modelo
model = GenerativeModel("gemini-2.5-pro")


def generate_analysis(alert_data):
    """Monta o prompt e chama a API da Gen AI usando a SDK do Vertex AI."""

    alert_name = alert_data['labels'].get('alertname', 'N/A')
    summary = alert_data['annotations'].get('summary', 'N/A')
    description = alert_data['annotations'].get('description', 'N/A')
    severity = alert_data['labels'].get('severity', 'N/A')

    prompt = f"""
    Você é um Engenheiro de Confiabilidade de Site (SRE) Sênior e especialista em observabilidade. 
    Você recebeu o seguinte alerta do Prometheus. Sua tarefa é analisá-lo e fornecer um resumo claro e acionável para a equipe de plantão em um canal do Slack.

    **Dados do Alerta:**
    - **Nome do Alerta:** {alert_name}
    - **Severidade:** {severity}
    - **Sumário:** {summary}
    - **Descrição:** {description}
    - **Dados brutos (JSON):** ```json\n{request.get_json(silent=True)}\n```

    **Seu Relatório (formate para o Slack usando mrkdwn):**

    1.  ***:rotating_light: O que Aconteceu?***
        Explique o problema em uma ou duas frases simples.

    2.  ***:mag: Análise e Possíveis Causas:***
        Com base nos dados do alerta, liste 2 a 3 possíveis causas raiz.

    3.  ***:wrench: Próximos Passos Sugeridos:***
        Forneça uma lista de 3 passos acionáveis para investigar e mitigar o problema.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao contatar a API do Vertex AI: {e}"


def send_to_slack(message):
    """Envia a mensagem formatada para o Slack."""
    payload = {
        "text": "Análise Inteligente de Alerta Recebida!",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": message}},
            {"type": "divider"},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Analisado por VertexAI-Prometheus Alerter"}]}
        ]
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload)


@app.route('/webhook', methods=['POST'])
def alert_webhook():
    data = request.json
    print("Webhook recebido:", data)

    if data['status'] == 'firing':
        for alert in data['alerts']:
            analysis = generate_analysis(alert)
            send_to_slack(analysis)

    return jsonify(status="success"), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)