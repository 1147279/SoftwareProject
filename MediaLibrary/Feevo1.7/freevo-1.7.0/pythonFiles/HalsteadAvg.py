infile = open("Halstead.txt",'r')
n1=0
n2=0
N1=0
N2=0
vocab=0
length=0
calclength=0
vol=0
diff=0
effo=0
time=0
bugs = 0
count = 0
for line in infile:
	linething = line.split()
	n1 = n1 + float(linething[1])
	n2 = n2 + float(linething[2])
	N1 = N1 + float(linething[3])
	N2 = N2 + float(linething[4])
	vocab = vocab + float(linething[5])
	length = length + float(linething[6])
	calclength = calclength + float(linething[7])
	vol = vol + float(linething[8])
	diff = diff + float(linething[9])
	effo = effo + float(linething[10])
	time = time + float(linething[11])	
	bugs = bugs + float(linething[12])
	count = count +1

n1avg = n1/count
n2avg = n2/count
N1avg = N1/count
N2avg = N2/count
vocabavg = vocab/count
lengthavg = length/count
calclengthavg = calclength/count
volavg = vol/count
diffavg = diff/count
effoavg = effo/count
timeavg = time/count
bugsavg = bugs/count

ofile = open("HalsteadAVG.txt",'w')
outstring = "n1: " + str(n1avg) + "\nn2: " + str(n2avg) + "\nN1: " + str(N1avg) + "\nN2: " + str(N2avg) + "\nvocab: " + str(vocabavg) + "\nlength: " + str(lengthavg) + "\ncalc. length: " + str(calclengthavg) + "\nVolume: " + str(volavg) + "\nDifficulty: " + str(diffavg) + "\nEffort: " + str(effoavg) + "\nTime: " + str(timeavg) + "\nBugs: " + str(bugsavg)
ofile.write(outstring)
