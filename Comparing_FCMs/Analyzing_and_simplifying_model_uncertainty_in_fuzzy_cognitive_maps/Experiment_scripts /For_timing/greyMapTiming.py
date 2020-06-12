"""
Created on Mon Jan 30 15:36:28 2017

@author: Eric
"""

from math import exp
import FCM
import sys
import multiprocessing as mp
import time
from copy import deepcopy
import numpy as np
import itertools as it
from functools import reduce
import operator

'''
Main
pass the file to get grey map to get the set up for the fcm
create the initial fcm
figure out number of processors and make a pool with that many processors
'''

debug = False


def runTest(fcm, num, k, edgeDict,stableList):
	config,minMaxList = fcmConfiguration(num, k)
	testFCM, updatedEdgeDict = newFCM(fcm,edgeDict, config)
	sim = createSim(testFCM,stableList)
	res = runSims(sim)

	products = results(res, minMaxList, stableList)
	if debug:
		print 'Products are: ', products
		print 'MinMax list is: ', minMaxList 
	return products    
	#return (res, updatedEdgeDict)


def createSim(fcm,stableList):
	sim = FCM.simulation(fcm)
	sim.steps(100)
	for element in stableList:
		sim.stabilize(element,.001)
    
	return sim

def newEdgeDict(edgeDict,config):
	returnDict = {}
	count = 0
    
	for key in edgeDict:
		returnDict[(key[0],key[1])] = edgeDict[key[0],key[1]][int(config[count])]        
		count += 1
        
	return returnDict
        

'''
getGreyMap
Args: inFile: A text file formatted as i have the example file greyMap.txt
            node: value
            
            edge edge w1 w2
            
returns: two dictionaries, nodes which is a dictionary of the nodes and their starting values, and
        edges, which uses the tuple set of the edges as a key and has a tuple of the 2 values as the value
        
Desc: Read in the text file of the grey FCM formatted as stated above and return dictionaries for the nodes and edges
'''
def getGreyMap(inFile):
    
     #open text file and declare dictionaries
	f = open(inFile)
	nodes = {}
	edges = {}
	stable = []
	for line in f:
        #split the line into a list
		content = line.split()
		if content: #if the list is not empty
			if content[0] == "Stable:":
				for line in f:
					content = line.split()
					if not content:
						break
					stable.append(content[0])

		if content:
			if content[0] == "Nodes:":
				for line in f: #for all lines in node section add them to node dict. leave on blank line
					content = line.split()
					if not content:
						break
					nodes[content[0].strip(':')] = float(content[1])
                
                
		if content:#reach edge lists
			inOrder = []	
			if content[0] == "Edges:":
				for line in f: #for each line in edge section add tuples of node to node edges and tuple weights
					content = line.split()
					inOrder.append(content[0]+'->'+content[1])
					edges[(content[0],content[1])] = (float(content[2]), float(content[3]))
                
					if not content:
						break
	
	fcm = createInitialFCM(nodes, edges)  
	return fcm,len(edges),edges,stable,inOrder          
    

'''
Create the initial FCM, all binary values are 0. Will create a separate function to modify it from the binary values later
'''
def createInitialFCM(nodeDict, edgeDict):
	fcm = FCM.FCM()
    
	for key in nodeDict:
		fcm.add_concept(key)
		fcm.set_value(key, nodeDict[key])
        
	for key in edgeDict:
		fcm.add_edge(key[0], key[1], edgeDict[key[0],key[1]][0])
        
	return fcm
    
'''
create a new FCM with the same node values but adjust edge weights according to the next one needed for the 2^k test
'''
def newFCM(fcm, edgeDict, binary):
	newFcm = deepcopy(fcm)
	count = 0
   	newEdgeDict = {}
	for key in edgeDict:
		newFcm.add_edge(key[0], key[1], edgeDict[key[0],key[1]][int(binary[count])])#same code to create an edge will change the wieght if it already exists		
		newEdgeDict[(key[0],key[1])] = edgeDict[key[0],key[1]][int(binary[count])]        
		count += 1
        
	return newFcm, newEdgeDict

'''
Run the simulation and return the final concept values
'''
def runSims(sim):
	return sim.run()[-1]
    
    
'''
fcmConfiguration
arguments: num: an integer for which configuration of the FCM to run
           k: an integer that represents how many edges there are. used for padding
return: the binary configuration for the FCM
Desc: Takes in the number for which FCM is being run in a fuzzy grey map, and returns the binary configuration 
that will determine which values are on each edge.
'''
def fcmConfiguration(num, k): 
	minMaxList = []
	string = '{0:0'+str(k)+'b}'#format string for binary conversion
	config = string.format(num)#get a binary string of the value
	if debug:
		print 'Length of config is: ', len(config) 
	for element in config:
        	if int(element) == 0:
			minMaxList.append(-1)
	        else:
			minMaxList.append(1)
	if debug:
		print 'in configuration length of minMaxLIst is: ', len(minMaxList)	
	return config,minMaxList
    


'''
results
Gets all the min and max information and the simulation results. It creates the interactions and multiplies the 
results in a dictionary of stable elements and multiplies each by the interaction effect
'''
def results(simResults, minMaxList, stableList):
	result2 = list(it.combinations(minMaxList, 2))#get interaction for the second degree
	result3 = list(it.combinations(minMaxList, 3))#get list of all interaction for 3rd degree effects
	interactions = []
	for element in minMaxList:
		interactions.append(element)

    	#add the second degree interactions to the list
	for element in result2:
		interactions.append(prod(element))
    	#add the 3rd degree interacitons to the list
	for element in result3:
		interactions.append(prod(element))
        if debug:
		print 'The interaction list is: ', interactions
	returnDict = {}
    
	for element in stableList:
		returnDict[element] = []
		returnDict[element] = map(lambda x: x * simResults[element], interactions)
		if debug:
			print 'Element is: ', element
			print 'Element value is: ', simResults[element]
		
	if debug:
		print 'After all multplication Value is:', returnDict


	return returnDict

'''
Will get the porduct of all elements in the iterable. Used for the diffferent combinations for interactions
'''
def prod(iterable):
	return reduce(operator.mul, iterable, 1)

'''
tupleToString
takes a tuple of strings and returns is as a single string fr writing
'''
def tupleToString(element):
	returnString = ''
	first = True
	for i in range(0,len(element)):
		if first:
			returnString += element[i]
			first = False
		else:
			returnString += '&'+element[i]
	return returnString

'''
Main is here
4 command lne arguments:
1: Input file with fcm configuration
2: start point for iteration
3: total range to be examined
4: output file
'''
print 'End is: ', sys.argv[3]
inFile = sys.argv[1]#[0] is program name
start = int(sys.argv[2])#start of range
end = start + int(sys.argv[3]) #range 
outFile = sys.argv[4]#output filename

fcm, k, edges, stableList,inOrderEdges = getGreyMap(inFile)#fcm is the inital fcm(binary 0) and k is the number of edges

numCores = mp.cpu_count() #returns the number of cpu's and stores for size of pool

if __name__ == "__main__":
    avgTimeList = []
    #for count in range(1,numCores +1):
    timeList = []
    pool = mp.Pool()#create maximum number of processes
    for k in range(0,100):
        startTime = time.time()
        #print 'Processing run: '. count
        #count += 1
        debug = False
        
        resultsa = [pool.apply_async(runTest, (fcm,num,k,edges,stableList))for num in range(start,end)]
	
        if debug:
            print 'Have exited parallel'
            print
        #sumDict = {}
        #print resultsa[0].get()
        #for element in stableList:
         #   sumDict[element] = [0]*len(resultsa[0].get()[element])
        #count1 = 0
        #for result in resultsa:
         #   count1+=1
          #  for element in stableList:
                    
           #     for i in range(0,len(sumDict[element])):
            #        sumDict[element][i] = sumDict[element][i] + result.get()[element][i]
    #                if debug:
                        
	#	print 'Number of results processed was: ', count
        head2 = list(it.combinations(inOrderEdges,2))#2nd degree
        head3 = list(it.combinations(inOrderEdges,3))#3rd degree
        header = 'index'
        for element in inOrderEdges:
            header = header + ',' + element#only one not a set of tuples
         
        for element in head2:
            header = header + ',' + tupleToString(element)
         
        for element in head3:
            header = header + ',' + tupleToString(element)
            header = header + '\n'
       # pool.terminate()
        endTime = time.time()
        print endTime - startTime
        timeList.append(endTime - startTime)
    pool.terminate()
    npTime = np.array(timeList)
    #avgTimeList.append((np.mean(npTime),np.std(npTime)))
    g = open('Timing-WorkStation Hardware2.csv', 'w')
    g.write('Time\n')
    for element in timeList:
        g.write(str(element)+'\n')#+ ',' + str(element[1]) + '\n')
    g.close()
'''
	f = open(outFile,'w')
	f.write(header)

	for key in sumDict:
		writeLine = ''
		writeLine += key
		for element in sumDict[key]:
			writeLine = writeLine + ',' + str(element)
		writeLine += '\n'
		f.write(writeLine)

	f.close()
'''
