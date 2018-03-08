import unittest
import os
from contextlib import closing

from opengrass_config import SingletonConfig as Config



class ConfigurationTest(unittest.TestCase):

    def setUp(self):
        """ create a YAML file for testing"""
        self.filename = "config.yaml"
        with closing(open(self.filename, 'wt')) as f:
            f.write(self.content())
        # make sure the config is empty
        Config().add_to_root({}, replace=True)

    def tearDown(self):
        """ remove the yaml file"""
        try:
            os.remove(self.filename)
        except:
            pass

    def test_class_runs(self):
        """ basic smoke tests"""
        Config()

    def test_singleton(self):
        """tests singleton works"""
        s1 = Config()
        s2 = Config()

        # adding properties to s1 exists in s2
        s1.add_to_root({'KeyA': 'ValueA', 'KeyB': 'ValueB'})
        self.assertEqual(s1.get_all(), s2.get_all())
        self.assertEqual(s1.get('KeyA'), 'ValueA')
        self.assertEqual(s2.get('KeyA'), 'ValueA')
        self.assertEqual(s1.get('KeyB'), 'ValueB')
        self.assertEqual(s2.get('KeyB'), 'ValueB')

        # removing properties
        s1.remove('KeyB')
        self.assertEqual(s1.get('KeyB'), None)
        self.assertEqual(s2.get('KeyB'), None)

        # ad property to s2
        s2.set('KeyC', 'ValueC')
        self.assertEqual(s1.get('KeyC'), 'ValueC')

    def test_add_to_root(self):
        config = Config()
        testDictA = {'keyA': 'ValueA', 'KeyB': 'ValueB'}
        testDictB = {'keyC': 'ValueC', 'KeyD': 'ValueD'}
        mergeDict = {**testDictA, **testDictB}

        self.assertEqual(config.get_all(), {})
        config.add_to_root(testDictA)
        self.assertEqual(config.get_all(), testDictA)
        config.add_to_root(testDictB)
        self.assertEqual(config.get_all(), mergeDict)
        config.add_to_root({}, replace=True)
        self.assertEqual(config.get_all(), {})

        config.add_to_root(testDictA)
        self.assertEqual(config.get_all(), testDictA)

    def test_load_properties(self):
        config = Config()

        self.assertEqual(config.get_all(), {})

        # no config file
        with self.assertRaises(FileNotFoundError):
            config.load_properties("NoFile.dat")

        # not a yaml file
        _localname = "config.dat"
        with closing(open(_localname, 'wb')) as f:
            f.write(b"This is not a YAMl file\nThis file contains nonsense\n")
        with self.assertRaises(TypeError):
            config.load_properties(_localname)
        try:
            os.remove(_localname)
        except:
            pass

        # load the files (make sure we have a clean load)
        config.load_properties(self.filename, replace=True)
        self.assertEqual(config.get_all(), self.file_dict())

        # load the files with a merge
        testDictA = {'keyA': 'ValueA', 'KeyB': 'ValueB'}
        mergeDict = {**config.get_all(), **testDictA}
        #reset and load for reset = False
        Config().add_to_root({}, replace=True)
        config.add_to_root(testDictA)
        config.load_properties(self.filename, replace=False)
        self.assertEqual(config.get_all(), mergeDict)
        #reset and load for reset = True
        Config().add_to_root({}, replace=True)
        config.add_to_root(testDictA)
        config.load_properties(self.filename, replace=True)
        self.assertEqual(config.get_all(), self.file_dict())

    def test_is_key(self):
        """ Test the is_key method"""
        config = Config()

        self.assertEqual(config.get_all(), {})
        self.assertFalse(config.is_key('base'))

        config.load_properties(self.filename, replace=True)

        self.assertFalse(config.is_key('NoKey'))
        self.assertFalse(config.is_key(''))
        self.assertFalse(config.is_key(None))

        self.assertTrue(config.is_key('base'))
        self.assertTrue(config.is_key('base.dictionary'))
        self.assertTrue(config.is_key('base.dictionary.root_dir'))
        self.assertFalse(config.is_key('base.dictionary.notKey'))

    def test_get(self):
        """ Test the get with complex dictionary"""
        config = Config()
        config.load_properties(self.filename, replace=True)

        self.assertEqual(config.get(''), None)
        self.assertEqual(config.get('noValue'), None)
        self.assertEqual(config.get('noValue.noValue'), None)
        self.assertEqual(config.get('base.noValue'), None)
        self.assertEqual(config.get('base.noValue.noValue'), None)

        self.assertEqual(config.get('catalogue'), self.file_dict().get('catalogue'))
        self.assertEqual(config.get('base.dictionary'), self.file_dict().get('base').get('dictionary'))
        self.assertEqual(config.get('catalogue.activity.filename'), self.file_dict().get('catalogue').get('activity').get('filename'))
        self.assertEqual(config.get_all(), self.file_dict())

    def test_load_into_same_tree(self):
        config = Config()
        config.load_properties(self.filename, replace=True)

        self.assertEqual(config.get('base.dictionary.data_dir'), self.file_dict().get('base').get('dictionary').get('data_dir'))
        # add something to an existing branch
        config.set('base.dictionary.keyAdd1','valueAdd1')
        # add a value
        self.assertEqual(config.get('base.dictionary.keyAdd1'), 'valueAdd1')
        self.assertEqual(config.get('base.dictionary.data_dir'), self.file_dict().get('base').get('dictionary').get('data_dir'))

        # add a dict
        add_dict = {'dictionary':{'keyAdd2': 'valueAdd2', 'keyAdd3': 'valueAdd3' }}

        config.set('base.dictionary', add_dict)
        self.assertEqual(config.get('base.dictionary.keyAdd1'), 'valueAdd1')
        self.assertEqual(config.get('base.dictionary.data_dir'), self.file_dict().get('base').get('dictionary').get('data_dir'))
        self.assertEqual(config.get('base.dictionary.keyAdd2'), 'valueAdd2')
        self.assertEqual(config.get('base.dictionary.keyAdd3'), 'valueAdd3')

        config.set('base', {'newItem': 'newValue'})
        self.assertEqual(config.get('base.dictionary.data_dir'), self.file_dict().get('base').get('dictionary').get('data_dir'))
        self.assertTrue('newItem' in config.get('base'))

    def test_load_config(self):
        # Configuration
        config = Config()
        config.load_properties('~/code/projects/prod/discovery-transitioning-utils/config/base_config.yaml')
        self.assertEqual(config.get('base.directories.data_dir'), 'data')
        config.load_properties('~/code/projects/prod/discovery-transitioning-utils/config/data_config.yaml')
        self.assertEqual(config.get('base.directories.data_dir'), 'data')
        self.assertEqual(config.get('base.directories.data_catalogue'), 'data_catalogue')

    def test_replace_list(self):
        # Configuration
        config = Config()
        config.load_properties('~/code/projects/prod/discovery-transitioning-utils/config/base_config.yaml')

        config.set('base.directories', { 'keyList': ['list1', 'list2', 'list3'], 'newItem': 'newValue'})
        self.assertEqual(['list1', 'list2', 'list3'], config.get('base.directories.keyList'))
        self.assertEqual('newValue', config.get('base.directories.newItem'))
        config.set('base.directories', { 'keyList': ['list5', 'list6', 'list7'], 'newItem': 'newValue'})
        self.assertNotEqual(['list1', 'list2', 'list3'], config.get('base.directories.keyList'))
        self.assertEqual(['list5', 'list6', 'list7'], config.get('base.directories.keyList'))



    def content(self):
        return '\n'.join([r"base:",
                         r"  dictionary:",
                         r"    root_dir: '/opt/data_files'",
                         r"    data_dir: 'data'",
                         r"catalogue:",
                         r"  activity:",
                         r"    filename: 'Activity_Anonymous.csv'",
                         r"    data_catalogue:",
                         r"      remove:",
                         r"        - 'Attr01'",
                         r"        - 'Attr02'",
                         r"        - 'Attr05'",
                         r"      to_int:",
                         r"      to_category:",
                         r"        - 'Attr04'"
                        ])

    def file_dict(self):
        return {'base':
                    {'dictionary':
                         {'root_dir': '/opt/data_files',
                          'data_dir': 'data'
                          }},
                'catalogue':
                    {'activity':
                         {'filename': 'Activity_Anonymous.csv',
                          'data_catalogue':
                             {'remove': ['Attr01', 'Attr02', 'Attr05'],
                              'to_int': None,
                              'to_category': ['Attr04']
                              }}}}


if __name__ == '__main__':
    unittest.main()
