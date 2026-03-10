import dns.resolver

def dns_lookup(domain: str) -> str:
    """Queries detailed DNS records (A, AAAA, MX, TXT) for a specified domain name."""
    try:
        output = f"--- DNS RECORDS FOR {domain.upper()} ---\n\n"
        
        record_types = ['A', 'AAAA', 'MX', 'TXT']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                output += f"[{rtype} Records]\n"
                for rdata in answers:
                    output += f" - {rdata.to_text()}\n"
            except dns.resolver.NoAnswer:
                output += f"[{rtype} Records]\n - No records found.\n"
            except dns.resolver.NXDOMAIN:
                return f"Error: Domain '{domain}' does not exist (NXDOMAIN)."
            except Exception as e:
                output += f"[{rtype} Records]\n - Error: {e}\n"
                
            output += "\n"
        return output
        
    except Exception as e:
        return f"Total failure resolving DNS for {domain}: {str(e)}"
