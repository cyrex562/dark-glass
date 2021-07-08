from itertools import repeat
from pprint import pprint
from exceptions import CountException, ValidationError

class Config:
    def __init__(self, path=None):
        self.path = path
        self.config = {'[Interface]': 'Header',
                       'Address': '',
                       'ListenPort': '',
                       'PrivateKey': '',
                       'PostUp': '',
                       'PostDown': ''
                       }
        self.peer = {'\n[Peer]': 'Header',
                     '#': '',
                     'PublicKey': '',
                     'AllowedIPs': ''
                     }
        self.str_config = ''
        self.address = None
        self.name = None

    def create(self, address: str, name, port: int, private_key: str):
        if self.path is not None:
            raise FileExistsError
        self.name = name
        self.address = address
        up, down = self._iptables_rules()
        self.config['Address'] = address
        self.config['ListenPort'] = port
        self.config['PrivateKey'] = private_key
        self.config['PostUp'] = up
        self.config['PostDown'] = down
        self.str_config = self._generate(self.config)

    def add_peer(self, name: str, pub_key: str, ip: str):
        for value in name, pub_key, ip:
            self._validate(value)
        self.peer['#'] = name
        self.peer['PublicKey'] = pub_key
        self.peer['AllowedIPs'] = ip
        peer = self._generate(self.peer)
        if self.path is not None:
            with open(f'./{self.path}', 'a') as cfg:
                cfg.write(peer)
        else:
            self.str_config += peer

    def remove_peer(self, name: str) -> bool:
        counter = 0
        cfg = self._read_config()
        for item in cfg:
            if name in item:
                counter += 1
        if counter > 1:
            raise CountException('More than 1 peer found!')
        elif counter == 0:
            raise CountException('No peers found!')
        else:
            for item in cfg:        
                if name in item and counter == 1:
                    popie = cfg.index(item) - 2
                    for _ in repeat(None, 5):
                        cfg.pop(popie)
            with open(f'./{self.path}', 'w') as new_cfg:
                for item in cfg:
                    new_cfg.write(item)
            return True

    def print(self):
        print(self.str_config)

    def save(self, name: str):
        with open(f'./{name}', 'w') as file:
            file.write(self.str_config)

    def _validate(self, validator: str):
        with open(f'./{self.path}', 'r') as f:
            cfg = f.readlines()
            for line in cfg:
                if validator in line:
                    raise ValidationError(f'{validator} exsits!')

    def _read_config(self) -> list:
        if self.path is not None:
            with open(f'./{self.path}', 'r') as f:
                cfg = f.readlines()
            return cfg
        else:
            raise FileNotFoundError

    def _generate(self, config_dict: dict) -> str:
        string = ''
        for key, value in config_dict.items():
            if value == 'Header':
                string += f'{key}\n'
            elif key == '#':
                string += f'{key} {value}\n'
            else:
                string += f'{key} = {value} \n'
        return string

    def _iptables_rules(self) -> list:
        chars = ('A', 'D')
        rules = []
        for char in chars:
            rules.append(f"iptables -{char} FORWARD -i {self.address} -j ACCEPT; iptables -t nat -{char} POSTROUTING -o {self.name} -j MASQUERADE")
        return rules
