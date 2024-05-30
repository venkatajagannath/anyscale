import ipaddress
from typing import Set, Union

import pytest

from anyscale.utils.network_verification import (
    check_inbound_firewall_permissions,
    Direction,
    FirewallRule,
    Protocol,
)


@pytest.mark.parametrize(
    ("ports_in", "output"),
    [
        pytest.param(None, set(range(1, 65536)), id="None"),
        pytest.param({}, set(range(1, 65536)), id="EmptySet"),
        ({22, 443}, {22, 443}),
        ({"22-23", 443}, {22, 23, 443}),
        ({"22-23", 443, "440-443"}, {22, 23, 440, 441, 442, 443}),
        ({"1", "300"}, {1, 300}),
    ],
)
def test_firewall_rule_port_creation(ports_in: Set[Union[str, int]], output: Set[int]):
    assert (
        FirewallRule(
            protocol=Protocol.tcp,
            direction=Direction.INGRESS,
            ports=ports_in,  # type: ignore
            network=ipaddress.IPv4Network("127.0.0.0/24"),
        ).ports
        == output
    )


@pytest.mark.parametrize(
    ("protos_in", "output"),
    [
        ("tcp", "tcp"),
        ("all", "all"),
        (17, "udp"),
        ("17", "udp"),
        ("1024", "other"),
        ("gre", "other"),
    ],
)
def test_firewall_rule_protocol_resolution(protos_in: Union[str, int], output: str):
    assert (
        FirewallRule(
            protocol=Protocol.from_val(protos_in),
            direction=Direction.INGRESS,
            ports=None,
            network=ipaddress.IPv4Network("127.0.0.0/24"),
        ).protocol.value
        == output
    )


@pytest.mark.parametrize("direction", [Direction.INGRESS, Direction.EGRESS])
@pytest.mark.parametrize(
    ("firewall_ports", "wanted_ports", "result"),
    [
        pytest.param({22}, {22}, True, id="simple"),
        pytest.param(None, None, True, id="all"),
        pytest.param({22, 44}, None, False, id="MissingPorts"),
        pytest.param(["1-65535"], None, True, id="MissingZero"),
        pytest.param(
            ["1-65535"], set(range(65536)), True, id="AccidentallyWantPortZero"
        ),
    ],
)
def test_check_inbound_firewall_permissions_ports(
    firewall_ports, wanted_ports, result: bool, direction: Direction
):
    check = check_inbound_firewall_permissions(
        [
            FirewallRule(
                direction=direction,
                protocol=Protocol.tcp,
                network=ipaddress.IPv4Network("127.0.0.0/24"),
                ports=firewall_ports,
            )
        ],
        Protocol.tcp,
        wanted_ports,
        ipaddress.IPv4Network("127.0.0.0/24"),
    )
    if direction == Direction.INGRESS:
        assert check == result
    else:
        assert not check


def test_check_inbound_firewall_permissions_ports_over_several_rules():
    assert check_inbound_firewall_permissions(
        [
            FirewallRule(
                direction="INGRESS",
                protocol=Protocol.tcp,
                network=ipaddress.IPv4Network("127.0.0.0/24"),
                ports=ports,
            )
            for ports in [["20-30"], [443, 445], [2000]]
        ],
        Protocol.tcp,
        {22, 443, 2000},
        ipaddress.IPv4Network("127.0.0.0/24"),
    )


def test_check_inbound_firewall_permissions_ports_without_checking_source_range():
    assert check_inbound_firewall_permissions(
        [
            FirewallRule(
                direction="INGRESS",
                protocol=Protocol.tcp,
                network=ipaddress.IPv4Network("127.0.0.0/24"),
                ports=[22, 443],
            )
        ],
        Protocol.tcp,
        {22, 443},
        ipaddress.IPv4Network("0.0.0.0/0"),
        False,
    )


@pytest.mark.parametrize(
    ("firewall_proto", "wanted_proto", "result"),
    [
        pytest.param("all", "all", True, id="all"),
        pytest.param("all", "tcp", True, id="Overlybroad"),
        pytest.param("all", "icmp", True, id="ICMP"),
        pytest.param("tcp", "all", False, id="insufficient"),
        pytest.param("tcp", "udp", False, id="Mismatch"),
    ],
)
def test_check_inbound_firewall_permissions_protocols(
    firewall_proto: str, wanted_proto: str, result: bool
):
    assert (
        check_inbound_firewall_permissions(
            [
                FirewallRule(
                    direction=Direction.INGRESS,
                    protocol=Protocol.from_val(firewall_proto),
                    network=ipaddress.IPv4Network("127.0.0.0/24"),
                    ports=None,
                )
            ],
            Protocol.from_val(wanted_proto),
            None,
            ipaddress.IPv4Network("127.0.0.0/24"),
        )
        == result
    )


@pytest.mark.parametrize(
    ("firewall_net", "wanted_net", "result"),
    [
        pytest.param("10.0.0.0/8", "10.0.0.0/20", True, id="larger"),
        pytest.param("10.0.0.0/8", "10.0.0.0/8", True, id="exactMatch"),
        pytest.param("0.0.0.0/0", "172.23.0.0/16", True, id="AllFirewall"),
        pytest.param("0.0.0.0/0", "0.0.0.0/0", True, id="AllAll"),
        pytest.param("10.0.0.0/9", "0.0.0.0/0", False, id="WantAll"),
        pytest.param("::/0", "0.0.0.0/0", False, id="V6Firewall"),
        pytest.param("0.0.0.0/0", "::/0", False, id="V6Source"),
        pytest.param("10.0.0.0/10", "10.0.0.0/8", False, id="FirewallSmall"),
    ],
)
def test_check_inbound_firewall_permissions_networks(
    firewall_net: str, wanted_net: str, result: bool
):
    assert (
        check_inbound_firewall_permissions(
            [
                FirewallRule(
                    direction=Direction.INGRESS,
                    protocol=Protocol.all,
                    network=ipaddress.ip_network(firewall_net),
                    ports=None,
                )
            ],
            Protocol.all,
            None,
            ipaddress.ip_network(wanted_net),
        )
        == result
    )
