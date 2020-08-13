from api_server import APIServer
import threading
import time


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController:
	
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("NodeController start")
		while self.running:
			with self.apiServer.etcdLock:
				if len(self.apiServer.etcd.endPointList) > 0:
					for endPoint in self.apiServer.etcd.endPointList:
						if self.apiServer.CheckEndPoint(endPoint):
							if endPoint.pod.status == 'FAILED':
								print('***Removing endpoint: {}'.format(endPoint.deploymentLabel))
								self.apiServer.etcd.runningPodList.remove(endPoint.pod)
								self.apiServer.etcd.pendingPodList.append(endPoint.pod)
								endPoint.pod.status = 'PENDING'
								endPoint.node.podList.remove(endPoint.pod)
								endPoint.node.available_cpu += endPoint.pod.available_cpu
							elif endPoint.pod.status == 'TERMINATING':
								self.apiServer.etcd.endPointList.remove(endPoint)
								pass
						else:
							self.apiServer.etcd.endPointList.remove(endPoint)
				else:
					pass
		time.sleep(self.time)
		print("NodeContShutdown")
