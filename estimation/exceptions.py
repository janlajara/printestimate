class MeasurementMismatch(Exception):
    def __init__(self, measurement, expected_measure):
        self.message = "Provided measurement '%s' is not of expected measure '%s'." % \
                       (measurement, expected_measure)
        super().__init__(self.message)


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
        self.message = "Sheet size must be less than %s and greater than %. Actual size provided is '%s'." % \
                       (min_expected_size, max_expected_size, actual_size)
        super().__init__(self.message)
