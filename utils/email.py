"""Email service for sending password reset emails."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

def _send_smtp_email(message, host: str, port: int, user: str, password: str):
    """Helper function to send email synchronously (run in executor)."""
    # Use SSL for port 465, STARTTLS for port 587
    if port == 465:
        # SSL connection
        server = smtplib.SMTP_SSL(host, port, timeout=30)
        server.login(user, password)
        server.send_message(message)
        server.quit()
    else:
        # STARTTLS connection (default for 587, 25, etc.)
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls()
        server.login(user, password)
        server.send_message(message)
        server.quit()

async def send_password_reset_email(to_email: str, reset_code: str = None, reset_token: str = None, user_name: str = None):
    """Send password reset email to user.
    
    All email configuration is loaded from .env file:
    - EMAIL_HOST: SMTP server hostname
    - EMAIL_PORT: SMTP server port (465 for SSL, 587 for STARTTLS)
    - EMAIL_USER: SMTP username (email address)
    - EMAIL_PASSWORD: SMTP password
    - EMAIL_FROM: From address shown in emails
    - APP_URL: Base URL for reset links
    
    Args:
        to_email: Recipient email address
        reset_code: 6-digit security code (new method)
        reset_token: Reset token (legacy method, optional)
        user_name: User's name
    """
    try:
        # Initialize variables
        email_subject = "Password Reset Request - Pole Star"
        reset_link = None  # Initialize to avoid reference errors
        
        # Use reset code if provided, otherwise fall back to token (for backward compatibility)
        if reset_code:
            # New 6-digit code method
            logger.info(f"Generating password reset email with code: {reset_code} for {to_email}")
            email_subject = "Password Reset Code - Pole Star"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #004733; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #2B6A4D 0%, #004733 100%); 
                              color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                    .content {{ background: #E8F0EB; padding: 30px; border-radius: 0 0 5px 5px; }}
                    .code-box {{ background: white; border: 3px solid #2B6A4D; border-radius: 10px; 
                               padding: 20px; text-align: center; margin: 30px 0; 
                               user-select: all; -webkit-user-select: all; }}
                    .code {{ font-size: 36px; font-weight: bold; color: #2B6A4D; letter-spacing: 4px; 
                           font-family: 'Courier New', monospace; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #DF8080; 
                               padding: 10px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Code</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_name or 'User'},</p>
                        
                        <p>We received a request to reset your password for your Pole Star account.</p>
                        
                        <p>Use this security code to reset your password:</p>
                        
                        <div class="code-box">
                            <div class="code">{reset_code}</div>
                        </div>
                        
                        <p style="text-align: center; font-weight: bold;">Enter this code on the password reset page to continue.</p>
                        
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong><br>
                            This code will expire in 15 minutes. If you didn't request a password reset, 
                            please ignore this email or contact support if you have concerns.
                        </div>
                        
                        <p>Best regards,<br>
                        <strong>Pole Star by PinnaklTech</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message, please do not reply to this email.</p>
                        <p>&copy; 2025 Pole Star by PinnaklTech. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Password Reset Code
            
            Hi {user_name or 'User'},
            
            We received a request to reset your password for your Pole Star account.
            
            Your security code is: {reset_code}
            
            Enter this code on the password reset page to continue.
            
            This code will expire in 15 minutes.
            
            If you didn't request a password reset, please ignore this email.
            
            Best regards,
            Pole Star by PinnaklTech
            """
        else:
            # Legacy token method (for backward compatibility)
            reset_link = f"{settings.app_url}/reset-password?token={reset_token}"
            # email_subject already set above
            
            html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #004733; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2B6A4D 0%, #004733 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #E8F0EB; padding: 30px; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #2B6A4D; 
                          color: white; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: #004733; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #DF8080; 
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
                    
                    <p>We received a request to reset your password for your Pole Star account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </center>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #2B6A4D;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong><br>
                        This link will expire in 15 minutes. If you didn't request a password reset, 
                        please ignore this email or contact support if you have concerns.
                    </div>
                    
                    <p>Best regards,<br>
                    <strong>Pole Star by PinnaklTech</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                    <p>&copy; 2025 Pole Star by PinnaklTech. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hi {user_name},
        
        We received a request to reset your password for your Pole Star account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 15 minutes.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        Pole Star by PinnaklTech
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = email_subject
        message["From"] = settings.email_from
        message["To"] = to_email
        
        # Attach both text and HTML versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email using thread pool to avoid blocking
        # All email credentials are loaded from .env file via settings
        if not settings.email_user or not settings.email_password:
            # Email not configured - log warning and return False
            if reset_code:
                logger.error(f"Email not configured. Password reset code: {reset_code}")
            elif reset_token:
                reset_link = f"{settings.app_url}/reset-password?token={reset_token}"
                logger.error(f"Email not configured. Password reset link: {reset_link}")
            logger.error("Set EMAIL_USER and EMAIL_PASSWORD in your .env file")
            return False
        
        try:
            logger.info(f"Sending password reset email via {settings.email_host}:{settings.email_port} as {settings.email_user} to {to_email}")
            
            # Use get_running_loop() for Python 3.7+, fallback to get_event_loop()
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            
            await loop.run_in_executor(
                None,
                _send_smtp_email,
                message,
                settings.email_host,      # From .env: EMAIL_HOST
                settings.email_port,       # From .env: EMAIL_PORT
                settings.email_user,       # From .env: EMAIL_USER
                settings.email_password    # From .env: EMAIL_PASSWORD
            )
            logger.info(f"Password reset email successfully sent to {to_email}")
            return True
        except smtplib.SMTPAuthenticationError as auth_error:
            logger.error(f"SMTP Authentication failed: {auth_error}")
            logger.error("Check EMAIL_USER and EMAIL_PASSWORD in your .env file")
            raise
        except smtplib.SMTPConnectError as conn_error:
            logger.error(f"SMTP Connection failed: {conn_error}")
            logger.error(f"Check EMAIL_HOST ({settings.email_host}) and EMAIL_PORT ({settings.email_port})")
            raise
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP Error: {smtp_error}")
            raise
        except Exception as smtp_error:
            logger.error(f"Failed to send password reset email via SMTP: {smtp_error}", exc_info=True)
            raise  # Re-raise to be caught by outer try-except
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        return False

async def send_welcome_email(to_email: str, user_name: str):
    """Send welcome email to new user."""
    try:
        subject = "Welcome to Pole Star!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #004733; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2B6A4D 0%, #004733 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #E8F0EB; padding: 30px; border-radius: 0 0 5px 5px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Pole Star!</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Thank you for joining Pole Star! We're excited to have you on board.</p>
                    
                    <p>You can now start designing steel transmission poles with our powerful engineering tools.</p>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>Pole Star by PinnaklTech</strong></p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Pole Star by PinnaklTech. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to Pole Star!
        
        Hi {user_name},
        
        Thank you for joining Pole Star! We're excited to have you on board.
        
        You can now start designing steel transmission poles with our powerful engineering tools.
        
        Visit: {settings.app_url}
        
        Best regards,
        Pole Star by PinnaklTech
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
        
        # Send email using thread pool to avoid blocking
        if settings.email_user and settings.email_password:
            try:
                # Use get_running_loop() for Python 3.7+, fallback to get_event_loop()
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    _send_smtp_email,
                    message,
                    settings.email_host,
                    settings.email_port,
                    settings.email_user,
                    settings.email_password
                )
                logger.info(f"Welcome email sent to {to_email}")
            except Exception as smtp_error:
                logger.error(f"Failed to send welcome email via SMTP: {smtp_error}")
                raise  # Re-raise to be caught by outer try-except
        else:
            logger.warning("Email not configured. Skipping welcome email.")
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        return False

