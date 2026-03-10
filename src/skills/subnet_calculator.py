import ipaddress

def subnet_calculator(cidr_network: str) -> str:
    """Calculates granular IP address range, netmask, and broadcast data for a given IPv4 CIDR block (e.g. 192.168.1.0/24)."""
    try:
        network = ipaddress.IPv4Network(cidr_network, strict=False)
        
        output = f"--- SUBNET CALCULATION for {cidr_network} ---\n"
        output += f"Network Address: {network.network_address}\n"
        output += f"Broadcast Address: {network.broadcast_address}\n"
        output += f"Netmask / Subnet Mask: {network.netmask}\n"
        output += f"Number of Hosts Available: {network.num_addresses - 2} (excluding net/broadcast addresses)\n"
        output += f"Total IPs in Range: {network.num_addresses}\n"
        output += f"Host Range (Usable IPs): {network.network_address + 1} - {network.broadcast_address - 1}\n"
        
        return output
    except ValueError as e:
        return f"Invalid IP/CIDR Subnet format: {e}"
    except Exception as e:
        return f"Error calculating subnet boundaries: {str(e)}"
