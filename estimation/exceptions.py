class MeasurementMismatch(Exception):
    def __init__(self, measurement, expected_measure):
        self.message = "Provided measurement='%s' is not of expected measure='%s'." % \
                       (measurement, expected_measure)
        super().__init__(self.message)
