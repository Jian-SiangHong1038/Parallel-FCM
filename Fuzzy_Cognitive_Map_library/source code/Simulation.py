# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 21:21:39 2016

@author: Eric
"""
import numpy as np
from FCM import *
from copy import deepcopy
from networkx import to_numpy_matrix
from sys import maxsize


class InputTypeError(Exception) :

    def __init__(self,message,errors) :
        message=message+" : "+str(errors)
        super(Exception, self).__init__(message)

class InvalidValueError(Exception) :

    def __init__(self,message,errors) :
        message=message+" : "+str(errors)
        super(Exception, self).__init__(message)





class simulation:

    '''
    This class is responsible for the simulation of the Fuzzy Cognitive Maps.
    It has a method called 'run()' which can run Regular Simulation 

    '''


    def __init__(self, FCM,converge_concepts_dict=None):
        '''
        Constructor
        The constructor takes the following parameters
        1) FCM object
        2) a dictionary with key as concept and value as a tuple of size 2
        '''


        ''' an fcm object '''
        self.fcm = deepcopy(FCM)
        self.numSteps = maxsize
        #should look for a way to do this without storing both the keys and the dict. More for convenience in checking later and acces
        self.stabilizers = []
        self.stableDict = {}
        self.converge_concepts_dict=converge_concepts_dict
        # Set "tanh" as transfer function
        self.transferFunction = np.tanh
        # Graph adjacency matrix with weight.
        self.edgeMatrix = to_numpy_matrix(self.fcm._fcm_graph).transpose() #influence to a node in stored in the row
        self.stable_concepts = self._stable_concepts() #indexes of concepts that should not be changed by the transfer function

    def stabilize(self, concept, threshold):


        '''
        stabilize
        parameters: concept: A valid concept in the fcm
        threshold: A threshold that states a difference of this amount means stable
        Returns: void
        Description: We check that a valid concept in the fcm has been input and add it to the dictionary of all stabilizers.
        if the stabilizer is already in the list of stabilizers we just set the new threshold
        '''




        if concept not in self.fcm.concepts():
            print ("Please input a valid concept")
            return
        else:
            if concept not in self.stabilizers:
                self.stabilizers.append(concept)
                self.stableDict[concept] = threshold
            else:
                self.stableDict[concept] = threshold

    def steps(self,numsteps):

        '''
        A function which takes input as a number of steps
        '''


        if type(numsteps) is not int:
            raise InputTypeError("Invalid steps value type")
        if numsteps > 0 and numsteps < maxsize:
            self.numSteps = numsteps

        else:
            print ("Please input a positive number of steps that is less than ", sys.maxsize)
            return

    def changeTransferFunction(self,function):

        '''
        changeTransferFunction
        Parameters: function (function with 1 argument): a function that takes one argument and maintains values in range [-1,1]
        return: void
        Description: Changes the transfer function. error check will pass 100 and -100  to see if they stay in range
        '''

        if callable(function):
            if function(100) > 1 or function(-100) < -1:
                raise InvalidValueError("Error Transfer function must keep values in range [-1,1]")
            else:
                self.transferFunction = function
        else:
            raise InputTypeError("Must pass a function")

    def _updateNodes(self, nodeValues, c = None): #nodevalues is a list of the node values
        '''
        updateNodes(should only be called by run method)
        parameters: nodevalues(iterable list): a list in node order that matches the edge matrix
        c(optional double): a weight to modify the values of the nodes
        returns: the updated values of the nodes after one time step
        Description: will convert the list into a numpy array and multiply it with the edge list to get the changes to each node.
        the changes will be applied. Applies all nodes to the transfer function. If a node has no incoming edges it is declared
        stable and returned to its old value
        '''

        values_vector = np.asarray(nodeValues) #make list into a numpy vector
        update = np.dot(self.edgeMatrix, values_vector)# get new vector of values to be added
        # print('values_vector',values_vector, 'edgeMatrix',self.edgeMatrix, 'update_dot',update)
        if c is not None:
            if type(c) is not float:
                raise InvalidValueError("Weight c needs to be a decimal value")
            values_vector = values_vector*c

        newValues = np.add(values_vector, update) #values after addition
        newValList = newValues.tolist()[0] #convert to list
        #only apply if hs an incom,ing edge
        newNodeValueTrans = [self.transferFunction(x) for x in newValList] #applies transfer function to each value

        # if self.stable_concepts is not None:
        #     for index in self.stable_concepts:
        #         print('stable index', index)
        #         newNodeValueTrans[index] = nodeValues[index]

        return newNodeValueTrans

    def _is_Stable(self, oldNodes, newNodes): #oldNods and newNodes are lists
        '''
        is_stable(should only be called by run function)
        Arguments: oldNodes(iterable list): list of node values from before the timestep update
        newNodes(iterable list): list of node values from after the time step
        Returns: Boolean
        Description: Checks the absolute value of the difference between the old and new values of the nodes to see if they are
        less than the designated threshold
        '''
        '''
        for node in self.stabilizers:
            index = self.fcm._fcm_graph.nodes().index(node)
            if abs(newNodes[index] - oldNodes[index]) >= self.stableDict[node]:
                return False

        return True
        '''
        # edit by JSH
        for index, node in enumerate(self.fcm._fcm_graph.nodes()):
            # print('index', index, 'node', node, 'value', abs(newNodes[index] - oldNodes[index]))
#            print('self.stableDict[node]',self.stableDict[node]) = 0.001
            if abs(newNodes[index] - oldNodes[index]) >= self.stableDict[node]:
                return False
        return True

    def run(self,c = None):

        '''
        Run
        Arguments: c (optional): weight for the nodes to be adjusted by in the time step updates
        returns: the dictionary of the new concept values
        Description: Will run the simulation until either time step limit is hit or is stable
        Will print out the number of steps and the nodes with their correlated values
        '''

        count = 0
        returnList = []
        oldValues = []
        nodeOrder = self.fcm._fcm_graph.nodes() #edge matrix is in order of nodes
        for node in nodeOrder:
                oldValues.append(self.fcm.concepts()[node])

        while count < self.numSteps:
            returnList.append(self._makeDict(oldValues))
            newValues = self._updateNodes(oldValues, c)
            # print('oldValues', oldValues, 'newValues', newValues)

            if self._is_Stable(oldValues,newValues):
                break

            oldValues = newValues

            count += 1

        # newValues = \
        self._output_results(newValues,count)

        if count == self.numSteps:
            # max number of steps is 100.
            print ("Max number of steps used. Values may not be stable")

        # print ('Total time taken =' +(str(end_time-start_time))+ ' seconds')

        return returnList


    def _output_results(self, conceptValues, steps):

       '''
       output_result(should only be called by run)
       Parameters: conceptValues(iterable list): list of the final concept values in nodeOrder
       steps(int): the number of steps the simulation runs for
       returns: void
       Description: Will relate the concept values with the concepts due to node order. will print out the
       1)number of steps
       2)the initial concept values
       3)the final concept values
       '''




       outDict = self._makeDict(conceptValues)

       print ("The number of Steps was: ", steps)
       print ("The Initial concept Values were: ", self.fcm.concepts())
       print ("The final concept Values were: ", outDict)
        #return outDict

    def _stable_concepts(self):

         '''
         stable_concepts(called on init)
         arguments: none
         Returns: iterabl List: List of the index positions for nodes to remain stable
         Description: Checks which nodes have no incoming edges and marks them as to remain stable throughout the simulation
         '''

         stableList = []
         index = 0
         for node in self.fcm._fcm_graph.nodes():
            if self.fcm._fcm_graph.in_degree(node) == 0:
                stableList.append(index)
            index += 1
         return stableList


    def _makeDict(self, values):
         '''
         _makeDict
         Arguments: values(List): list of concept values in node order
         returns: A dictionary of concepts with their corresponding values
         Description: Turns the lists of concept values in node order into a dictionary
         and returns the dictionary. Only call in methods
         '''
         outDict = {}
         index = 0
         #nodeOrder guaranteed to be the same size as concept values and in the order needed
         for node in self.fcm._fcm_graph.nodes():
            outDict[node] = values[index]
            index += 1

         return outDict
