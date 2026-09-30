# NetSage AI - Demo Video & Presentation Script
## Timed Walkthrough for Academic Defense & Project Demonstrations (5–10 Minutes)

---

### Timing Overview
| Timestamp | Segment Title | Primary Focus & Visual |
| :--- | :--- | :--- |
| **0:00 – 1:00** | Introduction to NetSage AI | Project concept, problem statement, safety architecture |
| **1:00 – 2:00** | Explain Packet Tracer Topology | Lab scenario, devices (PC, Switch, Router), subnets |
| **2:00 – 3:00** | Show the Broken Network | Failed ping, APIPA or timeout symptoms in Packet Tracer |
| **3:00 – 4:00** | Collect Show-Command Evidence | Running CLI commands on switch/router and capturing output |
| **4:00 – 5:00** | Run Python Rule Checker | Demonstrating deterministic check on IP/gateway/VLAN |
| **5:00 – 6:00** | Run AI Diagnosis Engine | Generating structured diagnosis, confidence, and cited evidence |
| **6:00 – 7:00** | Show Human Review (HITL) | Reviewing AI output, showing deliberate error & correction |
| **7:00 – 8:00** | Apply the Fix Manually | Copying recommended Cisco IOS commands into Packet Tracer |
| **8:00 – 9:00** | Verify Connectivity | Rerunning ping/traceroute to prove problem resolution |
| **9:00 – 10:00**| Dashboard & Responsible AI Log | Agreement rate metrics, Excel export, Responsible AI log |

---

### Segment-by-Segment Script & Actions

#### 0:00 – 1:00: Introduction to NetSage AI
- **On Screen:** NetSage AI Streamlit Home Page (`1. Home`).
- **Presenter (Speaking):**
  > *"Good morning, esteemed evaluators. Today I am presenting **NetSage AI**, an AI-assisted network troubleshooting platform with mandatory human review, designed for Cisco Packet Tracer and enterprise networking labs.*
  > 
  > *In networking education, troubleshooting is challenging because symptoms can span all seven OSI layers. Many people ask: why not just ask an AI to fix it automatically? In mission-critical networks, unsupervised AI is dangerous because LLMs can hallucinate configurations and cause severe outages.*
  > 
  > *NetSage AI solves this with three core principles: First, deterministic validation using Python's `ipaddress` library; second, evidence-grounded AI advisories in structured JSON; and third, mandatory human-in-the-loop review where human engineers retain 100% control over configuration changes."*

---

#### 1:00 – 2:00: Explain the Packet Tracer Topology
- **On Screen:** Cisco Packet Tracer window displaying a Router-on-a-Stick or Gateway topology (e.g., Case `NET005`: Client Default Gateway Outside Host Subnet, or `NET001`: Access Port in Wrong VLAN).
- **Presenter (Speaking):**
  > *"Let's observe our lab topology in Cisco Packet Tracer. We have:*
  > - *Workstation PC1 on the left connected to Switch-1 FastEthernet0/2.*
  > - *Switch-1 connected via GigabitEthernet0/1 to Router R1.*
  > - *Router R1 acts as the default gateway for local subnet 192.168.10.0/24 with LAN IP 192.168.10.1.*
  > - *An external ISP connection simulated on Serial0/0/0.*
  > 
  > *In our case scenario (Case NET005), the client workstation PC1 was statically assigned IP 192.168.10.25 with subnet mask 255.255.255.0, but a user misconfigured the default gateway as 192.168.20.1."*

---

#### 2:00 – 3:00: Show the Broken Network
- **On Screen:** Packet Tracer Desktop Command Prompt on PC1.
- **Presenter (Speaking & Typing):**
  > *"Let's test connectivity. First, we run `ipconfig /all` on PC1.*
  > *We observe: IP Address 192.168.10.25, Subnet Mask 255.255.255.0, Default Gateway 192.168.20.1.*
  > 
  > *Now let's ping a peer in the same subnet: `ping 192.168.10.50`. Pings reply successfully!*
  > *Now let's attempt to ping an external address or gateway: `ping 8.8.8.8` or `ping 192.168.20.1`.*
  > *Notice that we immediately receive: 'Request timed out' and 'Destination host unreachable'. The user complains they cannot browse the Internet."*

---

#### 3:00 – 4:00: Collect Show-Command Evidence
- **On Screen:** Cisco IOS CLI on Switch-1 and Router R1.
- **Presenter (Speaking):**
  > *"As network engineers, we gather facts rather than guessing. We collect evidence:*
  > - *On PC1: `ipconfig /all` shows the IP and Gateway parameters.*
  > - *On Switch-1: `show interfaces status` confirms FastEthernet0/2 is connected and up.*
  > - *On Router R1: `show ip interface brief` confirms GigabitEthernet0/0 is 192.168.10.1 and UP/UP.*
  > 
  > *Now, we take these exact observations and input them into NetSage AI for structured diagnostic analysis."*

---

#### 4:00 – 5:00: Run Python Rule Checker
- **On Screen:** NetSage AI -> Page `3. Troubleshoot a Case` (or Page `5. Python Rule Checker`). Select Case `NET005`.
- **Presenter (Speaking):**
  > *"Now we open NetSage AI and select Case NET005. Before invoking any AI, we click **'Run Deterministic Rule Checker'**.*
  > 
  > *Watch the result: The rule checker instantly flags a **FAIL** on `gateway_mismatch`:*
  > *'Default gateway is outside the host subnet. Evidence: 192.168.20.1 is not in 192.168.10.0/24'.*
  > 
  > *This check is 100% deterministic, calculated mathematically using Python's `ipaddress` module. It proves that no generative AI was needed to catch this foundational Layer 3 boundary violation."*

---

#### 5:00 – 6:00: Run AI Diagnosis Engine
- **On Screen:** NetSage AI -> Click `Run AI Diagnosis Engine`.
- **Presenter (Speaking):**
  > *"Now, we click **'Run AI Diagnosis Engine'**. NetSage AI evaluates the symptom, topology, and command outputs.*
  > 
  > *Look at the structured JSON output rendered on screen:*
  > - *Root Cause: 'DNS resolution failure: PC cannot resolve external hosts. Update DNS to 8.8.8.8.'*
  > - *Confidence: HIGH (88%)*
  > - *OSI Layer: Layer 7 - Application*
  > 
  > *Notice something fascinating here: The AI saw the symptom 'cannot browse Internet' and hallucinated that this was a DNS failure, even suggesting we change the DNS server! This is a deliberate educational test case in our Responsible AI dataset."*

---

#### 6:00 – 7:00: Show Human Review (HITL)
- **On Screen:** Scroll down to the `Mandatory Human Review Submission` form on the same page.
- **Presenter (Speaking):**
  > *"This brings us to the most vital feature of our project: **The Human-in-the-Loop Review Gate**.*
  > 
  > *Because NetSage AI never automatically applies changes, an engineer must review this diagnosis. As the reviewer, I see that the AI is wrong. The PC cannot even reach its gateway, so DNS cannot possibly be the root cause!*
  > 
  > *I select the decision: **EDITED**.*
  > *I enter the corrected diagnosis: 'Client default gateway 192.168.20.1 is outside local subnet 192.168.10.0/24. Correct gateway to 192.168.10.1.'*
  > *I enter my engineering rationale, and click **'Save Human Review Decision'**.*
  > 
  > *The review is immediately timestamped and saved into our immutable audit database."*

---

#### 7:00 – 8:00: Apply the Fix Manually
- **On Screen:** Packet Tracer -> PC1 -> Network Configuration / IP Configuration Dialog.
- **Presenter (Speaking):**
  > *"Now we return to Cisco Packet Tracer to apply the human-verified fix manually:*
  > - *We open PC1 -> Desktop -> IP Configuration.*
  > - *We change Default Gateway from `192.168.20.1` to `192.168.10.1`.*
  > - *Notice how the student remains actively engaged in understanding the network behavior rather than blindly trusting an AI script."*

---

#### 8:00 – 9:00: Verify Connectivity
- **On Screen:** Packet Tracer Command Prompt.
- **Presenter (Speaking & Typing):**
  > *"Let's verify our repair:*
  > - *First: `ping 192.168.10.1` — Success! 4 packets sent, 4 received (0% loss).*
  > - *Second: `ping 8.8.8.8` — Success! Packets are successfully routed through Router R1 across the WAN.*
  > - *Third: `tracert 8.8.8.8` — Hop 1 is 192.168.10.1, Hop 2 is 203.0.113.2.*
  > 
  > *The network fault is completely resolved."*

---

#### 9:00 – 10:00: Show Dashboard and Responsible AI Log
- **On Screen:** NetSage AI -> Page `8. Dashboard` and Page `7. Responsible AI Log`.
- **Presenter (Speaking):**
  > *"Finally, let's inspect the **Analytics Dashboard**.*
  > 
  > *Here we see:*
  > - *Total Cases: 32 spanning VLANs, DHCP, Routing, ACLs, and NAT.*
  > - *Human Agreement Rate: 50.0%*
  > - *Human Correction Rate: 50.0%*
  > - *Notice the crucial academic distinction: Agreement Rate measures how often the human agreed with the AI, whereas Accuracy reflects grounded technical truth.*
  > 
  > *Next, on the **Responsible AI Log** page, we see 6 documented cases where AI failed and why. This provides an audit trail that instructors can use to teach students why blind reliance on AI is dangerous.*
  > 
  > *Lastly, we can click **'Generate Summary Spreadsheet'** to produce an Excel workbook with all KPIs for our viva documentation.*
  > 
  > *In conclusion, NetSage AI proves that combining deterministic Python verification with advisory AI and mandatory human review creates a safe, reliable, and academically rigorous network troubleshooting framework. Thank you, and I look forward to your questions."*
