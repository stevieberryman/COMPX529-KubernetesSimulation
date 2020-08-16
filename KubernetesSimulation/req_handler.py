from api_server import APIServer
import time

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler:
	def __init__(self, APISERVER):
		self.apiServer = APISERVER
		self.running = True
	
	def __call__(self):
		print("reqHandler start")
		while self.running:
			self.apiServer.requestWaiting.wait()
			with self.apiServer.etcdLock:
				if len(self.apiServer.etcd.pendingReqs) > 0: # list not empty
					for req in self.apiServer.etcd.pendingReqs: # iterate reqs
						for endPoint in self.apiServer.etcd.endPointList: # iterate endPoints
							if endPoint.pod.status != 'TERMINATING' or endPoint.pod.status != 'FAILED': # ensure pod not marked for Termination or reQue
								if endPoint.pod.deploymentLabel == req.deploymentLabel: # pod matches req
									if endPoint.pod.status == 'RUNNING':
										endPoint.pod.HandleRequest(req.execTime) # handle request
				else:
					pass
			
			self.apiServer.requestWaiting.clear()
		print("ReqHandlerShutdown")