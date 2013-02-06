#!/usr/bin/python
#                                                                                                                                                            
# CDDL HEADER START                                                                                                                                          
#                                                                                                                                                            
# The contents of this file are subject to the terms of the                                                                                                  
# Common Development and Distribution License (the "License").                                                                                               
# You may not use this file except in compliance with the License.                                                                                           
#                                                                                                                                                            
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE                                                                                        
# or http://www.opensolaris.org/os/licensing.                                                                                                                
# See the License for the specific language governing permissions                                                                                            
# and limitations under the License.                                                                                                                         
#                                                                                                                                                            
# When distributing Covered Code, include this CDDL HEADER in each                                                                                           
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.                                                                                          
# If applicable, add the following below this CDDL HEADER, with the                                                                                          
# fields enclosed by brackets "[]" replaced with your own identifying                                                                                        
# information: Portions Copyright [yyyy] [name of copyright owner]                                                                                           
#                                                                                                                                                            
# CDDL HEADER END                                                                                                                                            
#                                                                                                                                                            
# Copyright 2008 Sun Microsystems, Inc.  All rights reserved.                                                                                                
# Use is subject to license terms.                                                                                                                           
#                                                                                          
# sample boot chart renderer for dtrace log (required SUNWpython-imaging)
# Alexander Eremin <eremin@milax.org> 2008
# 

import sys, re, os, time, datetime
import Image, ImageFont, ImageDraw, ImageOps                                                                         
                                                                                                              

class Node:
    def __init__(self, pid, forks, stime,etime,cmd):
	self.pid = pid
	self.forks = []
	self.stime = stime
	self.etime = etime
	self.cmd = cmd

class Fork:
    def __init__(self, pid, etime,cmd):
	self.pid = pid
	self.etime = etime
	self.cmd = cmd

try:
    dlog = sys.argv[1];  
except:
    print "Usage:",sys.argv[0], "dtrace_log_file"
    sys.exit(1)

w=1000 # image width
h=8000	# image height	

img=Image.new("RGB", (w,h), "white")                                                                      
fb = ImageFont.truetype("/usr/X11/lib/X11/fonts/TrueType/core/Arial.ttf", 16)                                       
f = ImageFont.truetype("/usr/X11/lib/X11/fonts/TrueType/core/Arial.ttf", 10)                                       
                                                                                                              
draw = ImageDraw.Draw(img)                                                                                    
		 
# parsing processes	      
log = open(dlog)
list = []
for line in log:
    line = line.rstrip()
    if re.search("<proc",line):
	pid = re.findall("[\s]pid=[^\s]*",line)[0].split("=")[1]
	time = re.findall("time=[^\s]*",line)[0].split("=")[1]
	execname = re.findall("execname=[^\s]*",line)[0].split("=")[1]
	node = Node(pid,0,time,0,execname)
#	if execname!="ksh93":
	list.append(node)

# parsing forks
log = open(dlog)
for line in log:
    line = line.rstrip()
    if re.search("<fork",line):
        ppid = re.findall("[\s]ppid=[^\s]*",line)[0].split("=")[1]
	cpid = re.findall("[\s]cpid=[^\s]*",line)[0].split("=")[1]
	time = re.findall("time=[^\s]*",line)[0].split("=")[1]
	execname = re.findall("execname=[^\s]*",line)[0].split("=")[1]
	for node in list:
	    if execname==str(node.cmd) and ppid==str(node.pid):
		node.forks.append(Fork(cpid,0,execname))
	    for fork in node.forks:
		if execname==str(fork.cmd) and ppid==str(fork.pid):
		    node.forks.append(Fork(cpid,0,execname))
# parsing endtime
log = open(dlog)
for line in log:
    line = line.rstrip()
    if re.search("<end",line):
        pid = re.findall("[\s]pid=[^\s]*",line)[0].split("=")[1]
	time = re.findall("time=[^\s]*",line)[0].split("=")[1]
	execname = re.findall("execname=[^\s]*",line)[0].split("=")[1]
	for node in list:
	    if execname==str(node.cmd) and pid==str(node.pid):
		node.etime=time

	    for fork in node.forks:
		if execname==str(fork.cmd) and pid==str(fork.pid):
		    fork.etime=time

# calculate endtime for process - if fork live, endtime = 0
for node in list:
	if len(node.forks)>0:
	    n=0
	    e=0
	    etime=0
	    for fork in node.forks:
		if fork.etime==0:
	    	    n+=1
		else:
	    	    e+=1	
	    	    etime=fork.etime	
	    if n>e:
		node.etime=0


n=0
tm=0
y2=50

# draw header
t = datetime.datetime.now()                                                                                   
draw.text((6,2),"Boot chart for " + os.uname()[1] + " (" + t.ctime() + ")",font=fb,fill=(0,0,0))                
draw.text((6,25), "uname: " + os.uname()[0] + " " + os.uname()[2]+ " " +os.uname()[3] + " " + os.uname()[4],font=f,fill=(0,0,0))                
                                                                                    
# draw frame 
draw.rectangle((2,50,w-2,h-2), outline=(153,153,204), fill="white")                              

for n in range (100):
    draw.line((n*10,50,n*10,h-2), fill=(220,220,220))
n=-5
while n!=100:
    n+=5
    draw.text((n*10,40),str(n)+"s",font=f,fill=(61,61,61))
    draw.line((n*10,50,n*10,h-2), fill=(180,180,180))

for node in list:
	n=n+1
	x1=int(node.stime) 
	if n==1:
	    y1=x1
	if node.etime==0:
	    x2=w-3
	else:
	    x2=int(node.etime)     
	y1=y2
	y2=y1+15
# draw processes
	draw.rectangle((x1,y1,x2,y2), outline=(185,185,236), fill=(242,242,242))                              
	draw.text( (x1+5,y1+1), node.cmd,  font=f, fill=(41,41,41))                                                    
		                                                                                                                

log.close()
del draw                                                                                                      
		                                                                                                                
img.save("bootchart.png", "PNG") 
