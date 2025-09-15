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
            """, "eper"
        )

        fig10 = [
            {
                "number": 1,
                "sex": "male",
                "age": 30,
                "firstName": "Taro",
                "lastName": "Yamada",
                "single": False,
                "children": [{"firstName": "Jiro", "age": 3}]
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

        result = bytes(
            [
                0x54, # offset and bit field 

                # 1st record
                    0x02, # number part sequence-of
                    0x01, # number
                    0x1e, # age,
                    
                    0x04, # first name "Taro" - First record
                    0x54,
                    0x61, 
                    0x72, 
                    0x6f,

                    0x06, # lastname "Yamada"
                    0x59,
                    0x61,
                    0x60,
                    0x61, 
                    0x64,
                    0x61,

                        0x01, # number part sequence-of (Child Information)

                        0x04, # first name "Jiro"
                        0x4a, 
                        0x69,
                        0x72,
                        0x6f,

                        0x03, # Age

                # 2nd Personal Record
                
                    0x02, # number
                    0x19, # age

                    0x04, # first name "Hana"
                    0x48,
                    0x61,
                    0x6e,
                    0x61,

                    0x04, # last name "Sato"
                    0x53,
                    0x61,
                    0x74,
                    0x6f


            ]
        )

        datas = [
            ('Employees', fig10, result)
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)


if __name__ == '__main__':
    unittest.main()
