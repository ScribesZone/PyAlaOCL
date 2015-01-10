Limitations
===========
The current implementation of PyAlaOCL suffers from various limitations with respect to the OCL standard. Some limitations will remain in the further as they are linked by to the rationales behind PyAlaOCL. Other limitations may disappear in the future with further development effort.

Significant limitations
-----------------------
* **No support for OCL syntax**. Python syntax has to be used instead. For instance instead of writing `->` for operators one collections one have to write `.`.

* **No implicit context binding**. While in OCL one can write expression like `people->forAll( x > 0)` in PyAlaOCL one have to write `people.forAll(lambda p:p.x)` if x is an attribute of the Person type.

* The scope of all iterate operations is limited to the variable of the previous iteration and no other variable coming from the context are used.

* Operations cannot be applied to python built-in collections such as tuple, list and set.


Not implemented yet
-------------------
The following OCL features are not implemented yet:

* `OrderedSet` type.
* `iterate` operation on collections.
* `Tuple` type.
* Product operation.
* Multiple variables in `forAll` and `exists`.

