Python Project Skeleton
#########################

This product is to provide a python skeleton project that out the box is ready to go with
appropriate base files and guides


.. class:: no-web no-pdf

|pypi|


.. contents::

.. section-numbering::

Main features
=============

* Out the box python project skeleton as a template for all projects
* provides good governance and best practice from the start
* has a built-in, thread safe, fully featured configuration module
* full test coverage for the configuration package


Installation

package install
---------------

The best way to install this package is directly from the github repository using pip

.. code-block:: bash

    $ pip install -e git+https://git.repo/some_pkg.git#egg=SomeProject

if you want to upgrade your current version then using pip

.. code-block:: bash

    $ pip install --upgrade -e git+https://git.repo/some_pkg.git#egg=SomeProject


env setup
---------

The configuration class uses a default yaml file for persisted configuration values.
by default it looks for this file in your user root directory under ``.cs_cfg``.
to creat this file do the following:

.. code-block:: bash

    $ mkdir ~/.cs_cfg
    $ touch ~/.cs_cfg/base_config.yaml

it is recomended to set the permission of the file so only you can acess it:

.. code-block:: bash

    $ chmod 600 ~/.cs_cfg/base_config.yaml

Example Usage
-------------
import the libraries and load the configuration file

.. code-block:: python

    ...
    import skeleton.configuration as config
    import skeleton.discover as du

    cfg = config.SingletonConfig()
    cfg.load_properties()

To use the properties you can access those loaded or create an in memory attributes

.. code-block:: python

    # from config file
    filename = cfg.get('base.directories.root_dir')
    # set and get
    cfg.set('profile.name', 'myName')
    name = cfg.get('profile.name')

you can even load a dictionary from config and put it back into memory
```base_config.yaml``` config file

.. code-block:: yaml

    # snippet from 'base_config.yaml'
    base:
      directories:
        root_dir: '/Users/gigas64/projects'
        data_dir: 'data'
        data_files: 'files'
    ...


Python version
--------------

Python 2.6 and 2.7 are not supported.It is recommended to install against the latest Python 3.6.x whenever possible.
Python 3.6.4 or higher is the prefered version.


Change log
----------

See `CHANGELOG <https://github.com/git.repo/some_pkg/blob/master/CHANGELOG.rst>`_.


Licence
-------

BSD-3-Clause: `LICENSE <https://github.com/git.repo/some_pkg/blob/master/LICENSE.txt>`_.


Authors
-------

`Gigas64`_  (`@gigas64`_) created python-project-skeleton.


.. _pip: https://pip.pypa.io/en/stable/installing/
.. _Github API: http://developer.github.com/v3/issues/comments/#create-a-comment
.. _Gigas64: http://opengrass.io
.. _@gigas64: https://twitter.com/gigas64


.. |pypi| image:: 	https://img.shields.io/pypi/pyversions/Django.svg?style=flat-square&label=latest%20stable%20version
    :target: https://pypi.python.org/pypi
    :alt: Latest version released on PyPI

