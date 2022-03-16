import pytest
from core.utils.measures import CostingMeasure

def test_costing_measure__create(db):
    measure = CostingMeasure.create('perimeter')
    
    assert measure.name == 'perimeter'
    expected = [('mm', 'Millimeter'), ('cm', 'Centimeter'),
                ('m', 'Meter'), ('inch', 'Inch'), ('ft', 'Feet')]

    for index, unit in enumerate(measure.units):
        assert unit.value == expected[index][0]
        assert unit.display_name == expected[index][1]


def test_costing_measure__get_all_measures(db):
    measures = CostingMeasure.get_all_measures()
    
    assert measures is not None
    assert len(measures) == 5