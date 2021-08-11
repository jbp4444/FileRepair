# FileRepair
Investigating ways to repair files from checksum/parity info, in the event of unrecoverable disk errors.

The current program calculates one or more RAID-5-ish parity blocks across the file by treating the file
as a set of "virtual disks".  Each virtual-disk is checksummed so that we can detect per-disk damage.
As per RAID-5, if a (single) virtual-disk is found to be damaged (checksum doesn't match), then we
can repair the file by re-calculating the damaged disk from the parity blocks.

## Included Programs/Scripts:
* fileraid
.. The main code; can create a RAID-5 parity file, can verify from an existing file, and can repair
.. a damaged file from the parity info

* adderror.py
.. Adds bit- or byte-sized errors to an existing file; used for testing

* showbits.py
.. Similar to hexdump, prints out the bits or bytes in a given file

* makemockup.py
.. A start at recording the "important" bits that changed inside a damaged file.  Right now, it just
.. dumps all changed bits, one at a time.

* maketest.py
.. Uses adderror.py and the output from makemockup.py to create a file that is similar (in damage
.. structure) to another file.  I.e. it lays down a set of random bits, then twiddles the ones
.. that got twiddled in a previous damage-event.

