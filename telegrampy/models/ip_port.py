class IpPort:

    def __init__(self, ip_port_str: str):
        splited = ip_port_str.split(":")
        self._ip: str = splited[0]
        self._port: int = int(splited[1])
        if not (0 < self._port < 65535):
            raise Exception(f"\"{self._port}\" is not a valid port")

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port
