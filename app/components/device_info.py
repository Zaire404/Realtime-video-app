class DeviceInfo():
    def __init__(self, id: int = None, name: str = None, ip: str = None, describe: str = None):
        self.id = id
        self.name = name
        self.ip = ip
        self.describe = describe
        
    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip": self.ip,
            "describe": self.describe
        }