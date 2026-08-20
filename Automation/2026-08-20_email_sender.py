"""
This script provides a simple way to send emails using Python's smtplib and email modules.
It connects to an SMTP server, authenticates with user credentials, and sends an email
with a specified subject and body to a recipient.

It's designed to be beginner-friendly, showing basic email sending functionality.
For services like Gmail, users often need to generate an "App Password" if 2-Step
Verification is enabled, as using the regular account password directly might be blocked
for security reasons.
"""

import smtplib
import ssl
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, receiver_email, subject, body, smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Sends an email using the specified credentials and message details.

    Args:
        sender_email (str): The email address of the sender.
        sender_password (str): The password for the sender's email account.
                               For Gmail, this often needs to be an 'App Password'.
        receiver_email (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The main content of the email.
        smtp_server (str, optional): The SMTP server address. Defaults to "smtp.gmail.com".
        smtp_port (int, optional): The SMTP server port. Defaults to 587 (for STARTTLS).
    """
    
    # Create a MIMEText object to represent the email content.
    # This correctly formats the email headers and body.
    message = MIMEText(body)
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Create a default SSL context for secure connection.
    # This helps in establishing a secure (encrypted) connection with the SMTP server.
    context = ssl.create_default_context()

    try:
        # Connect to the SMTP server.
        # We use smtplib.SMTP for port 587, which typically uses STARTTLS.
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Secure the connection with TLS (Transport Layer Security).
            # This upgrades the connection to encrypted mode before authentication.
            server.starttls(context=context)
            
            # Log in to the email account using the provided credentials.
            server.login(sender_email, sender_password)
            
            # Send the email.
            # message.as_string() converts the MIMEText object into a format
            # that can be sent over the SMTP protocol.
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print(f"\nEmail successfully sent to {receiver_email}!")

    except smtplib.SMTPAuthenticationError:
        print("\nFailed to authenticate. Please check your email and password.")
        print("If using Gmail, you likely need an 'App Password' because Google has disabled 'Less secure app access'.")
        print("You can generate an App Password here: https://myaccount.google.com/apppasswords")
    except smtplib.SMTPServerDisconnected:
        print("\nFailed to connect to the SMTP server. Please check the server address and port.")
        print(f"Attempted to connect to: {smtp_server}:{smtp_port}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    print("--- Simple Email Sender Script ---")
    print("This script will help you send an email. You'll need your email credentials.")
    print("\nIMPORTANT NOTE FOR GMAIL USERS:")
    print("If you have 2-Step Verification enabled on your Gmail account (which is highly recommended),")
    print("you MUST use an 'App Password' instead of your regular Gmail password.")
    print("You can generate an App Password by visiting: https://myaccount.google.com/apppasswords")
    print("Google has deprecated 'Less secure app access', so App Passwords are the way to go.")
    print("-" * 40)
    
    # Prompt user for email details
    sender_email_input = input("Enter your sender email address (e.g., yourname@gmail.com): ").strip()
    sender_password_input = input("Enter your email password (or App Password for Gmail): ").strip()
    receiver_email_input = input("Enter the recipient's email address: ").strip()
    subject_input = input("Enter the email subject: ").strip()
    body_input = input("Enter the email body: ").strip()

    # Call the send_email function with user inputs
    send_email(
        sender_email_input,
        sender_password_input,
        receiver_email_input,
        subject_input,
        body_input
    )
