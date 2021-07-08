import json
import sys
import subprocess

# Generates Server's Config
def server_config(server):
    client_string = ""
    for client in server["clients"]:
        client_string +=  "\n[Peer]\n"
        client_string += f"PublicKey = {client['public_key']}\n"
        client_string += f"AllowedIPs = {client['cidr']}\n"


    output = "[Interface]\n" \
            f"Address = {server['cidr']}\n"\
            f"ListenPort = {server['port']}\n"\
            f"PrivateKey = {server['private_key']}\n"\
            "MTU = 1450\n"\
            f"PostUp = iptables -A FORWARD -i {server['name']} -j ACCEPT; iptables -t nat -A POSTROUTING -o {server['name']} -j MASQUERADE\n"\
            f"PostDown = iptables -D FORWARD -i {server['name']} -j ACCEPT; iptables -t nat -D POSTROUTING -o {server['name']} -j MASQUERADE\n"\
            f"{client_string}"
    return output

# Generates Client Configs
def client_config(server):
    client_configs = []
    for client in server['clients']:
        output = f"[Interface]\n" \
                 f"Address = {client['cidr']}\n"\
                 f"PrivateKey = {client['private_key']}\n"\
                 f"DNS = 1.1.1.1\n"\
                 f"\n[Peer]\n"\
                 f"PublicKey = {server['public_key']}\n"\
                 # TODO: Proper Input is `AllowedIPs = 10.80.91.0/24`
                 # This allows all the ips from the subnet to access this device
                 f"AllowedIPs = {client['cidr']}\n"\
                 f"Endpoint = {server['public_ip']}:{server['port']}\n"\
                 f"PersistentKeepalive = 15\n"
        client_configs.append(output)
    return client_configs


def main():
    config = sys.argv[1]
    with open(config) as f:
        data = json.load(f)
        # Create Server Config
        generated_server_config = server_config(data)
        print(generated_server_config)
        print()

        # Create Clients Config
        generated_clients_config = client_config(data)
        for config in generated_clients_config:
            # Display QR Code
            out = subprocess.run(["qrencode", "-t", "utf8", config])
            print(config)

if __name__ == "__main__":
    main()
