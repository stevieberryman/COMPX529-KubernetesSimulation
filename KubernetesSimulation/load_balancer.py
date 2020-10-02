from api_server import APIServer
from deployment  import Deployment
import time

#LoadBalancer distributes requests to pods in Deployments

class LoadBalancer:
	def __init__(self, APISERVER, DEPLOYMENT):
		self.apiServer = APISERVER
		self.deployment = DEPLOYMENT
		self.running = True
		requests = []
	
	def __call__(self):
		pass

class RoundRobinLoadBalancer(LoadBalancer):
	def __call__(self):
		print("RoundRobinLoadBalancer start")
		while self.running:
			self.deployment.waiting.wait()
			with self.deployment.lock:
				while len(self.deployment.pendingReqs) > 0:
					self.requests = self.deployment.pendingReqs.copy()
					self.deployment.pendingReqs.clear()
				if len(self.requests) > 0:
					for request in self.requests:
						# Request code
						print('RoundRobin')
						endpoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
						if len(endpoints)>0:
							for endpoint in endpoints:
								endpoint.pod.available_cpu -= 1
								endpoint.pod.HandleRequest(request)
								break
						else:
							print("No pod available to handle Request_"+request.label)
				self.deployment.waiting.clear()
		print("ReqHandlerShutdown")

class UtilityAwareLoadBalancer(LoadBalancer):
	def __call__(self):
		print("UtilityAwareLoadBalancer start")
		while self.running:
			self.deployment.waiting.wait()
			with self.deployment.lock:
				while len(self.deployment.pendingReqs) > 0:
					self.requests = self.deployment.pendingReqs.copy()
					self.deployment.pendingReqs.clear()
				if len(self.requests) > 0:
					for request in self.requests:
						# Request code
						print('UtilityAware')
						endpoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
						if len(endpoints)>0:
							for endpoint in endpoints:
								if endpoint.pod.available_cpu > 0:
									if endpoint.pod.available_cpu > 1:
										print("Pod", endpoint.pod.podName, "handling Request_"+request.label)
										endpoint.pod.available_cpu -= 1
										endpoint.pod.HandleRequest(request)
										break
						else:
							print("No pod available to handle Request_"+request.label)
				self.deployment.waiting.clear()	
		print("ReqHandlerShutdown")