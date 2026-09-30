"""
ai_diagnosis.py
==============================================================================
NetSage AI - AI Troubleshooting & Diagnosis Engine
==============================================================================
Supports two modes:
 1. MOCK MODE (Default, Zero-cost, Offline):
    - Uses deterministic dataset knowledge base to construct realistic AI responses.
    - Deliberately includes realistic AI misconceptions on selected cases
      (NET005, NET010, NET015, NET019, NET024, NET026) to test and demonstrate
      the mandatory Human Review and Responsible AI workflow.
 2. API MODE:
    - Calls OpenAI-compatible LLM endpoints using system prompt and structured JSON.
    - Validates JSON output against the required schema.
    - Falls back to Mock Mode if API key is absent, network fails, or output is invalid.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from config import (
    ALLOWED_CONFIDENCE,
    DIAGNOSE_PROMPT_FILE,
    MIN_CONFIDENCE_SCORE,
    MAX_CONFIDENCE_SCORE,
    NETSAGE_MODE,
    NETSAGE_MODEL,
    OPENAI_API_KEY,
    is_mock_mode,
)

# -----------------------------------------------------------------------------
# Deliberate Mock AI Errors (Demonstrating the Need for Human Review)
# -----------------------------------------------------------------------------
MOCK_AI_FLAWED_CASES: Dict[str, Dict[str, Any]] = {
    "NET005": {
        "case_id": "NET005",
        "root_cause": "DNS resolution failure: PC cannot resolve external hosts. The client DNS server should be updated to public resolver 8.8.8.8.",
        "confidence": "HIGH",
        "confidence_score": 88,
        "osi_layer": "Layer 7 - Application",
        "concept": "DNS Name Resolution",
        "evidence": [
            "Client reported symptom: 'cannot communicate with any remote subnet or Internet destination'",
            "PC1 is currently unable to reach internet domains",
        ],
        "next_commands": ["nslookup google.com", "ping 8.8.8.8"],
        "recommended_fix": "Change client DNS server to 8.8.8.8 in Windows Network Adapter settings.",
        "alternative_causes": ["Local browser cache corruption"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI confused inability to reach internet with DNS failure, overlooking that Default Gateway 192.168.20.1 is outside local subnet 192.168.10.0/24.",
    },
    "NET010": {
        "case_id": "NET010",
        "root_cause": "Upstream ISP WAN gateway is unresponsive or experiencing a provider outage.",
        "confidence": "MEDIUM",
        "confidence_score": 62,
        "osi_layer": "Layer 3 - Network",
        "concept": "WAN Edge Gateway Reachability",
        "evidence": [
            "Client IP address 192.168.1.55 is assigned normally",
            "Gateway address 192.168.1.254 does not respond to ping",
        ],
        "next_commands": ["traceroute 8.8.8.8", "show ip interface brief"],
        "recommended_fix": "Contact the Internet Service Provider (ISP) to verify upstream line status.",
        "alternative_causes": ["Physical WAN cable disconnected"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI assumed 192.168.1.254 was an ISP gateway, ignoring the DHCP pool config on R1 where default-router was typo'd to .254 instead of .1.",
    },
    "NET015": {
        "case_id": "NET015",
        "root_cause": "NAT translation failure: The router has no active dynamic NAT mappings to translate LAN private IP 192.168.1.25 to public IP.",
        "confidence": "HIGH",
        "confidence_score": 85,
        "osi_layer": "Layer 3 - Network",
        "concept": "Network Address Translation (NAT)",
        "evidence": [
            "LAN host cannot ping public Internet addresses (203.0.113.2, 8.8.8.8)",
            "Local LAN interface GigabitEthernet0/0 is UP",
        ],
        "next_commands": ["show ip nat translations", "show ip nat statistics"],
        "recommended_fix": "R1(config)# ip nat inside source list 1 interface Serial0/0/0 overload",
        "alternative_causes": ["ISP ACL blocking outbound packets"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI blamed NAT, missing that edge router R1 explicitly shows 'Gateway of last resort is not set' (missing default route 0.0.0.0/0).",
    },
    "NET019": {
        "case_id": "NET019",
        "root_cause": "802.1Q Inter-VLAN Trunking failure: Switch-1 trunk port is failing to forward VLAN 20 frames across the backbone.",
        "confidence": "HIGH",
        "confidence_score": 81,
        "osi_layer": "Layer 2 - Data Link",
        "concept": "802.1Q Inter-VLAN Trunking",
        "evidence": [
            "PC1 is in VLAN 10 and cannot ping Server in VLAN 20",
            "Gateway 192.168.10.1 responds to ping",
        ],
        "next_commands": ["show interfaces trunk", "show spanning-tree vlan 20"],
        "recommended_fix": "Switch-1(config-if)# switchport trunk allowed vlan add 20",
        "alternative_causes": ["Server NIC disabled"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI guessed trunking issue without checking 'show access-lists 10' which showed 87 implicit deny matches blocking host 192.168.10.10.",
    },
    "NET024": {
        "case_id": "NET024",
        "root_cause": "WAN Serial interface link failure: Upstream WAN provider link line protocol is down.",
        "confidence": "HIGH",
        "confidence_score": 79,
        "osi_layer": "Layer 1 - Physical",
        "concept": "WAN Interface Physical Connectivity",
        "evidence": [
            "Internal LAN clients cannot browse the Internet",
            "No active sessions reaching outside servers",
        ],
        "next_commands": ["show interfaces GigabitEthernet0/1", "show cdp neighbors"],
        "recommended_fix": "Check fiber/Ethernet WAN patch cable to ISP NTU equipment.",
        "alternative_causes": ["Clock rate mismatch on serial link"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI hallucinated a physical WAN link failure when Gi0/1 was UP and show ip nat statistics showed 'Outside interfaces: None' (missing ip nat outside).",
    },
    "NET026": {
        "case_id": "NET026",
        "root_cause": "Wi-Fi WPA2 pre-shared key compromise: Unauthorized guest client obtained corporate Wi-Fi credentials.",
        "confidence": "MEDIUM",
        "confidence_score": 70,
        "osi_layer": "Layer 2 - Data Link",
        "concept": "WPA2 Pre-Shared Key (PSK) Security",
        "evidence": [
            "Guest laptop has IP 192.168.99.12 and can ping Payroll Server 10.0.10.50",
        ],
        "next_commands": ["show wlan summary", "show running-config | section wlan"],
        "recommended_fix": "Rotate corporate WPA2 passphrase and re-authenticate authorized endpoints.",
        "alternative_causes": ["Rogue AP in building"],
        "needs_human_review": True,
        "_mock_note": "FLAWED: AI misidentified an authentication issue when the real cause was lack of inter-VLAN ACL isolation on Router R1.",
    },
}


def load_system_prompt() -> str:
    """Load the master diagnosis prompt from disk."""
    if DIAGNOSE_PROMPT_FILE.exists():
        return DIAGNOSE_PROMPT_FILE.read_text(encoding="utf-8")
    return (
        "You are NetSage AI, a Cisco network troubleshooting assistant. "
        "Analyze only the evidence provided and return strictly structured JSON."
    )


def build_user_prompt(case_data: Dict[str, Any]) -> str:
    """Construct the user prompt payload from case attributes."""
    return f"""Analyze this Cisco Packet Tracer networking case and output strictly the required JSON:

Case ID: {case_data.get('case_id', 'NET000')}
Title: {case_data.get('title', 'Unknown Case')}
Symptom: {case_data.get('symptom', 'No symptom specified')}
Topology: {case_data.get('topology', 'Not specified')}
Device: {case_data.get('device', 'Unknown device')}

Client Configuration:
{case_data.get('client_configuration', 'None provided')}

Show Command:
# {case_data.get('show_command', 'show version')}

Show Command Output:
{case_data.get('show_output', 'No output')}

Required JSON Schema:
{{
  "case_id": "{case_data.get('case_id', 'NET000')}",
  "root_cause": "...",
  "confidence": "LOW" | "MEDIUM" | "HIGH",
  "confidence_score": 0-100,
  "osi_layer": "...",
  "concept": "...",
  "evidence": ["..."],
  "next_commands": ["..."],
  "recommended_fix": "...",
  "alternative_causes": ["..."],
  "needs_human_review": true
}}
"""


def validate_ai_response(data: Any, case_id: str = "NET000") -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate and sanitize the AI response dictionary against project requirements.
    Ensures confidence bounds (0-100), required keys, and sets needs_human_review=True.
    """
    if not isinstance(data, dict):
        return False, "Response is not a valid JSON object.", get_fallback_diagnosis(case_id, "Non-dictionary response")

    required_keys = [
        "case_id",
        "root_cause",
        "confidence",
        "confidence_score",
        "osi_layer",
        "concept",
        "evidence",
        "next_commands",
        "recommended_fix",
        "needs_human_review",
    ]

    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"Missing required JSON keys: {missing}", get_fallback_diagnosis(case_id, f"Missing keys: {missing}")

    # Validate confidence enum
    conf = str(data.get("confidence", "MEDIUM")).upper()
    if conf not in ALLOWED_CONFIDENCE:
        conf = "MEDIUM"
    data["confidence"] = conf

    # Validate & clamp confidence score
    try:
        score = int(data.get("confidence_score", 70))
        score = max(MIN_CONFIDENCE_SCORE, min(MAX_CONFIDENCE_SCORE, score))
    except (ValueError, TypeError):
        score = 70
    data["confidence_score"] = score

    # Validate list fields
    if not isinstance(data.get("evidence"), list):
        data["evidence"] = [str(data.get("evidence", ""))]
    if not isinstance(data.get("next_commands"), list):
        data["next_commands"] = [str(data.get("next_commands", ""))]
    if not isinstance(data.get("alternative_causes"), list):
        data["alternative_causes"] = [str(data.get("alternative_causes", ""))] if "alternative_causes" in data else []

    # Mandatory Safety Enforcers
    data["needs_human_review"] = True
    data["case_id"] = str(data.get("case_id", case_id))

    return True, "Valid", data


def get_fallback_diagnosis(case_id: str, reason: str = "Fallback triggered") -> Dict[str, Any]:
    """Safe fallback diagnosis returned when AI response cannot be parsed or validated."""
    return {
        "case_id": case_id,
        "root_cause": f"Diagnosis requires manual human inspection ({reason}).",
        "confidence": "LOW",
        "confidence_score": 30,
        "osi_layer": "Undetermined",
        "concept": "Manual Verification Required",
        "evidence": ["Raw output could not be automatically validated."],
        "next_commands": ["show tech-support", "show running-config"],
        "recommended_fix": "Examine show command evidence manually in Cisco Packet Tracer.",
        "alternative_causes": ["System parser error", "Insufficient evidence"],
        "needs_human_review": True,
    }


def generate_mock_diagnosis(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an offline, high-fidelity mock AI diagnosis.
    Returns deliberate flawed diagnoses for designated cases to test human review.
    """
    case_id = str(case_data.get("case_id", "NET000")).strip()

    # Check if this case is one of our deliberate human-in-the-loop review test cases
    if case_id in MOCK_AI_FLAWED_CASES:
        flawed = dict(MOCK_AI_FLAWED_CASES[case_id])
        flawed["case_id"] = case_id
        return flawed

    # Otherwise, generate high-quality evidence-grounded diagnosis from expected case data
    show_output = str(case_data.get("show_output", ""))
    first_lines = [line.strip() for line in show_output.splitlines() if line.strip()][:3]
    evidence_cite = case_data.get("expected_evidence") or ("; ".join(first_lines) if first_lines else "Output reviewed.")

    next_cmd = case_data.get("expected_next_command") or "show running-config"
    fix_cmd = case_data.get("expected_fix") or "Apply standard Cisco IOS interface configuration."

    diagnosis = {
        "case_id": case_id,
        "root_cause": case_data.get("expected_root_cause", "Network configuration fault detected."),
        "confidence": "HIGH",
        "confidence_score": 94,
        "osi_layer": case_data.get("osi_layer", "Layer 3 - Network"),
        "concept": case_data.get("concept", "Network Protocol Verification"),
        "evidence": [
            evidence_cite,
            f"Observed on device: {case_data.get('device', 'Cisco Device')}",
        ],
        "next_commands": [next_cmd, "show ip interface brief"],
        "recommended_fix": fix_cmd,
        "alternative_causes": [
            "Hardware transceiver failure (ruled out by interface line status)",
            "Duplicate MAC/IP address collision",
        ],
        "needs_human_review": True,
    }
    return diagnosis


def call_openai_api(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Call OpenAI-compatible LLM endpoint if API key and package are available."""
    try:
        from openai import OpenAI
    except ImportError:
        # Fall back to mock if openai library is not installed
        return generate_mock_diagnosis(case_data)

    client = OpenAI(api_key=OPENAI_API_KEY)
    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(case_data)

    response = client.chat.completions.create(
        model=NETSAGE_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        parsed = json.loads(content)
        valid, msg, clean_data = validate_ai_response(parsed, case_data.get("case_id", "NET000"))
        if valid:
            return clean_data
        return generate_mock_diagnosis(case_data)
    except json.JSONDecodeError:
        return generate_mock_diagnosis(case_data)


def diagnose_case(case_data: Dict[str, Any], mode_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for AI network troubleshooting diagnosis.
    Respects mode setting ('mock' or 'api') and falls back gracefully.
    """
    active_mode = (mode_override or NETSAGE_MODE).strip().lower()

    if active_mode == "api" and OPENAI_API_KEY:
        try:
            return call_openai_api(case_data)
        except Exception as e:
            # Fall back safely on network or API error
            mock_diag = generate_mock_diagnosis(case_data)
            mock_diag["_api_error_fallback"] = str(e)
            return mock_diag
    else:
        return generate_mock_diagnosis(case_data)
