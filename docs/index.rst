PyAlaOCL's Documentation
========================

PyAlaOCL is a small framework that aims to bring features *à la* OCL_
to python_ world. OCL_ refers to the **Object Constraint Language**
of UML_ (Unified Modeling Language).

PyAlaOCL does *not* provide a OCL interpreter implemented in python.
It "just" allows python programmers familiar with OCL to write expressions
*à la* OCL_ in python programs. For instance instead of writing the
following OCL_ expression::

    Set{-3,2,-1,-2,-5}->excluding(2)->forAll(x|x<0)

joe the programmer will write instead this python expression::

    >>> Set(-3,2,-1,-2,-5).excluding(2).forAll(lambda x:x<0)
    True

It is worth mentionning that while the OCL_ syntax is not
retained (python syntax can not be extended), the **power of OCL_**
is still there. Almost the full OCL_ library is supported including
features like *closure*. This makes it possible to write rather complex
traversals in a rather concise and elegant way *à la* OCL_.
Moreover some *additional operators* are also added to take profit of
python while keeping the spirit of OCL_.

And last, but not least, PyAlaOCL can (optionally) be integrated in
different python settings making it even more handy to use:

*  jinja2_ integration. PyAlaOCL expressions can be written within jinja2_
   templates, increasing the expression power of jinja2_.

*  jython_ integration. Java collections such as Set or List can be
   instrumented so that PyAlaOCL expressions work on them. This makes
   it possible to work with Java apis in a seamless way.

*  modelio_ integration. PyAlaOCL can be used in the context
   of modelio_, the open source UML_ environment, bringing *à la* OCL support to modelio_.

.. note::

   The integration with the `USE OCL`_ environment
   has been moved to its own project. See PyUseOCL_ documentation.

The code is open source, and `available at github`_.

Documentation
=============

.. toctree::
   :maxdepth: 2

   quickStart
   rationales
   features
   limitations
   jinja2Integration
   jythonIntegration
   modelioIntegration


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _OCL: http://en.wikipedia.org/wiki/Object_Constraint_Language
.. _UML: http://en.wikipedia.org/wiki/Unified_Modeling_Language
.. _python: https://www.python.org/
.. _model transformation languages: http://en.wikipedia.org/wiki/Model_transformation_language
.. _OCL specification: http://www.omg.org/spec/OCL/
.. _`USE OCL`: http://sourceforge.net/projects/useocl/
.. _PyUseOCL: http://pyuseocl.readthedocs.org
.. _jinja2: http://jinja.pocoo.org/docs/dev/
.. _jython: http://www.jython.org/
.. _modelio: http://www.modelio.org/
.. _available at github: https://github.com/megaplanet/PyAlaOCL
