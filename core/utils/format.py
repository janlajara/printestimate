import inflect

_inflect = inflect.engine()

class Inflect:

    @classmethod
    def to_plural(cls, unit_of_measure, quantity=None):
        uom = _inflect.plural(unit_of_measure)
        if quantity is not None and abs(quantity) == 1:
            uom = unit_of_measure
        return uom


    @classmethod
    def format_quantity(cls, quantity, unit_of_measure):
        if abs(quantity) > 1 or quantity == 0:
            unit_of_measure = _inflect.plural(unit_of_measure)
        return '%s %s' % (quantity, unit_of_measure)

