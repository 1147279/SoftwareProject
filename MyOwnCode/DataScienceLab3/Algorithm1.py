from mrjob.job import MRJob
import os
import time

class matrixMultiply(MRJob):
	
	def sortbyJ(listItem):
		return listItem[0]
	
	def mapper(self, _, line):
		#info1 = matrixM.readline()
		#info2 = matrixN.readline()
		if len(line.split()) == 3: 
			nameFile = os.environ['map_input_file']
			if nameFile == "outA1.list":			
				iM,jM,valueM =  line.split()
				#print '---',iM,jM,valueM,jN,kN,valueN,'---'
				for k in range(0,int(columnsN)):
				        yield (int(iM),int(k)),('M',int(jM),int(valueM))
					#print iM, k, 'M', jM, valueM
			else:
				jN,kN,valueN =  line.split()
				for i in range(0,int(rowsM)):
					yield (int(i),int(kN)),('N',int(jN),int(valueN))
		        		#print i, kN, 'N', jN, valueN


	def reducer(self, key, values):
		oldlistM = []
		oldlistN = []
		
		for i in values:
			if i[0]=='M':
				oldlistM.append([i[1],i[2]])
			else:
				oldlistN.append([i[1],i[2]])
		#print oldlistM
		#print oldlistN
		listM = sorted(oldlistM, key=lambda x:x[1])
		listN = sorted(oldlistN, key=lambda x:x[1])
		#print listM
		#print listN
		P = []
		k=0;
		#for i in range((len(listM)/(int(columnsM))-1)*int(columnsM),len(listM)):
		for i in listM:
			for l in range(0,len(listN)):
				if listN[l][0]==i[0]:			
					P.append(i[1]*listN[l][1])
					k=k+1
				else:
					P.append(0)
					
		#key.sort()
		sumofP=sum(P)
		if sumofP != 0:
			yield key,sumofP
			f=""
			g=""
			keystr=str(key).split(',')
			for i in range(1,len(keystr[0])):
				f+=keystr[0][i]
			for i in range(0,len(keystr[1])-1):
				g+=keystr[1][i]
			stringOut = f+g+' '+str(sumofP)+"\n"
			outputFile.write(stringOut)
		

		#print key, sum(P)
	


if __name__ == '__main__':
	matrixM = open("outA1.list","r")
	rowsM,columnsM = matrixM.readline().split()
	matrixN = open("outB1.list","r")
	rowsN,columnsN = matrixN.readline().split()
	print rowsN," ", columnsN
	if int(columnsN) == 1:
		#print "----"
		tempFile = open('Temp.txt','w')
		tempFile.write(rowsN+' '+columnsN+"\n")
		count=0	
		line = matrixN.readline()
		
		while line != "":
			i,val = line.split()
			tempFile.write(str(count)+' '+'0 '+val+"\n")
			count = count+1
			line = matrixN.readline()
			
		tempFile.close()
		reWrite = open('outB1.list','w')
		reWrite.truncate(0)
		tempFile = open('Temp.txt','r')
		for iterator in range (0,int(rowsN)+1):
			reWrite.write(tempFile.readline())
		reWrite.close()
	
	#print "columnsN=", columnsN
	outputFile = open('Output.txt','w')
	outputFile.write(str(rowsM)+' '+str(columnsN)+"\n")	
	starttime = time.time()  
	matrixMultiply.run()
	endtime = time.time()
	duration = endtime-starttime
	print "Time: ", duration 
	outputFile.close()
	matrixM.close()
	matrixN.close()
	









