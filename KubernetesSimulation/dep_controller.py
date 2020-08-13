from api_server import APIServer
import threading
import time


#DepController is a control loop that creates and terminates Pod objects based on
#the expected number of replicas.
class DepController:
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("depController start")
		while self.running:
			with self.apiServer.etcdLock:
				for deployment in self.apiServer.etcd.deploymentList:
					while deployment.currentReplicas <= deployment.expectedReplicas:
						self.apiServer.CreatePod(deployment.deploymentLabel)
						deployment.currentReplicas += 1
				pass
		time.sleep(self.time)
		print("DepContShutdown")
