# -*- coding: utf-8 -*-
#
# Test of spreadsheet_lib functions.
# Created by Japp on 200120
#

import pytest
import spreadsheet_lib

def test_cellname():
    ''' Tests correct spreadsheet cell name returned. '''

    assert cellname(1, 2) == 'A2'
    assert cellname(3, 4) == 'C4'
    assert cellname(26, 6) == 'Z6'
    assert cellname(27, 8) == 'AA8'
    assert cellname(52, 10) == 'AZ10'
    assert cellname(53, 12) == 'BA12'
    assert cellname(78, 14) == 'BZ14'
    assert cellname(79, 16) == 'CA16'
    assert cellname(27*26, 702) == 'ZZ702'
    #assert cellname(27*26+1, 2) == ''
