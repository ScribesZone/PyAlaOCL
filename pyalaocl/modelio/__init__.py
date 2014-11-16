# coding=utf-8
try:
    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio
    WITH_MODELIO = True
except:
    WITH_MODELIO = False

if WITH_MODELIO:

    __all__ = [
        'MetaInterface',
        'isMetaInterface',
        #  ...
        # THIS LIST IS EXTENDED DYNAMICALLY
        #  ...
        'allMetaClasses',
        'getMetaClass',
        'getMetaInterface',
        #
        # is<Class>()
    ]


    from pyalaocl import asSet, Invalid, registerIsKindOfFunction, \
        registerIsTypeOfFunction
    from pyalaocl.injector import export
    import pyalaocl.jython
    # noinspection PyUnresolvedReferences
    from org.modelio.vcore.smkernel.meta import SmClass
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel import Metamodel as ModelioMetamodel
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import Stereotype
    # noinspection PyUnresolvedReferences
    from java.lang import Class as JavaClass
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import Element
    # noinspection PyUnresolvedReferences
    from org.modelio.vcore.smkernel.mapi import MClass


    #--------------------------------------------------------------------------
    #  Add OCL Seq operations on JavaList returned by modelio
    #--------------------------------------------------------------------------

    def _addOCLSequenceOperationsOnModelioList():
        # noinspection PyUnresolvedReferences
        from org.eclipse.emf.common.util import EList
        # noinspection PyUnresolvedReferences
        from org.modelio.vcore.smkernel import SmList
        # noinspection PyUnresolvedReferences
        from org.modelio.vcore.smkernel import SmConstrainedList

        MODELIO_LISTS = [
            # FIXME: useless as addSuperClass does not works with inheritance
            # Another solution should probably be find
            # noinspection PyUnresolvedReferences
            EList,

            SmList,
            SmConstrainedList,
        ]

        print 'pyalaocl.modelio:'
        print '    Injecting Seq methods in Modelio list classes'
        pyalaocl.injector.addSuperclass(
            pyalaocl.jython.JavaListExtension, MODELIO_LISTS)


    #--------------------------------------------------------------------------
    #  Add on each metaclass methods:
    #  * allInstances()
    #  * named(str)
    #  * selectByAttribute(str,value)
    #  and metaclass attributes
    #  * metaFullName
    #  * metaName
    #  * metaPackage
    #  * metaClass
    #--------------------------------------------------------------------------

    def _addOperationsToAllModelioMetaInterfaces():

        def _allInstances(cls):
            """
            Return the set of all instances of a given metaclass or java meta
            interface.

            Provides both the direct instances but also instances of all
            subclasses. :return: The set all all instances, direct or indirect.
            :rtype: Set[MObject]
            """
            return asSet(_theSession().findByClass(cls))


        def _named(cls, name):
            """
            Return the only instance that have the given name.
            If there is more than one instance then raise an exception Invalid
            (MClass|Class)*String -> MObject|NameError
            """
            r = _theSession().findByAtt(cls, 'Name', name)
            if len(r) == 1:
                return r[0]
            elif len(r) == 0:
                raise Invalid('No %s named "%s"' % (cls, name))
            else:
                raise Invalid('More than one element named %s (%s elements)' \
                              % (name, str(len(r))))

        def _selectByAttribute(cls, attribute, value):
            """
            Return the list of all the instances that have the
            property set to the given value.
            NOTE: Not sure how to deal with property that are not string.
            (MClass|Class)*String*String -> List(MObject)
            EXAMPLES
              selectedInstances(DataType,"Name","string")
            """
            return asSet(_theSession().findByAtt(cls, attribute, value))

        # for some reason it is not possible to inject elements intro MClasses

        print '    Injecting class methods/attributes in ' \
              + 'Modelio MInterfaces (%s)' \
                % MetaInterface.allInstances().size()
        for mi in MetaInterface.allInstances():
            mi.metaFullName = mi.getCanonicalName()
            mi.metaName = mi.metaFullName.split('.')[-1]
            mi.metaPackage = '.'.join(mi.metaFullName.split('.')[:-1])
            mi.metaClass = getMetaClass(mi)
            mi.allInstances = classmethod(_allInstances)
            mi.named = classmethod(_named)
            mi.selectByAttribute = classmethod(_selectByAttribute)


    #--------------------------------------------------------------------------
    #  Define operations on Modelio 'Element' metaclass
    #  * .getMInterface()
    #--------------------------------------------------------------------------

    def _addOperationsToModelioElementMetaClass():

        # noinspection PyUnresolvedReferences
        from org.modelio.metamodel.uml.infrastructure import Element

        def _getMetaInterface(self):
            return self.getMClass().getJavaInterface()

        print "    Adding object methods to Element"
        Element.getMetaInterface = _getMetaInterface


    #--------------------------------------------------------------------------
    #  Define global level functions get access to modelio metamodel
    #--------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio


    class MetaInterface(object):

        @classmethod
        def allInstances(cls):
            """ Return the list of all known metaclasses as Java interfaces.
                () -> [ Class ]
                EXAMPLE:
                  for m in allMetaClasses(): print m
            """
            return allMetaClasses() \
                .collect(ModelioMetamodel.getJavaInterface).asSet()

        @classmethod
        def named(cls, name):
            return getMetaClass(name).getJavaInterface()

    def isMetaInterface(value):
        return issubclass(value, Element)


    def _theSession():
        """ Return the current session.
            () -> IModelingSession
        """
        return Modelio.getInstance().getModelingSession()


    def allMetaClasses():
        """ Return the list of all known metaclasses as MClass objects.
            () -> [ MClass ]
            EXAMPLE:
              for m in allMetaClasses(): print m
        """
        return asSet(SmClass.getRegisteredClasses())


    # def allMetaInterfaces():
    #     """ Return the list of all known metaclasses as Java interfaces.
    #         () -> [ Class ]
    #         EXAMPLE:
    #           for m in allMetaClasses(): print m
    #     """
    #    return allMetaClasses().collect(Metamodel.getJavaInterface).asSet()


    def getMetaClass(nameOrMInterfaceOrElement):
        """ Return the MClass corresponding to a name, a java interface
            or an element.
            (Class | String | Element) -> MClass
            EXAMPLES:
              print getMClass(UseCase)
              print getMClass("UseCase")
              print getMClass(myUseCase1)
        """
        if isinstance(nameOrMInterfaceOrElement, Element):
            return nameOrMInterfaceOrElement.getMClass()
        else:
            return ModelioMetamodel.getMClass(nameOrMInterfaceOrElement)


    def getMetaInterface(nameOrMClassOrElement):
        """ Return the Java Interface corresponding to a name or a MClass
            (MClass | String) -> CLass
            EXAMPLES
              print getMInterface("UseCase")
              print getMInterface(getMClass("UseCase"))
              print getMInterface(instanceNamed(DataType,"string"))
        """
        if isinstance(nameOrMClassOrElement, Element):
            return nameOrMClassOrElement.getMClass().getJavaInterface()
        elif isinstance(nameOrMClassOrElement, basestring):
            return getMetaClass(nameOrMClassOrElement).getJavaInterface()
        else:
            return nameOrMClassOrElement.getJavaInterface()


    def theMetamodelExtensions():
        """ TODO, Warning this is not a list!
        """
        return _theSession().getMetamodelExtensions()



    #--------------------------------------------------------------------------
    #  Register isKindOf and isTypeOf to main ocl module
    #--------------------------------------------------------------------------

    def _registerIsKindTypeOfFunctions():
        def _isKindOf(element, mClassOrMInterface):
            """ Check if the element is a direct  or indirect instance of a MClass
                or interface. Use isTypeOf to test if the type is exactly
                the one specified.
                EXAMPLES
                  print isKindOf(instanceNamed(DataType,"string"),Element)
                  print isKindOf(instanceNamed(DataType,"string"),UseCase)
            """
            if isinstance(mClassOrMInterface, MClass):
                mClassOrMInterface = mClassOrMInterface.getJavaInterface()
            return isinstance(element, mClassOrMInterface)


        def _isTypeOf(element, mClassOrMInterface):
            """ Check if the element has exactly the type specified, not one of
                its subtype. Use isKindOf to test if the type is exactly the one
                specified.
                EXAMPLES
                  print isTypeOf(instanceNamed(DataType,"string"),DataType)
                  print isTypeOf(instanceNamed(DataType,"string"),Element)
            """
            if isinstance(mClassOrMInterface, JavaClass):
                mClassOrMInterface = \
                    ModelioMetamodel.getMClass(mClassOrMInterface)
            try:
                return element.getMClass() is mClassOrMInterface
            except:
                return False

        registerIsKindOfFunction(_isKindOf)
        registerIsTypeOfFunction(_isTypeOf)


    #--------------------------------------------------------------------------
    #  Define global level functions get access to modelio metamodel
    #--------------------------------------------------------------------------



    def _addGlobalFunctionsIsXXXMETACLASS():
        # add global functions like isKindOfUseCase, isTypeOfClass, etc.

        def _newIsKindOfMETAINERFACE(metaInterface):
            def isKindOfMETAINTERFACE(value):
                return isinstance(value, metaInterface)
            return isKindOfMETAINTERFACE

        def _newIsTypeOfMETAINERFACE(metaInterface):
            meta_class = ModelioMetamodel.getMClass(metaInterface)

            def isTypeOfMETAINERFACE(value):
                try:
                    return value.getMClass() is meta_class
                except:
                    return False
            return isTypeOfMETAINERFACE


        for mi in MetaInterface.allInstances():
            export(globals(),
                   'isKindOf'+mi.metaName, _newIsKindOfMETAINERFACE(mi))
            export(globals(),
                   'isTypeOf'+mi.metaName, _newIsTypeOfMETAINERFACE(mi))


    _registerIsKindTypeOfFunctions()
    _addOCLSequenceOperationsOnModelioList()
    _addOperationsToAllModelioMetaInterfaces()
    _addOperationsToModelioElementMetaClass()
    _addGlobalFunctionsIsXXXMETACLASS()


