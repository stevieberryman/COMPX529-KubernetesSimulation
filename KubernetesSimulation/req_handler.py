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
				for req in self.apiServer.etcd.pendingReqs:
					for endPoint in self.apiServer.etcd.endPointList:
						if endPoint.pod.podName == req.deploymentLabel:
							endPoint.pod.HandleRequest(req.execTime)
				pass
			self.apiServer.requestWaiting.clear()
		time.sleep(5)
		print("ReqHandlerShutdown")