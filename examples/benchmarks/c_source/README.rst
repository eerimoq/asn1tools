About
=====

Benchmark of generated C source code from asn1c and asn1tools.

Executable size
---------------

The `asn1c` executable is a lot bigger because it contains encode and
decode functions for all codecs, not only uper as for
`asn1tools`. There is no `asn1c` option to only generate uper
code. `asn1c` also supports more ASN.1 construts and uses dynamic
memory.

asn1c:

.. code-block::

      text    data     bss     dec     hex      filename
     77514    5304     200   83018   1444a      main

asn1tools:

.. code-block::

      text    data     bss     dec     hex      filename
      7225     584       8    7817    1e89      main

Runtime memory usage
--------------------

The runtime memory usage was captured with Valgrind Massif on a 64
bits Ubuntu 16 machine.

asn1c:

.. code-block::

   --------------------------------------------------------------------------------
     n        time(B)         total(B)   useful-heap(B) extra-heap(B)    stacks(B)
   --------------------------------------------------------------------------------
    41        207,168            1,376                0             0        1,376
    42        214,080            1,408              560            64          784
    43        220,872            1,736              564            84        1,088
    44        225,968            1,472              903           185          384
    45        232,560            2,592              920           208        1,464
    46        239,304            2,184              920           208        1,056
    47        244,424            1,272              665            79          528
    48        251,080            1,816              434            54        1,328
    49        254,440            2,136              528            88        1,520
    50        257,200            2,240              522            70        1,648
    51        259,936            2,432              638           146        1,648
    52        262,704            2,640              689           231        1,720
    53        265,480            2,008              719           217        1,072
    54        268,216            2,504              920           256        1,328
    55        270,968            1,688              828           204          656
    56        273,704              776              280            24          472
    57        276,592              784                0             0          784
    58        279,328              448                0             0          448

asn1tools:

.. code-block::

   --------------------------------------------------------------------------------
     n        time(B)         total(B)   useful-heap(B) extra-heap(B)    stacks(B)
   --------------------------------------------------------------------------------
    66        202,640            1,376                0             0        1,376
    67        204,536              216                0             0          216
    68        206,432              944                0             0          944
    69        208,328              904                0             0          904
    70        210,224              880                0             0          880
    71        212,176            1,760                0             0        1,760
    72        214,224              816                0             0          816
    73        216,120              904                0             0          904
    74        218,016              880                0             0          880
    75        219,912              872                0             0          872
    76        221,808              320                0             0          320
    77        223,888            1,440                0             0        1,440
    78        225,784              472                0             0          472
    79        227,696              464                0             0          464
    80        229,648              496                0             0          496
    81        231,552              464                0             0          464
