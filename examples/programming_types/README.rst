About
=====

Types commonly used in programming languages, defined in the ASN.1
module `programming_types.asn`_.

+--------------+---------------+-----------+
| ASN.1 type   | C             | Python    |
+==============+===============+===========+
| Int8         | ``int8_t``    | ``int``   |
+--------------+---------------+-----------+
| Int16        | ``int16_t``   | ``int``   |
+--------------+---------------+-----------+
| Int32        | ``int32_t``   | ``int``   |
+--------------+---------------+-----------+
| Int64        | ``int64_t``   | ``int``   |
+--------------+---------------+-----------+
| Uint8        | ``uint8_t``   | ``int``   |
+--------------+---------------+-----------+
| Uint16       | ``uint16_t``  | ``int``   |
+--------------+---------------+-----------+
| Uint32       | ``uint32_t``  | ``int``   |
+--------------+---------------+-----------+
| Uint64       | ``uint64_t``  | ``int``   |
+--------------+---------------+-----------+
| Double       | ``double``    | ``float`` |
+--------------+---------------+-----------+
| Float        | ``float``     | ``float`` |
+--------------+---------------+-----------+
| Bool         | ``bool``      | ``bool``  |
+--------------+---------------+-----------+
| String       | ``char *``    | ``str``   |
+--------------+---------------+-----------+
| Bytes        | ``uint8_t *`` | ``bytes`` |
+--------------+---------------+-----------+

Double is defined as `64 bits`_ and Float as `32 bits`_.

.. _programming_types.asn: https://github.com/eerimoq/asn1tools/tree/master/examples/programming_types/programming_types.asn

.. _64 bits: https://en.wikipedia.org/wiki/Double-precision_floating-point_format

.. _32 bits: https://en.wikipedia.org/wiki/Single-precision_floating-point_format
