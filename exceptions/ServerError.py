import json

class ServerError(Exception):
    
    def __init__(self, data, *args, **kwargs):
        data = json.loads(data)
        super(ServerError, self).__init__(data["error"], *args, **kwargs)
