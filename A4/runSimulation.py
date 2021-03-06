import threading
from request import Request
from dep_controller import DepController
from api_server import APIServer
from req_handler import ReqHandler
from node_controller import NodeController
from scheduler import Scheduler
import matplotlib.pyplot as plt
from hpa import HPA
from load_balancer import LoadBalancer
from supervisor import Supervisor
import time



#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 1
_depCtlLoop = 1
_scheduleCtlLoop =1
_hpaCtlLoop = 2

kind = 'UA'
apiServer = APIServer()
depController = DepController(apiServer, _depCtlLoop)
nodeController = NodeController(apiServer, _nodeCtlLoop)
reqHandler = ReqHandler(apiServer)
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
depControllerThread = threading.Thread(target=depController)
nodeControllerThread = threading.Thread(target=nodeController)
reqHandlerThread = threading.Thread(target=reqHandler)
schedulerThread = threading.Thread(target = scheduler)
print("Threads Starting")
reqHandlerThread.start()
nodeControllerThread.start()
depControllerThread.start()
schedulerThread.start()
print("ReadingFile")
#Graphing information
depPods1 = []
depPods2 = []
depPods3 = []
depPendPods1 = []
depPendPods2 = []
depPendPods3 = []
dep1PendReqs = []
dep2PendReqs = []
dep3PendReqs = []
stepList = []
#Simulation information
loadBalancers = []
hpas = []
supervisors = []
hpaThreads = []
loadBalancerThreads = []
supervisorThreads = []
count = 0
instructions = open("instructions.txt", "r")
commands = instructions.readlines()

for command in commands:
	cmdAttributes = command.split()
	print(str(command))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			loadbalancer = LoadBalancer(kind, apiServer, deployment)
			lbThread = threading.Thread(target=loadbalancer)
			lbThread.start()
			loadBalancers.append(loadbalancer)
			loadBalancerThreads.append(lbThread)
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			#We have to makesure that our load balancer will end gracefully here
			for loadBalancer in loadBalancers:
				if loadBalancer.deployment.deploymentLabel == cmdAttributes[1]:
					loadBalancer.running=False
			apiServer.RemoveDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CreateHPA':
			hpa = HPA(apiServer, _hpaCtlLoop, cmdAttributes[1:])
			hpaThread = threading.Thread(target=hpa)
			hpaThread.start()
			hpas.append(hpa)
			hpaThreads.append(hpaThread)
			supervisor = Supervisor(apiServer, hpa)
			supervisorThread = threading.Thread(target=supervisor)
			supervisorThread.start()
			supervisors.append(supervisor)
			supervisorThreads.append(supervisorThread)
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	#The instructions will sleep after each round of requests. The following code stores values for graphing
	if cmdAttributes[0] == 'Sleep':
		count+=1
		time.sleep(int(cmdAttributes[1]))
		if len(apiServer.etcd.deploymentList) == 1:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(0)
			depPods3.append(0)
			count1 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
			depPendPods1.append(count1)
			depPendPods2.append(0)
			depPendPods3.append(0)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(0)
			dep3PendReqs.append(0)
		elif len(apiServer.etcd.deploymentList) == 2:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(apiServer.etcd.deploymentList[1].expectedReplicas)
			depPods3.append(0)
			count1 = 0
			count2 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count2+=1
			depPendPods1.append(count1)
			depPendPods2.append(count2)
			depPendPods3.append(0)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(len(apiServer.etcd.deploymentList[1].pendingReqs))
			dep3PendReqs.append(0)
		elif len(apiServer.etcd.deploymentList) == 3:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(apiServer.etcd.deploymentList[1].expectedReplicas)
			depPods3.append(apiServer.etcd.deploymentList[2].expectedReplicas)
			count1 = 0
			count2 = 0
			count3 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count2+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count3+=1
			depPendPods1.append(count1)
			depPendPods2.append(count2)
			depPendPods3.append(count3)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(len(apiServer.etcd.deploymentList[1].pendingReqs))
			dep3PendReqs.append(len(apiServer.etcd.deploymentList[2].pendingReqs))
		else:
			depPods1.append(0)
			depPods2.append(0)
			depPods3.append(0)
			depPendPods1.append(0)
			depPendPods2.append(0)
			depPendPods3.append(0)
			dep1PendReqs.append(0)
			dep2PendReqs.append(0)
			dep3PendReqs.append(0)
		#pendReqsList.append(len(apiServer.etcd.pendingReqs))
		stepList.append(count)
time.sleep(5)
print("Shutting down threads")
for hpa in hpas:
	hpa.running = False
	hpa.calibrate.set()
reqHandler.running = False
depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
for lbthread in loadBalancerThreads:
	lbthread.join()
for hpathread in hpaThreads:
	hpathread	.join()
for supervisorThread in supervisorThreads:
	supervisorThread.join()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
reqHandlerThread.join()
fig, ((hpa1, hpa2, hpa3), (pp, ap, pr)) = plt.subplots(2,3)
hpa1.plot(hpas[0].xValues, hpas[0].setPoints, color='black', label = 'Setpoint Dep1')
hpa1.plot(hpas[0].xValues, hpas[0].utilValues, color='blue', label = 'CPU util Dep1')
hpa1.set_title('HPA for Deployment 1')
hpa2.plot(hpas[1].xValues, hpas[1].setPoints, color='black', label = 'Setpoint Dep2')
hpa2.plot(hpas[1].xValues, hpas[1].utilValues, color='green', label = 'CPU util Dep2')
hpa2.set_title('HPA for Deployment 2')
hpa3.plot(hpas[2].xValues, hpas[2].setPoints, color='black', label = 'Setpoint Dep3')
hpa3.plot(hpas[2].xValues, hpas[2].utilValues, color='red', label = 'CPU util Dep3')
hpa3.set_title('HPA for Deployment 3')
pp.plot(stepList, depPendPods1, color = 'blue', label = 'Pending Pods Dep1')
pp.plot(stepList, depPendPods2, color = 'green', label = 'Pending Pod Dep2')
pp.plot(stepList, depPendPods3, color = 'red', label = 'Pending Pod Dep3')
ap.plot(stepList, depPods1, color = 'blue', label = 'Active Pods Dep1')
ap.plot(stepList, depPods2, color = 'green', label = 'Active Pods Dep2')
ap.plot(stepList, depPods3, color = 'red', label = 'Active Pods Dep3')
pr.plot(stepList, dep1PendReqs, color='blue', label = 'Pending Requests Dep1')
pr.plot(stepList, dep1PendReqs, color='green', label = 'Pending Requests Dep2')
pr.plot(stepList, dep1PendReqs, color='red', label = 'Pending Requests Dep3')
for ax in fig.get_axes():
	ax.legend()
plt.savefig('figure.png')
plt.show()
