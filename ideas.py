### Ideas and quick tests go here.

# I don't know if this is a good idea:

class mdict():

    def __init__(self, parent, my_data):
        self.parent = parent
        self.my_data = dict(my_data)

        self.parent_keys = self.parent.viewkeys()
        self.my_keys = self.my_data.viewkeys()

    def __len__(self):
        return len(self.keys())

    def __setitem__(self, key, value):
        self.my_data[key] = value

    def __delitem__(self, key):
        if key in self.my_data:
            del(self.my_data[key])
        elif key in self.parent:
            pass
        else:
            raise KeyError(key)
   
    def pop(self, key):
        if key in self.my_data:
            return self.my_data.pop(key)
        elif key in self.parent:
            return self.parent[key]
        else:
            raise KeyError(key)

    def keys(self):
        return self.parent_keys | self.my_keys

    def __iter__(self):
        return self.keys().__iter__()

    def values(self):
        return [self[x] for x in self.keys()]

    def itervalues(self):
        return self.values.__iter__()

    def items(self):
        return zip(self.keys(), self.values())

    def iteritems(self):
        return self.items().__iter__()

    def __getitem__(self, what):
            return self.my_data[what] if what in self.my_data else self.parent[what]

if __name__ == '__main__':
    parent = {'dir':'/users/','width':1000,'a':'aye','l':[1,2,3]}
    child = {'a':11, 'title':'page_title'}
    me = mdict(parent,child)
