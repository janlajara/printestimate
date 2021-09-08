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


def test_binpacker__get_cut(db):
    rects = [(4, 2)] * 27
    bin = [(18, 13)]

    packer = BinPacker.pack_rectangles(rects, bin, True)

    all_rects = packer.rect_list()
    unique_x = []
    unique_y = []

    for rect in all_rects:
        b, x, y, w, h, rid = rect
        if x not in unique_x and x > 0:
            unique_x.append(x)
            if x+w < 18:
                unique_x.append(x+w)
        if y not in unique_y and y > 0:
            unique_y.append(y)
            if y+h < 13:
                unique_y.append(y+h)
        
    print(unique_x)
    print(unique_y)

    assert len(packer[0]) == 27
    assert False