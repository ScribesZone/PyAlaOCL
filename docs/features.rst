Features
========

OCL support
-----------

Collection of classes and functions to ease the translation of OCL expressions
into python.

* =   -> ==
* x.isUndefined() -> isUndefined(x)
* x.isUndefined() -> isUndefined(x)

Number
------
* x.abs() -> abs(x)
* x.min(y) -> min(x,y)
* x.max(y) -> max(x,y)

Integer
-------
* div   /
* mod   %

Real
----
* x.floor() ->   floor(x)
* x.round() ->   round(x)

String
------
* s1.size()             -> len(s1)
* s1.contact(s2)        -> s1+s2
* s1.substring(i1,i2)   -> s1[i1,i2]   TODO: check
* s1.toUpper()          -> s1.upper()
* s1.toLower()          -> s1.lower()

Boolean
-------
* true                       -> True
* false                      -> False
* xor                        -> ^  but it must be applied between boolean
* implies                    -> \|implies|
* if c then a else b endif   -> ( a if c else b )

Enumeration
-----------
* E::x                  -> E.x

Collection
----------
* coll                  C(coll)
* coll->op(...)         C(coll).op(...)

* Set{ ... }            -> Set( ... )
* Bag{ ... }            -> Bag( ... )
* OrderedSet{ ... }     -> OrderedSet( ... )
* Sequence{ ... }       -> Seq( ... )
* Sequence {1..5, 10..20} -> Seq.new(range(1,5)+range(10,20))

UML based features
------------------
* oclIsNew              -> Not available. Can be use only with post condition
* oclAsType             -> Not necessary thanks for dynamic typing in python.


Examples
--------

.. automodule:: pyalaocl
   :members:


