from radon.metrics import h_visit
import sys
ffile = open(str(sys.argv[1]),'r')
data=ffile.read()
h = h_visit(data)
print str(sys.argv[1]),h[0],h[1],h[2],h[3],h[4],h[5],h[6],h[7],h[8],h[9],h[10],h[11]
