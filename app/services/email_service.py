from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import (
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)
from app.core.logger import logger


def build_updates_email(updates: list[dict]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Radar Processual | Atualizações detectadas: {len(updates)}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    lines: list[str] = []
    lines.append("Atualizações detectadas pelo Radar Processual")
    lines.append("")

    for item in updates:
        lines.append(f"Processo: {item['numero_processo']}")
        lines.append(f"Tribunal: {item['tribunal']}")
        lines.append(f"Tribunal alias: {item['tribunal_alias']}")
        lines.append(f"Última atualização anterior: {item['ultima_atualizacao_antiga']}")
        lines.append(f"Última atualização nova: {item['ultima_atualizacao_nova']}")
        lines.append(f"Último movimento anterior: {item['ultimo_movimento_antigo']}")
        lines.append(f"Último movimento novo: {item['ultimo_movimento_novo']}")
        lines.append(f"Checado em: {item['checked_at']}")
        lines.append("-" * 60)

    msg.set_content("\n".join(lines))
    return msg


def send_email_message(message: EmailMessage) -> None:
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]):
        raise ValueError("Configuração de email incompleta no .env")

    logger.info("Enviando email | para=%s assunto=%s", EMAIL_TO, message["Subject"])

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)

    logger.info("Email enviado com sucesso | para=%s", EMAIL_TO)


def send_updates_email(updates: list[dict]) -> None:
    if not updates:
        logger.info("Nenhuma atualização para enviar por email")
        return

    msg = build_updates_email(updates)
    send_email_message(msg)

def send_test_email() -> None:
    msg = EmailMessage()
    msg["Subject"] = "Radar Processual | Teste de email"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.set_content("Este é um email de teste enviado pelo Radar Processual.")

    send_email_message(msg)