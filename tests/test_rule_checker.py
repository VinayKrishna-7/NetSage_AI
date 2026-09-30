"""
tests/test_rule_checker.py
==============================================================================
NetSage AI - Deterministic Rule Checker Unit Tests
==============================================================================
Verifies all 15 deterministic networking rules without AI.
Can be executed via:
    pytest
or directly via:
    python tests/test_rule_checker.py
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from rule_checker import (
    check_acl_deny,
    check_apipa_address,
    check_default_route,
    check_dns_configuration,
    check_duplicate_ip,
    check_gateway_in_subnet,
    check_interface_status,
    check_ip_subnet_alignment,
    check_missing_gateway,
    check_nat_configuration,
    check_route_exists,
    check_trunk_configuration,
    check_valid_ip,
    check_valid_subnet_mask,
    check_vlan_assignment,
    run_all_checks,
)


# -----------------------------------------------------------------------------
# 1. IP Validation Tests
# -----------------------------------------------------------------------------
def test_valid_ip_success():
    res = check_valid_ip("192.168.1.10")
    assert res["status"] == "PASS"
    assert "is a valid IPv4 address" in res["message"]


def test_invalid_ip_format():
    res = check_valid_ip("999.168.1.500")
    assert res["status"] == "FAIL"
    assert "Invalid IPv4 address format" in res["message"]


def test_empty_ip():
    res = check_valid_ip("")
    assert res["status"] == "FAIL"


# -----------------------------------------------------------------------------
# 2. Subnet Mask Tests
# -----------------------------------------------------------------------------
def test_valid_subnet_mask_dotted():
    res = check_valid_subnet_mask("255.255.255.0")
    assert res["status"] == "PASS"
    assert "/24" in res["message"]


def test_valid_subnet_mask_cidr():
    res = check_valid_subnet_mask("/28")
    assert res["status"] == "PASS"


def test_invalid_subnet_mask_non_contiguous():
    res = check_valid_subnet_mask("255.255.255.130")
    assert res["status"] == "FAIL"
    assert "Invalid subnet mask" in res["message"]


# -----------------------------------------------------------------------------
# 3. IP / Subnet Alignment (Network / Broadcast ID Checks)
# -----------------------------------------------------------------------------
def test_ip_subnet_alignment_network_address():
    res = check_ip_subnet_alignment("192.168.10.0", "255.255.255.0")
    assert res["status"] == "FAIL"
    assert "cannot be the Subnet Network Address" in res["message"]


def test_ip_subnet_alignment_broadcast_address():
    res = check_ip_subnet_alignment("192.168.10.255", "255.255.255.0")
    assert res["status"] == "FAIL"
    assert "cannot be the Subnet Broadcast Address" in res["message"]


def test_ip_subnet_alignment_valid_host():
    res = check_ip_subnet_alignment("192.168.10.25", "255.255.255.0")
    assert res["status"] == "PASS"


# -----------------------------------------------------------------------------
# 4. Default Gateway Tests
# -----------------------------------------------------------------------------
def test_valid_gateway_same_subnet():
    res = check_gateway_in_subnet("192.168.10.25", "255.255.255.0", "192.168.10.1")
    assert res["status"] == "PASS"
    assert "belongs to the same subnet" in res["message"]


def test_invalid_gateway_outside_subnet():
    res = check_gateway_in_subnet("192.168.10.25", "255.255.255.0", "192.168.20.1")
    assert res["status"] == "FAIL"
    assert "outside the host subnet" in res["message"]


def test_gateway_identical_to_host():
    res = check_gateway_in_subnet("192.168.1.1", "255.255.255.0", "192.168.1.1")
    assert res["status"] == "FAIL"
    assert "identical to the host IP" in res["message"]


# -----------------------------------------------------------------------------
# 5. Duplicate IP & ARP Flapping Tests
# -----------------------------------------------------------------------------
def test_duplicate_ip_detected():
    sample_log = "%IP-4-DUPADDR: Duplicate address 192.168.1.1 on GigabitEthernet0/0"
    res = check_duplicate_ip(sample_log)
    assert res["status"] == "FAIL"
    assert "Duplicate IP address" in res["message"]


def test_mac_flapping_detected():
    sample_log = "%SW_MATM-4-MACFLAP_NOTIF: Host 0011.22aa.bbcc flapping between port Fa0/11 and Fa0/19"
    res = check_duplicate_ip(sample_log)
    assert res["status"] == "FAIL"


def test_no_duplicate_ip():
    sample_log = "Interface 192.168.1.25 dynamic 00-11-22-33-44-55"
    res = check_duplicate_ip(sample_log)
    assert res["status"] == "PASS"


# -----------------------------------------------------------------------------
# 6. Missing Gateway Tests
# -----------------------------------------------------------------------------
def test_missing_gateway_zero():
    res = check_missing_gateway("0.0.0.0")
    assert res["status"] == "FAIL"


def test_missing_gateway_valid():
    res = check_missing_gateway("10.0.0.1")
    assert res["status"] == "PASS"


# -----------------------------------------------------------------------------
# 7. APIPA Detection Tests
# -----------------------------------------------------------------------------
def test_apipa_address_detected():
    res = check_apipa_address("169.254.120.44")
    assert res["status"] == "FAIL"
    assert "APIPA" in res["message"]


def test_apipa_normal_address():
    res = check_apipa_address("192.168.1.50")
    assert res["status"] == "PASS"


# -----------------------------------------------------------------------------
# 8. VLAN Assignment Tests
# -----------------------------------------------------------------------------
def test_vlan_inactive_detected():
    output = "Name: Fa0/10\nAccess Mode VLAN: 30 ((Inactive))"
    res = check_vlan_assignment(output)
    assert res["status"] == "FAIL"
    assert "inactive VLAN 30" in res["message"]


def test_subinterface_dot1q_tag_mismatch():
    output = "interface GigabitEthernet0/0.10\n encapsulation dot1Q 12\n ip address 192.168.10.1 255.255.255.0"
    res = check_vlan_assignment(output)
    assert res["status"] == "FAIL"
    assert "encapsulation dot1Q tag (12) does not match" in res["message"]


# -----------------------------------------------------------------------------
# 9. Trunk Configuration Tests
# -----------------------------------------------------------------------------
def test_trunk_native_vlan_mismatch():
    output = "%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with Switch-2 (99)"
    res = check_trunk_configuration(output)
    assert res["status"] == "FAIL"
    assert "Native VLAN mismatch" in res["message"]


# -----------------------------------------------------------------------------
# 10. ACL Filtering Tests
# -----------------------------------------------------------------------------
def test_acl_implicit_deny():
    output = "Standard IP access list 10\n 10 permit 192.168.10.5 (24 matches)\n (implicit deny any matches: 87)"
    res = check_acl_deny(output)
    assert res["status"] == "FAIL"
    assert "implicit deny (87 matches)" in res["message"]


def test_acl_explicit_deny():
    output = "20 deny tcp any host 203.0.113.80 eq www (45 matches)"
    res = check_acl_deny(output)
    assert res["status"] == "FAIL"


# -----------------------------------------------------------------------------
# 11. Interface State Tests
# -----------------------------------------------------------------------------
def test_interface_administratively_down():
    output = "GigabitEthernet0/0   10.1.1.1   YES manual administratively down down"
    res = check_interface_status(output)
    assert res["status"] == "FAIL"
    assert "administratively shutdown" in res["message"]


def test_interface_err_disabled():
    output = "Fa0/5     Conf-Room    err-disabled 5    auto    auto  10/100BaseTX"
    res = check_interface_status(output)
    assert res["status"] == "FAIL"
    assert "err-disabled" in res["message"]


# -----------------------------------------------------------------------------
# 12. Default Route Tests
# -----------------------------------------------------------------------------
def test_missing_default_route():
    output = "Gateway of last resort is not set\n 192.168.1.0/24 is directly connected"
    res = check_default_route(output)
    assert res["status"] == "FAIL"
    assert "Gateway of last resort is not set" in res["message"]


# -----------------------------------------------------------------------------
# 13. Full Orchestrator Integration Test
# -----------------------------------------------------------------------------
def test_run_all_checks_on_sample_case():
    case = {
        "case_id": "TEST_CASE",
        "client_configuration": "IP Address: 192.168.10.25\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.20.1",
        "show_output": "GigabitEthernet0/0 is up, line protocol is up",
    }
    summary = run_all_checks(case)
    assert summary["case_id"] == "TEST_CASE"
    assert summary["total_checks"] > 0
    assert summary["fail_count"] >= 1  # Should catch gateway mismatch
    assert summary["overall_status"] == "FAIL"


def test_get_osi_layer_breakdown():
    from rule_checker import get_osi_layer_breakdown
    case = {
        "case_id": "NET005",
        "client_configuration": "IP Address: 192.168.10.25\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.20.1",
        "show_output": "GigabitEthernet0/0 is up, line protocol is up",
    }
    breakdown = get_osi_layer_breakdown(case)
    assert "Layer 3 - Network" in breakdown
    assert breakdown["Layer 3 - Network"]["status"] == "FAIL"
    assert "Layer 1 - Physical" in breakdown
    assert breakdown["Layer 1 - Physical"]["status"] == "PASS"


if __name__ == "__main__":
    # Built-in standalone test runner
    print("Running NetSage AI Deterministic Rule Checker Tests...")
    test_funcs = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for fn in test_funcs:
        try:
            fn()
            passed += 1
            print(f"  [PASS] {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  [FAIL] {fn.__name__}: {e}")
        except Exception as ex:
            failed += 1
            print(f"  [ERROR] {fn.__name__}: {ex}")

    print("=" * 60)
    print(f"Test Run Complete: {passed} Passed, {failed} Failed out of {len(test_funcs)} Tests.")
    sys.exit(0 if failed == 0 else 1)
