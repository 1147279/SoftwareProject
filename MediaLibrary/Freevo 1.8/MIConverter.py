fp = open("freevoMI.txt","r")
sumof=0
count = 0
writefile = open("MINew.txt","w")
for line in fp:
	s = line.rpartition('(')[-1]
	s2= s[:-5]
	sumof = sumof + int(s2)
	count = count +1
avg = sumof/count
writefile.write("MI Summary Avg \n")
writefile.write(str(avg))

