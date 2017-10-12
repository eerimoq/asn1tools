.. asn1tools documentation master file, created by
   sphinx-quickstart on Sat Apr 25 11:54:09 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2

ASN.1 tools
===========

.. include:: ../README.rst

Basic Usage
===========

.. autofunction:: asn1tools.compile_files

.. autoclass:: asn1tools.compiler.Specification
    :members:

Types
=====

ASN.1 types are mapped to Python types as shown in the table below.

+-------------------+-------------+-----------------------+
| ASN.1 type        | Python type | Example               |
+===================+=============+=======================+
| BOOLEAN           | ``bool``    | ``True``              |
+-------------------+-------------+-----------------------+
| INTEGER           | ``int``     | ``87``                |
+-------------------+-------------+-----------------------+
| BIT STRING        | ``tuple``   | ``(b'\x4b', 7)``      |
+-------------------+-------------+-----------------------+
| OCTET STRING      | ``bytes``   | ``b'\x44\x1e\xff'``   |
+-------------------+-------------+-----------------------+
| NULL              | --          | ``None``              |
+-------------------+-------------+-----------------------+
| OBJECT IDENTIFIER | ``str``     | ``'1.33.2'``          |
+-------------------+-------------+-----------------------+
| ObjectDescriptor  | --          | --                    |
+-------------------+-------------+-----------------------+
| REAL              | ``float``   | ``33.12``             |
+-------------------+-------------+-----------------------+
| ENUMERATED        | ``str``     | ``'one'``             |
+-------------------+-------------+-----------------------+
| UTF8String        | ``str``     | ``'hello'``           |
+-------------------+-------------+-----------------------+
| SEQUENCE          | ``dict``    | ``{'a': 52, 'b': 1}`` |
+-------------------+-------------+-----------------------+
| SEQUENCE OF       | ``list``    | ``[1, 3]``            |
+-------------------+-------------+-----------------------+
| SET               | ``dict``    | ``{'foo': 'bar'}``    |
+-------------------+-------------+-----------------------+
| SET OF            | ``list``    | ``[3, 0, 7]``         |
+-------------------+-------------+-----------------------+
| NumericString     | ``str``     | ``'234359'``          |
+-------------------+-------------+-----------------------+
| PrintableString   | ``str``     | ``'goo'``             |
+-------------------+-------------+-----------------------+
| IA5String         | ``str``     | ``'name'``            |
+-------------------+-------------+-----------------------+
| UTCTime           | ``str``     | ``'170912120239'``    |
+-------------------+-------------+-----------------------+
| VisibleString     | ``str``     | ``'gle'``             |
+-------------------+-------------+-----------------------+

Advanced Usage
==============

.. autofunction:: asn1tools.compile_string

.. autofunction:: asn1tools.compile_dict

.. autofunction:: asn1tools.parse_files

.. autofunction:: asn1tools.parse_string
