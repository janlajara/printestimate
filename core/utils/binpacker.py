import math
from rectpack import newPacker


class BinPacker:

    @classmethod
    def estimate_rectangles(cls, parent_width, parent_length, child_width, child_length):
        parent_area = parent_width * parent_length
        child_area = child_width * child_length
        return math.ceil(parent_area / child_area)

    @classmethod
    def pack_rectangles(cls, rectangles, bins, rotation=False):
        packer = newPacker(rotation=rotation)

        for b in bins:
            packer.add_bin(*b)
        for r in rectangles:
            packer.add_rect(*r)

        packer.pack()

        return packer
