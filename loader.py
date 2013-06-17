import imp
import glob
import types

class Loader(object):
    
    _models = {}

    def __init__(self, pypump):
        # goes through and and populates the models with pypump
        self._pypump = pypump

        for model in glob.glob("models/*.py"):
            self.load_model(model)

    def preload(self, path):
        """ Called before the load of a plugin """
        pass # nothing to do

    def postload(self, model):
        """ Called after loading a plugin with the models """
        for klass in dir(models):
            if type(klass) in [types.ClassType]:
                klass.pump = self._pypump 

    def load_model(self, path):
        """ Loads a model from a path """
        name = self.get_name(path)
        self._models[name] = imp.load_source(name, path)

    def get_name(self, path):
        """ Gets the name from the path """
        # todo: make it work on non-unix systems
        name = path.split("/")[-1]
        name.replace(".py", "")
        return name
