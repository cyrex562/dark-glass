import subprocess
import os
import sys
import click
import pathlib
from typing import List, Optional


DEFAULT_KEEPALIVE = 30
DEFAULT_PORT = 51820


class InterfacePeer:
    def __init__(
        self,
        name="",
        allowed_ips=None,
        endpoint="",
        public_key="",
        persistent_keepalive=DEFAULT_KEEPALIVE,
    ):
        self.name = name
        if allowed_ips is None:
            self.allowed_ips = []
        else:
            self.allowed_ips = []
        self.endpoint = endpoint
        self.public_key = public_key
        self.persistent_keepalive = persistent_keepalive


def get_line_val(line: str) -> str:
    return line[line.find("= ") + 2 :]


class InterfaceConfig:
    def __init__(
        self,
        name="",
        address="",
        listen_port: int = 51820,
        private_key="",
        dns: Optional[List[str]] = None,
        table="",
        mtu=1500,
        pre_up="",
        post_up="",
        pre_down="",
        post_down="",
        peers: Optional[List[InterfacePeer]] = None,
    ):
        self.address: str = address
        self.name: str = name
        self.listen_port: int = listen_port
        self.private_key: str = private_key
        if dns is None:
            self.dns = []
        else:
            self.dns = dns
        self.table: str = table
        self.mtu: int = mtu
        self.pre_up: str = pre_up
        self.pre_down: str = pre_down
        self.post_down: str = post_down
        self.post_up: str = post_up
        self.peers: List[InterfacePeer] = []
        if peers is not None and len(peers) > 0:
            for p in peers:
                self.peers.append(p)

    def clear(self):
        self.address = ""
        self.name = ""
        self.listen_port = 0
        self.private_key = ""
        self.dns = []
        self.table = ""
        self.mtu = 0
        self.pre_up = ""
        self.pre_down = ""
        self.post_down = ""
        self.post_up = ""
        self.peers = []

    def from_file(self, file_name: str):
        path = pathlib.Path(file_name)
        if not path.exists():
            raise ValueError(f"interface configuration file {file_name} does not exist")
        with path.open() as fd:
            self.clear()
            curr_peer = None
            section = ""
            lines = fd.readlines()
            for line in lines:
                _line = line.strip()
                if "[Interface]" in _line:
                    section = "interface"
                elif "[Peer]" in _line:
                    if curr_peer is not None:
                        self.peers.append(curr_peer)
                    section = "peer"
                    curr_peer = InterfacePeer()
                elif "Name" in _line:
                    if section == "interface":
                        self.name = _line
                    elif section == "peer":
                        curr_peer.name = _line
                    else:
                        raise ValueError(f'line "{_line}" outside of section')
                elif "Address" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.address = get_line_val(_line)
                elif "ListenPort" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.listen_port = int(get_line_val(_line))
                elif "PrivateKey" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.private_key = get_line_val(_line)
                elif "DNS" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    vals = [x.strip() for x in get_line_val(_line).split(",")]
                    for v in vals:
                        self.dns.append(v)
                elif "Table" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.table = get_line_val(_line)
                elif "MTU" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.mtu = int(get_line_val(_line))
                elif "PreUp" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.pre_up = get_line_val(_line)
                elif "PostUp" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.post_up = get_line_val(_line)
                elif "PreDown" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.pre_down = get_line_val(_line)
                elif "PostDown" in _line:
                    if section != "interface":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    self.post_down = get_line_val(_line)
                elif "AllowedIPs" in _line:
                    if section != "peer":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    vals = [x.strip() for x in get_line_val(_line).split(",")]
                    for v in vals:
                        curr_peer.allowed_ips.append(v)
                elif "Endpoint" in _line:
                    if section != "peer":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    curr_peer.endpoint = get_line_val(_line)
                elif "PublicKey" in _line:
                    if section != "peer":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    curr_peer.public_key = get_line_val(_line)
                elif "PersistentKeepalive" in _line:
                    if section != "peer":
                        raise ValueError(f'line "{_line}" outside of interface section')
                    curr_peer.persistent_keepalive = int(get_line_val(_line))
                else:
                    # un-handled line
                    pass
            if curr_peer is not None:
                self.peers.append(curr_peer)

    def to_file(self, file_name: str = ""):
        buf = ""
        buf += "[Interface]\n"
        if self.name != "":
            if "#" not in self.name:
                buf += "# "
            buf += self.name
            buf += "\n"
        if self.address == "":
            raise ValueError("Address field cannot be empty in config file")
        buf += f"Address = {self.address}\n"
        if self.listen_port != "":
            buf += f"ListenPort = {self.listen_port}\n"
        if self.private_key == "":
            raise ValueError("PrivateKey field cannot be empty in config file")
        buf += f"PrivateKey = {self.private_key}\n"
        if len(self.dns) > 0:
            buf += f"DNS = {'.'.join(self.dns)}\n"
        if self.table != "":
            buf += f"Table = {self.table}\n"
        if self.mtu > 0:
            buf += f"MTU = {self.mtu}\n"
        if self.pre_up != "":
            buf += f"PreUp = {self.pre_up}\n"
        if self.post_up != "":
            buf += f"PostUp = {self.post_up}\n"
        if self.pre_down != "":
            buf += f"PreDown = {self.pre_down}\n"
        if self.post_down != "":
            buf += f"PostDown = {self.post_down}\n"
        buf += "\n"
        for peer in self.peers:
            buf += "[Peer]\n"
            if peer.name != "":
                if "#" not in peer.name:
                    buf += "# "
                buf += peer.name
                buf += "\n"
            if len(peer.allowed_ips) > 0:
                buf += f"AllowedIPs = {','.join(peer.allowed_ips)}\n"
            if peer.endpoint != "":
                buf += f"Endpoint = {peer.endpoint}\n"
            if peer.public_key == "":
                raise ValueError("Peer PublicKey field cannot be empty")
            buf += f"PublicKey = {peer.public_key}\n"
            if peer.persistent_keepalive > 0:
                buf += f"PersistentKeepalive = {peer.persistent_keepalive}\n"
            buf += "\n"
        if file_name != "":
            out_file = pathlib.Path(file_name)
            with out_file.open("w") as fd:
                fd.write(buf)
        else:
            sys.stdout.write(buf)


def get_public_key(private_key: str) -> str:
    output = subprocess.run(
        f"wg pubkey",
        shell=True,
        input=private_key.encode(),
        check=True,
        capture_output=True,
    )
    pub_key = output.stdout.decode().strip()
    return pub_key


def gen_priv_key() -> str:
    output = subprocess.run("wg genkey", shell=True, check=True, capture_output=True)
    priv_key = output.stdout.decode().strip()
    return priv_key


@click.group()
def cli():
    pass


@click.command()
@click.option("--ifc-cfg", default="", help="interface configuration file name")
@click.option("--srv-allow", multiple=True, help="networks to allow on the server")
@click.option("--peer-allow", multiple=True, help="networks to allow on the peer")
@click.option(
    "--peer-priv-key",
    default="",
    help="client private key to use or if blank, generate one",
)
@click.option("--endpoint", help="interface listen address and port", default="")
@click.option(
    "--keepalive",
    default=DEFAULT_KEEPALIVE,
    help="keepalive interval to use for client",
)
@click.option("--name", default="", help="optional name for the peer")
@click.option(
    "--address", help="address to use for peer in CIDR dot notation format", default=""
)
@click.option(
    "--network", help="network in use by tunnel in CIDR dot + slash prefix format"
)
@click.option("--listen", help="port for peer to listen on", default=DEFAULT_PORT)
def add_peer(
    ifc_cfg,
    srv_allow,
    peer_allow,
    peer_priv_key,
    endpoint,
    keepalive,
    name,
    address,
    listen,
    network,
):
    # find configuration file and open with configparser
    if not os.path.exists(ifc_cfg):
        raise ValueError(f"interface configuratio file {ifc_cfg} does not exist")

    peer_address = address
    net_prefix = network.split("/")[1]

    if peer_priv_key == "":
        peer_priv_key = gen_priv_key()

    # configuration file for the interface
    ifc_config = InterfaceConfig()
    ifc_config.from_file(ifc_cfg)
    new_peer = InterfacePeer()
    if name != "":
        new_peer.name = name
    new_peer.allowed_ips.append(f"{peer_address}/32")
    for a in srv_allow:
        new_peer.allowed_ips.append(a)
    new_peer.public_key = get_public_key(peer_priv_key)
    new_peer.persistent_keepalive = keepalive
    ifc_config.peers.append(new_peer)
    ifc_config.to_file(ifc_cfg)

    # configuration file for the peer
    peer_config = InterfaceConfig()
    if name != "":
        peer_config.name = name
    peer_config.listen_port = listen
    peer_config.address = f"{address}/{net_prefix}"
    peer_config.private_key = peer_priv_key

    peer_peer = InterfacePeer()
    peer_peer.public_key = get_public_key(ifc_config.private_key)
    peer_peer.endpoint = endpoint
    peer_peer.allowed_ips.append(network)
    for a in peer_allow:
        peer_peer.allowed_ips.append(a)
    peer_config.peers.append(peer_peer)
    peer_config.to_file()


cli.add_command(add_peer)


if __name__ == "__main__":
    cli()
