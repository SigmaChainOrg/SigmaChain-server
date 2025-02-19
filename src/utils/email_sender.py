import resend
from decouple import config

resend.api_key = config("RESEND_API_KEY")

email_from = config("EMAIL_FROM")


def send_html_email(to: str, subject: str, html: str) -> bool:
    params: resend.Emails.SendParams = {
        "from": f"SigmaChain Info <{email_from}>",
        "to": to,
        "subject": subject,
        "html": html,
    }

    email = resend.Emails.send(params)

    if email is None:
        return False

    return True
