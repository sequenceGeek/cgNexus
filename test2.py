
class Test:

    def __init__(self):
        self.ids = dict( (i,i) for i in range(10) )
        self._iterIDGen = None
        self.currentID = None
    
    def nextID(self):
        if self._iterIDGen:
            try:
                self.currentID = self._iterIDGen.next()
                return True
            except StopIteration:
                self._iterIDGen = None
                return False
        else:
            self._iterIDGen = self.ids.iterkeys()
            self.currentID = self._iterIDGen.next()
            return True
            
a = Test()
print a.ids
while a.nextID():
    print a.currentID
for i in a.nextID():
    print a.currentID
    
