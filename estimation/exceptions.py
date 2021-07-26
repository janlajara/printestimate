class MeasurementMismatch(Exception):
    def __init__(self, measurement, expected_measure):
        self.message = "Provided measurement '%s' is not of expected measure '%s'." % \
                       (measurement, expected_measure)
        super().__init__(self.message)


class MaterialTypeMismatch(Exception):
    def __init__(self, actual_material_type, actual_item_type, expected_type):
        self.message = "Provided types of material and/or item ('%s', '%s') is not equal to expected type '%s'." % \
                       (actual_material_type, actual_item_type, expected_type)
        super().__init__(self.message)


class CostingMeasureMismatch(Exception):
    def __init__(self, actual_costing_measure, expected_costing_measures):
        self.message = "Provided costing measure '%s' not found in expected machine costing measures: %s" % \
                       (actual_costing_measure, expected_costing_measures)
        super().__init__(self.message)

'''
class InvalidProductMeasure(Exception):
    def __init__(self, measure, measure_type, measure_options):
        self.message = "Invalid value or combination of measure='%s' and type='%s'. Valid values are: %s." % \
                       (measure, measure_type, measure_options)
        super().__init__(self.message)


class MismatchProductMeasure(Exception):
    def __init__(self, actual_measurement,  expected_measurement):
        self.message = "Provided measure '%s' does not match expected process measurement '%s'." % \
                       (actual_measurement, expected_measurement)
        super().__init__(self.message)


class UnrecognizedProductMeasure(Exception):
    def __init__(self, measure, class_name):
        self.message = "Measure '%s' is not recognized as a measure of the product '%s'." % \
                       (measure, class_name)
        super().__init__(self.message)


class SheetSizeInvalid(Exception):
    def __init__(self, min_expected_size, max_expected_size, actual_size):
        self.message = "Sheet size must be less than %s and greater than %s. Actual size configured is '%s'." % \
                       (min_expected_size, max_expected_size, actual_size)
        super().__init__(self.message)
'''