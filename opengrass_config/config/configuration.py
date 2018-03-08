import threading
import os
from pathlib import Path
from contextlib import closing
import copy
import yaml
from ds_discovery_utils.commons.decoratorpatterns import singleton

__author__ = 'Darryl Oatridge'


class SingletonConfig(object):
    """

    A thread safe singleton configuration class that allows for both dynamic (in-memory) key/value pairs or
    persisted kay/value pairs to be stored and retrieved. The persisted values are stored in a YAML file,
    by default under a .py_cfg directory in your home path.

    the value's are stored as a tree structure with the key being a dot separated string value up the tree.
    For example key 'root.directories.base_dir' returns [str]: 'filepath' .
    Where the underlying Dictionary looks like { root: { directories: { base_dir : 'filepath' }}}.

    The key can reference any part of the tree and will return the object at that point.
    From the example above key 'root' would return [dict]: { directories: { base_dir : 'filepath' }}

    Usage: Once you have initiated the class call load_properties() to retrieve
        persistent configuration parameters from the YAML configuration file.

    """

    __properties = {}

    __DEFAULT_CONFIG = Path(Path.home(), '.cs_cfg', 'base_config.yaml')

    @singleton
    def __new__(cls):
        return super().__new__(cls)

    @classmethod
    def load_properties(self, config_file=None, replace=False) -> None:
        """ loads the properties from the yaml configuration file. allows for multiple configuration
        files to be merged into the properties dictionary, or properties to be refreshed in real time.

        :param config_file: The path and filename of the YAML file.
            default to ~/.cs_cfg/base_config.yaml
        :param replace: option to replace the existing properties
            True: removes all existing key/value pairs and replaces them with those loaded from the config file
            False: merges the existing key/value pairs with those loaded from the config file

        :raises:
            IOError: if there is a problem opening the file
            FileNotFoundError: if no file is found with the given name
        """
        if config_file is None:
            _path = self.__DEFAULT_CONFIG
        else:
            _path = Path(os.path.expanduser(config_file))
        if _path.exists() and _path.is_file():
            try:
                with closing(_path.open()) as ymlfile:
                    cfg_dict = yaml.load(ymlfile)
            except IOError as e:
                raise IOError("The configuration file {} failed to open with: {}".format(_path, e))
            try:
                self.add_to_root(cfg_dict, replace=replace)
            except TypeError:
                raise TypeError("The configuration file {} could not be loaded as a dict type".format(_path))
        else:
            raise FileNotFoundError("The configuration file {} does not exist".format(_path))

    @classmethod
    def is_key(self, key) -> bool:
        """identifies if a key exists or not.

        :param key: the key of the value
            The key should be a dot separated string of keys from root up the tree
        :return:
            True if the key exists in the properties
            False if the key doesn't exist in the properties
        """
        if key is None or len(key) == 0:
            return False
        find_dict = self.__properties
        is_path, _, is_key = key.rpartition('.')
        if len(is_path) > 0:
            for part in is_path.split('.'):
                if isinstance(find_dict, dict):
                    find_dict = find_dict.get(part, {})
                else:
                    break
        if is_key in find_dict:
            return True
        return False

    @classmethod
    def get(self, key) -> object:
        """ gets a property value for the dot separated key. The key parts must point to a dictionary

        :param key: the key of the value
            The key should be a dot separated string of keys from root up the tree

        :return:
            an object found in the key can be any structure found under that key
            if the key is not found, None is returned
            If the key is None then the complete properties dictionary is returned
            will be the full tree under the requested key, be it a value, tuple, list or dictionary
        """
        if key is None or len(key) == 0:
            return None
        rtn_val = self.__properties
        for part in key.split('.'):
            if isinstance(rtn_val, dict):
                rtn_val = rtn_val.get(part)
                if rtn_val is None: return None
            else:
                return None
        with threading.Lock():
            return copy.deepcopy(rtn_val)

    @classmethod
    def get_all(self) -> dict:
        """ gets all the properties

        :returns:
            a deep copy of the  of key/value pairs
        """
        with threading.Lock():
            return copy.deepcopy(self.__properties)

    @classmethod
    def set(self, key, value) -> None:
        """adds a new key/value pair to the in-memory configuration dictionary

        :param key: the key of the value
            The key should be a dot separated string of keys from root up the tree
        :param value: the cvalue associated with the key
        """
        if key is None or len(key) == 0:
            return
        keys = key.split('.')
        _prop_branch = self.__properties
        for idx, k in list(enumerate(keys, start=0)):
            if k in _prop_branch:
                # if the key exists move up the tree
                _prop_branch = _prop_branch[k]
                # if the k exists in the value move up also
                if isinstance(value, dict):
                    if k in value:
                        value = value[k]
            else:
                if isinstance(value, dict):
                    with threading.Lock():
                        _prop_branch.update({k:value})
                else:
                    with threading.Lock():
                        _prop_branch[k] = value
                return
        # if we are here we have fallen of the end of the key and there are still matches
        # iterate through each of the branches and add when new
        self._add_value(k, value, _prop_branch)
        return

    @classmethod
    def add_to_root(self, props_dict, replace=False) -> None:
        """adds a new set of parameters to the root of the properties tree.
        WARNING,

        :param: props_dict: The dictionary to merge.
        :param: replace: removes all properties before adding the new dictionary
            Use with caustion!!. Default is False

        :raises:
            TypeError: when the passes attribute isn't an instance of a dictionary
        """
        if not isinstance(props_dict, dict):
            raise TypeError("The passed attribute {} is not an instance of a dictionary".format(props_dict))
        with threading.Lock():
            if replace:
                with threading.Lock():
                    self.__properties.clear()
                    self.__properties.update(props_dict)
            else:
                for key in props_dict.keys():
                    self.set(key, props_dict.get(key))
        return

    @classmethod
    def remove(self, key) -> bool:
        """removes a key/value from the in-memory configuration dictionary based on the key

        :param key: the key of the key/value to be removed
            The key should be a dot separated string of keys from root up the tree

        :return:
            True if the key was removed
            False if the key was not found
        """
        del_dict = self.__properties
        del_path, _, del_key = key.rpartition('.')
        if len(del_path) > 0:
            for part in del_path.split('.'):
                if isinstance(del_dict, dict):
                    del_dict = del_dict.get(part)
                else:
                    return False
        with threading.Lock():
            del del_dict[del_key]
        return True

    @classmethod
    def _add_value(self, key, value, base) -> None:
        if key is None: return None
        for k, v in value.items():
            if isinstance(v, dict):
                if k in base:
                    base = base[k]
                    self._add_value(k, v, base)
                else:
                    with threading.Lock():
                        base.update({k:v})
            else:
                with threading.Lock():
                    base[k] = v
        return

