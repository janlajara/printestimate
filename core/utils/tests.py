from .measures import Measure
from .binpacker import BinPacker
from .shapes import Rectangle


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


def test_binpacker__get_layout(db):
    parent = Rectangle.Layout(width=12, length=16, uom='inch')
    child = Rectangle.Layout(width=4, length=5, uom='inch')

    layout = Rectangle.get_layout(parent, child, True)

    assert layout is not None
    assert layout.count == 9
    assert layout.cut_count == 5


def test_binpacker_get_layout_2(db):
    parent = Rectangle.Layout(width=16, length=27, uom='inch')
    child = Rectangle.Layout(width=8, length=10, uom='inch')

    layout = Rectangle.get_layout(parent, child, True)

    assert layout is not None
    assert layout.count == 4
    assert layout.cut_count == 3