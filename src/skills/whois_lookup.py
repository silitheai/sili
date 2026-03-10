import whois

def whois_lookup(domain: str) -> str:
    """Performs a WHOIS record lookup for a given domain name."""
    try:
        domain_info = whois.whois(domain)
        
        # Extract the most meaningful clean text
        result = []
        result.append(f"WHOIS Result for: {domain}")
        result.append("-" * 30)
        
        if domain_info.registrar:
            result.append(f"Registrar: {domain_info.registrar}")
            
        if domain_info.creation_date:
            dates = domain_info.creation_date
            if isinstance(dates, list): dates = dates[0]
            result.append(f"Created On: {dates}")
            
        if domain_info.expiration_date:
            dates = domain_info.expiration_date
            if isinstance(dates, list): dates = dates[0]
            result.append(f"Expires On: {dates}")
            
        if domain_info.name_servers:
            result.append(f"Name Servers: {', '.join(domain_info.name_servers)}")
            
        if domain_info.org:
             result.append(f"Organization: {domain_info.org}")
            
        return "\n".join(result)
        
    except Exception as e:
        return f"Error performing WHOIS lookup on {domain}: {str(e)}"
