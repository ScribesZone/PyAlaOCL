import re

class UseOCLConverter(object):
    useCommand = 'use'
    iterators = (
        'select', 'reject',
        'forAll', 'exists', 'one',
        'any',
        'isUnique',
        'closure',
        'collect',
        'collectNested',
    )
    collectionOperators0 = (
        'size',
        'sum',
        'max',
        'min',
        'asSet',
        'asBag',
        'asSequence',
    )

    oclExpressionReplacements = (
        (r' = ', r' == '),
        (r' implies ', r' |implies| '),
        (r' xor ', r' ^ '),
        (r' div ', r' / '),
        (r'->notEmpty', r' is not None'),
        (r'->isEmpty', r' is None'),
        (r'->(' + '|'.join(collectionOperators0) + ')',
         r'.\1()'),
        (r'->(' + '|'.join(iterators) + ')\(\$([a-z0-9]+) : \w+ \| ',
         r'.\1(lambda \2: '),
        (r'\$e', r'e'),
        (r'\$(elem[0-9]+)', r'\1'),
    )

    @classmethod
    def convertCanonicalOCLExpression(cls, canOCLExpression):
        result = canOCLExpression
        for (pattern, target) in cls.oclExpressionReplacements:
            result = re.sub(pattern, target, result)
        result = 'return ' + result
        return result

    @classmethod
    def convertCanonicalOCLInvariantHeader(cls, canOCLInvariantHeader):
        return \
            re.sub(
                r'context self : (\w+) inv (\w+):',
                r'@invariant(\1)\ndef invariant_\2(self):',
                canOCLInvariantHeader)

    @classmethod
    def convertCanonicalOCLInvariants(cls, canOCLSpecification):
        i = canOCLSpecification.index('constraints')
        for line in canOCLSpecification[i:]:
            if line.startswith('  '):
                print cls.convertCanonicalOCLExpression(line)
            elif line.startswith('context self : '):
                print cls.convertCanonicalOCLInvariantHeader(line)
