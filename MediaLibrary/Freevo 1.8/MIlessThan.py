fp = open("freevoMI.txt","r")
count = 0
writefile = open("MINewCount.txt","w")
writefile.write("MI Summary Less than 20 \n")
for line in fp:
	sMI = line.rpartition('(')[-1]
	s = line
	s2= sMI[:-5]
	#print s2
	if int(s2)<20:
		count = count +1
		writefile.write(s+"\n")

writefile.write("Number Of Files with MI less than 20 = "+str(count))





