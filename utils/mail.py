# from flask_mail import Mail
# from flask import app
# from itsdangerous import URLSafeTimedSerializer
# import smtplib
# from email.mime.text import MIMEText

# mail = Mail()

# def init_mail(app):
#     """Initialize mail extension with the Flask app"""
#     mail.init_app(app)

# def send_reset_email(recipient_email, reset_link, user_name):
#     """Send password reset email"""
#     subject = "Password Reset Request"
#     sender = app.config['MAIL_DEFAULT_SENDER']
    
#     # HTML email template
#     html = f"""
#     <html>
#         <body>
#             <p>Hello {user_name},</p>
#             <p>You requested to reset your password. Click the link below to proceed:</p>
#             <p><a href="{reset_link}">Reset Password</a></p>
#             <p>This link will expire in 30 minutes.</p>
#             <p>If you didn't request this, please ignore this email.</p>
#         </body>
#     </html>
#     """
    
#     try:
#         msg = Message(
#             subject=subject,
#             recipients=[recipient_email],
#             html=html,
#             sender=sender
#         )
#         mail.send(msg)
#         return True
#     except smtplib.SMTPException as e:
#         app.logger.error(f"Failed to send email: {str(e)}")
#         return False

# def generate_reset_token(email):
#     """Generate a secure reset token"""
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

# def verify_reset_token(token, expiration=1800):
#     """Verify the reset token"""
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     try:
#         email = serializer.loads(
#             token,
#             salt=app.config['SECURITY_PASSWORD_SALT'],
#             max_age=expiration
#         )
#         return email
#     except Exception:
#         return None