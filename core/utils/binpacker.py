import math
from rectpack import newPacker, MaxRectsBl, MaxRectsBaf


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
        
        algorithms = [MaxRectsBaf, MaxRectsBl, None]
        most_output = None

        for algo in algorithms:
            packer = _pack(algo) if algo is not None else _pack()
            packer_rect_count = len(packer.rect_list())
            if most_output is None or packer_rect_count > len(most_output.rect_list()):
                most_output = packer

        return most_output
