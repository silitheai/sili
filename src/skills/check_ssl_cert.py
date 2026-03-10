import ssl
import socket
from datetime import datetime

def check_ssl_cert(domain: str) -> str:
    """Connects to a given HTTPS domain, extracts its SSL/TLS certificate, and checks its validity and expiration date."""
    try:
        # Strip protocol if present
        if "://" in domain:
            domain = domain.split("://")[1].split("/")[0]
            
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        # Extract meaningful data
        subject = dict(x[0] for x in cert['subject'])
        issuer = dict(x[0] for x in cert['issuer'])
        
        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        
        days_remaining = (not_after - datetime.now()).days
        
        output = f"--- SSL CERTIFICATE INFO FOR {domain} ---\n"
        output += f"Issued To: {subject.get('commonName', 'Unknown')}\n"
        output += f"Issued By: {issuer.get('organizationName', 'Unknown')} ({issuer.get('commonName', 'Unknown')})\n"
        output += f"Valid From: {not_before}\n"
        output += f"Expires On: {not_after}\n"
        
        if days_remaining < 0:
            output += f"\n🚨 WARNING: CERTIFICATE EXPIRED {abs(days_remaining)} DAYS AGO!\n"
        elif days_remaining < 30:
             output += f"\n⚠️ CAUTION: Certificate expires very soon ({days_remaining} days remaining).\n"
        else:
             output += f"\n✅ Status: Valid ({days_remaining} days remaining).\n"
             
        return output
    except ssl.SSLCertVerificationError as e:
         return f"SSL Verification Failed for {domain}: The certificate is invalid or untrusted.\nDetails: {e}"
    except Exception as e:
        return f"Error retrieving SSL certificate for {domain}: {str(e)}"
