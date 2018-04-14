fp = open("Dependencies.txt","r")
isdependency=0
writefile = open("DependencyNew.txt","w")
for line in fp:
	if line == "External dependencies\n":
		isdependency =1
	if line == "Raw metrics\n":
		isdependency =0
	if isdependency ==1:
		writefile.write(line + "\n")
		
	print line , "-------------" , isdependency, "\n"
	
