Documentation for adderror:

TODO: add basic usage info

Syntax for the script options:
* The basic syntax is a space-separated list:
** (bit_or_byte) (range) (operation) (value)
* where bit_or_byte is one of:
** 'bi' for bit operations
** 'by' for byte operations
* where range is one of:
** a single number will just operate on a single bit or byte
** a hyphen-separated range, (start-stop), to operate on a contiguous range
of bits or bytes; the range is exclusive, that is, it will _not_ include
the stopping-index
* where operation is one of:
** 'r' to set the bit or byte to a random value; value will be ignored
** 's' to set the bit or byte to the given value, overwriting the current value;
if no value is given, it will be set to 0
** 'x' to XOR the bit or byte with the given value; if no value is
given, it will be XOR'ed with 255
* where value is one of:
** 0x00 for a hex value; upper or lower case will work
** 0o000 for an octal value
** 0b00000000 for a binary value
** otherwise a decimal value is assumed
