import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.app import settings
from src.config.celery_app import celery_app
from src.models import PasswordResetToken, User

sync_engine = create_engine(settings.sync_database_url)
SyncSessionLocal = sessionmaker(bind=sync_engine)


@celery_app.task
def send_welcome_email(user_id: str):
    """Send welcome email to new user"""
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            return f"User {user_id} not found"

        msg = MIMEMultipart()
        msg["From"] = settings.smtp_username
        msg["To"] = user.email
        msg["Subject"] = "Welcome to Our Platform!"

        body = f"""
        Hello {user.first_name or user.username}!

        Welcome to our platform! We're excited to have you on board.

        Best regards,
        The Team
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        return f"Welcome email sent to {user.email}"

    except Exception as e:
        return f"Error sending welcome email: {str(e)}"
    finally:
        db.close()


@celery_app.task
def send_password_reset_email(email: str):
    """Send password reset email"""
    db = SyncSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return f"User with email {email} not found"

        reset_token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)

        reset_token_record = PasswordResetToken(
            user_id=user.id, token=reset_token, expires_at=expires_at
        )

        db.add(reset_token_record)
        db.commit()

        msg = MIMEMultipart()
        msg["From"] = settings.smtp_username
        msg["To"] = user.email
        msg["Subject"] = "Password Reset Request"

        reset_link = f"http://localhost:8000/reset-password?token={reset_token}"

        body = f"""
        Hello {user.first_name or user.username}!

        You requested a password reset. Click the link below to reset your password:
        {reset_link}

        This link will expire in 1 hour.

        If you didn't request this, please ignore this email.

        Best regards,
        The Team
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        return f"Password reset email sent to {email}"

    except Exception as e:
        db.rollback()
        return f"Error sending password reset email: {str(e)}"
    finally:
        db.close()
