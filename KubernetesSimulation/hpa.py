import threading
import time

#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
		self.deploymentLabel = INFOLIST[0]
		self.setPoint = int(INFOLIST[1])
		self.syncPeriod = int(INFOLIST[2])
	
	def __call__(self):
		deployment = self.apiServer.GetDepByLabel(self.deploymentLabel)
		ctrl = self.apiServer.controller
		while self.running:
			time.sleep(self.syncPeriod)
			cpu = 0
			average = 0
			error = 0
			correction = 0
			endpoints = self.apiServer.GetEndPointsByLabel(self.deploymentLabel)
			if len(endpoints) > 0:
				for endpoint in endpoints:
					cpu += endpoint.pod.assigned_cpu - endpoint.pod.available_cpu
					average = cpu / len(endpoints)
					average *= 100
			if average > 0:
				error = self.setPoint - average
				if error > 0:
					correction = ctrl.work(error)
					if correction >= 2:
						deployment.expectedReplicas = round(correction)
					else:
						deployment.expectedReplicas = 2
			print(deployment.deploymentLabel, "Pods:", deployment.expectedReplicas)
			time.sleep(self.time)
