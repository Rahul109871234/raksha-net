import sys ,subprocess ,time 
print (f'node {sys .argv [1 ]} up',flush =True )
subprocess .Popen (['iperf3','-s'])
while True :
    time .sleep (3600 )