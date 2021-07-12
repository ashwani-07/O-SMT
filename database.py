class Database(object):
    def __init__(self): #Initialise database
        self.reads = 0 
        self.writes = 0
        self.db = {}

    def get(self, k):
        self.reads += 1
        return self.db.get(k, None) #return None if data for key k not available

    def put(self, k, v):
        self.writes += 1
        self.db[k] = v