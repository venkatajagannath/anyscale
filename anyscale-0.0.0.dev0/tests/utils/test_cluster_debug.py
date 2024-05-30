import pytest

from anyscale.utils.cluster_debug import (
    _dns_over_https_test,
    _dns_test,
    _https_test,
    _tls_test,
)


def test_dns_test():
    assert _dns_test("localhost", "127.0.0.1") is None

    mismatched_ip = _dns_test("localhost", "100.100.100.100")
    assert mismatched_ip is not None
    assert "VPN" in mismatched_ip


def test_dns_over_https_test():
    assert _dns_over_https_test("dns.google.com", "8.8.8.8") is None

    mismatched_ip = _dns_over_https_test("dns.google.com", "100.100.100.100")
    assert mismatched_ip is not None
    assert "This should never happen" in mismatched_ip


def test_tls_test():
    assert _tls_test("checkip.amazonaws.com") is None


def test_https_test():
    with pytest.raises(RuntimeError) as exc:
        _https_test("checkip.amazonaws.com")

    exc.match("Unexpected status code")
