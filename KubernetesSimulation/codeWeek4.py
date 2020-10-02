
# Based Feedback Control for Computer Systems by Philipp K. Janert (O'Reilly Media)
# @author Panos Patros

# Lookup here to set up a Python Virtual Environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
import random
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
import math

class QueueBuffer:
	def __init__( self, max_wip, max_flow ):
		self.queued = 0
		self.wip = 0			 # work-in-progress ("ready pool")

		self.max_wip = max_wip
		self.max_flow = max_flow # avg outflow is max_flow/2

	def work( self, u ):
		# Add to ready pool
		u = max( 0, int(round(u)) )
		u = min( u, self.max_wip )
		self.wip += u

		# Transfer from ready pool to queue
		r = int( round( random.uniform( 0, self.wip ) ) )
		self.wip -= r
		self.queued += r

		# Release from queue to downstream process
		r = int( round( random.uniform( 0, self.max_flow ) ) )
		r = min( r, self.queued )
		self.queued -= r

		return self.queued


# ============================================================
def simulate( p, tm=5000 ):
	
	def inTasks():
		return (math.cos(t*0.01)+1)*100 + 50

	# Start simulation
	T = [] #Store time
	E = [] #Store errors
	U = [] #Store control signal values
	Y = [] #Store measured output values
	y = 0
	for t in range(tm):
		u = inTasks()
		y = p.work(u)
		
		T.append(t)
		U.append(u)
		Y.append(y)
		
	return {
		"T": T, 
		"U": U,
		"Y": Y
		}
	
# ============================================================
p = QueueBuffer( 400, 250 )

results = simulate( p, 20000)

plt.figure(1, figsize=(12,6))

plt.subplot(211)
plt.xlabel('Time')
plt.ylabel('Queue Length')
plt.plot(results["T"], results["Y"], label="Output (y)")
plt.legend(loc="upper left")


plt.subplot(212)
plt.xlabel('Time')
plt.ylabel('Requests to Handle')
plt.plot(results["T"], results["U"], label="Input (u)")
plt.legend(loc="upper left")


plt.show()




