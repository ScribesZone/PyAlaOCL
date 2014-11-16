# coding=utf-8


from pyalaocl.modelio import WITH_MODELIO, MetaInterface, Invalid, asSet

if WITH_MODELIO:

    from pyalaocl.injector import \
        readOnlyPropertyOf, methodOf, classMethodOf, export, \
        isValidNewIdentifier, attributeOf

    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.uml.infrastructure import Stereotype

    __all__ = [
        #  ...
        # THIS LIST IS EXTENDED DYNAMICALLY
        #  ...
        #
        # is<Class>()
        # is<Stereotype>()
        # <Stereotype>
    ]


    @readOnlyPropertyOf(Stereotype)
    def base(self):
        return MetaInterface.named(self.getBaseClassName())


    @readOnlyPropertyOf(Stereotype)
    def metaName(self):
        return self.name

    @readOnlyPropertyOf(Stereotype)
    def metaPackage(self):
        return '%s.%s' % (self.module.name, self.owner.name)

    @readOnlyPropertyOf(Stereotype)
    def metaFullName(self):
        return '%s.%s' % (self.metaPackage, self.metaName)

    # The trick below is necessary to have at the same time
    # Stereotype.allInstances() and for instance Invariant.allInstances().
    # The first one is a class method on Stereotype, the second
    # is an instance method on a the implementation class.
    # Invariant being (in this example) a instance of the Stereotype class
    # its not possibe to have on the same class, a instance and class method
    # of the same name
    # noinspection PyUnresolvedReferences
    from org.modelio.metamodel.impl.uml.infrastructure import StereotypeImpl

    @methodOf(StereotypeImpl)
    def allInstances(self):
        return asSet(self.getExtendedElement())

    @methodOf(StereotypeImpl)
    def named(self, name):
        r = self.getExtendedElement().select(
            lambda e: e.name == name)
        if len(r) == 1:
            return r[0]
        elif len(r) == 0:
            raise Invalid('No %s named "%s"' % (self.name, name))
        else:
            raise Invalid(
                'More than one element named %s (%s elements)' \
                % (name, str(len(r))))


#    class

    def _addMethodsToStereotypeBaseClasses():


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

        def _newNOTETYPENoteProperty(noteType):
            def getter(element):
                return \
                    element.descriptor.any(lambda x: x.model == noteType)
            def setter(element,value):
                raise NotImplementedError('_newNOTETYPENoteProperty')
            return property(fget=getter,fset=setter)

        def _newNOTETYPENotesProperty(noteType):
            # Property that allow:
            #    aSignal.OCLInvariantNotes    (with s)
            def getter(element):
                return \
                    element.descriptor.select(lambda x: x.model == noteType)
            return property(fget=getter)

        for stereotype in Stereotype.allInstances():
            base = stereotype.base

            name = 'is'+stereotype.name.title() #FIXME Title put lowercase
            p = _newIsSTEREOTYPEProperty(stereotype)
            attributeOf(base,name,p)

            name = 'isKindOf'+stereotype.name.title()  #FIXME Title put lowercase
            p = _newIsKindOfSTEREOTYPEProperty(stereotype)
            attributeOf(base, name, p)

            for noteType in stereotype.definedNoteType:
                name = noteType.name+'Note'  #FIXME Title put lowercase
                p = _newNOTETYPENoteProperty(noteType)
                attributeOf(base, name, p)

                name = noteType.name + 'Notes'  #FIXME Title put lowercase
                p = _newNOTETYPENotesProperty(noteType)
                attributeOf(base, name, p)



    def _addGlobalStereotypeNames():
        metaInterfaceNames = MetaInterface.allInstances().metaName
        for stereotype in Stereotype.allInstances():
            name = stereotype.name.title()
            if isValidNewIdentifier(name,
                                    existingIdentifiers=metaInterfaceNames):
                export(globals(),name,stereotype)
                #function_name = 'is' + stereotype.name.title()
                #globals()[function_name] = _newHasStereotype(stereotype.name)
                #__all__.append(function_name)


    # FIXME:
    def _addGlobalFunctionsIsSTEREOTYPE():
        pass
        # add global functions like isUseCase, isClass, isAttribute
        #for mi in Stereotype.allInstances().metaName:
        #    export(globals(), 'is' + mi.metaName,
              #     _newIsInstanceOfMetaClass(mi))

    _addGlobalStereotypeNames()
    _addMethodsToStereotypeBaseClasses()
#Signal.isInvariant  = property(lambda e:Invariant in e.getExtension())
#Signal.isInvariant.setter(lambda e,value:e.addStereotype('PyModelioLibraryModule','Invariant'))



# Signal.__getattr__ = lambda x, attr: 'toto' + attr


#@property
# def nb(self): return self.name + 'bizare'
#Stereotype.nb = nb
