import json

class AbstractModel:

    __mapping = {
        "objectType":"TYPE",
        "":""
    }

    _pump = None

    def __init__(self, pypump=None, *args, **kwargs):
        """ Sets up pump instance """
        self._pump = pypump if pypump else self._pump

    def serialize(self, *args, **kwargs):
        """ Changes it from obj -> JSON """
        data = {}
        for item in dir(self):
            if item.startswith("_"):
                continue # we don't want
            
            value =  getattr(self, item)
            
            # we need to double check we're not in mapper
            item = self.remap(item)
            data[item] = value

        return json.dumps(data, *args, **kwargs)

    @staticmethod
    def unserialize(self, data, *args, **kwargs):
        """ Changes it from JSON -> obj """
        data = json.loads(data)

        klass = self(pypump=self._pump)

        for key, value in data.items():
            key = self.remap(key)
            if key is None:
                continue

            setattr(klass, key, value)            

        return klass

    def remap(self, data):
        """ Remaps """
        if data in self.__mapping.keys():
            return self.__mappping[data]
        elif data in self.__mapping.values():
            for k, v in self.__mapping.items():
                if data == v:
                    return k

        return data
