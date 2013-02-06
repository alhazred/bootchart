#!/usr/sbin/dtrace -Cs

#pragma D option quiet

/* We need process pid, his forks and lifetime */
proc:::create
{
	printf("<fork ppid=%d cpid=%d execname=%s time=%d />\n",
	    pid,args[0]->pr_pid,execname,`lbolt*10/ `hz);
}

proc:::exec-success
{
	printf("<process pid=%d execname=%s time=%d />\n",
	    pid,execname,`lbolt*10/ `hz);

}

proc:::exit                                                                                                   
{                                                                                                             
        printf("<end pid=%d execname=%s time=%d />\n", pid, execname,`lbolt*10/ `hz);                                          
}                                                                                                             
	       
