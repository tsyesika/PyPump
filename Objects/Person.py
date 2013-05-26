
class Person:
    
    id = ""
    username = ""
    display_name = ""
    url = "" # url to profile
    updated = None # Last time this was updated
    published = None # when they joined (I think?)
    location = None # place item
    summery = "" # lil bit about them =]    
    image = None # Image items

    links = [] # links to endpoints

    is_self = False # is this you?

    def follow(self): 
        """ You follow this user """
        pass

    def unfollow(self):
        """ Unfollow a user """
        pass

    def __repr__(self):
        return self.display_name

    def __str__(self):
        return self.__repr__()
