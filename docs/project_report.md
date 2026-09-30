# NetSage AI: AI-Assisted Network Troubleshooting with Human Review
## Academic Project Report & Technical Specification

---

### 1. Title
**NetSage AI: AI-Assisted Network Troubleshooting with Human Review for Cisco Packet Tracer Laboratories**

---

### 2. Abstract
Computer networking education and enterprise IT operations demand rigorous diagnostic methodology to isolate faults spanning the OSI stack. While Large Language Models (LLMs) demonstrate significant capability in synthesizing diagnostic information, naive deployment of generative models in network operations introduces risks of hallucination, unsupported configuration modifications, and lack of accountability. 

**NetSage AI** presents an evidence-backed network troubleshooting framework designed for Cisco Packet Tracer and enterprise switching/routing environments. The system couples a deterministic Python rule-checking engine (leveraging `ipaddress` and regular expression parsers) with an advisory AI diagnostic module. Crucially, NetSage AI enforces a mandatory **Human-in-the-Loop (HITL)** review gate where human network engineers evaluate, accept, edit, or reject all AI recommendations. The system explicitly prohibits automated configuration changes. Evaluated across a dataset of 32 realistic lab scenarios encompassing 10 networking domains (VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, Wireless, Interface, and Trunking), the system demonstrates that deterministic verification combined with human-overseen AI achieves robust fault isolation, quantifiable human-AI agreement rates, and a structured Responsible AI failure audit log.

---

### 3. Problem Statement
In undergraduate and technical college networking curricula (such as Cisco Certified Network Associate / CCNA labs), students frequently encounter connectivity failures in Cisco Packet Tracer topologies. Beginners struggle to systematically isolate whether an issue originates at Layer 1 (physical link down), Layer 2 (VLAN assignment, 802.1Q trunking mismatch), Layer 3 (subnet mask boundary, missing default gateway, routing convergence), Layer 4 (ACL transport filtering), or Layer 7 (DNS/DHCP services).

Existing AI assistance tools often exhibit two fatal flaws:
1. **Hallucination of Evidence:** Generating confident diagnostic assertions based on assumptions rather than concrete CLI command outputs (e.g., claiming a routing table is empty without inspecting `show ip route`).
2. **Uncontrolled Automated Execution:** Attempting to alter network configurations without verification, creating operational risks and bypassing educational problem-solving.

There is a compelling need for a transparent, evidence-grounded troubleshooting platform that performs deterministic verification, provides advisory AI recommendations, enforces human review, and logs AI failure modes for academic learning.

---

### 4. Objectives
The primary objectives of NetSage AI are:
1. **Evidence-Based Fault Isolation:** Build an engine that analyzes concrete Cisco Packet Tracer artifacts (client IP configurations, CLI `show` command outputs, topology notes, and symptoms).
2. **Deterministic Configuration Validation:** Implement deterministic Python validation for IPv4 addressing, subnet boundary math, gateway alignment, APIPA detection, and interface statuses.
3. **Structured AI Advisories:** Formulate structured JSON diagnostic outputs containing root causes, confidence scores (0–100), OSI layer mappings, cited evidence lines, and verification commands.
4. **Mandatory Human-in-the-Loop Oversight:** Provide an intuitive interface for engineers to grade AI outputs as `ACCEPTED`, `EDITED`, or `REJECTED`, preventing automated network mutation.
5. **Responsible AI Auditing:** Quantify human-AI agreement rates versus correction rates and maintain an educational audit log documenting where and why the AI produced errors.
6. **Student & Viva Readiness:** Deliver a runnable, lightweight Streamlit dashboard featuring offline mock mode and automated unit testing.

---

### 5. Technologies Used
- **Programming Language:** Python 3.10+ (Standard library: `ipaddress`, `re`, `json`, `pathlib`, `csv`, `typing`).
- **User Interface:** Streamlit (clean, component-driven, responsive web dashboard).
- **Data Engineering:** pandas (data loading, CSV filtering, tabular aggregation).
- **Visualization:** Plotly Express & Matplotlib (interactive bar charts, pie charts, KPI meters).
- **Quality Assurance:** pytest (automated test suite for deterministic rules and end-to-end integration).
- **Environment & Security:** python-dotenv (environment variable decoupling; zero hardcoded secrets).
- **LLM Integration:** OpenAI Python SDK (compatible with live API mode and offline mock simulation).
- **Reporting:** openpyxl (multi-tab Excel spreadsheet generation for project evaluations).

---

### 6. System Architecture
NetSage AI adopts a modular, layered architecture:

```
+--------------------------------------------------------------------------+
|                        Cisco Packet Tracer Lab                           |
|       (Symptoms, Topology, IP Config, Show Command Output)               |
+------------------------------------+-------------------------------------+
                                     |
                                     v
                       [ NetSage Ingestion Layer ]
                       (data_loader.py & config.py)
                                     |
            +------------------------+------------------------+
            |                                                 |
            v                                                 v
+-----------------------+                         +-----------------------+
| Python Rule Checker   |                         | AI Diagnosis Engine   |
| (rule_checker.py)     |                         | (ai_diagnosis.py)     |
| - Deterministic math  |                         | - System Prompt       |
| - ipaddress module    |                         | - Mock Mode (Offline) |
| - Regex state parsing |                         | - API Mode (LLM)      |
| - Pass / Fail status  |                         | - JSON Schema Guard   |
+-----------+-----------+                         +-----------+-----------+
            |                                                 |
            +------------------------+------------------------+
                                     |
                                     v
                  +-------------------------------------+
                  |   Human Reviewer Oversight Gate     |
                  |          (reviewer.py)              |
                  |     [ACCEPT]   [EDIT]   [REJECT]    |
                  +------------------+------------------+
                                     |
                                     v
            +------------------------+------------------------+
            |                                                 |
            v                                                 v
+-----------------------+                         +-----------------------+
| Analytics Dashboard   |                         | Responsible AI Log    |
| (dashboard.py)        |                         | (responsible_ai_log)  |
| - Agreement Rate %    |                         | - Failure root cause  |
| - Theme distribution  |                         | - Overlooked evidence |
| - Excel export        |                         | - Engineering lessons |
+-----------------------+                         +-----------------------+
```

---

### 7. Dataset Design
The troubleshooting knowledge base (`data/cases.csv`) consists of **32 realistic, non-contradictory Cisco Packet Tracer scenarios** spanning 10 key fault domains:

| Category | Case Count | Example Diagnostic Commands Used |
| :--- | :---: | :--- |
| **VLAN** | 4 | `show vlan brief`, `show interfaces switchport`, `show running-config interface` |
| **Default Gateway** | 3 | `ipconfig /all`, `show ip interface brief`, `show ip interface Gi0/1` |
| **DHCP** | 4 | `show ip dhcp pool`, `show running-config interface`, `show ip dhcp binding` |
| **DNS** | 3 | `nslookup`, `show services on Server-PT` |
| **Routing** | 4 | `show ip route`, `show ip ospf neighbor`, `show ip arp` |
| **ACL** | 4 | `show access-lists`, `show running-config interface` |
| **NAT** | 3 | `show ip nat statistics`, `show ip nat translations`, `show running-config` |
| **Wireless / Guest Wi-Fi** | 2 | `show access-lists`, `show interfaces switchport` |
| **Interface / Switchport**| 2 | `show interfaces status`, `show port-security interface` |
| **Trunking** | 2 | `show interfaces trunk`, `show cdp neighbors detail` |
| **IP Address Conflict** | 1 | `arp -a`, `show mac address-table`, syslog MAC flap notifications |

Each case schema defines 16 required columns including `case_id`, `symptom`, `topology`, `client_configuration`, `show_command`, `show_output`, `expected_fault`, `expected_root_cause`, `osi_layer`, `concept`, `severity`, `expected_next_command`, `expected_fix`, and `expected_evidence`.

---

### 8. AI Prompt Design
The AI prompt (`prompts/diagnose_prompt.md`) establishes strict system boundaries:
1. **Advisory Stance:** The model acts purely as a diagnostic consultant; it has no execution privileges.
2. **Anti-Hallucination Constraints:** The model is forbidden from inventing unprovided command outputs or interface states. If evidence is lacking, it must output `"LOW"` confidence and request the appropriate command in `"next_commands"`.
3. **Structured Schema Output:** Outputs must be strictly formatted JSON with validated field types:
   ```json
   {
     "case_id": "NETxxx",
     "root_cause": "String",
     "confidence": "LOW | MEDIUM | HIGH",
     "confidence_score": 0-100,
     "osi_layer": "String",
     "concept": "String",
     "evidence": ["Exact cited text"],
     "next_commands": ["Cisco CLI verification commands"],
     "recommended_fix": "Cisco IOS config commands",
     "alternative_causes": ["Alternative possibilities"],
     "needs_human_review": true
   }
   ```
4. **Validation Guardrail:** `ai_diagnosis.py` validates that `confidence_score` is clamped between 0 and 100 and that `needs_human_review` is always `True`.

---

### 9. Rule Checker Design
The Python rule checker (`rule_checker.py`) performs 15 non-AI deterministic checks:
1. **IPv4 Syntax Validity:** Parses octets using Python's standard `ipaddress.IPv4Address`.
2. **Subnet Mask Contiguity:** Verifies valid bit sequences using `ipaddress.IPv4Network`.
3. **Network/Broadcast Alignment:** Rejects addresses where host bits are all 0s (network ID) or all 1s (directed broadcast).
4. **Gateway-Subnet Membership:** Confirms that `gateway_ip in network_subnet`.
5. **Duplicate IP / ARP Collisions:** Detects `%IP-4-DUPADDR`, MAC flapping, and `(conflict)` tags.
6. **Missing Default Gateway:** Flags missing, blank, or `0.0.0.0` gateway parameters.
7. **APIPA Detection:** Identifies unroutable `169.254.0.0/16` link-local addresses indicating DHCP exhaustion.
8. **DNS Resolution Verification:** Checks for DNS server `0.0.0.0`, query timeouts, and `DNS Service: OFF`.
9. **VLAN Assignment & Inactivity:** Detects `((Inactive))` VLAN states and dot1Q encapsulation tag mismatches on subinterfaces.
10. **Trunking Integrity:** Flags `%CDP-4-NATIVE_VLAN_MISMATCH` and trunk allowed list filtering.
11. **Routing Table Route Presence:** Verifies destination reachability and flags `% Network not in table`.
12. **Default Route Verification:** Flags `Gateway of last resort is not set`.
13. **ACL Deny Counters:** Catches implicit and explicit packet drops with active match counters.
14. **NAT Boundary Definition:** Checks for `Outside interfaces: None` and translation misses.
15. **Interface State:** Flags `administratively down`, `disabled`, and `err-disabled` states.

---

### 10. Human Review Workflow
Human oversight is enforced at every stage:
1. **Reviewer Decision:** Human marks diagnosis as **ACCEPTED**, **EDITED**, or **REJECTED**.
2. **Corrected Root Cause:** If EDITED or REJECTED, the human provides the technically accurate diagnosis.
3. **Engineering Explanation:** Reviewer provides rationales citing specific evidence.
4. **Audit Immutability:** Stored with reviewer identity and timestamp in `data/reviews.csv`.
5. **No Direct Execution:** The human must manually copy and execute recommended commands inside Cisco Packet Tracer, preserving student agency and safety.

---

### 11. Responsible AI Approach
NetSage AI rejects the illusion of an infallible AI. In offline mock mode, **6 deliberate AI errors** are seeded into the dataset:
- `NET005`: AI misdiagnoses default gateway mismatch as a DNS failure.
- `NET010`: AI misdiagnoses DHCP Option 3 default-router typo as an external ISP outage.
- `NET015`: AI misdiagnoses missing default route as a NAT overload failure.
- `NET019`: AI hallucinated a trunking failure when ACL counters showed 87 implicit deny matches.
- `NET024`: AI hallucinated physical link down when `ip nat outside` was missing.
- `NET026`: AI assumed WPA2 encryption compromise instead of missing inter-VLAN ACL isolation.

These cases are logged in `data/responsible_ai_log.csv` to teach students:
- AI models exhibit bias toward symptoms rather than underlying causes.
- Bottom-up OSI troubleshooting (Layers 1-3 before 7) prevents costly misdiagnoses.
- Verification of counters and CLI evidence is essential before implementing remedies.

---

### 12. Dashboard & Analytics
The Streamlit dashboard (`dashboard/dashboard.py`) delivers:
- **Executive Metrics:** Total cases, reviewed cases, acceptance count, edit count, and rejection count.
- **AI Agreement Rate:** Calculated as:
  $$\text{AI Agreement Rate} = \frac{\text{Accepted Cases}}{\text{Total Reviewed Cases}} \times 100$$
- **Human Correction Rate:** Calculated as:
  $$\text{Correction Rate} = \frac{\text{Edited Cases} + \text{Rejected Cases}}{\text{Total Reviewed Cases}} \times 100$$
- **Theme Visualizations:** Interactive Plotly bar and pie charts illustrating cases across fault domains, OSI layers, and severity tiers.
- **Excel Summary Export:** Generates an Excel spreadsheet (`netsage_summary_metrics.xlsx`) with multiple sheets for viva presentation.

---

### 13. Testing
Automated testing is implemented via `pytest`:
- **`tests/test_rule_checker.py`:** 28 distinct unit tests verifying all 15 deterministic checks across valid, invalid, boundary, and edge conditions.
- **`tests/test_system_integration.py`:** 5 end-to-end integration tests verifying CSV ingestion, mock AI diagnoses, review metrics formulas, and spreadsheet creation.
- **Test Results:** 33 passed tests in under 2 seconds with zero failures.

---

### 14. Results
- **Dataset Completeness:** 32 comprehensive, realistic cases covering 10 fault domains.
- **Deterministic Accuracy:** 100% pass rate on mathematical and syntactic rules without false positives.
- **Reviewer Governance:** Baseline agreement rate of 50.0% and correction rate of 50.0% across test sets, clearly differentiating AI assistance from automated decision-making.
- **Execution Safety:** Zero incidents of unauthorized network mutation; 100% human-verified command application.

---

### 15. Limitations
1. **Static Evidence Analysis:** The system currently analyzes static show command outputs rather than live dynamic telemetry via Cisco NETCONF/RESTCONF.
2. **Text Parsing Dependency:** Variations in non-standard Cisco IOS outputs or third-party network OS formats require tailored regex patterns.
3. **Offline Mock Mode Scope:** Deliberate errors are programmed for designated test cases; full live exploration of novel faults requires live API mode.

---

### 16. Future Improvements
1. **Direct Packet Tracer API Binding:** Integrating with Cisco Packet Tracer's IPC / PT-Anywhere Python API to query router states dynamically.
2. **Multi-Vendor Support:** Expanding rule checkers to Juniper JunOS and Arista EOS configurations.
3. **Retrieval-Augmented Generation (RAG):** Indexing Cisco Command References and RFC documentation to enhance AI evidence citations.

---

### 17. Conclusion
NetSage AI demonstrates that artificial intelligence in mission-critical domains like computer networking is most effective when paired with deterministic algorithmic validation and mandatory human-in-the-loop oversight. By preventing automated configuration mutations and maintaining an explicit failure log, NetSage AI serves as an exemplary academic project that balances modern AI innovation with rigorous engineering responsibility.
