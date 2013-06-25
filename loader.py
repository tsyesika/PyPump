from  compatability import *
from models import AbstractModel
import imp
import glob

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

    def postload(self, name, model):
        """ Called after loading a plugin with the models """
        for klass in dir(model):
            klass_obj = getattr(model, klass)
            if is_class(klass_obj) and issubclass(klass_obj, AbstractModel):
                klass_obj._pump = self._pypump
                setattr(self._pypump, klass, klass_obj)

    def load_model(self, path):
        """ Loads a model from a path """
        name = self.get_name(path)
        self.preload(path)
        self._models[name] = imp.load_source(name, path)
        self.postload(name, self._models[name])

    def get_name(self, path):
        """ Gets the name from the path """
        # todo: make it work on non-unix systems
        name = path.split("/")[-1]
        name = name.replace(".py", "")
        return name
