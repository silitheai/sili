from urllib.parse import urlparse
import socket

def port_scanner(target_ip: str, start_port: int = 1, end_port: int = 1024) -> str:
    """Scans a target IP address for open TCP ports within the specified range."""
    # Basic validation
    try:
        if "://" in target_ip:
            target_ip = urlparse(target_ip).hostname
        socket.inet_aton(target_ip)
    except Exception:
        # Try resolving host to IP if it's a domain
        try:
            target_ip = socket.gethostbyname(target_ip)
        except Exception as e:
            return f"Error: Invalid IP or Domain - {e}"

    if end_port - start_port > 2000:
        return "Error: Maximum port scan range is 2000 ports per request for safety/speed."

    open_ports = []
    
    # Extremely fast connect scanner
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1) # 100ms timeout
        
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
        
    if not open_ports:
        return f"Scan complete. No open ports found on {target_ip} between {start_port}-{end_port}."
        
    return f"Scan complete for {target_ip}. Open Ports Found: {', '.join(map(str, open_ports))}"
