import math
import time


'''
The utility proportional fairness algorithm is described in the below paper

Wei-Hua Wang, Marimuthu Palaniswami, and Steven H. Low.
Application-Oriented Flow Control: Fundamentals, Algorithms and Fairness. 
IEEE/ACM TRANSAC- TIONS ON NETWORKING, VOL. 14, NO. 6), December 2006.


The code is hardcoded for the network

the network is shown below
          
    h1-           -h2
       s1 ----- s2 
    h3-           -h4

'''

gama = 0.005
FLOWS_COUNT = 2

c0 = 1 		# HD flow, not easily satisfied
c1 = 4    	# easily satisfied, as it is an low quality SD flow

def U(s,x):
	if s==0: 
		# return 1.0/(1.0 + (math.e)**(10-(2*x)) )
		if x < m[s]:
			return 0
		else:
			return c0*x
	elif s==1:
		if x < m[s]:
			return 0
		else:
			return c1*x
	else:
		assert(False)


def Uinv(s,x):
	if s==0: 
		# print "arg of log : ", (1.0/x) - 1
		# return 0.5*(10 - math.log((1.0/x)-1))
		return (1.0/c0)*x
	elif s==1:
		return (1.0/c1)*x
	else:
		assert(False)


# xf(l) is the aggregate source rate at link l
def xf(l):
	if l==0:
		return x[0] + x[1]
	else:
		assert(False)

# pf(s) is the path price of source s
def pf(s):
	if s==0 or s==1: 
		return p[0]
	else:
		assert(False)


# c is the list of maximum bandwidth capacity of links
c = [3.0]

# minimum and maximum bandwidth requirements
m = [0.00001, 0.00001]
M = [10.0, 10.0]

p = [0.00001]
x = [0.00001, 0.00001]

# x is the list of bandwidth allocation of flows


print "Utilities Range: ",
for s in xrange(0,FLOWS_COUNT):
	l = U(s,m[s])
	r = U(s,M[s])
	print "[{}, {}],  ".format(l,r),
print

# print "Utilities Range: ",
# for s in xrange(0,3):
# 	l = Uinv(s,m[s])
# 	r = Uinv(s,M[s])
# 	print "[{}, {}],  ".format(l,r),
# print


itr = 0
while True:
	# if itr==6:
	# 	break

	# xf(l) is the aggregate source rate at link l
	print "p : ",
	for l in xrange(0,1):
		p[l] = max(p[l] + gama*(xf(l) - c[l]), 0.00001)
		print "{0} ,\t".format(p[l]),
		#print "p[{0}] = {1}".format(l,p[l])
	print


	print "x : ",
	for s in xrange(0,FLOWS_COUNT):

		# pf(s) is the path price of source s
		if pf(s) >= 1.0/(U(s,m[s])):
			x[s] = m[s]
		elif pf(s) <= 1.0/(U(s,M[s])):
			x[s] = M[s]
		else:
			arg = max( U(s,m[s]), min(U(s,M[s]), (1.0/(pf(s)))  )  )
			x[s] = Uinv(s,arg)

		print "{0} ,\t".format(x[s]),
	print

	print "Sum of Utilitites : {0}".format(U(0,x[0]) + U(1,x[1]))

	# time.sleep(1)

	itr = itr + 1
