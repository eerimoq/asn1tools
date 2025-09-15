#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')
sys.path.append('tests/files/oma')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from s1ap_14_4_0 import EXPECTED as S1AP_14_4_0
from x691_a4 import EXPECTED as X691_A4
from ulp import EXPECTED as OMA_ULP


class Asn1ToolsPerTest(Asn1ToolsBaseTest):

    def test_fig_11(self):
        # noted that this example is from the patent and the sex coding is not
        # representing the views of the programmer or project
        foo = asn1tools.compile_string(
            """
            US5638066 DEFINITIONS ::= BEGIN
            Employees ::= SEQUENCE OF PersonalRecord
            PersonalRecord ::= SEQUENCE {
                number INTEGER, sex ENUMERATED { male(0), female (1)},
                age INTEGER, firstName PrintableString, lastName
                PrintableString, single BOOLEAN, children ChildInformation
                OPTIONAL}
            ChildInformation ::= SEQUENCE OF SEQUENCE{
                firstName PrintableString, age INTEGER
            }
            END
            """
        )

        fig10 = [
            {
                "number": 1,
                "sex": "male",
                "age": 30,
                "firstName": "Taro",
                "lastName": "Yamada",
                "single": False,
                "children": {"firstName": "Jiro", "age": 3}
            },
            {
                "number": 2,
                "sex": "female",
                "age": 25,
                "firstName": "Hana",
                "lastName": "Sato",
                "single": True
            }
        ]


if __name__ == '__main__':
    unittest.main()
