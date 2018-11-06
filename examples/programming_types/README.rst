About
=====

Types often found in programming languages, defined in the ASN.1
module `programming_types.asn`_.

+------------+---------------+-----------+------------+
| ASN.1      | C             | Python    | Java       |
+============+===============+===========+============+
| ``Int8``   | ``int8_t``    | ``int``   | ``byte``   |
+------------+---------------+-----------+------------+
| ``Int16``  | ``int16_t``   | ``int``   | ``short``  |
+------------+---------------+-----------+------------+
| ``Int32``  | ``int32_t``   | ``int``   | ``int``    |
+------------+---------------+-----------+------------+
| ``Int64``  | ``int64_t``   | ``int``   | ``long``   |
+------------+---------------+-----------+------------+
| ``Uint8``  | ``uint8_t``   | ``int``   | ``byte``   |
+------------+---------------+-----------+------------+
| ``Uint16`` | ``uint16_t``  | ``int``   | ``short``  |
+------------+---------------+-----------+------------+
| ``Uint32`` | ``uint32_t``  | ``int``   | ``int``    |
+------------+---------------+-----------+------------+
| ``Uint64`` | ``uint64_t``  | ``int``   | ``long``   |
+------------+---------------+-----------+------------+
| ``Float``  | ``float``     | ``float`` | ``float``  |
+------------+---------------+-----------+------------+
| ``Double`` | ``double``    | ``float`` | ``double`` |
+------------+---------------+-----------+------------+
| ``Bool``   | ``bool``      | ``bool``  | ``bool``   |
+------------+---------------+-----------+------------+
| ``String`` | ``char *``    | ``str``   | ``String`` |
+------------+---------------+-----------+------------+
| ``Bytes``  | ``uint8_t *`` | ``bytes`` | ``byte[]`` |
+------------+---------------+-----------+------------+

Double is defined as `64 bits`_ and Float as `32 bits`_.

.. _programming_types.asn: https://github.com/eerimoq/asn1tools/tree/master/examples/programming_types/programming_types.asn

.. _64 bits: https://en.wikipedia.org/wiki/Double-precision_floating-point_format

.. _32 bits: https://en.wikipedia.org/wiki/Single-precision_floating-point_format
