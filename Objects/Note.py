
class Note(object):
    
    content = ""
    actor = None # who posted.
    updated = None # last time this was updated
    published = None # When this was published

    # where to?
    to = []
    cc = []
    
    def comment(self, comment):
        pass

    def delete(self):
        pass

    def __repr__(self):
        return self.body
   
    def __str__(self):
        return self.__repr__()
