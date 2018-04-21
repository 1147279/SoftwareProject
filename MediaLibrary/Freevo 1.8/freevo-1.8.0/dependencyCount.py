fp = open("Dependency18.txt","r")
isdependency=0
count=0
writefile = open("DependencyCount.txt","w")
for line in fp:
	if len(line)>5:
		sMI = line.rpartition('      ')[-1]
		if sMI[0] != "E":
			if sMI[0] != "-":
				if sMI != "    src \n":
					if sMI != "    pythonFiles \n":
						#print sMI[:-2]
						count = count +1
writefile.write("Number of Dependencies \n")
writefile.write(str(count))
	#if line[1]=="\":
	#	count = count+1
	#print line , "-------------" , isdependency, "\n"
