import math
from rectpack import newPacker, MaxRectsBl


class BinPacker:

    @classmethod
    def estimate_rectangles(cls, parent_width, parent_length, child_width, child_length):
        parent_area = parent_width * parent_length
        child_area = child_width * child_length
        if parent_area == 0 or child_area == 0:
            return 0

        return math.ceil(parent_area / child_area)

    @classmethod
    def pack_rectangles(cls, rectangles, bins, rotation=False):
        packer = newPacker(pack_algo=MaxRectsBl, rotation=rotation)

        for b in bins:
            packer.add_bin(*b)
        for r in rectangles:
            packer.add_rect(*r)

        packer.pack()

        return packer
