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
    bin_width = 32 #18
    bin_height = 27 #13

    rect_width = 21 #4
    rect_height = 26 #2
    rect_count = 1 #27

    rects = [(rect_width, rect_height)] * rect_count
    bin = [(bin_width, bin_height)]

    packer = BinPacker.pack_rectangles(rects, bin, True)

    all_rects = packer.rect_list()
    unique_x = []
    unique_y = []

    assert len(all_rects) == rect_count
    assert packer[0].width == bin_width
    assert packer[0].height == bin_height

    for rect in all_rects:
        b, x, y, w, h, rid = rect
        if x not in unique_x:
            if x > 0:
                unique_x.append(x)
            if x+w < bin_width:
                unique_x.append(x+w)
        if y not in unique_y:
            if y > 0:
                unique_y.append(y)
            if y+h < bin_height:
                unique_y.append(y+h)
        
    print(unique_x)
    print(unique_y)

    assert False