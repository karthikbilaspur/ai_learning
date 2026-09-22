import os, json, boto3, requests

def k8s_restart(service):
    # In real, use EKS API via boto3
    print(f"Restarting {service}")
    # kubectl rollout restart deployment/{service}

def post_slack(msg):
    webhook = os.environ.get('SLACK_WEBHOOK')
    if webhook:
        requests.post(webhook, json={"text": msg})
    print(msg)

def handler(event, context):
    alarm = event.get('alarm', 'high-cpu')
    service = event.get('service', 'api')
    print(f"Alarm {alarm} for {service}")
    k8s_restart(service)
    post_slack(f":rotating_light: Auto-healed `{service}` due to `{alarm}`. Logs: {event}")
    return {"status": "healed"}
