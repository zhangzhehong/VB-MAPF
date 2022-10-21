# function: generate a set of randomly distributed locations
# author: zhehong
# date: 2021.4.3

import math
import numpy as np
import random

from numpy.lib.function_base import average

class RandomPoints:
    def __init__(self):
        self.cnt = 0

    def generateRandomPoints1(self,r,c,n):
        randompoints_list = []
        average_num = int(n / r + 0.5)
        count = 0
        # print(n,average_num,r)
        for i in range(r-1):
            # cnt = random.sample(range(average_num-2,average_num+1),1)
            count = count + average_num
            num_list = random.sample(range(0,c + average_num),average_num)
            for j in num_list:
                randompoints_list.append([j,i])
        count = n - count
        # print(count)
        num_list = random.sample(range(0,count+1),count)
        for j in num_list:
            randompoints_list.append([j,r-1])                                
        return randompoints_list

    def generateRandomPoints2(self,r,c,n):
        allpoints_list = []
        for i in range(0,r):
            for j in range(0,c):
                allpoints_list.append([j,i])
        random_index = random.sample(range(0,r*c),n)
        randompoints_list = []
        for index in random_index:
            randompoints_list.append(allpoints_list[index])
        return randompoints_list                                



