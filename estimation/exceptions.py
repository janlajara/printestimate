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
