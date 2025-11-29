import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def debug_smtp():
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    
    print("=== DEBUG SMTP ===")
    print(f"Email: '{SMTP_USER}'")
    print(f"Password: '{SMTP_PASS}'")
    print(f"Password length: {len(SMTP_PASS)}")
    print(f"Password chars: {[ord(c) for c in SMTP_PASS]}")
    
    try:
        # Cách 1: Port 587 với STARTTLS
        print("\nTrying port 587...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        print("✅ SUCCESS with port 587!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Failed port 587: {e}")
        
        try:
            # Cách 2: Port 465 với SSL
            print("\nTrying port 465...")
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            server.login(SMTP_USER, SMTP_PASS)
            print("✅ SUCCESS with port 465!")
            server.quit()
            return True
        except Exception as e2:
            print(f"❌ Failed port 465: {e2}")
            return False

debug_smtp()