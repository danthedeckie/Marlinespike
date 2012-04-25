### Ideas and quick tests go here.

"""
   This is currently semi-working.

   PROBLEM:

   b = {} 
   a = mdict(b,{})
   b['l'] = [1,2,3]

   a['l'] -> [1,2,3]

   a['l'].append(4)

   b['l'] -> [1,2,3,4]

"""

from collections import KeysView, ValuesView, ItemsView

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


    # -- the following methods support python 3.x style dictionary views --

    def viewkeys(self):
        "od.viewkeys() -> a set-like object providing a view on od's keys"
        return KeysView(self)

    def viewvalues(self):
        "od.viewvalues() -> an object providing a view on od's values"
        return ValuesView(self)

    def viewitems(self):
        "od.viewitems() -> a set-like object providing a view on od's items"
        return ItemsView(self)


    def __getitem__(self, what):
            return self.my_data[what] if what in self.my_data else self.parent[what]

if __name__ == '__main__':
    parent = {'dir':'/users/','width':1000,'a':'aye','l':[1,2,3]}
    child = {'a':11, 'title':'page_title'}
    me = mdict(parent,child)
