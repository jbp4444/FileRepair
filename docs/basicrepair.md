Documentation for basicrepair:

TODO: add basic usage info

The basicrepair tool attempts to repair a damage file based on a single
whole-file checksum (from before the file was damaged).  It does this by
testing, one at a time, every possible value for every single byte in the
entire file.  THIS CAN BE A VERY TIME-CONSUMING PROCESS!

To speed things up, you may choose to use multiple CPUs on a single
computer.  This will potentially slow down all other work on your machine,
but should accelerate the time-to-solution by N-times (for N CPUs).  Use
the '-n' option to set the number of CPUs (don't set it to more than the
number of CPUs present on the machine; trying to use 10 CPUs on a 8-CPU
machine could slow things down).
