# coding=utf-8

__all__ =(
    'allMetaClasses',
    'allMetaInterfaces',
    'getMetaClass',
    'getMetaInterface',
)



from alaocl import asSet,Invalid
import alaocl.injector
import alaocl.jython

try:
    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio
    WITH_MODELIO = True
except:
    WITH_MODELIO = False

if WITH_MODELIO:


    #-----------------------------------------------------------------------------
    #  Add OCL Seq operations on JavaList returned by modelio
    #-----------------------------------------------------------------------------

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

        print 'alaocl.modelio:'
        print '    Injecting Seq methods in Modelio list classes'
        alaocl.injector.addSuperclass(
            alaocl.jython.JavaListExtension, MODELIO_LISTS)




    #--------------------------------------------------------------------------
    #  Add on each metaclass methods:
    #  * allInstances()
    #  * named(str)
    #  * selectByAttribute(str,value)
    #  and metaclass attributes
    #  * metaFullName
    #  * metaName
    #  * metaPackage
    #--------------------------------------------------------------------------

    def _addOperationsToAllModelioMetaClasses():

        def _allInstances(cls):
            """
            Return the set of all instances of a given metaclass or java meta
            interface.

            Provides both the direct instances but also instances of all
            subclasses. :return: The set all all instances, direct or indirect.
            :rtype: Set[MObject]
            """
            return asSet(_theSession().findByClass(cls))


        def _named(cls,name):
            """
            Return the only instance that have the given name.
            If there is more than one instance then raise an exception Invalid
            (MClass|Class)*String -> MObject|NameError
            """
            r = _theSession().findByAtt(cls,'Name',name)
            if len(r) == 1:
                return r[0]
            elif len(r) == 0:
                raise Invalid('No %s named "%s"' % (cls,name))
            else:
                raise Invalid('More than one (%s) elements named %s' \
                                % (str(len(r)),name))


        def _selectByAttribute(cls,attribute,value):
            """
            Return the list of all the instances that have the
            property set to the given value.
            NOTE: Not sure how to deal with property that are not string.
            (MClass|Class)*String*String -> List(MObject)
            EXAMPLES
              selectedInstances(DataType,"Name","string")
            """
            return asSet(_theSession().findByAtt(cls,attribute,value))

        # for some reason it is not possible to inject elements intro MClasses

        print '    Injecting class methods/attributes in '\
                + 'Modelio MInterfaces (%s)' % allMetaInterfaces().size()
        for mi in allMetaInterfaces():
            mi.metaFullName = mi.getCanonicalName()
            mi.metaName = mi.metaFullName.split('.')[-1]
            mi.metaPackage = '.'.join(mi.metaFullName.split('.')[:-1])
            mi.metaClass = getMetaClass(mi)
            mi.allInstances = classmethod(_allInstances)
            mi.named = classmethod(_named)
            mi.selectByAttribute = classmethod(_selectByAttribute)



    #--------------------------------------------------------------------------
    #  Define operations on Modelio Element metaclass
    #--------------------------------------------------------------------------

    def _addOperationsToModelioElementMetaClass():

        # noinspection PyUnresolvedReferences
        from org.modelio.metamodel.uml.infrastructure import Element

        def _getMInterface(self):
            return self.getMClass().getJavaInterface()

        print "    Adding object methods to Element"
        Element.getMInterface = _getMInterface





    #--------------------------------------------------------------------------
    #  Define global level functions get access to modelio metamodel
    #--------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    from org.modelio.api.modelio import Modelio

    def _theSession():
        """ Return the current session.
            () -> IModelingSession
        """
        return Modelio.getInstance().getModelingSession()


    # noinspection PyUnresolvedReferences
    from org.modelio.vcore.smkernel.meta import SmClass
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel import Metamodel


    def allMetaClasses():
        """ Return the list of all known metaclasses as MClass objects.
            () -> [ MClass ]
            EXAMPLE:
              for m in allMetaClasses(): print m
        """
        return asSet(SmClass.getRegisteredClasses())


    def allMetaInterfaces():
        """ Return the list of all known metaclasses as Java interfaces.
            () -> [ Class ]
            EXAMPLE:
              for m in allMetaClasses(): print m
        """
        return allMetaClasses().collect(Metamodel.getJavaInterface).asSet()


    def getMetaClass(nameOrMInterfaceOrElement):
        """ Return the MClass corresponding to a name, a java interface
            or an element.
            (Class | String | Element) -> MClass
            EXAMPLES:
              print getMClass(UseCase)
              print getMClass("UseCase")
              print getMClass(myUseCase1)
        """
        if isinstance(nameOrMInterfaceOrElement,Element):
            return nameOrMInterfaceOrElement.getMClass()
        else:
            return Metamodel.getMClass(nameOrMInterfaceOrElement)


    def getMetaInterface(nameOrMClassOrElement):
        """ Return the Java Interface corresponding to a name or a MClass
            (MClass | String) -> CLass
            EXAMPLES
              print getMInterface("UseCase")
              print getMInterface(getMClass("UseCase"))
              print getMInterface(instanceNamed(DataType,"string"))
        """
        if isinstance(nameOrMClassOrElement,Element):
            return nameOrMClassOrElement.getMClass().getJavaInterface()
        elif isinstance(nameOrMClassOrElement,basestring):
            return getMetaClass(nameOrMClassOrElement).getJavaInterface()
        else:
            return nameOrMClassOrElement.getJavaInterface()


    def theMetamodelExtensions():
        """ TODO, Warning this is not a list!
        """
        return _theSession().getMetamodelExtensions()

    # noinspection PyUnresolvedReferences

    from java.lang import Class as JavaClass
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel import Metamodel
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import Element
    # noinspection PyUnresolvedReferences
    from org.modelio.vcore.smkernel.mapi import MClass


    def isKindOf(element,mClassOrMInterface):
        """ Check if the element is a direct  or indirect instance of a MClass
            or interface. Use isTypeOf to test if the type is exactly
            the one specified.
            EXAMPLES
              print isKindOf(instanceNamed(DataType,"string"),Element)
              print isKindOf(instanceNamed(DataType,"string"),UseCase)
        """
        if isinstance(mClassOrMInterface,MClass):
            mClassOrMInterface = mClassOrMInterface.getJavaInterface()
        return isinstance(element,mClassOrMInterface)


    def isTypeOf(element,mClassOrMInterface):
        """ Check if the element has exactly the type specified, not one of
            its subtype. Use isKindOf to test if the type is exactly the one
            specified.
            EXAMPLES
              print isTypeOf(instanceNamed(DataType,"string"),DataType)
              print isTypeOf(instanceNamed(DataType,"string"),Element)
        """
        if isinstance(mClassOrMInterface,JavaClass):
            mClassOrMInterface = Metamodel.getMClass(mClassOrMInterface)
        return element.getMClass() is mClassOrMInterface




    #--------------------------------------------------------------------------
    #  Define global level functions get access to modelio metamodel
    #--------------------------------------------------------------------------

    _addOCLSequenceOperationsOnModelioList()
    _addOperationsToAllModelioMetaClasses()
    _addOperationsToModelioElementMetaClass()
