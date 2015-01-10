Quick Start Guide
=================

You should be able to install and try PyAlaOCL in minutes (assuming that you have a decent python environment installed and in particular pip_).

Installation
------------

Just like nearly all python packages, PyAlaOCL can be installed using pip_::

    $ pip install pyalaocl

You can also download the source from the `PyAlaOCL github project`_.

Giving it a first try
---------------------

Just launch the python interpreter and try the following statements::

    C:\joe\> python
    Python 2.7.8 ...
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pyalaocl import *
    >>> Seq("hello","world",2015).selectByKind(str)
    Seq(hello, world)

.. _pip: https://pip.pypa.io/en/latest/
.. _PyAlaOCL github project:  https://github.com/megaplanet/PyAlaOCL
