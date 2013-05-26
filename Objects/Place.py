
class Place:

    name = ""

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()

    # more will come later, I'm thinking hooks with OSM?
