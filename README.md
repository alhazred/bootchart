bootchart
=========

Bootchart using DTrace

dtrace -AFs boot.d
reboot

After reboot:

dtrace -ae -o bootlog
dtrace -A
bootchart.py bootlog

NOTE: that was written 5 years ago (2008), some things must be fixed for OpenIndiana