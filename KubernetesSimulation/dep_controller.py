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
				if len(self.apiServer.etcd.deploymentList) > 0:
					for deployment in self.apiServer.etcd.deploymentList:
						if deployment.currentReplicas <= deployment.expectedReplicas:
							while deployment.currentReplicas < deployment.expectedReplicas:
								self.apiServer.CreatePod(deployment.deploymentLabel)
								deployment.currentReplicas += 1
						elif deployment.currentReplicas > deployment.expectedReplicas:
							while deployment.currentReplicas > deployment.expectedReplicas:
								self.apiServer.TerminatePod(self.apiServer.GetEndPointsByLabel(deployment.deploymentLabel))
								deployment.currentReplicas -= 1
			time.sleep(self.time)
		print("DepContShutdown")
