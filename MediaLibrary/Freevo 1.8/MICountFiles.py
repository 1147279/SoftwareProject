fp = open("freevoMI.txt","r")
count = 0
writefile = open("NumOfFilesCount.txt","w")
writefile.write("Number Of Files Count \n")
for line in fp:
	count = count +1

writefile.write("Number Of Files = "+str(count))
