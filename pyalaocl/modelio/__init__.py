# coding=utf-8
try:
    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio
    WITH_MODELIO = True
except:
    WITH_MODELIO = False

if WITH_MODELIO:

    __all__ = [

        #  ...
        # THIS LIST IS EXTENDED DYNAMICALLY
        #  ...

        #----------------------------------------------------------------------
        #  Instrumentation of Modelio collections
        #----------------------------------------------------------------------

        # Class.ownedAttribute.select(...)  # ocl expressions on collection

        #----------------------------------------------------------------------
        #  MetaClass and instrumentation of MetaClasses (aka SmClass)
        #----------------------------------------------------------------------

        # UseCase    # a meta class, not a meta class (CHANGE!!!)
        #   metaClass
        #   metaInterface
        #   metaName
        #   metaPackage
        #   metaFullName
        #   metaFactory
        #   .new( ... )
        #   ( ... )         # not on interface :-(
        #   allInstances()
        #   named( name )
        #   selectByAttribute( attribute, value )

        'MetaClass',
        #   allInstances()
        #   named( name )
        #   selectByAttribute(attribute, value)
        'isMetaClass',

        #----------------------------------------------------------------------
        #  MetaInterface and instrumentation of MetaInterfaces (JavaInterfaces)
        #----------------------------------------------------------------------

        # UseCase  # was UseCase  (CHANGE!!!)
        #   metaClass
        #   metaInterface
        #   metaName
        #   metaPackage
        #   metaFullName
        #   metaIsAbstract    # isAbstract
        #   metaSuper         # return an MetaInterface
        #   metaSub           # return MetaInterfaces
        #   metaCmsNode
        #   metaFactory
        #   new(...)
        #   allInstances()
        #   named(name)
        #   selectByAttribute(attribute, value)
        #
        'MetaInterface',
        #   allInstances()
        #   named( name )
        #   selectByAttribute(attribute, value)
        'isMetaInterface',


        #----------------------------------------------------------------------
        #  Define global function isKindOfMETACLASS, isTypeOfMETACLASS
        #----------------------------------------------------------------------

        # isKindOfUseCase(value)
        # isTypeOfUseCase(value)

        #----------------------------------------------------------------------
        #  Register isKindOf and isTypeOf to main ocl module
        #----------------------------------------------------------------------

    ]

    import inspect


    import pyalaocl
    import pyalaocl.utils.injector
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
    #  Helpers
    #--------------------------------------------------------------------------


    def _theSession():
        return Modelio.getInstance().getModelingSession()


    _UML_BPMN_FACTORY = _theSession().getModel()
    _ANALYST_FACTORY = _theSession().getRequirementModel()


    def _getFactory(metaInterface):
        method_name = 'create' + metaInterface.metaName
        if hasattr(_UML_BPMN_FACTORY, method_name):
            return _UML_BPMN_FACTORY
        if hasattr(_ANALYST_FACTORY, method_name):
            return _ANALYST_FACTORY
        return None

    #--------------------------------------------------------------------------
    #  Instrumentation of Modelio collections
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

        # TODO log print 'pyalaocl.modelio:'
        # print '    Injecting Seq methods in Modelio list classes ... ',
        pyalaocl.utils.injector.addSuperclass(
            pyalaocl.jython.JavaListExtension, MODELIO_LISTS)
        # print 'done'


    def _selectByAttribute(cls, attribute, value):
            """
            Return the list of all the instances that have the
            property set to the given value.
            NOTE: Not sure how to deal with property that are not string.
            (MClass|Class)*String*String -> List(MObject)
            EXAMPLES
              selectedInstances(DataType,"Name","string")
            """
            return pyalaocl.asSet(
                _theSession().findByAtt(cls, attribute, value))




    #--------------------------------------------------------------------------
    #  MetaClass and instrumentation of MetaClasses (aka SmClass)
    #--------------------------------------------------------------------------

    def _addGlobalNameOfMetaClasses():
        for meta_class in MetaClass.allInstances():
            name = meta_class.name  # allowRedefinition is ok here
            pyalaocl.utils.injector.export(
                globals(), 'metaclass', name, meta_class,
                allowRedefinition=True)


    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaClass(metaClass):
        return metaClass

    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaInterface(metaClass):
        return metaClass.javaInterface

    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaName(metaClass):
        return metaClass.javaInterface.metaName

    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaPackage(metaClass):
        return metaClass.javaInterface.metaPackage

    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaFullName(metaClass):
        return metaClass.javaInterface.metaFullName


    @pyalaocl.utils.injector.readOnlyPropertyOf(SmClass, 'metaProperty')
    def metaFactory(metaClass):
        return metaClass.javaInterface.metaFactory

    @pyalaocl.utils.injector.methodOf(SmClass, 'metaProperty')
    def new(metaClass, *args, **kwargs):
        return metaClass.javaInterface.new(*args, **kwargs)

    @pyalaocl.utils.injector.methodOf(SmClass, 'metaProperty')
    def __call__(metaClass, *args, **kwargs):
        return metaClass.javaInterface.new(*args, **kwargs)

    @pyalaocl.utils.injector.methodOf(SmClass, 'metaProperty')
    def allInstances(metaClass):
        return metaClass.javaInterface.allInstances()

    @pyalaocl.utils.injector.methodOf(SmClass, 'metaProperty')
    def named(metaClass, name):
        return metaClass.javaInterface.named(name)

    @pyalaocl.utils.injector.methodOf(SmClass, 'metaProperty')
    def selectByAttribute(metaClass, attribute, value):
        # TODO: check if extensions needed for added attributes ?
        return metaClass.javaInterface.selectByAttribute(attribute, value)


    class MetaClass:

        @classmethod
        def allInstances(cls):
            return pyalaocl.asSet(SmClass.getRegisteredClasses())

        @classmethod
        def named(cls, name):
            return ModelioMetamodel.getMClass(name)

        @classmethod
        def selectByAttribute(cls, attribute, value):
            return cls.allInstances().select(
                lambda mc: getattr(mc,attribute) == value)

    def isMetaClass(value):
        return isinstance(value, SmClass)




    #--------------------------------------------------------------------------
    #  MetaInterface and instrumentation of MetaInterfaces (i.e.JavaInterfaces)
    #--------------------------------------------------------------------------


    def _addGlobalNameOfMetaInterfaces():
        for meta_class in MetaClass.allInstances():
            name = 'I'+meta_class.name
            value = meta_class.javaInterface
            # FIXME: the redefinition stuff is used for realoading, not good
            pyalaocl.utils.injector.export(
                globals(), 'metaInterface', name, value,
                allowRedefinition=True)



    def _addFeaturesToAllMetaInterfaces():

        def _new(cls, *args, **kwargs):
            method = getattr(cls.metaFactory, 'create' + cls.metaName)
            return method(*args, **kwargs)

        def _allInstances(cls):
            """
            Return the set of all instances of a given metaclass or java meta
            interface.

            Provides both the direct instances but also instances of all
            subclasses. :return: The set all all instances, direct or indirect.
            :rtype: Set[MObject]
            """
            return pyalaocl.asSet(_theSession().findByClass(cls))


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
                raise pyalaocl.Invalid('No %s named "%s"' % (cls, name))
            else:
                raise pyalaocl.Invalid(
                    'More than one element named %s (%s elements)' \
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
            return pyalaocl.asSet(
                _theSession().findByAtt(cls, attribute, value))

        # for some reason it is not possible to inject elements into MClasses

        # TODO: log print '    Injecting class methods/attributes in ' \
        #      + 'Modelio MetaInterfaces (%s) ...' \
        #        % MetaInterface.allInstances().size(),
        for mi in MetaInterface.allInstances():
            # FIXME: these properties should be registered with symbol manager
            mi.metaClass = ModelioMetamodel.getMClass(mi)
            mi.metaInterface = mi
            mi.metaFullName = mi.getCanonicalName()
            mi.metaPackage = '.'.join(mi.metaFullName.split('.')[:-1])
            mi.metaName = mi.metaClass.name
            mi.metaIsAbstract = mi.metaClass.isAbstract()

            meta_super = mi.metaClass.super
            mi.metaSuper = \
                None if meta_super is None else meta_super.javaInterface
            mi.metaSubs = mi.metaClass.getSub(False).javaInterface.asSet()
            mi.metaAllSub = mi.metaClass.getSub(True).javaInterface.asSet()
            mi.metaCmsNode = mi.metaClass.isCmsNode()
            mi.metaFactory = _getFactory(mi)
            if mi.metaFactory is not None:
                mi.new = classmethod(_new)
            mi.allInstances = classmethod(_allInstances)
            mi.named = classmethod(_named)
            mi.selectByAttribute = classmethod(_selectByAttribute)
        # print ' done'




    class MetaInterface(object):

        @classmethod
        def allInstances(cls):
            return MetaClass.allInstances().javaInterface.asSet()

        @classmethod
        def named(cls, name):
            return ModelioMetamodel.getMClass(name).getJavaInterface()

        @classmethod
        def selectByAttribute(cls, attribute, value):
            return cls.allInstances().select(
                lambda mc: getattr(mc, attribute) == value)

    # An adapted version of this function will be registered as isKind/TypeOf
    def isMetaInterface(value):
        if inspect.isclass(value):
            return issubclass(value, Element)
        else:
            return False

    #--------------------------------------------------------------------------
    #  Define global function isKindOfMETACLASS, isTypeOfMETACLASS
    #--------------------------------------------------------------------------



    def _addGlobalFunctionsIsXXXMETACLASS():
        # add global functions like isKindOfUseCase, isTypeOfClass, etc.

        # Not need to define this for metaClass, based on the name!
        # The argument metaInterface will disappear.
        def _newIsKindOfMETA(metaInterface):
            def isKindOfMETA(value):
                return isinstance(value, metaInterface)

            return isKindOfMETA

        def _newIsTypeOfMETA(metaInterface):
            meta_class = ModelioMetamodel.getMClass(metaInterface)
            def isTypeOfMETA(value):
                try:
                    return value.getMClass() is meta_class
                except:
                    return False
            return isTypeOfMETA


        for mi in MetaInterface.allInstances():

            name = 'isKindOf' + mi.metaName
            fun = _newIsKindOfMETA(mi)
            # FIXME: the redefinition stuff is used for reloading, not good
            pyalaocl.utils.injector.export(
                globals(), 'isKindOfFunctions', name, fun,
                allowRedefinition=True)
            name = 'isTypeOf' + mi.metaName
            fun = _newIsTypeOfMETA(mi)
            # FIXME: the redefinition stuff is used for reloading, not good
            pyalaocl.utils.injector.export(
                globals(), 'isTypeOfFunctions', name, fun,
                allowRedefinition=True)



    #--------------------------------------------------------------------------
    #  Define operations on Modelio 'Element' metaclass
    #--------------------------------------------------------------------------

    def _addOperationsToModelioElementMetaClass():

        # noinspection PyUnresolvedReferences
        from org.modelio.metamodel.uml.infrastructure import Element

        # TODO log print "    Adding object methods to Element ...",
        # Element.MetaInterface = property(_getMetaInterface)
        # TODO: remove if it remains useless
        # print 'done'



    #--------------------------------------------------------------------------
    #  Define global level functions get access to modelio metamodel
    #--------------------------------------------------------------------------



    def theMetamodelExtensions():
        """ TODO, Warning this is not a list!
        """
        return _theSession().getMetamodelExtensions()



    #--------------------------------------------------------------------------
    #  Register isKindOf and isTypeOf to main ocl module
    #--------------------------------------------------------------------------

    def _registerIsKindTypeOfFunctions():
        def _isKindOf(value1, value2):
            if isinstance(value2, MClass):
                return isinstance(value1, value2.getJavaInterface())
            if isinstance(value2, JavaClass):
                return isinstance(value1, value2)
            return False


        def _isTypeOf(value1, value2):
            if isinstance(value2, JavaClass):
                value2 = ModelioMetamodel.getMClass(value2)
            try:
                return value1.getMClass() is value2
            except:
                return False

        def _isTypeOfMetaInterface(value1, value2):
            if value2 is not MetaInterface:
                return False
            return isMetaInterface(value1)

        def _isTypeOfMetaClass(value1, value2):
            if value2 is not MetaClass:
                return False
            return isMetaClass(value1)

        # TODO log print '    Registering Modelio isKindOf/isTypeOf functions ...',
        pyalaocl.registerIsKindOfFunction(_isKindOf)
        pyalaocl.registerIsTypeOfFunction(_isTypeOf)
        # The function works both for Kind and Type since no hierarchy
        pyalaocl.registerIsKindOfFunction(_isTypeOfMetaInterface)
        pyalaocl.registerIsTypeOfFunction(_isTypeOfMetaInterface)
        # The function works both for Kind and Type since no hierarchy
        pyalaocl.registerIsKindOfFunction(_isTypeOfMetaClass)
        pyalaocl.registerIsTypeOfFunction(_isTypeOfMetaClass)
        # print 'done'



    def load():
        _addOCLSequenceOperationsOnModelioList()
        _addFeaturesToAllMetaInterfaces()
        _addOperationsToModelioElementMetaClass()
        _addGlobalFunctionsIsXXXMETACLASS()
        _registerIsKindTypeOfFunctions()
        _addGlobalNameOfMetaClasses()
        _addGlobalNameOfMetaInterfaces()

    def unload():
        pass

    load()


