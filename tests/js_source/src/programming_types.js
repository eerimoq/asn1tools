class Encoder {
    constructor() {
        this.buf = [];
    }

    append_bytes(buf) {
        this.buf = this.buf.concat(Array.from(buf));
    }

    append_uint8(value) {
        this.append_bytes(new Uint8Array([value]));
    }

    append_uint16(value) {
        this.append_bytes(new Uint8Array([
            (value >> 8) & 0xff,
            value & 0xff
        ]));
    }

    append_uint32(value) {
        this.append_bytes(new Uint8Array([
            (value >> 24) & 0xff,
            (value >> 16) & 0xff,
            (value >> 8) & 0xff,
            value & 0xff
        ]));
    }

    append_int8(value) {
        this.append_uint8(value);
    }

    append_int16(value) {
        this.append_uint16(value);
    }

    append_int32(value) {
        this.append_uint32(value);
    }

    append_uint(value, number_of_bytes) {
        switch (number_of_bytes) {

        case 1:
            this.append_uint8(value);
            break;

        case 2:
            this.append_uint16(value);
            break;

        case 3:
            this.append_uint8(value >> 16);
            this.append_uint16(value);
            break;

        default:
            this.append_uint32(value);
            break;
        }
    }

    append_bool(value) {
        if (value) {
            this.append_uint8(255);
        } else {
            this.append_uint8(0);
        }
    }

    append_length_determinant(length) {
        if (length < 128) {
            this.append_int8(length);
        } else if (length < 256) {
            this.append_uint8(0x81);
            this.append_uint8(length);
        } else if (length < 65536) {
            this.append_uint8(0x82);
            this.append_uint16(length);
        } else if (length < 16777216) {
            length |= (0x83 << 24);
            this.append_uint32(length);
        } else {
            this.append_uint8(0x84);
            this.append_uint32(length);
        }
    }

    toUint8Array() {
        return new Uint8Array(this.buf);
    }
}

class Decoder {
    constructor(data) {
        this.buf = data;
        this.pos = 0
    }

    read_bytes(size) {
        var data = this.buf.subarray(this.pos, this.pos + size);
        this.pos += size;

        return data;
    }

    read_uint8() {
        return this.read_bytes(1)[0];
    }

    read_uint16() {
        return ((this.read_bytes(1)[0] * 256)
                + this.read_bytes(1)[0]);
    }

    read_uint32() {
        return ((this.read_bytes(1)[0] * 16777216)
                + (this.read_bytes(1)[0] * 65536)
                + (this.read_bytes(1)[0] * 256)
                + this.read_bytes(1)[0]);
    }

    read_int8() {
        var value = this.read_uint8();

        if (value & 0x80) {
            value -= 256;
        }

        return value;
    }

    read_int16() {
        var value = this.read_uint16();

        if (value & 0x8000) {
            value -= 65536;
        }

        return value;
    }

    read_int32() {
        var value = this.read_uint32();

        if (value & 0x80000000) {
            value -= 0x100000000;
        }

        return value;
    }

    read_uint(number_of_bytes) {
        switch (number_of_bytes) {

        case 1:
            return this.read_uint8();

        case 2:
            return this.read_uint16();

        case 3:
            return ((this.read_uint8() * 65536)
                    + this.read_uint16());

        case 4:
            return this.read_uint32();

        default:
            throw "Too big value.";
        }
    }

    read_bool() {
        return this.read_uint8() != 0;
    }

    read_length_determinant() {
        var length = this.read_uint8();

        if (length & 0x80) {
            switch (length & 0x7f) {

            case 1:
                length = this.read_uint8();
                break;

            case 2:
                length = this.read_uint16();
                break;

            case 3:
                length = ((this.read_uint8() * 65536)
                          + this.read_uint16());
                break;

            case 4:
                length = this.read_uint32();
                break;

            default:
                throw "Too big value.";
            }
        }

        return length;
    }

    read_tag() {
        var tag = this.read_uint8();

        if ((tag & 0x3f) == 0x3f) {
            do {
                tag *= 256;
                tag += this.read_uint8();
            } while ((tag & 0x80) == 0x80);
        }

        return tag;
    }
}

function minimum_uint_length(value) {
    var length;

    if (value < 256) {
        length = 1;
    } else if (value < 65536) {
        length = 2;
    } else if (value < 16777216) {
        length = 3;
    } else {
        length = 4;
    }

    return length;
}

function c_source_a_encode_inner(encoder, data) {
    encoder.append_int8(data.a);
    encoder.append_int16(data.b);
    encoder.append_int32(data.c);
    encoder.append_uint8(data.e);
    encoder.append_uint16(data.f);
    encoder.append_uint32(data.g);
    encoder.append_bool(data.i);
    encoder.append_bytes(data.j);
}

function c_source_a_decode_inner(decoder) {
    return {
        a: decoder.read_int8(),
        b: decoder.read_int16(),
        c: decoder.read_int32(),
        e: decoder.read_uint8(),
        f: decoder.read_uint16(),
        g: decoder.read_uint32(),
        i: decoder.read_bool(),
        j: decoder.read_bytes(11)
    };
}

function c_source_a_encode(data) {
    var encoder = new Encoder();

    c_source_a_encode_inner(encoder, data);

    return encoder.toUint8Array();
}

function c_source_a_decode(buf)
{
    var decoder = new Decoder(buf);

    return c_source_a_decode_inner(decoder);
}

export {
    c_source_a_encode,
    c_source_a_decode,
    Encoder,
    Decoder
};
