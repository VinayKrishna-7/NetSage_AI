"""
generate_dataset.py
==============================================================================
Populates data/cases.csv with 32 realistic Cisco networking troubleshooting cases
spanning 10 fault domains (VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT,
Wireless, Interface, Trunking, IP Conflicts).
==============================================================================
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CASES_FILE = DATA_DIR / "cases.csv"

FIELDNAMES = [
    "case_id",
    "title",
    "symptom",
    "topology",
    "device",
    "client_configuration",
    "show_command",
    "show_output",
    "expected_fault",
    "expected_root_cause",
    "osi_layer",
    "concept",
    "severity",
    "expected_next_command",
    "expected_fix",
    "expected_evidence",
]

CASES = [
    # -------------------------------------------------------------------------
    # VLAN (4 Cases: NET001 - NET004)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET001",
        "title": "Access Port Assigned to Incorrect VLAN",
        "symptom": "PC1 in HR department cannot reach the HR Gateway (192.168.10.1) or HR File Server (192.168.10.50).",
        "topology": "PC1 [Fa0/2] ---> Switch-1 [Gi0/1 Trunk] ---> Router R1 (Subinterfaces .10 and .20)",
        "device": "Switch-1",
        "client_configuration": "IP Address: 192.168.10.15\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.10.1\nDNS: 192.168.10.50",
        "show_command": "show vlan brief",
        "show_output": (
            "VLAN Name                             Status    Ports\n"
            "---- -------------------------------- --------- -------------------------------\n"
            "1    default                          active    Fa0/1, Fa0/7, Fa0/8\n"
            "10   HR                               active    Fa0/5, Fa0/6\n"
            "20   Sales                            active    Fa0/2, Fa0/3, Fa0/4\n"
            "99   Management                       active"
        ),
        "expected_fault": "VLAN",
        "expected_root_cause": "Switchport FastEthernet0/2 connected to HR PC1 is mistakenly assigned to Sales VLAN 20 instead of HR VLAN 10.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "Access Port VLAN Membership & Broadcast Domain Isolation",
        "severity": "MEDIUM",
        "expected_next_command": "show interfaces FastEthernet0/2 switchport",
        "expected_fix": "Switch-1(config)# interface FastEthernet0/2\nSwitch-1(config-if)# switchport access vlan 10",
        "expected_evidence": "show vlan brief clearly displays Fa0/2 listed under VLAN 20 (Sales) rather than VLAN 10 (HR).",
    },
    {
        "case_id": "NET002",
        "title": "VLAN Database Missing Defined Access VLAN",
        "symptom": "Finance PC2 cannot ping its gateway or any network device; switchport LED is solid amber and link reports inactive.",
        "topology": "PC2 [Fa0/10] ---> Switch-2 [Gi0/1 Trunk] ---> Distribution Switch",
        "device": "Switch-2",
        "client_configuration": "IP Address: 192.168.30.22\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.30.1\nDNS: 8.8.8.8",
        "show_command": "show interfaces FastEthernet0/10 switchport",
        "show_output": (
            "Name: Fa0/10\n"
            "Switchport: Enabled\n"
            "Administrative Mode: static access\n"
            "Operational Mode: static access\n"
            "Administrative Trunking Encapsulation: dot1q\n"
            "Negotiation of Trunking: Off\n"
            "Access Mode VLAN: 30 ((Inactive))\n"
            "Trunking Native Mode VLAN: 1 (default)\n"
            "Voice VLAN: none"
        ),
        "expected_fault": "VLAN",
        "expected_root_cause": "Port Fa0/10 is assigned to VLAN 30, but VLAN 30 has not been created in the switch VLAN database, rendering the port inactive.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "VLAN Database Creation & Port Inactive State",
        "severity": "HIGH",
        "expected_next_command": "show vlan id 30",
        "expected_fix": "Switch-2(config)# vlan 30\nSwitch-2(config-vlan)# name Finance\nSwitch-2(config-vlan)# exit",
        "expected_evidence": "show interfaces switchport shows 'Access Mode VLAN: 30 ((Inactive))', confirming VLAN 30 does not exist in the VLAN table.",
    },
    {
        "case_id": "NET003",
        "title": "Router-on-a-Stick Subinterface 802.1Q Tag Mismatch",
        "symptom": "Hosts in VLAN 20 can ping default gateway 192.168.20.1, but hosts in VLAN 10 cannot ping default gateway 192.168.10.1.",
        "topology": "VLAN 10 / VLAN 20 Hosts ---> Switch-1 [Gi0/1 Trunk] ---> Router R1 [Gi0/0.10, Gi0/0.20]",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.10.100\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.10.1\nDNS: 192.168.10.5",
        "show_command": "show running-config interface GigabitEthernet0/0.10",
        "show_output": (
            "Building configuration...\n\n"
            "Current configuration : 138 bytes\n"
            "!\n"
            "interface GigabitEthernet0/0.10\n"
            " encapsulation dot1Q 12\n"
            " ip address 192.168.10.1 255.255.255.0\n"
            "end"
        ),
        "expected_fault": "VLAN",
        "expected_root_cause": "Subinterface Gi0/0.10 is configured with 802.1Q encapsulation tag 12 instead of tag 10, dropping tagged frames originating from VLAN 10.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "Router-on-a-Stick 802.1Q Subinterface Encapsulation",
        "severity": "HIGH",
        "expected_next_command": "show ip interface brief GigabitEthernet0/0.10",
        "expected_fix": "R1(config)# interface GigabitEthernet0/0.10\nR1(config-subif)# encapsulation dot1Q 10",
        "expected_evidence": "show running-config interface GigabitEthernet0/0.10 shows 'encapsulation dot1Q 12' while IP is configured for VLAN 10 (192.168.10.1/24).",
    },
    {
        "case_id": "NET004",
        "title": "Voice VLAN Configured as Data Access VLAN",
        "symptom": "Desktop PC plugged into Cisco IP Phone PC port is placed into Voice VLAN 150 and cannot communicate with corporate data servers.",
        "topology": "PC ---> Cisco IP Phone 7841 ---> Switch-1 [Fa0/3] ---> Corporate Network",
        "device": "Switch-1",
        "client_configuration": "IP Address: 192.168.150.45\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.150.1\nDNS: 192.168.150.1",
        "show_command": "show interfaces FastEthernet0/3 switchport",
        "show_output": (
            "Name: Fa0/3\n"
            "Switchport: Enabled\n"
            "Administrative Mode: static access\n"
            "Operational Mode: static access\n"
            "Access Mode VLAN: 150 (Voice)\n"
            "Trunking Native Mode VLAN: 1 (default)\n"
            "Voice VLAN: 150"
        ),
        "expected_fault": "VLAN",
        "expected_root_cause": "The switchport access VLAN was mistakenly configured as Voice VLAN 150 instead of Data VLAN 10, causing untagged PC frames to join the Voice broadcast domain.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "Voice VLAN vs. Native Access Data VLAN Separation",
        "severity": "MEDIUM",
        "expected_next_command": "show running-config interface FastEthernet0/3",
        "expected_fix": "Switch-1(config)# interface FastEthernet0/3\nSwitch-1(config-if)# switchport access vlan 10\nSwitch-1(config-if)# switchport voice vlan 150",
        "expected_evidence": "show interfaces FastEthernet0/3 switchport displays 'Access Mode VLAN: 150 (Voice)' matching the Voice VLAN.",
    },

    # -------------------------------------------------------------------------
    # Default Gateway (3 Cases: NET005 - NET007)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET005",
        "title": "Client Default Gateway Outside Host Subnet",
        "symptom": "PC1 can ping neighboring PCs in 192.168.10.0/24, but cannot communicate with any remote subnet or Internet destination.",
        "topology": "PC1 (192.168.10.25/24) ---> Switch-1 ---> Router R1 [Gi0/0: 192.168.10.1/24]",
        "device": "PC1",
        "client_configuration": "IP Address: 192.168.10.25\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.20.1\nDNS: 8.8.8.8",
        "show_command": "ipconfig /all",
        "show_output": (
            "Windows IP Configuration\n\n"
            "Ethernet adapter Local Area Connection:\n"
            "   IPv4 Address. . . . . . . . . . . : 192.168.10.25(Preferred)\n"
            "   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n"
            "   Default Gateway . . . . . . . . . : 192.168.20.1\n"
            "   DNS Servers . . . . . . . . . . . : 8.8.8.8"
        ),
        "expected_fault": "Default Gateway",
        "expected_root_cause": "The configured default gateway (192.168.20.1) does not reside within the client's local subnet (192.168.10.0/24), preventing ARP resolution for off-subnet routing.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Subnet Mask Boundaries and Default Gateway Reachability",
        "severity": "HIGH",
        "expected_next_command": "arp -a",
        "expected_fix": "Configure PC1 Default Gateway to 192.168.10.1 matching R1 GigabitEthernet0/0.",
        "expected_evidence": "ipconfig /all shows host IP 192.168.10.25 with mask 255.255.255.0, where default gateway 192.168.20.1 is in a different /24 network.",
    },
    {
        "case_id": "NET006",
        "title": "Default Gateway Router Interface Administratively Down",
        "symptom": "All workstations in 10.1.1.0/24 report 'Request timed out' when pinging their default gateway (10.1.1.1).",
        "topology": "LAN Workstations (10.1.1.0/24) ---> Switch-1 ---> Router R1 [Gi0/0]",
        "device": "Router R1",
        "client_configuration": "IP Address: 10.1.1.45\nSubnet Mask: 255.255.255.0\nDefault Gateway: 10.1.1.1\nDNS: 10.1.1.1",
        "show_command": "show ip interface brief",
        "show_output": (
            "Interface                  IP-Address      OK? Method Status                Protocol\n"
            "GigabitEthernet0/0         10.1.1.1        YES manual administratively down down\n"
            "GigabitEthernet0/1         203.0.113.1     YES manual up                    up\n"
            "Loopback0                  1.1.1.1         YES manual up                    up"
        ),
        "expected_fault": "Default Gateway",
        "expected_root_cause": "Router interface GigabitEthernet0/0 (the default gateway) is in 'administratively down' status due to a missing 'no shutdown' command.",
        "osi_layer": "Layer 1 - Physical",
        "concept": "Interface Administrative Status & Layer 1 Up State",
        "severity": "CRITICAL",
        "expected_next_command": "show interfaces GigabitEthernet0/0",
        "expected_fix": "R1(config)# interface GigabitEthernet0/0\nR1(config-if)# no shutdown",
        "expected_evidence": "show ip interface brief indicates GigabitEthernet0/0 is 'administratively down down'.",
    },
    {
        "case_id": "NET007",
        "title": "Mismatched Subnet Mask on Gateway Interface",
        "symptom": "Hosts with IP addresses 172.16.1.2 through 172.16.1.126 can reach the router, but hosts with IPs 172.16.1.130 through 172.16.1.250 cannot communicate with the gateway.",
        "topology": "Subnet 172.16.1.0/24 Clients ---> Switch-1 ---> Router R1 [Gi0/1]",
        "device": "Router R1",
        "client_configuration": "IP Address: 172.16.1.140\nSubnet Mask: 255.255.255.0\nDefault Gateway: 172.16.1.1\nDNS: 8.8.8.8",
        "show_command": "show ip interface GigabitEthernet0/1",
        "show_output": (
            "GigabitEthernet0/1 is up, line protocol is up\n"
            "  Internet address is 172.16.1.1/25\n"
            "  Broadcast address is 172.16.1.127\n"
            "  Address determined by setup command\n"
            "  MTU is 1500 bytes\n"
            "  Helper address is not set\n"
            "  Directed broadcast forwarding is disabled"
        ),
        "expected_fault": "Default Gateway",
        "expected_root_cause": "The router gateway interface Gi0/1 is configured with a /25 subnet mask (255.255.255.128) instead of /24 (255.255.255.0), causing it to ignore packets from upper half hosts.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Variable Length Subnet Masking (VLSM) & Broadcast Domain Limits",
        "severity": "HIGH",
        "expected_next_command": "show running-config interface GigabitEthernet0/1",
        "expected_fix": "R1(config)# interface GigabitEthernet0/1\nR1(config-if)# ip address 172.16.1.1 255.255.255.0",
        "expected_evidence": "show ip interface Gi0/1 shows 'Internet address is 172.16.1.1/25' with broadcast 172.16.1.127, while clients expect a /24 subnet.",
    },

    # -------------------------------------------------------------------------
    # DHCP (4 Cases: NET008 - NET011)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET008",
        "title": "DHCP Address Pool Exhaustion",
        "symptom": "Newly connected workstations fail to obtain an IP address and default to an APIPA address 169.254.x.x.",
        "topology": "Workstations ---> Switch-1 ---> Router R1 (DHCP Server)",
        "device": "Router R1",
        "client_configuration": "IP Address: 169.254.120.44\nSubnet Mask: 255.255.0.0\nDefault Gateway: 0.0.0.0\nDNS: 0.0.0.0",
        "show_command": "show ip dhcp pool LAN_POOL",
        "show_output": (
            "Pool LAN_POOL :\n"
            " Utilization mark (high/low)    : 100 / 0\n"
            " Subnet size (total/usable)     : 30/28\n"
            " Total addresses                : 30\n"
            " Leased addresses               : 28\n"
            " Excluded addresses             : 2\n"
            " Pending event                  : none\n"
            " 1 subnet is currently in the pool :\n"
            " Current index        IP pool range                    Leased addresses\n"
            " 192.168.1.30         192.168.1.1      192.168.1.30     28"
        ),
        "expected_fault": "DHCP",
        "expected_root_cause": "The configured DHCP pool subnet is only a /27 with 28 usable addresses, and 100% of available leases have been consumed.",
        "osi_layer": "Layer 7 - Application",
        "concept": "DHCP Address Pool Allocation & Lease Exhaustion",
        "severity": "HIGH",
        "expected_next_command": "show ip dhcp binding",
        "expected_fix": "R1(config)# ip dhcp pool LAN_POOL\nR1(config-dhcp)# network 192.168.1.0 255.255.255.0",
        "expected_evidence": "show ip dhcp pool indicates Total addresses: 30, Leased addresses: 28, with 100% utilization mark and no free addresses.",
    },
    {
        "case_id": "NET009",
        "title": "Missing IP Helper-Address on Gateway Router",
        "symptom": "Branch office PCs fail to obtain an IP address via DHCP from the central corporate DHCP server (10.10.10.5).",
        "topology": "Branch PCs ---> Branch Switch ---> Branch Router R1 [Gi0/0] ---> WAN ---> Central DHCP Server (10.10.10.5)",
        "device": "Branch Router R1",
        "client_configuration": "IP Address: 169.254.88.19\nSubnet Mask: 255.255.0.0\nDefault Gateway: 0.0.0.0\nDNS: 0.0.0.0",
        "show_command": "show running-config interface GigabitEthernet0/0",
        "show_output": (
            "Building configuration...\n\n"
            "Current configuration : 152 bytes\n"
            "!\n"
            "interface GigabitEthernet0/0\n"
            " description Branch Local LAN\n"
            " ip address 192.168.50.1 255.255.255.0\n"
            " duplex auto\n"
            " speed auto\n"
            "end"
        ),
        "expected_fault": "DHCP",
        "expected_root_cause": "The router interface GigabitEthernet0/0 does not have an 'ip helper-address' configured, dropping DHCP broadcast DISCOVER packets at Layer 3.",
        "osi_layer": "Layer 3 - Network",
        "concept": "DHCP Relay Agent & IP Helper-Address Broadcast Forwarding",
        "severity": "HIGH",
        "expected_next_command": "show ip interface GigabitEthernet0/0",
        "expected_fix": "R1(config)# interface GigabitEthernet0/0\nR1(config-if)# ip helper-address 10.10.10.5",
        "expected_evidence": "show running-config interface GigabitEthernet0/0 shows no 'ip helper-address' command configured.",
    },
    {
        "case_id": "NET010",
        "title": "DHCP Scope Default-Router Option Typo",
        "symptom": "Client PCs receive an IP address and DNS successfully via DHCP, but cannot access external networks; router LAN IP is 192.168.1.1.",
        "topology": "Client PCs ---> Switch-1 ---> Router R1 (DHCP Server LAN IP 192.168.1.1)",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.1.55\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.254\nDNS: 8.8.8.8",
        "show_command": "show running-config | section dhcp",
        "show_output": (
            "ip dhcp excluded-address 192.168.1.1 192.168.1.10\n"
            "!\n"
            "ip dhcp pool OFFICE_LAN\n"
            "   network 192.168.1.0 255.255.255.0\n"
            "   default-router 192.168.1.254\n"
            "   dns-server 8.8.8.8"
        ),
        "expected_fault": "DHCP",
        "expected_root_cause": "The DHCP pool configuration specifies 'default-router 192.168.1.254', which does not exist; the actual default gateway interface is 192.168.1.1.",
        "osi_layer": "Layer 7 - Application",
        "concept": "DHCP Option 3 (Default Router) Configuration",
        "severity": "MEDIUM",
        "expected_next_command": "show ip interface brief",
        "expected_fix": "R1(config)# ip dhcp pool OFFICE_LAN\nR1(config-dhcp)# default-router 192.168.1.1",
        "expected_evidence": "show running-config shows 'default-router 192.168.1.254' while R1 local interface is 192.168.1.1.",
    },
    {
        "case_id": "NET011",
        "title": "DHCP Pool Excluded Address Overlap with Gateway",
        "symptom": "Duplicate IP address alert '%IP-4-DUPADDR: Duplicate address 192.168.1.1' occurs; PC intermittently loses gateway connectivity.",
        "topology": "Workstations ---> Switch-1 ---> Router R1 (192.168.1.1)",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.1.1\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1",
        "show_command": "show ip dhcp binding",
        "show_output": (
            "IP address       Client-ID/              Lease expiration        Type\n"
            "                 Hardware address\n"
            "192.168.1.1      0100.5079.6668.01       Oct 12 2026 10:14 AM    Automatic\n"
            "192.168.1.2      0100.5079.6668.02       Oct 12 2026 10:15 AM    Automatic"
        ),
        "expected_fault": "DHCP",
        "expected_root_cause": "The router's own IP address 192.168.1.1 was not excluded from the DHCP pool via 'ip dhcp excluded-address', causing it to be handed out to a client.",
        "osi_layer": "Layer 3 - Network",
        "concept": "DHCP Excluded Addresses & Static IP Address Conflicts",
        "severity": "CRITICAL",
        "expected_next_command": "show running-config | include excluded-address",
        "expected_fix": "R1(config)# ip dhcp excluded-address 192.168.1.1 192.168.1.10\nR1# clear ip dhcp binding 192.168.1.1",
        "expected_evidence": "show ip dhcp binding reveals lease of 192.168.1.1 to client MAC 0100.5079.6668.01, conflicting with router interface IP.",
    },

    # -------------------------------------------------------------------------
    # DNS (3 Cases: NET012 - NET014)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET012",
        "title": "Incorrect DNS Server IP Address Configured",
        "symptom": "PC can ping public IP 8.8.8.8 and local gateway, but web browser fails to open any website by domain name (e.g. cisco.com).",
        "topology": "PC1 ---> Switch-1 ---> Router R1 ---> Internet DNS (8.8.8.8)",
        "device": "PC1",
        "client_configuration": "IP Address: 192.168.1.40\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1\nDNS Server: 8.8.4.40",
        "show_command": "nslookup cisco.com",
        "show_output": (
            "Server:  UnKnown\n"
            "Address:  8.8.4.40\n\n"
            "DNS request timed out.\n"
            "    timeout was 2 seconds.\n"
            "DNS request timed out.\n"
            "    timeout was 2 seconds.\n"
            "*** Request to UnKnown timed-out"
        ),
        "expected_fault": "DNS",
        "expected_root_cause": "Client DNS server address is configured as 8.8.4.40 (a typo for 8.8.4.4 or 8.8.8.8), which is unresponsive to DNS queries.",
        "osi_layer": "Layer 7 - Application",
        "concept": "DNS Resolver Configuration & UDP Port 53 Name Resolution",
        "severity": "MEDIUM",
        "expected_next_command": "ping 8.8.4.40",
        "expected_fix": "Update PC1 DNS server configuration to 8.8.8.8 or 8.8.4.4.",
        "expected_evidence": "nslookup shows request timeout attempting to query non-existent server 8.8.4.40 while IP connectivity is functional.",
    },
    {
        "case_id": "NET013",
        "title": "Packet Tracer DNS Service Disabled on Server",
        "symptom": "Internal domain name 'intranet.corp.local' does not resolve, but pinging server IP 192.168.1.10 succeeds.",
        "topology": "PC1 ---> Switch-1 ---> Server-PT (DNS/Web Server: 192.168.1.10)",
        "device": "Server-PT",
        "client_configuration": "IP Address: 192.168.1.30\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1\nDNS Server: 192.168.1.10",
        "show_command": "nslookup intranet.corp.local 192.168.1.10",
        "show_output": (
            "Server:  intranet.corp.local\n"
            "Address:  192.168.1.10\n\n"
            "*** intranet.corp.local can't find intranet.corp.local: No response from server\n"
            "Packet Tracer Server Services State:\n"
            "HTTP: ON\n"
            "DHCP: OFF\n"
            "DNS Service: OFF\n"
            "Resource Record: intranet.corp.local -> 192.168.1.10"
        ),
        "expected_fault": "DNS",
        "expected_root_cause": "The DNS service toggle on Cisco Packet Tracer Server-PT is set to 'OFF' despite records being present in the table.",
        "osi_layer": "Layer 7 - Application",
        "concept": "DNS Server Daemon/Service Operational State",
        "severity": "HIGH",
        "expected_next_command": "netstat -an | findstr :53",
        "expected_fix": "Navigate to Server-PT -> Services -> DNS -> Click radio button 'ON'.",
        "expected_evidence": "Show output indicates 'DNS Service: OFF' on Server-PT, rejecting inbound UDP/TCP 53 requests.",
    },
    {
        "case_id": "NET014",
        "title": "Missing DNS A Record for Web Server",
        "symptom": "Client PCs can resolve external websites but get NXDOMAIN error when attempting to resolve internal portal 'portal.lan'.",
        "topology": "PC1 ---> Switch-1 ---> Router R1 ---> Internal DNS Server (10.0.0.53)",
        "device": "Internal DNS Server",
        "client_configuration": "IP Address: 10.0.0.100\nSubnet Mask: 255.255.255.0\nDefault Gateway: 10.0.0.1\nDNS: 10.0.0.53",
        "show_command": "nslookup portal.lan 10.0.0.53",
        "show_output": (
            "Server:  dns.internal.lan\n"
            "Address:  10.0.0.53\n\n"
            "*** dns.internal.lan can't find portal.lan: Non-existent domain (NXDOMAIN)\n"
            "Zone Table Records:\n"
            "mail.lan      A    10.0.0.25\n"
            "files.lan     A    10.0.0.30\n"
            "dc1.lan       A    10.0.0.53"
        ),
        "expected_fault": "DNS",
        "expected_root_cause": "The internal authoritative DNS server is missing an 'A' resource record mapping 'portal.lan' to web server IP 10.0.0.80.",
        "osi_layer": "Layer 7 - Application",
        "concept": "Authoritative DNS Zone Resource Records (A Record)",
        "severity": "MEDIUM",
        "expected_next_command": "ping 10.0.0.80",
        "expected_fix": "Add DNS A-Record on DNS server: Name: portal.lan, Address: 10.0.0.80.",
        "expected_evidence": "nslookup returns 'Non-existent domain (NXDOMAIN)' and Zone Table Records confirm absence of portal.lan.",
    },

    # -------------------------------------------------------------------------
    # Routing (4 Cases: NET015 - NET018)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET015",
        "title": "Missing Default Route on Edge Router",
        "symptom": "LAN hosts can communicate internally and ping edge router R1, but cannot reach any Internet IP (e.g. 203.0.113.2 or 8.8.8.8).",
        "topology": "LAN (192.168.1.0/24) ---> Edge Router R1 [Se0/0/0] ---> ISP Router (203.0.113.2)",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.1.25\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1\nDNS: 8.8.8.8",
        "show_command": "show ip route",
        "show_output": (
            "Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP\n"
            "       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area\n\n"
            "Gateway of last resort is not set\n\n"
            "      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks\n"
            "C        192.168.1.0/24 is directly connected, GigabitEthernet0/0\n"
            "L        192.168.1.1/32 is directly connected, GigabitEthernet0/0\n"
            "      203.0.113.0/30 is variably subnetted, 2 subnets, 2 masks\n"
            "C        203.0.113.0/30 is directly connected, Serial0/0/0\n"
            "L        203.0.113.1/32 is directly connected, Serial0/0/0"
        ),
        "expected_fault": "Routing",
        "expected_root_cause": "Edge router R1 has no default route (gateway of last resort is not set), discarding off-net packets toward the Internet.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Default Static Route (0.0.0.0/0) & Gateway of Last Resort",
        "severity": "CRITICAL",
        "expected_next_command": "show ip route 0.0.0.0",
        "expected_fix": "R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.2",
        "expected_evidence": "show ip route explicitly states 'Gateway of last resort is not set' with no 0.0.0.0/0 route present.",
    },
    {
        "case_id": "NET016",
        "title": "OSPF Passive Interface Blocking Neighbor Adjacency",
        "symptom": "Routers R1 and R2 are directly connected via Gi0/1, but OSPF routes from R2 are not appearing in R1's routing table.",
        "topology": "Router R1 [Gi0/1: 10.0.12.1/30] <===> Router R2 [Gi0/1: 10.0.12.2/30]",
        "device": "Router R1",
        "client_configuration": "N/A (Router-to-Router link)",
        "show_command": "show ip ospf neighbor",
        "show_output": (
            "Neighbor ID     Pri   State           Dead Time   Address         Interface\n"
            "(Empty table)\n\n"
            "R1# show running-config | section ospf\n"
            "router ospf 1\n"
            " passive-interface GigabitEthernet0/1\n"
            " network 10.0.12.0 0.0.0.3 area 0"
        ),
        "expected_fault": "Routing",
        "expected_root_cause": "GigabitEthernet0/1 on R1 is configured as a passive-interface, suppressing OSPF Hello packets and preventing neighbor adjacency formation.",
        "osi_layer": "Layer 3 - Network",
        "concept": "OSPF Adjacency Formation & Passive Interface Behavior",
        "severity": "HIGH",
        "expected_next_command": "show ip ospf interface GigabitEthernet0/1",
        "expected_fix": "R1(config)# router ospf 1\nR1(config-router)# no passive-interface GigabitEthernet0/1",
        "expected_evidence": "show ip ospf neighbor is empty and running-config shows 'passive-interface GigabitEthernet0/1'.",
    },
    {
        "case_id": "NET017",
        "title": "Static Route Configured with Unreachable Next-Hop",
        "symptom": "Traffic destined to remote branch network 172.20.1.0/24 is dropped at R1; route does not install in the active routing table.",
        "topology": "LAN ---> Router R1 [Gi0/1: 10.1.1.1/30] ---> Router R2 [Gi0/1: 10.1.1.2/30] ---> Remote LAN (172.20.1.0/24)",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.1.15\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1",
        "show_command": "show ip route 172.20.1.0",
        "show_output": (
            "% Network not in table\n\n"
            "R1# show running-config | include ip route\n"
            "ip route 172.20.1.0 255.255.255.0 10.1.1.254\n\n"
            "R1# show ip arp 10.1.1.254\n"
            "(Incomplete ARP resolution for 10.1.1.254)"
        ),
        "expected_fault": "Routing",
        "expected_root_cause": "The static route next-hop is configured as 10.1.1.254, which does not exist in the 10.1.1.0/30 subnet; valid next hop is 10.1.1.2.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Static Route Recursive Lookup & Next-Hop Reachability",
        "severity": "HIGH",
        "expected_next_command": "show ip route 10.1.1.254",
        "expected_fix": "R1(config)# no ip route 172.20.1.0 255.255.255.0 10.1.1.254\nR1(config)# ip route 172.20.1.0 255.255.255.0 10.1.1.2",
        "expected_evidence": "show running-config shows next-hop 10.1.1.254, but the route is absent from 'show ip route' due to recursive lookup failure.",
    },
    {
        "case_id": "NET018",
        "title": "Asymmetric Routing / Missing Return Route on HQ Core",
        "symptom": "Branch PC can send packets to HQ Server (10.2.2.10) verified by debug, but receives no ICMP echo replies.",
        "topology": "Branch PC (192.168.30.50) ---> Branch R1 ---> HQ Core R2 ---> HQ Server (10.2.2.10)",
        "device": "HQ Core Router R2",
        "client_configuration": "IP Address: 192.168.30.50\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.30.1",
        "show_command": "show ip route 192.168.30.0",
        "show_output": (
            "Routing entry for 192.168.30.0/24\n"
            "  Known via \"static\", distance 1, metric 0\n"
            "% Subnet not in table\n\n"
            "Gateway of last resort is not set"
        ),
        "expected_fault": "Routing",
        "expected_root_cause": "HQ Core Router R2 has no routing entry for Branch subnet 192.168.30.0/24, dropping return traffic from the server.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Two-Way Symmetric IP Routing & Return Path Requirement",
        "severity": "HIGH",
        "expected_next_command": "show ip route",
        "expected_fix": "R2(config)# ip route 192.168.30.0 255.255.255.0 10.0.0.1",
        "expected_evidence": "show ip route 192.168.30.0 on R2 outputs '% Subnet not in table', confirming missing return routing.",
    },

    # -------------------------------------------------------------------------
    # ACL (4 Cases: NET019 - NET022)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET019",
        "title": "Standard ACL Implicit Deny Blocking Inter-VLAN Host",
        "symptom": "PC1 (192.168.10.10) can ping its default gateway 192.168.10.1, but cannot reach Server 192.168.20.50 in VLAN 20.",
        "topology": "VLAN 10 PC1 (192.168.10.10) ---> Router R1 [Gi0/0.10, Gi0/0.20] ---> VLAN 20 Server (192.168.20.50)",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.10.10\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.10.1",
        "show_command": "show access-lists 10",
        "show_output": (
            "Standard IP access list 10\n"
            "    10 permit 192.168.10.5 (24 matches)\n"
            "    (implicit deny any matches: 87)\n\n"
            "R1# show running-config interface GigabitEthernet0/0.20\n"
            "interface GigabitEthernet0/0.20\n"
            " encapsulation dot1Q 20\n"
            " ip address 192.168.20.1 255.255.255.0\n"
            " ip access-group 10 out"
        ),
        "expected_fault": "ACL",
        "expected_root_cause": "Access list 10 permits only host 192.168.10.5; traffic from PC1 192.168.10.10 hits the implicit deny at the end of the ACL.",
        "osi_layer": "Layer 3/4 - Network/Transport",
        "concept": "Access Control List (ACL) Implicit Deny Rule",
        "severity": "HIGH",
        "expected_next_command": "show ip interface GigabitEthernet0/0.20",
        "expected_fix": "R1(config)# access-list 10 permit 192.168.10.0 0.0.0.255",
        "expected_evidence": "show access-lists 10 shows only 'permit 192.168.10.5' with 87 implicit deny matches blocking 192.168.10.10.",
    },
    {
        "case_id": "NET020",
        "title": "Extended ACL Statement Denying HTTP/HTTPS Traffic",
        "symptom": "Client workstation can ping web server 203.0.113.80 successfully, but web browser connection to port 80/443 times out.",
        "topology": "Client (172.16.5.20) ---> Edge Router R1 ---> Web Server (203.0.113.80:80)",
        "device": "Router R1",
        "client_configuration": "IP Address: 172.16.5.20\nSubnet Mask: 255.255.255.0\nDefault Gateway: 172.16.5.1\nDNS: 8.8.8.8",
        "show_command": "show access-lists RESTRICT_WEB",
        "show_output": (
            "Extended IP access list RESTRICT_WEB\n"
            "    10 permit icmp any any (16 matches)\n"
            "    20 deny tcp any host 203.0.113.80 eq www (45 matches)\n"
            "    30 deny tcp any host 203.0.113.80 eq 443 (12 matches)\n"
            "    40 permit ip any any (130 matches)"
        ),
        "expected_fault": "ACL",
        "expected_root_cause": "Extended ACL RESTRICT_WEB contains explicit deny rules (lines 20 and 30) for TCP ports 80 and 443 targeting web server 203.0.113.80.",
        "osi_layer": "Layer 4 - Transport",
        "concept": "Extended ACL Protocol and Port Filtering (TCP 80/443 vs ICMP)",
        "severity": "HIGH",
        "expected_next_command": "show running-config interface GigabitEthernet0/1",
        "expected_fix": "R1(config)# ip access-list extended RESTRICT_WEB\nR1(config-ext-nacl)# no 20\nR1(config-ext-nacl)# no 30",
        "expected_evidence": "show access-lists shows 45 matches on 'deny tcp any host 203.0.113.80 eq www', confirming packets are filtered by ACL.",
    },
    {
        "case_id": "NET021",
        "title": "ACL Inbound/Outbound Directional Placement Error",
        "symptom": "Guest users in 192.168.50.0/24 cannot access Internet; security policy intended to protect LAN from guests accidentally blocked all guest traffic.",
        "topology": "Guest VLAN (192.168.50.0/24) ---> Router R1 [Gi0/0.50] ---> Internet",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.50.15\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.50.1\nDNS: 8.8.8.8",
        "show_command": "show running-config interface GigabitEthernet0/0.50",
        "show_output": (
            "Building configuration...\n\n"
            "interface GigabitEthernet0/0.50\n"
            " encapsulation dot1Q 50\n"
            " ip address 192.168.50.1 255.255.255.0\n"
            " ip access-group BLOCK_GUEST in\n"
            "!\n"
            "R1# show access-lists BLOCK_GUEST\n"
            "Standard IP access list BLOCK_GUEST\n"
            "    10 deny 192.168.50.0 0.0.0.255 (154 matches)"
        ),
        "expected_fault": "ACL",
        "expected_root_cause": "ACL BLOCK_GUEST was applied 'in' on subinterface Gi0/0.50, denying all guest traffic upon router entry before it can reach the Internet.",
        "osi_layer": "Layer 3/4 - Network/Transport",
        "concept": "ACL Interface Directionality (Inbound vs Outbound)",
        "severity": "HIGH",
        "expected_next_command": "show ip interface GigabitEthernet0/0.50",
        "expected_fix": "R1(config)# interface GigabitEthernet0/0.50\nR1(config-subif)# no ip access-group BLOCK_GUEST in",
        "expected_evidence": "show running-config shows 'ip access-group BLOCK_GUEST in' and ACL BLOCK_GUEST denies 192.168.50.0/24 with 154 matches.",
    },
    {
        "case_id": "NET022",
        "title": "Extended ACL Missing Established Keyword on Return Traffic",
        "symptom": "LAN PCs can establish outbound UDP sessions (DNS) to Internet, but outbound TCP web traffic receives no response.",
        "topology": "Internal LAN (10.0.0.0/24) ---> Router R1 [Gi0/1 WAN] ---> Internet",
        "device": "Router R1",
        "client_configuration": "IP Address: 10.0.0.45\nSubnet Mask: 255.255.255.0\nDefault Gateway: 10.0.0.1\nDNS: 8.8.8.8",
        "show_command": "show access-lists WAN_IN",
        "show_output": (
            "Extended IP access list WAN_IN\n"
            "    10 permit udp any any eq domain (50 matches)\n"
            "    20 deny ip any any (198 matches)\n\n"
            "R1# show running-config interface GigabitEthernet0/1\n"
            "interface GigabitEthernet0/1\n"
            " ip access-group WAN_IN in"
        ),
        "expected_fault": "ACL",
        "expected_root_cause": "The inbound WAN ACL lacks a 'permit tcp any any established' rule to allow return TCP packets (ACK/RST flags set) from external servers.",
        "osi_layer": "Layer 4 - Transport",
        "concept": "Stateful TCP Inspection & ACL 'established' Keyword",
        "severity": "HIGH",
        "expected_next_command": "show access-lists WAN_IN",
        "expected_fix": "R1(config)# ip access-list extended WAN_IN\nR1(config-ext-nacl)# 15 permit tcp any any established",
        "expected_evidence": "show access-lists WAN_IN contains no 'established' clause, and rule 20 deny ip any any has 198 matches.",
    },

    # -------------------------------------------------------------------------
    # NAT (3 Cases: NET023 - NET025)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET023",
        "title": "NAT Overload ACL Missing New LAN Subnet",
        "symptom": "Workstations in 192.168.1.0/24 can browse the Internet, but workstations in the newly added 192.168.2.0/24 subnet cannot access the Internet.",
        "topology": "Subnet 1 & 2 ---> Router R1 [Gi0/0 LAN, Gi0/1 WAN: 203.0.113.1] ---> ISP",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.2.50\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.2.1\nDNS: 8.8.8.8",
        "show_command": "show ip nat statistics",
        "show_output": (
            "Total active translations: 12 (0 static, 12 dynamic; 12 extended)\n"
            "Outside interfaces:\n"
            "  GigabitEthernet0/1\n"
            "Inside interfaces:\n"
            "  GigabitEthernet0/0\n"
            "Hits: 320  Misses: 45\n"
            "CEF Translated packets: 320, CEF Punted packets: 0\n"
            "Expired translations: 40\n"
            "Dynamic mappings:\n"
            "-- Inside Source\n"
            "[Id: 1] access-list 1 interface GigabitEthernet0/1 overload refcount 12\n\n"
            "R1# show access-lists 1\n"
            "Standard IP access list 1\n"
            "    10 permit 192.168.1.0 0.0.0.255 (320 matches)"
        ),
        "expected_fault": "NAT",
        "expected_root_cause": "NAT ACL 1 only permits subnet 192.168.1.0/24; subnet 192.168.2.0/24 is excluded from translation, causing outbound packets to remain untranslated private IPs.",
        "osi_layer": "Layer 3 - Network",
        "concept": "NAT Overload (PAT) ACL Source Filtering",
        "severity": "HIGH",
        "expected_next_command": "show ip nat translations",
        "expected_fix": "R1(config)# access-list 1 permit 192.168.2.0 0.0.0.255",
        "expected_evidence": "show access-lists 1 shows only 'permit 192.168.1.0 0.0.0.255' while Misses in NAT stats increment for 192.168.2.0/24.",
    },
    {
        "case_id": "NET024",
        "title": "Missing 'ip nat outside' Configuration on WAN Interface",
        "symptom": "All internal LAN clients fail to browse Internet; 'show ip nat translations' remains completely empty despite active traffic.",
        "topology": "Internal LAN (192.168.10.0/24) ---> Router R1 [Gi0/0 Inside, Gi0/1 WAN] ---> ISP",
        "device": "Router R1",
        "client_configuration": "IP Address: 192.168.10.20\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.10.1\nDNS: 8.8.8.8",
        "show_command": "show running-config interface GigabitEthernet0/1",
        "show_output": (
            "Building configuration...\n\n"
            "interface GigabitEthernet0/1\n"
            " description Connection to ISP\n"
            " ip address 203.0.113.6 255.255.255.252\n"
            " duplex auto\n"
            " speed auto\n"
            "end\n\n"
            "R1# show ip nat statistics\n"
            "Total active translations: 0\n"
            "Outside interfaces:\n"
            "  None\n"
            "Inside interfaces:\n"
            "  GigabitEthernet0/0"
        ),
        "expected_fault": "NAT",
        "expected_root_cause": "The outside interface GigabitEthernet0/1 is missing the 'ip nat outside' command, so R1 never triggers NAT translation on egress traffic.",
        "osi_layer": "Layer 3 - Network",
        "concept": "NAT Inside/Outside Domain Identification",
        "severity": "CRITICAL",
        "expected_next_command": "show ip nat statistics",
        "expected_fix": "R1(config)# interface GigabitEthernet0/1\nR1(config-if)# ip nat outside",
        "expected_evidence": "show ip nat statistics displays 'Outside interfaces: None' and 'Total active translations: 0'.",
    },
    {
        "case_id": "NET025",
        "title": "Static NAT Mapping to Wrong Internal Host IP",
        "symptom": "External clients connecting to DMZ public IP 203.0.113.10 receive SSH prompts instead of the expected Corporate Web Portal.",
        "topology": "External Client ---> Internet ---> R1 [NAT Router] ---> DMZ Web Server (192.168.100.80) & Admin PC (192.168.100.10)",
        "device": "Router R1",
        "client_configuration": "N/A (External client hitting public IP)",
        "show_command": "show ip nat translations",
        "show_output": (
            "Pro  Inside global         Inside local          Outside local         Outside global\n"
            "---  203.0.113.10          192.168.100.10        ---                   ---\n\n"
            "R1# show running-config | include ip nat inside source static\n"
            "ip nat inside source static 192.168.100.10 203.0.113.10"
        ),
        "expected_fault": "NAT",
        "expected_root_cause": "The static NAT rule maps public IP 203.0.113.10 to 192.168.100.10 (Admin PC) instead of 192.168.100.80 (Web Server).",
        "osi_layer": "Layer 3 - Network",
        "concept": "Static 1-to-1 NAT IP Mapping & Port Forwarding",
        "severity": "HIGH",
        "expected_next_command": "show running-config | include nat",
        "expected_fix": "R1(config)# no ip nat inside source static 192.168.100.10 203.0.113.10\nR1(config)# ip nat inside source static 192.168.100.80 203.0.113.10",
        "expected_evidence": "show ip nat translations lists Inside local as 192.168.100.10 rather than web server 192.168.100.80.",
    },

    # -------------------------------------------------------------------------
    # Wireless / Guest Wi-Fi (2 Cases: NET026 - NET027)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET026",
        "title": "Guest Wi-Fi Security Leak into Corporate Private Subnets",
        "symptom": "Security audit confirms that guest laptop connected to Guest SSID can ping and access the corporate Payroll Server (10.0.10.50).",
        "topology": "Guest Laptop (192.168.99.12) ---> Access Point ---> Switch-1 [VLAN 99] ---> Core Router R1 ---> Corporate VLAN 10 (10.0.10.50)",
        "device": "Core Router R1",
        "client_configuration": "IP Address: 192.168.99.12\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.99.1\nDNS: 8.8.8.8",
        "show_command": "show running-config interface GigabitEthernet0/0.99",
        "show_output": (
            "Building configuration...\n\n"
            "interface GigabitEthernet0/0.99\n"
            " description Guest Wi-Fi Network\n"
            " encapsulation dot1Q 99\n"
            " ip address 192.168.99.1 255.255.255.0\n"
            "end\n\n"
            "R1# show access-lists GUEST_FILTER\n"
            "% No such access list: GUEST_FILTER"
        ),
        "expected_fault": "Wireless / Guest Wi-Fi",
        "expected_root_cause": "The Guest Wi-Fi subinterface lacks an ACL to deny RFC1918 internal corporate subnets, allowing normal inter-VLAN routing to deliver traffic to corporate servers.",
        "osi_layer": "Layer 3/4 - Network/Transport",
        "concept": "Guest Wi-Fi Isolation & Inter-VLAN Access Control",
        "severity": "CRITICAL",
        "expected_next_command": "show ip route 10.0.10.50",
        "expected_fix": "R1(config)# ip access-list extended GUEST_RESTRICT\nR1(config-ext-nacl)# deny ip 192.168.99.0 0.0.0.255 10.0.0.0 0.255.255.255\nR1(config-ext-nacl)# permit ip 192.168.99.0 0.0.0.255 any\nR1(config)# interface GigabitEthernet0/0.99\nR1(config-subif)# ip access-group GUEST_RESTRICT in",
        "expected_evidence": "show running-config interface Gi0/0.99 shows no ip access-group configured, leaving inter-VLAN routing unrestricted.",
    },
    {
        "case_id": "NET027",
        "title": "Lightweight Access Point Switchport Configured as Access Instead of Trunk",
        "symptom": "Lightweight Access Point (LAP) cannot establish CAPWAP tunnel with WLC; AP status LED flashes red/amber.",
        "topology": "Cisco LAP [Fa0/8] ---> Switch-1 ---> Wireless LAN Controller (WLC: 10.10.10.10)",
        "device": "Switch-1",
        "client_configuration": "N/A (Infrastructure AP device)",
        "show_command": "show interfaces FastEthernet0/8 switchport",
        "show_output": (
            "Name: Fa0/8\n"
            "Switchport: Enabled\n"
            "Administrative Mode: static access\n"
            "Operational Mode: static access\n"
            "Administrative Trunking Encapsulation: dot1q\n"
            "Negotiation of Trunking: Off\n"
            "Access Mode VLAN: 1 (default)\n"
            "Trunking Native Mode VLAN: 1 (default)\n"
            "Voice VLAN: none"
        ),
        "expected_fault": "Wireless / Guest Wi-Fi",
        "expected_root_cause": "Switchport Fa0/8 is configured as an access port in VLAN 1 instead of a trunk port carrying management VLAN 100 and multiple SSID VLANs.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "Access Point Switchport Modes (Trunk vs. Access) & Multi-SSID Tagging",
        "severity": "HIGH",
        "expected_next_command": "show interfaces FastEthernet0/8 status",
        "expected_fix": "Switch-1(config)# interface FastEthernet0/8\nSwitch-1(config-if)# switchport mode trunk\nSwitch-1(config-if)# switchport trunk native vlan 100",
        "expected_evidence": "show interfaces FastEthernet0/8 switchport shows Administrative Mode: static access and Access Mode VLAN: 1.",
    },

    # -------------------------------------------------------------------------
    # Interface / Switchport (2 Cases: NET028 - NET029)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET028",
        "title": "Switchport Interface Administratively Shutdown",
        "symptom": "Server NIC shows 'Network Cable Unplugged'; link light on switchport Fa0/24 is completely dark.",
        "topology": "Database Server ---> Switch-1 [Fa0/24]",
        "device": "Switch-1",
        "client_configuration": "IP Address: 192.168.1.100\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1",
        "show_command": "show interfaces FastEthernet0/24 status",
        "show_output": (
            "Port      Name               Status       Vlan       Duplex  Speed Type\n"
            "Fa0/24    DB-Server-Link     disabled     10         auto    auto  10/100BaseTX\n\n"
            "Switch-1# show interfaces FastEthernet0/24\n"
            "FastEthernet0/24 is administratively down, line protocol is down (disabled)\n"
            "  Hardware is Fast Ethernet, address is 0011.2233.4455"
        ),
        "expected_fault": "Interface / Switchport",
        "expected_root_cause": "Switchport Fa0/24 is administratively disabled (shutdown) in software.",
        "osi_layer": "Layer 1 - Physical",
        "concept": "Interface Administrative Status & Layer 1 Physical Link State",
        "severity": "CRITICAL",
        "expected_next_command": "show running-config interface FastEthernet0/24",
        "expected_fix": "Switch-1(config)# interface FastEthernet0/24\nSwitch-1(config-if)# no shutdown",
        "expected_evidence": "show interfaces Fa0/24 status shows 'disabled' and interface state is 'administratively down, line protocol is down'.",
    },
    {
        "case_id": "NET029",
        "title": "Port Security Violation Causing Err-Disabled State",
        "symptom": "User connected an unauthorized laptop into conference room jack; link dropped immediately and port light turned solid amber.",
        "topology": "Conference PC [Fa0/5] ---> Switch-1",
        "device": "Switch-1",
        "client_configuration": "IP Address: 10.0.5.88 (Unreachable)",
        "show_command": "show interfaces FastEthernet0/5 status",
        "show_output": (
            "Port      Name               Status       Vlan       Duplex  Speed Type\n"
            "Fa0/5     Conf-Room          err-disabled 5          auto    auto  10/100BaseTX\n\n"
            "Switch-1# show port-security interface FastEthernet0/5\n"
            "Port Security              : Enabled\n"
            "Port Status                : Secure-shutdown\n"
            "Violation Mode             : Shutdown\n"
            "Aging Time                 : 0 mins\n"
            "Aging Type                 : Absolute\n"
            "SecureStatic Address Aging : Disabled\n"
            "Maximum MAC Addresses      : 1\n"
            "Total MAC Addresses        : 1\n"
            "Configured MAC Addresses   : 1\n"
            "Sticky MAC Addresses       : 0\n"
            "Last Source Address:Vlan   : a483.e721.b90c:5\n"
            "Security Violation Count   : 1"
        ),
        "expected_fault": "Interface / Switchport",
        "expected_root_cause": "Switchport Fa0/5 triggered a port-security violation because a foreign MAC address (a483.e721.b90c) exceeded maximum allowed MAC limit (1), placing port in err-disabled state.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "Cisco Port Security Violation Actions (Shutdown/Err-disable)",
        "severity": "HIGH",
        "expected_next_command": "show port-security interface FastEthernet0/5",
        "expected_fix": "Switch-1(config)# interface FastEthernet0/5\nSwitch-1(config-if)# shutdown\nSwitch-1(config-if)# no shutdown",
        "expected_evidence": "show interfaces status reports 'err-disabled' and port-security shows 'Security Violation Count: 1' and 'Secure-shutdown'.",
    },

    # -------------------------------------------------------------------------
    # Trunking (2 Cases: NET030 - NET031)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET030",
        "title": "Trunk Link Native VLAN Mismatch",
        "symptom": "Console logs continuously spam '%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with Switch-2 GigabitEthernet0/1 (99)'.",
        "topology": "Switch-1 [Gi0/1] <==== 802.1Q Trunk ====> Switch-2 [Gi0/1]",
        "device": "Switch-1",
        "client_configuration": "N/A (Switch-to-Switch Trunk Link)",
        "show_command": "show interfaces trunk",
        "show_output": (
            "Port        Mode             Encapsulation  Status        Native vlan\n"
            "Gi0/1       on               802.1q         trunking      1\n\n"
            "Port        Vlans allowed on trunk\n"
            "Gi0/1       1-4094\n\n"
            "Switch-1# show cdp neighbors GigabitEthernet0/1 detail\n"
            "Device ID: Switch-2\n"
            "Entry address(es): 192.168.99.2\n"
            "Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet0/1\n"
            "Native VLAN: 99"
        ),
        "expected_fault": "Trunking",
        "expected_root_cause": "Native VLAN mismatch across the 802.1Q trunk link: Switch-1 uses Native VLAN 1 while Switch-2 uses Native VLAN 99, risking traffic leakage and STP loop inconsistencies.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "802.1Q Native VLAN Tagging & CDP Mismatch Detection",
        "severity": "HIGH",
        "expected_next_command": "show spanning-tree interface GigabitEthernet0/1",
        "expected_fix": "Switch-1(config)# interface GigabitEthernet0/1\nSwitch-1(config-if)# switchport trunk native vlan 99",
        "expected_evidence": "show interfaces trunk shows Native vlan 1 on Switch-1 while CDP neighbor detail confirms Native VLAN 99 on Switch-2.",
    },
    {
        "case_id": "NET031",
        "title": "Trunk Allowed VLAN List Restricts Required VLAN",
        "symptom": "PCs in Engineering VLAN 40 cannot ping colleagues in VLAN 40 across the building trunk; VLAN 10 and VLAN 20 work normally.",
        "topology": "Switch-1 [Gi0/2 Trunk] <==== Trunk ====> Switch-2 [Gi0/2 Trunk]",
        "device": "Switch-1",
        "client_configuration": "IP Address: 192.168.40.12\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.40.1",
        "show_command": "show interfaces GigabitEthernet0/2 trunk",
        "show_output": (
            "Port        Mode             Encapsulation  Status        Native vlan\n"
            "Gi0/2       on               802.1q         trunking      1\n\n"
            "Port        Vlans allowed on trunk\n"
            "Gi0/2       1-30\n\n"
            "Port        Vlans allowed and active in management domain\n"
            "Gi0/2       1,10,20,30\n\n"
            "Port        Vlans in spanning tree forwarding state and not pruned\n"
            "Gi0/2       1,10,20,30"
        ),
        "expected_fault": "Trunking",
        "expected_root_cause": "Trunk interface Gi0/2 allowed VLAN list is restricted to '1-30', explicitly filtering and dropping all traffic for VLAN 40.",
        "osi_layer": "Layer 2 - Data Link",
        "concept": "802.1Q Trunk Allowed VLAN Filtering & Pruning",
        "severity": "HIGH",
        "expected_next_command": "show running-config interface GigabitEthernet0/2",
        "expected_fix": "Switch-1(config)# interface GigabitEthernet0/2\nSwitch-1(config-if)# switchport trunk allowed vlan add 40",
        "expected_evidence": "show interfaces trunk shows 'Vlans allowed on trunk: 1-30', omitting VLAN 40.",
    },

    # -------------------------------------------------------------------------
    # IP Address Conflict (1 Case: NET032)
    # -------------------------------------------------------------------------
    {
        "case_id": "NET032",
        "title": "Duplicate IP Address Assignment Between Static Printer and Workstation",
        "symptom": "Workstation PC-Finance experiences random disconnects; Windows popup alerts 'IP Address Conflict Detected with another system on the network'.",
        "topology": "PC-Finance (192.168.1.75) and HP LaserJet (192.168.1.75) ---> Switch-1",
        "device": "PC-Finance / Switch-1",
        "client_configuration": "IP Address: 192.168.1.75\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.1.1\nDNS: 8.8.8.8",
        "show_command": "arp -a",
        "show_output": (
            "Interface: 192.168.1.75 --- 0xb\n"
            "  Internet Address      Physical Address      Type\n"
            "  192.168.1.1           00-1b-d4-c1-52-01     dynamic\n"
            "  192.168.1.75          00-11-22-aa-bb-cc     invalid (conflict)\n\n"
            "Switch-1# show mac address-table | include 192.168.1.75\n"
            "1    0011.22aa.bbcc    DYNAMIC     Fa0/11\n"
            "1    0025.b34a.9912    DYNAMIC     Fa0/19\n"
            "%SW_MATM-4-MACFLAP_NOTIF: Host 0011.22aa.bbcc in vlan 1 is flapping between port Fa0/11 and Fa0/19"
        ),
        "expected_fault": "Default Gateway",
        "expected_root_cause": "The static IP 192.168.1.75 is configured simultaneously on both PC-Finance and an HP LaserJet printer, causing ARP table flapping on Switch-1.",
        "osi_layer": "Layer 3 - Network",
        "concept": "Gratuitous ARP & Duplicate IP Detection (RFC 5227)",
        "severity": "HIGH",
        "expected_next_command": "show mac address-table",
        "expected_fix": "Reconfigure PC-Finance with an unallocated static IP address (e.g., 192.168.1.76) or switch PC-Finance to DHCP.",
        "expected_evidence": "Switch console reports MAC flapping between Fa0/11 and Fa0/19 for IP 192.168.1.75, confirming duplicate IP assignment.",
    },
]


def generate():
    with open(CASES_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for c in CASES:
            writer.writerow(c)
    print(f"Successfully generated {len(CASES)} cases into {CASES_FILE}")


if __name__ == "__main__":
    generate()
