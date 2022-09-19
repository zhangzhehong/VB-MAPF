# function: generate a vein-based group
# author: zhehong
# date: 2022.5.28

from copy import deepcopy
import numpy as np
import random

class VeinCoalitions:
                def __init__(self,t,points,r,c):
                                self.t = t  #1: k=0; 2: k=pi/4; 3: k=pi/2; 4: k=3pi/4
                                self.points =  deepcopy(points) # deepcopy the input locations
                                self.r = r
                                self.c = c
                                self.index_list = []

                def veinBasedPartioning(self):
                                coalitions = {} # a set of coalitions
                                index_list=[] # The index list in coalition set
                                # slope k = 1
                                if self.t == 1:
                                                # initialize
                                                for index in range(0,self.r): 
                                                                coalitions[index]=[]
                                                                self.index_list.append(index)
                                                # parition
                                                for p in self.points:
                                                                coalitions[p[1]].append(p)
                                                # sort
                                                for index in range (0,self.r):
                                                                if len(coalitions[index]) > 1:
                                                                                coalitions[index].sort(key=lambda x:x[0])
                                # slope k = pi/2
                                elif self.t == 2:
                                                # initialize
                                                for index in range(0,self.c): 
                                                                coalitions[index]=[] 
                                                                self.index_list.append(index)                                              
                                                # partition
                                                for p in self.points:
                                                                coalitions[p[0]].append(p)
                                                # sort
                                                for index in range (0,self.c):
                                                                if len(coalitions[index]) > 1:
                                                                                coalitions[index].sort(key=lambda x:x[1])
                                # slope k = pi/2, y-x=r
                                elif self.t == 3:
                                                # initialize
                                                for index in range(-self.c,self.r): 
                                                                coalitions[index]=[] 
                                                                self.index_list.append(index)
                                                # partition
                                                for p in self.points:
                                                                coalitions[p[1]-p[0]].append(p)
                                                # sort
                                                for index in range (-self.c,self.r):
                                                                if len(coalitions[index]) > 1:
                                                                                coalitions[index].sort(key=lambda x:x[1])
                                # slope k = 3pi/4, x+y=r
                                else:
                                                # initialize
                                                for index in range(0,self.r+self.c): 
                                                                coalitions[index]=[] 
                                                                self.index_list.append(index)
                                                # partition
                                                for p in self.points:
                                                                coalitions[p[0]+p[1]].append(p)
                                                # sort
                                                for index in range (0,self.r+self.c):
                                                                if len(coalitions[index]) > 1:
                                                                                coalitions[index].sort(key=lambda x:x[1])  
                                                
                                return coalitions
                
                def getIndexList(self):
                                return self.index_list
                                




