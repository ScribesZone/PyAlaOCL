# coding=utf-8

#FIXME: Potential BUG with inheritance:
# print AttributeDefinition.allInstances().name.asSet()
# print OperationDefinition.allInstances().name.asSet()
# >>> print Constraint.allInstances().name.asSet()
# Set()

import pyalaocl.modelio

if pyalaocl.modelio.WITH_MODELIO:

    __all__ = [
        #  ...
        # THIS LIST IS EXTENDED DYNAMICALLY
        #  ...
        #
        'symbolGroups'
        #----------------------------------------------------------------------
        #  Stereotypes support
        #----------------------------------------------------------------------
        #
        #   is<Class>()
        # is<Stereotype>()
        # <Stereotype>

        # PostCondition
        #     base
        #     metaName
        #     metaPackage
        #     metaFullName
        #     new( ...)
        #     ( ... )
        #     allTypeInstances()
        #     named(name)
        #     selectByAttribute(attribute, value)
        #     added(element)
        #
        # Operation   # base class stereotyped by PostCondition
        #     isPostCondition   RW add read/write/read attribute
        #     isKindOfPostCondition
        #
        #----------------------------------------------------------------------
        # NoteTypeStereotypes support
        #----------------------------------------------------------------------
        #     oclPostConditionNote
        #     oclPostConditionNotes   TODO

    ]

    import pyalaocl
    import pyalaocl.utils.injector
    # from  import \
    #    readOnlyPropertyOf, methodOf, export, attributeOf

    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import Stereotype
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import MetaclassReference



    #--------------------------------------------------------------------------
    #  Global symbols management
    #--------------------------------------------------------------------------

    symbolGroups = ('stereotypes')  # TODO  used ?



    #--------------------------------------------------------------------------
    #     MetaclassReferences support
    #--------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.impl.uml.infrastructure import \
        MetaclassReferenceImpl

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        MetaclassReferenceImpl, 'metaProperty')
    def base(self):
        return pyalaocl.modelio.MetaInterface.named(
            self.getReferencedClassName())

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        MetaclassReferenceImpl, 'metaProperty')
    def metaName(self):
        return self.base.metaName

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        MetaclassReferenceImpl, 'metaProperty')
    def metaPackage(self):
        return self.base.metaPackage

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        MetaclassReferenceImpl, 'metaProperty')
    def metaFullName(self):
        return self.base.metaFullName

    #--------------------------------------------------------------------------
    #     Stereotypes support
    #--------------------------------------------------------------------------


    # The trick below is necessary to have at the same time
    # Stereotype.allInstances() and for instance Invariant.allInstances().
    # The first one is a class method on Stereotype, the second
    # is an instance method on a the implementation class.
    # Invariant being (in this example) a instance of the Stereotype class
    # its not possible to have on the same class, a instance and class method
    # of the same name

    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.impl.uml.infrastructure import StereotypeImpl




    @pyalaocl.utils.injector.readOnlyPropertyOf(
        StereotypeImpl, 'metaProperty')
    def base(self):
        return pyalaocl.modelio.MetaInterface.named(self.getBaseClassName())

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        StereotypeImpl, 'metaProperty')
    def metaName(self):
        return self.name

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        StereotypeImpl, 'metaProperty')
    def metaPackage(self):
        return '%s.%s' % (self.module.name, self.owner.name)

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        StereotypeImpl, 'metaProperty')
    def metaFullName(self):
        return '%s.%s' % (self.metaPackage, self.metaName)

    @pyalaocl.utils.injector.readOnlyPropertyOf(
        StereotypeImpl, 'metaProperty')
    def allChildren(self):
        return pyalaocl.Set(self).closure('child').excluding(self).asSet()

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def new(self, *args, **kwargs):
        if self.base.metaFactory is not None:
            element = self.base.new(*args, **kwargs)
            self.addedTo(element)
            return element
        else:
            NotImplementedError('Modelio do not provide a createXXX method')

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def __call__(self, *args, **kwargs):
        return self.new(*args, **kwargs)

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def allTypeInstances(self):
        return \
            self.base.allInstances().select(
                _isTypeOfSTEREOTYPEMethodName(self)).asSet()

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def allInstances(self):
        raise NotImplementedError()

    # FIXME: should take inheritance into account

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def named(self, name):
        r = self.allInstances().select(
            lambda e: e.name == name)
        if len(r) == 1:
            return r[0]
        elif len(r) == 0:
            raise pyalaocl.Invalid('No %s named "%s"' % (self.name, name))
        else:
            raise pyalaocl.Invalid(
                'More than one element named %s (%s elements)' \
                % (name, str(len(r))))

    @pyalaocl.utils.injector.methodOf(
        StereotypeImpl, 'metaProperty')
    def selectByAttribute(self, attribute, value):
        return self.allInstances.select(
            lambda element: getattr(element, attribute) == value
        )


    @pyalaocl.utils.injector.methodOf(StereotypeImpl, 'profile')
    def addedTo(self, element):
        moduleName = self.module.name
        stereotypeName = self.name
        if not element.isStereotyped(moduleName, stereotypeName):
            element.addStereotype(moduleName, stereotypeName)

    def _isTypeOfSTEREOTYPEMethodName(stereotype):
        return 'isTypeOf' + stereotype.name #FIXME Title put lowercase

    def _isKindOfSTEREOTYPEMethodName(stereotype):
        return 'isKindOf' + stereotype.name  #FIXME Title lowercase


    def _addStereotypeSupportToBaseClasses():
        def _newIsSTEREOTYPEProperty(stereotype):
            # Property that allows:
            #   print aSignal.isInvariant  ->True/False
            #   aSignal.isInvariant = True ->add the stereotype Invariant
            #   aSignal.isInvariant = False ->remove the stereotype Invariant
            moduleName = stereotype.module.name
            stereotypeName = stereotype.name
            def getter(element):
                return stereotype in element.extension
            def setter(element, value):
                # if True add the stereotype
                # if False remove the stereotype
                if value:
                    if not element.isStereotyped(moduleName, stereotypeName):
                        element.addStereotype(moduleName, stereotypeName)
                else:
                    if element.isStereotyped(moduleName, stereotypeName):
                        element.removeStereotypes(moduleName, stereotypeName)
            return property(fget=getter, fset=setter)

        def _newIsKindOfSTEREOTYPEProperty(stereotype):
            # Property that allow:
            #  print aSignal.isKindOfSignal
            moduleName = stereotype.module.name
            stereotypeName = stereotype.name
            def getter(element):
                # this modelio method take stereotype inheritance into account
                return element.isStereotyped(moduleName, stereotypeName)
            return property(fget=getter)

        for stereotype in Stereotype.allInstances():
            base = stereotype.base

            name = _isTypeOfSTEREOTYPEMethodName(stereotype)
            p = _newIsSTEREOTYPEProperty(stereotype)
            pyalaocl.utils.injector.attributeOf(base, 'profile', name, p)

            name = _isKindOfSTEREOTYPEMethodName(stereotype)
            p = _newIsKindOfSTEREOTYPEProperty(stereotype)
            pyalaocl.utils.injector.attributeOf(base, 'profile', name, p)





    def _addGlobalStereotypeNames():
        metaInterfaceNames = \
            pyalaocl.modelio.MetaInterface.allInstances().metaName
        for stereotype in Stereotype.allInstances():
            name = stereotype.name      # .title()#FIXME Title lowercase
            # FIXME: should not be redef true
            pyalaocl.utils.injector.export(globals(), 'sterotype', name, stereotype,
                   allowRedefinition=True)

    def _registerIsTypeOfAndIsKindOfOCLPredicate():
        def _isKindOf(value1,value2):
            if isinstance(value2,Stereotype):
                return (
                    _isTypeOf(value1,value2)
                    or
                    value2.allChildren.exists(
                        lambda child: _isTypeOf(value1, child)) )
            else:
                return False
        def _isTypeOf(value1,value2):
            if isinstance(value2,Stereotype):
                try:
                    return value2 in value1.extension
                except:
                    return False
            else:
                return False
        pyalaocl.registerIsTypeOfFunction(_isTypeOf)
        pyalaocl.registerIsKindOfFunction(_isKindOf)

    def _addGlobalFunctionsIsSTEREOTYPE():
        pass
        #TODO: check what to do. The problem is with synonyms
        # add global functions like isUseCase, isClass, isAttribute
        #for mi in Stereotype.allInstances().metaName:
        #    export(globals(), 'is' + mi.metaName,
              #     _newIsInstanceOfMetaClass(mi))





    #--------------------------------------------------------------------------
    #     NoteTypes support
    #--------------------------------------------------------------------------

    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.impl.uml.infrastructure import NoteTypeImpl

    @pyalaocl.utils.injector.methodOf(NoteTypeImpl, 'note')
    def allInstances(noteType):
        all_bases = noteType.ownerStereotype.base.allInstances()
        return all_bases.descriptor.select(
            lambda note: note.model is noteType
            ).asSet()


    def _addNoteTypeSupportToBaseClasses():

        def _newNOTETYPENoteProperty(noteType):
            # TODO: change to return None or 1
            def getter(element):
                return \
                    element.descriptor.any(lambda x: x.model == noteType)

            def setter(element, value):  #FIXME
                raise NotImplementedError('_newNOTETYPENoteProperty')

            return property(fget=getter, fset=setter)

        def _newNOTETYPENotesProperty(noteType):
            # Property that allow:
            #    aSignal.OCLInvariantNotes    (with s)
            def getter(element):
                return \
                    element.descriptor.select(lambda x: x.model == noteType)

            # TODO: Add the possibility to add and remove notes
            return property(fget=getter)

        # TODO: add support for rich notes
        # TODO: add support for tags

        noteContainers = \
            Stereotype.allInstances() | MetaclassReference.allInstances()
        for noteContainer in noteContainers:
            base = noteContainer.base
            for noteType in noteContainer.definedNoteType:
                name = noteType.name + 'Note'  #FIXME Title put lowercase
                p = _newNOTETYPENoteProperty(noteType)
                pyalaocl.utils.injector.attributeOf(base, 'profile', name, p)

                name = noteType.name + 'Notes'  #FIXME Title put lowercase
                p = _newNOTETYPENotesProperty(noteType)
                pyalaocl.utils.injector.attributeOf(base, 'profile', name, p)

    # TODO ADD A GLOBAL NAMES ?  NOTETYPE, isNOTETYPE, isKindOf/TypeOf, new



    #--------------------------------------------------------------------------
    #     DocumentTypes
    #--------------------------------------------------------------------------

    # TODO

    def _addDocumentTypeSupportToBaseClasses():
        pass


    #--------------------------------------------------------------------------
    #     TagTypes
    #--------------------------------------------------------------------------

    # TODO

    def _addTagTypeSupportToBaseClasses():
        pass

    def loadModule():
        _addGlobalStereotypeNames()
        _addStereotypeSupportToBaseClasses()
        _registerIsTypeOfAndIsKindOfOCLPredicate()
        _addNoteTypeSupportToBaseClasses()
        _addDocumentTypeSupportToBaseClasses()
        _addTagTypeSupportToBaseClasses()



    loadModule()





#Signal.isInvariant  = property(lambda e:Invariant in e.getExtension())
#Signal.isInvariant.setter(lambda e,value:e.addStereotype('PyModelioLibraryModule','Invariant'))



# Signal.__getattr__ = lambda x, attr: 'toto' + attr


#@property
# def nb(self): return self.name + 'bizare'
#Stereotype.nb = nb
