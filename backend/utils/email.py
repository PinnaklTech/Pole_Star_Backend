"""Email service for sending password reset emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)

async def send_password_reset_email(to_email: str, reset_token: str, user_name: str):
    """Send password reset email to user."""
    try:
        # Create reset link
        reset_link = f"{settings.app_url}/reset-password?token={reset_token}"
        
        # Email content
        subject = "Password Reset Request - Pole Wizard Forge"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                           padding: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>We received a request to reset your password for your Pole Wizard Forge account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </center>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong><br>
                        This link will expire in 15 minutes. If you didn't request a password reset, 
                        please ignore this email or contact support if you have concerns.
                    </div>
                    
                    <p>Best regards,<br>
                    <strong>Pole Wizard Forge Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2025 Pole Wizard Forge. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hi {user_name},
        
        We received a request to reset your password for your Pole Wizard Forge account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 15 minutes.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        Pole Wizard Forge Team
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.email_from
        message["To"] = to_email
        
        # Attach both text and HTML versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        if settings.email_user and settings.email_password:
            with smtplib.SMTP(settings.email_host, settings.email_port) as server:
                server.starttls()
                server.login(settings.email_user, settings.email_password)
                server.send_message(message)
            
            logger.info(f"Password reset email sent to {to_email}")
        else:
            # Log the reset link for development (when email is not configured)
            logger.warning(f"Email not configured. Password reset link: {reset_link}")
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False

async def send_welcome_email(to_email: str, user_name: str):
    """Send welcome email to new user."""
    try:
        subject = "Welcome to Pole Wizard Forge!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                          color: white; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Pole Wizard Forge!</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Thank you for joining Pole Wizard Forge! We're excited to have you on board.</p>
                    
                    <p>You can now start designing steel transmission poles with our powerful engineering tools.</p>
                    
                    <center>
                        <a href="{settings.app_url}" class="button">Get Started</a>
                    </center>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>Pole Wizard Forge Team</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Pole Wizard Forge. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Pole Wizard Forge!
        
        Hi {user_name},
        
        Thank you for joining Pole Wizard Forge! We're excited to have you on board.
        
        You can now start designing steel transmission poles with our powerful engineering tools.
        
        Visit: {settings.app_url}
        
        Best regards,
        Pole Wizard Forge Team
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.email_from
        message["To"] = to_email
        
        # Attach both text and HTML versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        if settings.email_user and settings.email_password:
            with smtplib.SMTP(settings.email_host, settings.email_port) as server:
                server.starttls()
                server.login(settings.email_user, settings.email_password)
                server.send_message(message)
            
            logger.info(f"Welcome email sent to {to_email}")
        else:
            logger.warning("Email not configured. Skipping welcome email.")
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False

