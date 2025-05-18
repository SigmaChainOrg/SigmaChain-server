from pathlib import Path
from uuid import UUID

from decouple import config

from src.utils.email_sender import send_html_email
from src.utils.template_loader import load_html_template

VALIDATION_CODE_URL: str = (
    str(
        config(
            "VALIDATION_CODE_URL",
            default="http://localhost:3000/validate_code/{code_id}",
        )
    )
    + "/{code_id}"
)


def send_secure_code_email(email: str, code: str, code_id: UUID) -> bool:
    template_path = Path("templates/secure_code_email.html")

    html = load_html_template(
        str(template_path),
        secure_code=code,
        link=VALIDATION_CODE_URL.format(code_id=str(code_id)),
    )

    email_sent = send_html_email(
        to=email,
        subject="Secure code for SigmaChain",
        html=html,
    )

    return email_sent
    return email_sent
    return email_sent
