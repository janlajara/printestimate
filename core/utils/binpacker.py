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
    def pack_rectangles(cls, rectangles, bins, rotation=False, algorithm=None):
        def _pack(algorithm=None):
            args = {'rotation': rotation}
            if algorithm is not None:
                args['pack_algo'] = algorithm
            packer = newPacker(**args)

            for b in bins:
                packer.add_bin(*b)
            for r in rectangles:
                packer.add_rect(*r)

            packer.pack()

            return packer
        
        a1 = _pack()
        a2 = _pack(MaxRectsBl)
        
        if len(a1.rect_list()) > len(a2.rect_list()):
            return a1
        else:
            return a2
