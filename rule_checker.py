"""
rule_checker.py
==============================================================================
NetSage AI - Deterministic Networking Rule Checker
==============================================================================
Performs strict, non-AI deterministic networking rule checks using Python's
standard `ipaddress` library and regex pattern parsing.

Covers all 15 required networking verification rules:
 1. Invalid IP address
 2. Invalid subnet mask
 3. IP/subnet mismatch (network or broadcast address assigned as host)
 4. Gateway outside local subnet
 5. Duplicate IP address / ARP collision
 6. Missing default gateway
 7. DHCP/APIPA address (169.254.x.x)
 8. DNS configuration problems / resolution failure
 9. VLAN mismatch / inactive access VLAN
10. Trunk configuration problems (Native VLAN mismatch / allowed VLAN filtering)
11. Missing route in routing table
12. Default route problems (Gateway of last resort not set)
13. ACL deny statements / packet drop counters
14. NAT configuration / interface inside-outside missing
15. Interface administratively shutdown / err-disabled / down state
"""

import ipaddress
import re
from typing import Any, Dict, List, Optional


def check_valid_ip(ip_str: Optional[str]) -> Dict[str, Any]:
    """1. Validate IPv4 address format."""
    if not ip_str or not str(ip_str).strip():
        return {
            "check": "valid_ip",
            "status": "FAIL",
            "message": "IP address is missing or empty.",
            "evidence": f"Provided IP: '{ip_str}'",
        }
    cleaned = str(ip_str).strip()
    try:
        addr = ipaddress.IPv4Address(cleaned)
        if addr.is_unspecified:
            return {
                "check": "valid_ip",
                "status": "WARNING",
                "message": "IP address is 0.0.0.0 (unspecified).",
                "evidence": f"{cleaned} is not a routable host address.",
            }
        return {
            "check": "valid_ip",
            "status": "PASS",
            "message": f"IP address {cleaned} is a valid IPv4 address.",
            "evidence": f"{cleaned} parsed successfully.",
        }
    except ValueError as e:
        return {
            "check": "valid_ip",
            "status": "FAIL",
            "message": f"Invalid IPv4 address format: {e}",
            "evidence": f"Provided IP '{cleaned}' is not valid IPv4.",
        }


def check_valid_subnet_mask(mask_str: Optional[str]) -> Dict[str, Any]:
    """2. Validate IPv4 subnet mask format and contiguity."""
    if not mask_str or not str(mask_str).strip():
        return {
            "check": "valid_subnet_mask",
            "status": "FAIL",
            "message": "Subnet mask is missing or empty.",
            "evidence": f"Provided Mask: '{mask_str}'",
        }
    cleaned = str(mask_str).strip()
    # Support CIDR prefix like /24 or dotted decimal 255.255.255.0
    if cleaned.startswith("/"):
        try:
            prefix = int(cleaned.lstrip("/"))
            if 0 <= prefix <= 32:
                return {
                    "check": "valid_subnet_mask",
                    "status": "PASS",
                    "message": f"CIDR prefix {cleaned} is valid.",
                    "evidence": f"Prefix length {prefix} bits.",
                }
            return {
                "check": "valid_subnet_mask",
                "status": "FAIL",
                "message": f"Prefix length {prefix} out of bounds (0-32).",
                "evidence": cleaned,
            }
        except ValueError:
            return {
                "check": "valid_subnet_mask",
                "status": "FAIL",
                "message": f"Invalid CIDR prefix: {cleaned}",
                "evidence": cleaned,
            }

    try:
        # Create a dummy network with the mask to check validity & bit contiguity
        net = ipaddress.IPv4Network(f"0.0.0.0/{cleaned}", strict=False)
        return {
            "check": "valid_subnet_mask",
            "status": "PASS",
            "message": f"Subnet mask {cleaned} is valid (/{net.prefixlen}).",
            "evidence": f"Netmask {cleaned} corresponds to /{net.prefixlen}.",
        }
    except ValueError as e:
        return {
            "check": "valid_subnet_mask",
            "status": "FAIL",
            "message": f"Invalid subnet mask (non-contiguous or invalid octets): {e}",
            "evidence": f"Mask '{cleaned}' is not a valid IPv4 netmask.",
        }


def check_ip_subnet_alignment(ip_str: str, mask_str: str) -> Dict[str, Any]:
    """3. Check if host IP equals the network ID or broadcast address."""
    try:
        net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
        addr = ipaddress.IPv4Address(ip_str)
        if addr == net.network_address:
            return {
                "check": "ip_subnet_alignment",
                "status": "FAIL",
                "message": f"Host IP {ip_str} cannot be the Subnet Network Address.",
                "evidence": f"{ip_str} is the network address for {net}.",
            }
        if addr == net.broadcast_address:
            return {
                "check": "ip_subnet_alignment",
                "status": "FAIL",
                "message": f"Host IP {ip_str} cannot be the Subnet Broadcast Address.",
                "evidence": f"{ip_str} is the directed broadcast address for {net}.",
            }
        return {
            "check": "ip_subnet_alignment",
            "status": "PASS",
            "message": f"Host IP {ip_str} is a valid usable address in {net}.",
            "evidence": f"{ip_str} is within usable host range for {net}.",
        }
    except ValueError as e:
        return {
            "check": "ip_subnet_alignment",
            "status": "FAIL",
            "message": f"Could not evaluate IP/mask alignment: {e}",
            "evidence": f"IP: {ip_str}, Mask: {mask_str}",
        }


def check_gateway_in_subnet(ip_str: str, mask_str: str, gateway_str: Optional[str]) -> Dict[str, Any]:
    """4. Check if the default gateway is within the host's subnet."""
    if not gateway_str or gateway_str.strip() in ["0.0.0.0", "None", ""]:
        return {
            "check": "gateway_mismatch",
            "status": "FAIL",
            "message": "Default gateway is missing or unassigned (0.0.0.0).",
            "evidence": f"Gateway value: '{gateway_str}'",
        }
    gw = gateway_str.strip()
    try:
        net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
        gw_addr = ipaddress.IPv4Address(gw)
        host_addr = ipaddress.IPv4Address(ip_str)

        if gw_addr == host_addr:
            return {
                "check": "gateway_mismatch",
                "status": "FAIL",
                "message": "Default gateway IP is identical to the host IP (loopback conflict).",
                "evidence": f"Host IP: {ip_str}, Gateway IP: {gw}",
            }

        if gw_addr not in net:
            return {
                "check": "gateway_mismatch",
                "status": "FAIL",
                "message": "Default gateway is outside the host subnet.",
                "evidence": f"{gw} is not in {net}",
            }

        return {
            "check": "gateway_mismatch",
            "status": "PASS",
            "message": "Default gateway belongs to the same subnet as the host.",
            "evidence": f"{gw} is in local subnet {net}.",
        }
    except ValueError as e:
        return {
            "check": "gateway_mismatch",
            "status": "FAIL",
            "message": f"Invalid IP/Gateway address: {e}",
            "evidence": f"Host: {ip_str}, Mask: {mask_str}, Gateway: {gw}",
        }


def check_duplicate_ip(text_evidence: str) -> Dict[str, Any]:
    """5. Detect duplicate IP address alerts or ARP collisions."""
    patterns = [
        r"%IP-4-DUPADDR.*Duplicate address\s+(\d+\.\d+\.\d+\.\d+)",
        r"IP address conflict detected",
        r"invalid \(conflict\)",
        r"%SW_MATM-4-MACFLAP_NOTIF.*flapping between",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_evidence, re.IGNORECASE)
        if match:
            return {
                "check": "duplicate_ip",
                "status": "FAIL",
                "message": "Duplicate IP address conflict or ARP MAC flapping detected.",
                "evidence": match.group(0).strip(),
            }
    return {
        "check": "duplicate_ip",
        "status": "PASS",
        "message": "No duplicate IP or ARP MAC flapping conflicts detected in evidence.",
        "evidence": "ARP and syslog show normal unique mappings.",
    }


def check_missing_gateway(gateway_str: Optional[str]) -> Dict[str, Any]:
    """6. Check for missing default gateway."""
    if not gateway_str or str(gateway_str).strip() in ["", "0.0.0.0", "None"]:
        return {
            "check": "missing_gateway",
            "status": "FAIL",
            "message": "Default gateway is missing or set to 0.0.0.0.",
            "evidence": f"Gateway: '{gateway_str}'",
        }
    return {
        "check": "missing_gateway",
        "status": "PASS",
        "message": f"Default gateway is specified as {gateway_str}.",
        "evidence": f"Gateway: {gateway_str}",
    }


def check_apipa_address(ip_str: Optional[str]) -> Dict[str, Any]:
    """7. Detect APIPA (169.254.x.x) address indicating DHCP lease failure."""
    if not ip_str:
        return {
            "check": "apipa_check",
            "status": "WARNING",
            "message": "No IP address provided to check for APIPA.",
            "evidence": "Empty IP",
        }
    try:
        addr = ipaddress.IPv4Address(ip_str.strip())
        apipa_net = ipaddress.IPv4Network("169.254.0.0/16")
        if addr in apipa_net:
            return {
                "check": "apipa_check",
                "status": "FAIL",
                "message": "Client has received an APIPA (Automatic Private IP Addressing) address, indicating DHCP failure.",
                "evidence": f"{ip_str} belongs to link-local block 169.254.0.0/16.",
            }
        return {
            "check": "apipa_check",
            "status": "PASS",
            "message": f"IP address {ip_str} is not an APIPA address.",
            "evidence": f"{ip_str} is outside 169.254.0.0/16.",
        }
    except ValueError:
        return {
            "check": "apipa_check",
            "status": "FAIL",
            "message": f"Invalid IP address format: {ip_str}",
            "evidence": str(ip_str),
        }


def check_dns_configuration(dns_str: Optional[str], show_output: str) -> Dict[str, Any]:
    """8. Detect DNS configuration problems or resolution failures."""
    evidence_items = []
    # Check DNS IP format if given
    if dns_str:
        cleaned_dns = dns_str.strip()
        try:
            addr = ipaddress.IPv4Address(cleaned_dns)
            if addr.is_unspecified:
                return {
                    "check": "dns_configuration",
                    "status": "FAIL",
                    "message": "DNS server IP is 0.0.0.0 (unconfigured).",
                    "evidence": f"DNS Server: {cleaned_dns}",
                }
        except ValueError:
            evidence_items.append(f"Invalid DNS IP format: {cleaned_dns}")

    # Check for DNS service OFF or DNS timeouts in show_output
    if re.search(r"DNS Service:\s*OFF", show_output, re.IGNORECASE):
        return {
            "check": "dns_configuration",
            "status": "FAIL",
            "message": "Packet Tracer Server DNS service is turned OFF.",
            "evidence": "Found 'DNS Service: OFF' in service output.",
        }

    if re.search(r"DNS request timed out", show_output, re.IGNORECASE):
        return {
            "check": "dns_configuration",
            "status": "FAIL",
            "message": "DNS query request timed out, server is unreachable or unresponsive.",
            "evidence": "nslookup shows 'DNS request timed out.'",
        }

    if re.search(r"Non-existent domain|NXDOMAIN", show_output, re.IGNORECASE):
        return {
            "check": "dns_configuration",
            "status": "FAIL",
            "message": "DNS server returned NXDOMAIN (missing A record).",
            "evidence": "nslookup returned 'Non-existent domain (NXDOMAIN)'",
        }

    if evidence_items:
        return {
            "check": "dns_configuration",
            "status": "FAIL",
            "message": "DNS configuration error detected.",
            "evidence": "; ".join(evidence_items),
        }

    return {
        "check": "dns_configuration",
        "status": "PASS",
        "message": "DNS configuration and query responses appear normal.",
        "evidence": "No DNS timeouts or service interruptions detected.",
    }


def check_vlan_assignment(show_output: str) -> Dict[str, Any]:
    """9. Detect inactive VLANs or improper access VLAN configurations."""
    if re.search(r"Access Mode VLAN:\s*\d+\s*\(\(Inactive\)\)", show_output, re.IGNORECASE):
        match = re.search(r"Access Mode VLAN:\s*(\d+)\s*\(\(Inactive\)\)", show_output)
        vlan_id = match.group(1) if match else "Unknown"
        return {
            "check": "vlan_assignment",
            "status": "FAIL",
            "message": f"Access switchport is assigned to inactive VLAN {vlan_id} (missing in VLAN database).",
            "evidence": f"Found 'Access Mode VLAN: {vlan_id} ((Inactive))'.",
        }

    if re.search(r"encapsulation dot1Q\s+(\d+)", show_output, re.IGNORECASE):
        match = re.search(r"interface\s+(\S+)\.(\d+).*?encapsulation dot1Q\s+(\d+)", show_output, re.DOTALL | re.IGNORECASE)
        if match:
            subif, sub_vlan, dot1q_vlan = match.group(1), match.group(2), match.group(3)
            if sub_vlan != dot1q_vlan:
                return {
                    "check": "vlan_assignment",
                    "status": "FAIL",
                    "message": f"Subinterface {subif}.{sub_vlan} encapsulation dot1Q tag ({dot1q_vlan}) does not match subinterface number.",
                    "evidence": f"Subinterface {sub_vlan} configured with dot1Q {dot1q_vlan}.",
                }

    return {
        "check": "vlan_assignment",
        "status": "PASS",
        "message": "VLAN memberships and subinterface tags appear consistent.",
        "evidence": "No inactive VLANs or mismatched dot1Q tags detected.",
    }


def check_trunk_configuration(show_output: str) -> Dict[str, Any]:
    """10. Check for Native VLAN mismatch or trunk allowed list filtering."""
    if re.search(r"%CDP-4-NATIVE_VLAN_MISMATCH|Native VLAN mismatch discovered", show_output, re.IGNORECASE):
        return {
            "check": "trunk_configuration",
            "status": "FAIL",
            "message": "Native VLAN mismatch detected across trunk link.",
            "evidence": "CDP alert '%CDP-4-NATIVE_VLAN_MISMATCH' present in log.",
        }

    if re.search(r"Vlans allowed on trunk:\s*1-(\d+)", show_output, re.IGNORECASE):
        match = re.search(r"Vlans allowed on trunk:\s*1-(\d+)", show_output)
        max_allowed = int(match.group(1)) if match else 4094
        if max_allowed < 100:
            return {
                "check": "trunk_configuration",
                "status": "WARNING",
                "message": f"Trunk restricts allowed VLANs to 1-{max_allowed}. Higher VLANs are pruned/blocked.",
                "evidence": f"Vlans allowed on trunk: 1-{max_allowed}",
            }

    return {
        "check": "trunk_configuration",
        "status": "PASS",
        "message": "Trunk port status and Native VLAN settings appear normal.",
        "evidence": "No CDP native VLAN mismatch reported.",
    }


def check_route_exists(destination_ip: Optional[str], show_output: str) -> Dict[str, Any]:
    """11. Check if routing table contains destination route."""
    if "% Network not in table" in show_output or "% Subnet not in table" in show_output:
        return {
            "check": "route_exists",
            "status": "FAIL",
            "message": "Destination route is missing from active routing table.",
            "evidence": "show ip route returned '% Network/Subnet not in table'.",
        }
    if "(Incomplete ARP resolution" in show_output:
        return {
            "check": "route_exists",
            "status": "FAIL",
            "message": "Static route next-hop is unreachable (incomplete ARP).",
            "evidence": "Incomplete ARP resolution for configured next-hop.",
        }
    return {
        "check": "route_exists",
        "status": "PASS",
        "message": "No missing route errors found in routing table output.",
        "evidence": "Routing output contains valid path entries.",
    }


def check_default_route(show_output: str) -> Dict[str, Any]:
    """12. Check for missing default route (Gateway of last resort)."""
    if re.search(r"Gateway of last resort is not set", show_output, re.IGNORECASE):
        return {
            "check": "default_route",
            "status": "FAIL",
            "message": "Gateway of last resort is not set on the router.",
            "evidence": "show ip route states 'Gateway of last resort is not set'.",
        }
    return {
        "check": "default_route",
        "status": "PASS",
        "message": "Gateway of last resort or default route is configured.",
        "evidence": "Routing table contains a default route or gateway of last resort.",
    }


def check_acl_deny(show_output: str) -> Dict[str, Any]:
    """13. Detect ACL packet drops or explicit deny statements."""
    # Check for implicit deny matches
    implicit_match = re.search(r"implicit deny.*?(?:matches:\s*(\d+)|\((\d+)\s+matches\))", show_output, re.IGNORECASE)
    if implicit_match:
        count = implicit_match.group(1) or implicit_match.group(2) or "several"
        if count != "0":
            return {
                "check": "acl_deny",
                "status": "FAIL",
                "message": f"Traffic is being blocked by ACL implicit deny ({count} matches).",
                "evidence": f"Found implicit deny with {count} matched dropped packets.",
            }

    # Check for explicit deny rule matches (e.g. "deny tcp ... (45 matches)" or "matches: 45")
    deny_match = re.search(r"deny\s+(tcp|udp|ip).*?(?:matches:\s*([1-9]\d*)|\(([1-9]\d*)\s+matches\))", show_output, re.IGNORECASE)
    if deny_match:
        return {
            "check": "acl_deny",
            "status": "FAIL",
            "message": f"Traffic matches explicit ACL deny rule ({deny_match.group(0).strip()}).",
            "evidence": deny_match.group(0).strip(),
        }

    return {
        "check": "acl_deny",
        "status": "PASS",
        "message": "No active ACL deny matches or drop counters detected in evidence.",
        "evidence": "ACL show output has no active deny packet matches.",
    }


def check_nat_configuration(show_output: str) -> Dict[str, Any]:
    """14. Detect NAT configuration errors."""
    if re.search(r"Outside interfaces:\s*None", show_output, re.IGNORECASE):
        return {
            "check": "nat_configuration",
            "status": "FAIL",
            "message": "NAT outside interface is not defined ('Outside interfaces: None').",
            "evidence": "show ip nat statistics reveals missing 'ip nat outside' on WAN interface.",
        }

    if re.search(r"Hits:\s*\d+\s+Misses:\s*([1-9]\d*)", show_output, re.IGNORECASE):
        match = re.search(r"Hits:\s*(\d+)\s+Misses:\s*(\d+)", show_output)
        if match and int(match.group(2)) > 0:
            return {
                "check": "nat_configuration",
                "status": "WARNING",
                "message": f"NAT translation misses detected ({match.group(2)} misses), indicating unpermitted subnets.",
                "evidence": f"NAT statistics: Hits={match.group(1)}, Misses={match.group(2)}",
            }

    return {
        "check": "nat_configuration",
        "status": "PASS",
        "message": "NAT configuration and interface roles appear normal.",
        "evidence": "Outside interfaces defined, no missing NAT boundaries detected.",
    }


def check_interface_status(show_output: str) -> Dict[str, Any]:
    """15. Check for administrative shutdown or err-disabled interface states."""
    if re.search(r"administratively down", show_output, re.IGNORECASE):
        return {
            "check": "interface_status",
            "status": "FAIL",
            "message": "Interface is administratively shutdown ('administratively down').",
            "evidence": "Interface status reports 'administratively down down'.",
        }

    if re.search(r"err-disabled", show_output, re.IGNORECASE):
        return {
            "check": "interface_status",
            "status": "FAIL",
            "message": "Interface is in 'err-disabled' state (port security or loop violation).",
            "evidence": "Interface status reports 'err-disabled'.",
        }

    if re.search(r"status\s+disabled", show_output, re.IGNORECASE):
        return {
            "check": "interface_status",
            "status": "FAIL",
            "message": "Interface port is disabled.",
            "evidence": "Port status reports 'disabled'.",
        }

    return {
        "check": "interface_status",
        "status": "PASS",
        "message": "Interface operational and administrative status appear normal.",
        "evidence": "No administratively down or err-disabled states found.",
    }


# =============================================================================
# Master Verification Orchestrator
# =============================================================================

def parse_client_config(config_text: str) -> Dict[str, str]:
    """Extract IP, Subnet Mask, Default Gateway, and DNS from client configuration string."""
    info = {"ip": "", "mask": "", "gateway": "", "dns": ""}
    if not config_text:
        return info

    for line in config_text.splitlines():
        line_clean = line.strip()
        # IP Address
        ip_match = re.search(r"(?:IP Address|IPv4 Address)[.\s:]+([0-9.]+)", line_clean, re.IGNORECASE)
        if ip_match:
            info["ip"] = ip_match.group(1).strip()

        # Subnet Mask
        mask_match = re.search(r"(?:Subnet Mask)[.\s:]+([0-9.]+)", line_clean, re.IGNORECASE)
        if mask_match:
            info["mask"] = mask_match.group(1).strip()

        # Default Gateway
        gw_match = re.search(r"(?:Default Gateway)[.\s:]+([0-9.]+)", line_clean, re.IGNORECASE)
        if gw_match:
            info["gateway"] = gw_match.group(1).strip()

        # DNS Server
        dns_match = re.search(r"(?:DNS Server|DNS Servers|DNS)[.\s:]+([0-9.]+)", line_clean, re.IGNORECASE)
        if dns_match:
            info["dns"] = dns_match.group(1).strip()

    return info


def run_all_checks(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute all 15 deterministic checks against a case's configuration and show outputs.
    Returns a unified diagnostic summary with pass/fail/warning counts.
    """
    client_raw = str(case_data.get("client_configuration", ""))
    show_output = str(case_data.get("show_output", ""))
    parsed = parse_client_config(client_raw)

    ip = parsed.get("ip") or ""
    mask = parsed.get("mask") or ""
    gateway = parsed.get("gateway") or ""
    dns = parsed.get("dns") or ""

    results: List[Dict[str, Any]] = []

    # 1. Valid IP check
    if ip:
        results.append(check_valid_ip(ip))

    # 2. Subnet Mask check
    if mask:
        results.append(check_valid_subnet_mask(mask))

    # 3. IP/Subnet alignment
    if ip and mask:
        results.append(check_ip_subnet_alignment(ip, mask))

    # 4. Gateway in Subnet
    if ip and mask and gateway:
        results.append(check_gateway_in_subnet(ip, mask, gateway))

    # 5. Duplicate IP
    results.append(check_duplicate_ip(f"{client_raw}\n{show_output}"))

    # 6. Missing Gateway
    if "gateway" in client_raw.lower():
        results.append(check_missing_gateway(gateway))

    # 7. APIPA Address
    if ip:
        results.append(check_apipa_address(ip))

    # 8. DNS Configuration
    results.append(check_dns_configuration(dns, show_output))

    # 9. VLAN Assignment
    results.append(check_vlan_assignment(show_output))

    # 10. Trunk Configuration
    results.append(check_trunk_configuration(show_output))

    # 11. Route Exists
    results.append(check_route_exists(None, show_output))

    # 12. Default Route
    results.append(check_default_route(show_output))

    # 13. ACL Deny
    results.append(check_acl_deny(show_output))

    # 14. NAT Configuration
    results.append(check_nat_configuration(show_output))

    # 15. Interface Status
    results.append(check_interface_status(show_output))

    # Aggregate counts
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    warn_count = sum(1 for r in results if r["status"] == "WARNING")
    failures = [r for r in results if r["status"] == "FAIL"]
    warnings = [r for r in results if r["status"] == "WARNING"]

    return {
        "case_id": case_data.get("case_id", "N/A"),
        "total_checks": len(results),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "warning_count": warn_count,
        "results": results,
        "failures": failures,
        "warnings": warnings,
        "overall_status": "FAIL" if fail_count > 0 else ("WARNING" if warn_count > 0 else "PASS"),
    }


def get_osi_layer_breakdown(case_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Categorize deterministic checks into the 5 operational OSI layers:
    - Layer 1 (Physical): Interface status, cabling/speed/duplex
    - Layer 2 (Data Link): VLAN assignment, 802.1Q trunking, MAC/ARP, port-security
    - Layer 3 (Network): IP, subnet mask, default gateway, routing table, NAT
    - Layer 4 (Transport): ACL protocol/port filtering (TCP/UDP 80/443), established flags
    - Layer 7 (Application): DNS resolution, DHCP leasing, HTTP/SSH services
    """
    summary = run_all_checks(case_data)
    results = summary["results"]

    layer_mapping = {
        "Layer 1 - Physical": ["interface_status"],
        "Layer 2 - Data Link": ["vlan_assignment", "trunk_configuration", "duplicate_ip"],
        "Layer 3 - Network": ["valid_ip", "valid_subnet_mask", "ip_subnet_alignment", "gateway_mismatch", "missing_gateway", "apipa_check", "route_exists", "default_route", "nat_configuration"],
        "Layer 4 - Transport": ["acl_deny"],
        "Layer 7 - Application": ["dns_configuration"],
    }

    breakdown = {}
    for layer, check_names in layer_mapping.items():
        layer_results = [r for r in results if r["check"] in check_names]
        if not layer_results:
            breakdown[layer] = {"status": "NOT_TESTED", "message": "No specific Layer checks applied.", "failures": []}
            continue

        layer_fails = [r for r in layer_results if r["status"] == "FAIL"]
        layer_warns = [r for r in layer_results if r["status"] == "WARNING"]

        if layer_fails:
            status = "FAIL"
            msg = f"{len(layer_fails)} rule violation(s) detected at this layer."
        elif layer_warns:
            status = "WARNING"
            msg = f"{len(layer_warns)} potential warning(s) at this layer."
        else:
            status = "PASS"
            msg = "All evaluated layer parameters passed deterministic validation."

        breakdown[layer] = {
            "status": status,
            "message": msg,
            "failures": layer_fails,
            "results": layer_results,
        }

    return breakdown

