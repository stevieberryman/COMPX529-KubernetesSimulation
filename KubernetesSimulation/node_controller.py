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
				if len(self.apiServer.etcd.endPointList) > 0: # List not empty
					for endPoint in self.apiServer.etcd.endPointList: # iterate endpoints
						if self.apiServer.CheckEndPoint(endPoint): # check endpoint is not stale
							if endPoint.pod.status == 'FAILED': # status check Failed pods should be requed
								print('***Removing endpoint: {}'.format(endPoint.deploymentLabel))
								for j in self.apiServer.etcd.runningPodList: # pod in runningList reque into pendingList
									if j == endPoint.pod:
										self.apiServer.etcd.runningPodList.remove(endPoint.pod)
										self.apiServer.etcd.pendingPodList.append(endPoint.pod)
								endPoint.pod.status = 'PENDING' # set new status
								endPoint.node.podList.remove(endPoint.pod) # remove pod from worker podlist
								endPoint.node.available_cpu += endPoint.pod.available_cpu # restore node resources
								self.apiServer.etcd.endPointList.remove(endPoint)
								del endPoint
							elif endPoint.pod.status == 'TERMINATING': # status check Terminated pods should be deleted from the system with the deployment
								# remove from pending if exists in list
								for i in self.apiServer.etcd.pendingPodList:
									if i == endPoint.pod:
										self.apiServer.etcd.pendingPodList.remove(i)
										# remove stale endpoint
										self.apiServer.etcd.endPointList.remove(endPoint)
										del i
										del endPoint
										break
								# remove from running if exists in list
								for j in self.apiServer.etcd.runningPodList:
									if j == endPoint.pod:
										self.apiServer.etcd.runningPodList.remove(j)
										# remove stale endpoint
										self.apiServer.etcd.endPointList.remove(endPoint)
										del j
										del endPoint
										break
						else:
							self.apiServer.etcd.endPointList.remove(endPoint)
				else:
					pass
			time.sleep(self.time)
		print("NodeContShutdown")
