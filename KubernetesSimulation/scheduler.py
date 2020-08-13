from api_server import APIServer
import threading
import time

#The Scheduler is a control loop that checks for any pods that have been created
#but not yet deployed, found in the etcd pendingPodList.
#It transfers Pod objects from the pendingPodList to the runningPodList and creates an EndPoint object to store in the etcd EndPoint list
#If no WorkerNode is available that can take the pod, it remains in the pendingPodList
class Scheduler(threading.Thread):
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print('Scheduler start')
		while self.running:
			with self.apiServer.etcdLock:
				if len(self.apiServer.etcd.pendingPodList) > 0:
					print('***Attempting to assign {} pod(s)***'.format(len(self.apiServer.etcd.pendingPodList)))
					for pod in self.apiServer.etcd.pendingPodList: # iterate pods
							for worker in self.apiServer.etcd.nodeList: # iterate workerNodes
								if worker.available_cpu >= pod.available_cpu: # check cpu availability
									self.apiServer.CreateEndPoint(pod, worker)
									self.apiServer.etcd.pendingPodList.remove(pod)
									self.apiServer.etcd.runningPodList.append(pod)
									pod.status = 'RUNNING'
									worker.podList.append(pod)
									worker.available_cpu -= 1
									print('***Pod {} assigned to Node: {}***\n'.format(pod.podName, worker.label))
									break
								else: # not enough cpu resources
									continue
				else:
					pass
				# print('Current scheduler pass metrics:\nPending pods: {}\nRunning pods: {}\n'.format(len(self.apiServer.etcd.pendingPodList), len(self.apiServer.etcd.runningPodList)))
			time.sleep(self.time)
		print('SchedShutdown')
