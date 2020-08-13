from deployment import Deployment
from end_point import EndPoint
from etcd import Etcd
from pod import Pod
from worker_node import WorkerNode
import threading
from request import Request
from random import randrange

#The APIServer handles the communication between controllers and the cluster. It houses
#the methods that can be called for cluster management

class APIServer:
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Lock()
		self.kubeletList = [] 
		self.requestWaiting = threading.Event()
	
# 	GetDeployments method returns the list of deployments stored in etcd 	
	def GetDeployments(self):
		return self.etcd.deploymentList
		
#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.nodeList
		
#	GetPending method returns the list of PendingPods stored in etcd
	def GetPending(self):
		return self.etcd.pendingPodList
		
#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints(self):
		return self.etcd.endPointList
		
# CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd nodeList
	def CreateWorker(self, info):
		print('***Creating Worker***')
		worker = WorkerNode(info) # Init worker
		print('Current amount of nodes: {}'.format(len(self.etcd.nodeList)))
		self.etcd.nodeList.append(worker) # Add to nodeList
		print('New amount of nodes: {}\n'.format(len(self.etcd.nodeList)))
		pass
# CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(self, info):
		deployment = Deployment(info) # Init worker
		print('***Creating Deployment***')
		print('Current amount of deployments: {}'.format(len(self.etcd.deploymentList)))
		self.etcd.deploymentList.append(deployment) # Add to nodeList
		print('New amount of deployments: {}\n'.format(len(self.etcd.deploymentList)))
		# self.CreatePod(deployment.deploymentLabel)
		pass
# RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, deploymentLabel):
		print('***Removing {}***'.format(deploymentLabel[0]))
		print('Current amount of deployments: ', len(self.etcd.deploymentList))
		for i in self.etcd.deploymentList:
			if i.deploymentLabel == deploymentLabel[0]:
				self.etcd.deploymentList.remove(i)
				print('***Removed {}***'.format(deploymentLabel))
			else:
				continue
		print('New amount of deployments: ', len(self.etcd.deploymentList))
		# Terminate pods
		endPoints = self.GetEndPointsByLabel(deploymentLabel) # For pod reference to deployment being removed
		for j in endPoints:
			if j.deploymentLabel == deploymentLabel:
				self.TerminatePod(j) # Call local method to terminate pod based on endpoint
			else:
				continue
		pass
# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it 
# to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):
		endPoint = EndPoint(pod, pod.deploymentLabel, worker)
		self.etcd.endPointList.append(endPoint)
		pass
# CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):
		result = False
		for i in self.etcd.nodeList:
			if endPoint.node == i:
				result = True
			else:
				continue
		return result
# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):
		endPointList = []
		for i in self.etcd.endPointList:
			if i.deploymentLabel == deploymentLabel:
				endPointList.append(i)
			else:
				continue
		return endPointList
# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deploymentLabel):
		print('***Creating new pod***')
		deployment = Deployment
		for i in self.etcd.deploymentList:
			if i.deploymentLabel == deploymentLabel:
				deployment = i
				print('***Found deployment {}***'.format(deploymentLabel))
				break
			else:
				continue
		name = deploymentLabel + '_POD_' + str(randrange(1, 100))
		pod = Pod(name, deployment.cpuCost, deploymentLabel)
		self.etcd.pendingPodList.append(pod)
		print('***Pod {} created***\n'.format(name))
		pass
# GetPod returns the pod object stored in the internal podList of a WorkerNode
	def GetPod(self, endPoint):
		return endPoint.pod
# TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
# No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
# it will be deleted by the Kubelet
	def TerminatePod(self, endPoint):
		print('***Terminating pods***')
		pod = endPoint.pod
		pod.status = 'TERMINATING'
		print('***Pod {} status TERMINATING\n'.format(pod.podName))
		pass
# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, deploymentLabel):
		pass
# AssignNode takes a pod in the pendingPodList and transfers it to the internal podList of a specified WorkerNode
	def AssignNode(self, pod, worker):
		self.etcd.pendingPodList.remove(pod)
		worker.podList.append(pod)
		pass
#	pushReq adds the incoming request to the handling queue	
	def PushReq(self, info):
	    self.etcd.reqCreator.submit(self.ReqHandle, info)

#Creates requests and notifies the handler of request to be dealt with
	def ReqHandle(self, info): # reqAppend. This does not handle only adds requests singly
		self.etcd.pendingReqs.append(Request(self, info))
		self.requestWaiting.set()
