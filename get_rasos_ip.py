import os

for i in range(255):
	os.system("ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no" + " pi@192.168.0." + str(i))