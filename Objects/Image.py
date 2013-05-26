
class Image:
    
    # we need some methods to go grab the image for us.

    url = ""

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.__repr__()
