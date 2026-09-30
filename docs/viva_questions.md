# NetSage AI - Comprehensive Viva Voce Questions & Answers
## 32 Master Questions for Project Defense, Technical Evaluation, and CCNA Viva

---

### SECTION 1: SYSTEM ARCHITECTURE & PROJECT MOTIVATION

#### 1. Why did you use AI in this project?
> **Answer:** Large Language Models (LLMs) excel at contextual reasoning, synthesizing complex multi-source evidence (symptoms, topologies, and multi-line Cisco CLI outputs), and mapping natural-language complaints to networking fault domains. AI serves as an advisory assistant to rapidly narrow down potential root causes across complex topologies, reducing mean time to diagnosis (MTTD) for students and junior engineers.

#### 2. Why is human review strictly required before applying any fix?
> **Answer:** In computer networking and production infrastructure, an incorrect configuration command can cause a network partition, routing loop, or security breach. Because generative AI models can hallucinate non-existent interfaces or misdiagnose symptoms, human-in-the-loop (HITL) oversight guarantees that a qualified engineer verifies the physical and logical evidence before committing any changes.

#### 3. Why should the AI never directly apply network configurations to hardware?
> **Answer:** Automated network mutation violates the principle of least privilege and fail-safe defaults. Autonomous execution risks applying syntactically valid but topologically disastrous commands (such as an incorrect `no shutdown` or misconfigured `ip access-group`). Keeping the AI advisory preserves human responsibility and prevents automated cascading failures.

#### 4. What is AI hallucination in the context of network troubleshooting?
> **Answer:** Hallucination occurs when an LLM asserts facts or diagnoses that are not grounded in the provided evidence. For example, claiming "the default gateway router has no route" when `show ip route` was never executed, or claiming an interface is physically down when the output clearly shows `line protocol is up`.

#### 5. How does NetSage AI control and prevent AI hallucination?
> **Answer:** Through three mechanisms:
> 1. Strict system prompt engineering forbidding unsupported assertions and requiring verbatim citations of evidence.
> 2. Structured JSON schema enforcement with clamped confidence scores (0–100).
> 3. Running a deterministic Python rule checker before AI evaluation to catch objective mathematical and syntactic violations.

#### 6. How does the offline Mock Mode work, and why is it important?
> **Answer:** Mock mode uses a deterministic knowledge base and case dataset to simulate realistic AI responses without requiring an internet connection or paid API key. It enables seamless classroom demonstrations, academic defenses, and viva evaluations regardless of external API outages or subscription constraints.

#### 7. How did you implement deliberate AI errors in Mock Mode?
> **Answer:** We intentionally seeded 6 realistic misconceptions into selected mock cases (e.g. diagnosing a gateway subnet mismatch as a DNS failure in NET005, or blaming NAT when a default route is missing in NET015). This demonstrates that the Human Review system and Responsible AI failure logs are functional and actively catch AI mistakes.

---

### SECTION 2: NETWORKING CONCEPTS & CISCO LABS

#### 8. What is the OSI Model, and why is it critical in troubleshooting?
> **Answer:** The Open Systems Interconnection (OSI) model is a 7-layer conceptual framework for network communications:
> Layer 1 (Physical), Layer 2 (Data Link), Layer 3 (Network), Layer 4 (Transport), Layer 5 (Session), Layer 6 (Presentation), and Layer 7 (Application).
> Troubleshooting follows a structured "bottom-up" or "divide-and-conquer" approach: verifying physical cables and link states (L1) and VLANs (L2) before diagnosing IP routing (L3) or DNS resolution (L7).

#### 9. What is a VLAN, and what problem does it solve?
> **Answer:** A Virtual Local Area Network (VLAN) is a logical partition of a Layer 2 broadcast domain on a switch. VLANs segment traffic, reduce broadcast overhead, enhance network security, and isolate departmental traffic (e.g. HR in VLAN 10, Finance in VLAN 20) on shared physical switches.

#### 10. What is an 802.1Q Trunk port and Native VLAN?
> **Answer:** A trunk port carries traffic for multiple VLANs across a single physical link between switches or between a switch and router using IEEE 802.1Q frame tagging. The **Native VLAN** carries untagged frames across the trunk link. If Native VLANs mismatch on either end of a trunk (e.g., VLAN 1 vs VLAN 99), traffic can leak between broadcast domains or trigger STP loop detection alerts (`%CDP-4-NATIVE_VLAN_MISMATCH`).

#### 11. What is Inter-VLAN Routing and Router-on-a-Stick (ROAS)?
> **Answer:** Because VLANs are isolated Layer 2 broadcast domains, traffic between different VLANs must pass through a Layer 3 routing device. **Router-on-a-Stick (ROAS)** connects a router to a switch trunk port using a single physical interface divided into logical subinterfaces (e.g., `Gi0/0.10` and `Gi0/0.20`), each configured with 802.1Q encapsulation (`encapsulation dot1Q <vlan>`) and serving as the default gateway for that VLAN.

#### 12. What is DHCP, and what does an APIPA (169.254.x.x) address signify?
> **Answer:** Dynamic Host Configuration Protocol (DHCP) automatically assigns IPv4 addresses, subnet masks, default gateways, and DNS servers to client devices using the DORA (Discover, Offer, Request, Acknowledge) process. When a client cannot reach a DHCP server (due to pool exhaustion, missing `ip helper-address`, or VLAN misconfiguration), Windows assigns an **APIPA** (Automatic Private IP Addressing) address from `169.254.0.0/16`, enabling link-local communication but preventing internet routing.

#### 13. What is an `ip helper-address` and when is it required?
> **Answer:** DHCP Discover packets are sent as Layer 2/3 broadcasts (`255.255.255.255`). Because routers do not forward broadcasts across subnets, an `ip helper-address <DHCP_server_IP>` command configured on the router's inbound interface acts as a DHCP Relay Agent, converting the broadcast into a unicast packet directed to a central DHCP server on a remote network.

#### 14. What is DNS, and why is "DNS failure" often misdiagnosed when pinging IPs fails?
> **Answer:** Domain Name System (DNS) translates human-readable hostnames (e.g., `cisco.com`) into IP addresses (`203.0.113.80`) over UDP/TCP port 53. If a host cannot ping a raw IP address (e.g. `ping 8.8.8.8`), the problem is strictly at Layer 1–3 (cabling, IP, gateway, or routing). DNS is only involved when resolving names; asserting DNS failure when raw IP pings fail is technically impossible.

#### 15. What is Network Address Translation (NAT) and NAT Overload (PAT)?
> **Answer:** NAT translates private IPv4 addresses (RFC 1918) to public globally routable IPv4 addresses. **NAT Overload (Port Address Translation / PAT)** maps multiple internal private IP addresses to a single public IP address by assigning unique source Layer 4 TCP/UDP port numbers.

#### 16. In Cisco IOS, what is the prerequisite relationship between Routing and NAT?
> **Answer:** In Cisco IOS packet architecture, **routing table lookup occurs before NAT translation** on outbound traffic. If an edge router lacks a default route (`0.0.0.0/0`), the router immediately discards outbound packets with no route to host; NAT translation counters will never increment.

#### 17. What is an Access Control List (ACL), and what is the Implicit Deny rule?
> **Answer:** An ACL is an ordered list of permit or deny statements applied to router interfaces to filter packets based on Layer 3 addresses and Layer 4 port numbers. At the very end of every Cisco ACL resides an unseen **implicit deny all** statement (`deny ip any any`). Any packet that does not match an explicit permit statement is silently dropped.

#### 18. What is the difference between Standard and Extended ACLs?
> **Answer:** Standard ACLs (numbered 1–99 or named) filter traffic based **solely on source IP address** and should be placed close to the destination. Extended ACLs (numbered 100–199 or named) filter traffic based on **source IP, destination IP, protocol (TCP/UDP/ICMP), and port numbers (e.g. eq 80, eq 443)**, and should be placed as close to the traffic source as possible.

#### 19. What is an `err-disabled` switchport state?
> **Answer:** A Cisco switch places an interface into the `err-disabled` (error-disabled) state when software detects an operational violation, such as a port-security MAC address violation, BPDU Guard trigger, or duplex flapping. The port is shut down automatically and requires manual administrative recovery (`shutdown` followed by `no shutdown`) or errdisable auto-recovery.

#### 20. What is Gratuitous ARP and how do IP conflicts manifest?
> **Answer:** Gratuitous ARP (RFC 5227) is an ARP broadcast sent by a host announcing its own IP and MAC address to check if another system already uses that IP. If duplicate IPs exist, both hosts respond with different MACs, causing switch MAC address table flapping (`%SW_MATM-4-MACFLAP_NOTIF`) and Windows IP conflict alerts.

---

### SECTION 3: PYTHON IMPLEMENTATION & DETERMINISTIC ENGINE

#### 21. Why did you implement the Python Rule Checker without AI?
> **Answer:** Deterministic problems require deterministic solutions. Subnet boundaries, IP bitwise AND operations, and interface down states follow mathematical and logical certainties. Using Python's standard `ipaddress` library guarantees 100% mathematical precision, deterministic validation, millisecond execution time, and zero computational cost.

#### 22. What specific checks does your Python rule checker perform?
> **Answer:** It performs 15 independent checks:
> 1. Valid IPv4 syntax
> 2. Subnet mask contiguity
> 3. Network/broadcast address avoidance
> 4. Default gateway subnet containment
> 5. Duplicate IP and MAC flapping detection
> 6. Missing default gateway detection
> 7. APIPA (169.254.x.x) detection
> 8. DNS server validity and timeout detection
> 9. Inactive VLAN and dot1Q tag mismatch detection
> 10. Trunk Native VLAN mismatch and allowed list filtering
> 11. Missing routes in routing table
> 12. Missing default route (Gateway of last resort)
> 13. ACL deny matches and implicit drops
> 14. NAT missing outside interface and unpermitted subnets
> 15. Interface administratively down and err-disabled states.

#### 23. How does the `ipaddress` module calculate gateway-in-subnet membership?
> **Answer:** It instantiates an `IPv4Network` object from the host IP and subnet mask:
> `net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)`.
> Then it verifies whether the gateway address falls within the subnet: `ipaddress.IPv4Address(gateway) in net`. If false, a FAIL verdict is returned.

#### 24. How did you structure your unit tests, and can they run without pytest?
> **Answer:** Unit tests are located in `tests/test_rule_checker.py` and `tests/test_system_integration.py`. While they are fully compatible with `pytest`, we also built a standalone Python runner (`if __name__ == '__main__':`) that executes all tests and returns exit code 0 or 1, ensuring maximum portability.

---

### SECTION 4: METRICS, GOVERNANCE & RESPONSIBLE AI

#### 25. What is the difference between AI Agreement Rate and AI Accuracy?
> **Answer:** 
> - **AI Agreement Rate** is the percentage of reviewed cases where the human reviewer marked the AI diagnosis as `ACCEPTED` ($$\frac{\text{Accepted}}{\text{Total Reviewed}} \times 100$$). It measures alignment between human judgment and AI output.
> - **AI Accuracy** measures whether the diagnosis matches objective ground truth. In cases where the AI is flawed and human reviewers mark it as `EDITED` or `REJECTED`, the agreement rate drops, which accurately reflects that the human caught the mistake.

#### 26. How is the Human Correction Rate calculated?
> **Answer:** 
> $$\text{Correction Rate} = \frac{\text{Edited Cases} + \text{Rejected Cases}}{\text{Total Reviewed Cases}} \times 100$$
> Together, Agreement Rate + Correction Rate = 100%.

#### 27. What is the Responsible AI Log and why is it included?
> **Answer:** The Responsible AI Log (`data/responsible_ai_log.csv`) explicitly documents cases where the AI produced incorrect, misleading, or hallucinated advice. Each record logs the flawed AI claim, the human decision, the corrected diagnosis, the reason the AI failed, and the engineering lesson. It demonstrates that the student understands AI limitations and system safety.

#### 28. What are the allowed human review decisions?
> **Answer:**
> - **ACCEPTED:** The reviewer confirms the AI diagnosis is technically accurate and grounded in show command evidence.
> - **EDITED:** The AI identified the general area, but missed specific details or cited wrong parameters, requiring human refinement.
> - **REJECTED:** The AI was fundamentally incorrect or hallucinated, requiring complete rejection.

#### 29. What does the AI confidence score represent?
> **Answer:** It is a score from 0 to 100 representing evidentiary certainty:
> - `80–100 (HIGH)`: Conclusive, direct proof present in CLI output (e.g., explicit deny counter or inactive port status).
> - `50–79 (MEDIUM)`: Probable cause based on symptom and partial evidence, requiring verification commands.
> - `0–49 (LOW)`: Insufficient evidence; the AI explicitly flags uncertainty and recommends next commands.

#### 30. How would you connect NetSage AI to a live OpenAI API?
> **Answer:** By copying `.env.example` to `.env`, setting `OPENAI_API_KEY=your_key_here`, and setting `NETSAGE_MODE=api`. The system automatically detects the key, switches from mock simulation to live LLM generation, validates the returned JSON against the schema, and falls back to mock mode if the API fails.

#### 31. What are the primary limitations of the current implementation?
> **Answer:** The system currently processes static text captures of show commands rather than polling live network devices via SNMP or Cisco RESTCONF/NETCONF. Additionally, parsing depends on standard Cisco IOS output formats; non-standard or vendor-specific outputs (like Juniper JunOS) require additional regex parsers.

#### 32. What is the single most important takeaway from this project?
> **Answer:** Generative AI is a powerful advisory partner, but it cannot replace foundational engineering principles. In mission-critical systems like computer networks, deterministic validation, empirical CLI evidence, and mandatory human-in-the-loop oversight are indispensable for safe, reliable operation.
