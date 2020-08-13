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
				if len(self.apiServer.etcd.pendingReqs) > 0:
					for req in self.apiServer.etcd.pendingReqs:
						for endPoint in self.apiServer.etcd.endPointList:
							if endPoint.pod.status != 'TERMINATING' or endPoint.pod.status != 'FAILED':
								if endPoint.pod.deploymentLabel == req.deploymentLabel:
									endPoint.pod.HandleRequest(req.execTime)
					pass
				else:
					pass
			self.apiServer.requestWaiting.clear()
		print("ReqHandlerShutdown")