from .measures import Measure
from .binpacker import BinPacker


# Create your tests here.
def test_measure__get_measure_distance(db):
    measure = Measure.get_measure('m')
    assert measure == Measure.DISTANCE


def test_measure__get_measure_area(db):
    measure = Measure.get_measure('sq_m')
    assert measure == Measure.AREA


def test_measure__get_measure_quantity(db):
    measure = Measure.get_measure('pc')
    assert measure == Measure.QUANTITY


def test_measure__get_units(db):
    units = Measure.get_units(Measure.DISTANCE)
    assert len(units) == 5


def test_binpacker__pack_rectangles(db):
    rects = [(14, 8)] * 7
    bin = [(36, 24)]

    packer = BinPacker.pack_rectangles(rects, bin, True)

    assert len(packer[0]) == 7