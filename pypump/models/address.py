from pypump.models import AbstractModel

class Address(AbstractModel):
    
    LIST_ENDPOINT = "/api/user/%s/lists/person"
    FOLLOWER_ENDPOINT = "/api/user/%s/followers"
    PUBLIC = {"id":"http://activityschema.org/collection/public",
              "objectType":"collection"}

    def __init__(self, id=None, name=None, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)
        self.FOLLOWERS = {"id": "https://" + self._pump.server + self.FOLLOWER_ENDPOINT % self._pump.nickname,
                     "objectType":"collection"}
        self.id = self.FOLLOWERS['id']
        self.name = name

    def createPublic(self):
        return self.PUBLIC

    def createFollowers(self):
        return self.FOLLOWERS

    def userList(self):
        return {"id":self.id, "objectType":"collection"}

    def __str__(self):
        return self.name


        
