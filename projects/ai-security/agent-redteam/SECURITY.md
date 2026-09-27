
# Security Policy

## Reporting a Vulnerability
This is an educational lab. If you find a real vulnerability in the *secure* agent, please open an issue.

## What's Intentionally Vulnerable
`src/vulnerable_agent.py` is intentionally vulnerable to demonstrate:
- OWASP LLM01 - Prompt Injection
- OWASP LLM02 - Insecure Output Handling
- OWASP LLM06 - Sensitive Information Disclosure

Do NOT deploy vulnerable_agent.py.

## Safe Usage
- Only run locally
- Never commit `.env`
- Use `.env.example` as template
