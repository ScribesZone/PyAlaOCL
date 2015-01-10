Rationales
==========

The design of PyAlaOCL is due to various rationales.

Why PyAlaOCL?
-------------
While the `OCL specification`_ corresponds to a rather a cool language, not so many implementation exists. Currently OCL_ is mostly available as:
* standalone tools, such as `USE OCL`_
* OCL variants or subsets embedded in high level languages such as `model transformation languages`_ such as ATL
* OCL interpreters in java environments, most notably `OCL Eclipse`_

We are not aware of any implementation in the context of python_. Hence PyAlaOCL...

What is PyAlaOCL?
-----------------
PyAlaOCL is *not* an interpreter of the OCL_ language implemented in the python_ language. It is best described as the implementation of the OCL library for python programmers allowing them to write à la OCL expressions. While the syntax of OCL is not supported, the expressions writen using python syntax are quite close.



Rationales
----------
PyAlaOCL is developed with the following rationales in mind:

* **simplicity** : Developing
* **python integration** : the goal is to provided a
*



.. _OCL: http://en.wikipedia.org/wiki/Object_Constraint_Language
.. _python: https://www.python.org/
.. _model transformation languages: http://en.wikipedia.org/wiki/Model_transformation_language
.. _OCL specification: http://www.omg.org/spec/OCL/
.. _USE OCL: http://sourceforge.net/projects/useocl/
.. _jinja2: http://jinja.pocoo.org/docs/dev/
.. _jython: http://www.jython.org/
.. _modelio: http://www.modelio.org/
.. _OCL Eclipse:  http://www.eclipse.org/modeling/mdt/?project=ocl
