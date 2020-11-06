import pytest
from measurement.measures import Distance
from .models import SheetfedPress
from ..exceptions import SheetSizeInvalid

@pytest.fixture
def gto_machine(db):
    return SheetfedPress.objects.create(name='GTO Press',
                                           min_sheet_length=Distance(inch=15), max_sheet_length=Distance(inch=22),
                                           min_sheet_width=Distance(inch=15), max_sheet_width=Distance(inch=22))


def test_machine__validate_input(db, gto_machine):
    with pytest.raises(SheetSizeInvalid):
        gto_machine.validate_input(runsheet_length=Distance(inch=14),
                                   runsheet_width=Distance(inch=14))
