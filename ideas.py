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

_temp_specials_list_ = ['__setattr__','len','parent_data','own_data','__str__',
                        '_make_local','__setitem__','append']

class mutant(object):
    """ a list [] or dict {} type of data structure which takes another list or dict as
        it's "parent".  until you try to change an element in the list,
        it will not copy the list, but reference the parent.  When you
        change something, then a new copy is made. """

    own_data = False
    parent_data = []

    def __init__(self, parent):
       self.parent_data = parent

    def __getattribute__(self, name):
        return object.__getattribute__(self, name) \
                if name in _temp_specials_list_ else \
                    object.__getattribute__(self, 'parent_data').__getattribute__(name)

    def __getitem__(self, key):
        return self.parent_data[key]

    def len(self):
        return self.__len__()

    def __len__(self):
        return len(self.parent_data)
   
    def __str__(self):
        return self.parent_data.__str__()

    def _make_local(self):
        """ If we're still proxying to the 'parent' data,
            swap now to using our own copy. """
        if not self.own_data:
            object.__setattr__(self,'own_data', True)
            object.__setattr__(self,'parent_data',type(self.parent_data)((self.parent_data)))

    def __setattr__(self, name, value):
        self._make_local()
        if name in _temp_specials_list_:
            return object.__setattr__(self, name, value)
        else:
            self.parent_data.__setattr__(name, value)

    def __setitem__(self, key, value):
        self._make_local()
        self.parent_data[key] = value

    def append(self, value):
        self._make_local()
        self.parent_data.append(value)


class mdict():
    """ a dictionary {} type data structure which has a 'parent'.
        if it's own internal dictionary doesn't have a key, then
        it will pass the request on to it's parent.

    NOTE: 

        This *doesn't* delete items from the parent if you ask it to,
        and if you try to, nothing will happen.  It will fail silently.
        """


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
        real_what = self.my_data[what] if what in self.my_data else self.parent[what] 

        # TODO something like self.my_data[what] = real_what?
        # should this be earlier? or is it better being 'lazy' like this?

        if type(real_what) in [list, dict, mutant, mdict]:
            return mutant(real_what)
        else:
            return real_what

if __name__ == '__main__':
    parent = {'dir':'/users/','width':1000,'a':'aye','l':[1,2,3]}
    child = {'a':11, 'title':'page_title'}
    me = mdict(parent,child)


    a = [1,2,3]
    b = mutant(a)

    print len(b)
