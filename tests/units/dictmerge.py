'''
Unit Tests for marlinespike.useful.dictmerge


'''

from unittest import TestCase
from copy import deepcopy
from marlinespike.useful import dictmerge as dm

base = {
    'name': 'PAGE',
    'weight': 42,
    'tags': ['cool','stuff'],
    'images': {
        'A': {'url':'blah.jpg','alt':'Blah...' },
        'B': {'url':'tomato.jpg','alt':'Sauce'} }
    }

############################################

class TestBasics(TestCase):
    ' test throwing empty and non-modifying dicts at dictmerge '

    def test_empty(self):
        self.assertEqual({}, dm({}, {}))

    def test_empty_additions(self):
        self.assertEqual(base, dm(base, {}))

    def test_empty_base(self):
        self.assertEqual(base, dm({}, base))

    def test_merge_same(self):
        self.assertEqual(base, dm(base, base))

class DMTest(TestCase):
    ''' dictmerge unit test boilerplate removal '''

    def setUp(self):
        ''' setup a copy of base to say what the end result should be '''
        self.shouldbe = deepcopy(base)

    def compare(self, against):
        ''' compare shouldbe against another dict '''
        self.assertEqual(self.shouldbe, against)

    def compareDM(self, changes):
        ''' given a changes-dict, dictmerge them,
            and compare against shouldbe '''
        self.assertEqual(self.shouldbe, dm(base, changes))

class TestNewKeys(DMTest):
    ' Test adding new keys '

    def test_newkey(self):
        self.shouldbe['number'] = 42

        self.compareDM({'number':42})

    def test_replacekey(self):
        self.shouldbe['name'] = 'King Arthur'

        self.compareDM({'name':'King Arthur'})

class TestAdd(DMTest):

    def test_listadd(self):
        self.shouldbe['tags'] = ['cool','stuff','123']

        # Single addition:
        self.compareDM({'tags+':'123'})

        # Single list-type addition:
        self.compareDM({'tags+':['123']})

    def test_stradd(self):
        self.shouldbe['name'] = 'PAGE42'

        # String addition:
        self.compareDM({'name+':'42'})

        # Number addition:
        self.compareDM({'name+':42})

        # Dict addition:
        self.shouldbe['name'] = 'PAGE{}'
        self.compareDM({'name+':{}})

    def test_numadd(self):
        # Add num to num:
        self.shouldbe['weight'] = 52

        self.compareDM({'weight+':10})

        # Add str to num:
        self.compareDM({'weight+':'10'})

        # Fail!
        with self.assertRaises(TypeError):
            self.compareDM({'weight+':'Not a Number'})

    def test_dictadd(self):
        # add a dict to a dict:
        self.shouldbe['images']['C'] = 'potato'

        self.compareDM({'images+':{'C':'potato'}})


class TestSubtract(DMTest):

    def test_listsubtract(self):
        self.shouldbe['tags'] = ['cool']

        # Single subtractition:
        self.compareDM({'tags-':'stuff'})

        # Single list-type subtractition:
        self.compareDM({'tags-':['stuff']})


    def test_pop(self):
        self.shouldbe.pop('name')
        self.compareDM({'name-':  '__pop__'})

    def test_strsubtract(self):
        self.shouldbe['name'] = 'PA'

        # String subtraction:
        self.compareDM({'name-':'GE'})

    def test_numsubtract(self):
        # Add num to num:
        self.shouldbe['weight'] = 32

        self.compareDM({'weight-': 10})

        # Remove str from num:
        self.compareDM({'weight-': '10'})

        # Fail!
        with self.assertRaises(TypeError):
            self.compareDM({'weight-':'Not a Number'})

    def test_dictsubtract(self):
        # subtract a dict from a  dict:
        self.shouldbe['images']['C'] = 'potato'

        self.compareDM({'images+':{'C':'potato'}})
