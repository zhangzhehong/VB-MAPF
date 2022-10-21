# vein-based structure for formation task
# function: vein-based pattern formation where slope k = pi/2
# author : zhehong
# date : 2022.6.1

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from copy import deepcopy
import time

from numpy.core.defchararray import index

from Preprocess import Shape
from RandomPoints import RandomPoints
from VeinCoalitions import VeinCoalitions

timesteps_list = {}
max_distance_list = {}
sum_distance_list = {}

data_timestep = []
data_max_dis = []
data_sum_dis = []

file_data_timestep = open('output/VB2_timestep.txt','w')
file_data_max_dis = open('output/VB2_max_dis.txt','w')
file_data_sum_dis = open('output/VB2_sum_dis.txt','w')

labels = []
img_index = 3
#1: k=0,y=0; 2: y=x, k=pi/4; 3:y-x=c k=pi/2; 4:x+y=c, k=3pi/4
vein_type = 2 
size_list=[100,400,900,1500,2000]
# n=100
# shape_index= 8
# the number of target points n
# for size in range(10,31,2):
#                 n = size * size
for n in size_list:
    labels.append(str(n))
    timesteps_list[n] = []
    max_distance_list[n] = []
    sum_distance_list[n] = []
    for shape_index in range(1,37):
        #########################################################################
        ################ step 1 : get target shape locations ####################
        #########################################################################
        # the filename of the input
        file = 'input/shape'+str(shape_index)+'/img'+str(img_index)+'.png'   
        print("size = ",n, "shape :",file)
        # get the image by the filename
        img = Shape(file)      
         # get the set of original target locations from the input
        img.getTargetShape(n) 
        #store target points
        target_points=[]      
        for p in img.targetShape:
            #get the set of target locations after somve shifts
            target_points.append([p[0] - img.min_width,p[1] - img.min_height])  
        #########################################################################
        ################ step 2 : get original shape locations ##################
        #########################################################################
        # get the height of the target locations
        num_rows = img.max_height - img.min_height + 1   
        # get the width of the target locations
        num_cols = img.max_width - img.min_width + 1     
        print("map:",num_rows,"X",num_cols)
        # intialize a RandomPoints class R
        R =  RandomPoints()  
        # get a set of original dot locations
        original_points = R.generateRandomPoints2(num_rows,num_cols,n) 

        #########################################################################################
        ##### step 3 : get vein-based coalitions on target locations and original locations #####
        #########################################################################################
        t_coalition = VeinCoalitions(vein_type,target_points,num_rows,num_cols)
        # get the vein-based decomposition on target locations
        target_coalitions = t_coalition.veinBasedPartioning() 
        o_coalition = VeinCoalitions(vein_type,original_points,num_rows,num_cols)
        # get vein-based coalitions on original locations
        original_coalitions = o_coalition.veinBasedPartioning() 
        index_list = o_coalition.getIndexList()

        #########################################################################
        ############################ step 4 : rectify ###########################
        ######################################################################### 
        # the optimal coalition                               
        exact_coalitions = deepcopy(original_coalitions)  
        exact = 0
        #record extra agents in the glut coalition
        glut = 0  
        # record understaffed agents in the shortage coalition
        demand = 0 
        timestep = 0

        flag = []
        dis = []
        for i in range(num_rows):
            flag.append([0]*num_cols)
            dis.append([0]*num_cols)
        for p in original_points:
            flag[p[1]][p[0]] = 1
            dis[p[1]][p[0]] = 0
        # compensate from glut coalitions
        while True:
            # draw_x=[]
            # draw_y=[]
            timestep += 1
            demand = 0
            glut = 0
            exact = 0
            for current_index in index_list:
                len1 = len(exact_coalitions[current_index])
                len2 = len(target_coalitions[current_index])
                if len1 == len2:
                    exact += 1
                # understaffed coalition
                elif  len1 < len2:
                    #only compensate from the previous coalition
                    if glut >= (len2 - len1):
                        demand = len2 - len1
                        glut -= demand
                        if current_index - 1 >=index_list[0]:
                            search_index = current_index - 1
                            search_list = deepcopy(exact_coalitions[search_index])
                            for search_point in search_list:
                                if demand == 0:
                                    break
                                else:
                                    # current coalition gets agents from search(previous) coalition
                                    if flag[search_point[1]][search_index] != 0 and flag[search_point[1]][current_index]== 0:
                                        flag[search_point[1]][search_index] = 0
                                        flag[search_point[1]][current_index] = 1
                                        demand -= 1
                                        exact_coalitions[search_index].remove([search_index,search_point[1]])
                                        exact_coalitions[current_index].append([current_index,search_point[1]])
                                        dis[search_point[1]][current_index] += dis[search_point[1]][search_index] + 1
                                        dis[search_point[1]][search_index] = 0
                            exact_coalitions[current_index].sort(key=lambda x:x[1])
                            # adjust search coalition
                            if demand > 0 and len(exact_coalitions[search_index])>0:
                                target_list = deepcopy(target_coalitions[current_index])
                                move_flag=[-1]*num_rows
                                mark = 0
                                for target_point in target_list:
                                    stride = 1
                                    if flag[target_point[1]][current_index] == 0:
                                        # seach toward down
                                        while target_point[1]-stride>= exact_coalitions[search_index][0][1]:
                                            if flag[target_point[1]-stride][search_index]==1 and move_flag[target_point[1]-stride]== -1:
                                                if target_point[1]-stride+1 <= num_rows and flag[target_point[1]-stride+1][search_index] == 0:
                                                    flag[target_point[1]-stride][search_index] = 0
                                                    flag[target_point[1]-stride + 1][search_index] = 1
                                                    exact_coalitions[search_index].remove([search_index,target_point[1]-stride])
                                                    exact_coalitions[search_index].append([search_index,target_point[1]-stride + 1])
                                                    dis[target_point[1]-stride + 1][search_index] += dis[target_point[1]-stride][search_index] + 1
                                                    dis[target_point[1]-stride][search_index]=0
                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                    move_flag[target_point[1]-stride + 1] = 1
                                                    mark = 1
                                                    break
                                            stride += 1
                                        # search toward up
                                        if mark == 0:
                                            while target_point[1]+stride<=exact_coalitions[search_index][-1][1]:
                                                if flag[target_point[1]+stride][search_index] == 1 and  move_flag[target_point[1]+stride] == -1:
                                                    if target_point[1]+stride - 1 >=0 and flag[target_point[1]+stride - 1][search_index]==0: 
                                                        flag[target_point[1]+stride][search_index] = 0
                                                        flag[target_point[1]+stride - 1][search_index] = 1
                                                        exact_coalitions[search_index].remove([search_index,target_point[1]+stride])
                                                        exact_coalitions[search_index].append([search_index,target_point[1]+stride - 1])
                                                        dis[target_point[1]+stride - 1][search_index] += dis[target_point[1]+stride][search_index] + 1
                                                        dis[target_point[1]+stride][search_index]=0
                                                        exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                        move_flag[target_point[1]+stride - 1] = 1
                                                        mark = 1
                                                        break
                                                stride += 1 
                        demand = 0
                    # compensate from the previous coalition and next coalition
                    elif glut > 0 and glut <  (len2 - len1):
                                    # compensate from the previous coalitions to let glut = 0
                                    demand = len2- len1
                                    demand -= glut 
                                    if current_index - 1 >=index_list[0]:
                                                    search_index = current_index - 1
                                                    search_list = deepcopy(exact_coalitions[search_index])
                                                    for search_point in search_list:
                                                                    if glut == 0 :
                                                                                    break
                                                                    else:
                                                                                    if flag[search_point[1]][search_index] != 0 and flag[search_point[1]][current_index] == 0:
                                                                                                    flag[search_point[1]][search_index] = 0
                                                                                                    flag[search_point[1]][current_index] = 1
                                                                                                    glut -= 1
                                                                                                    exact_coalitions[search_index].remove([search_index,search_point[1]])
                                                                                                    exact_coalitions[current_index].append([current_index,search_point[1]])
                                                                                                    dis[search_point[1]][current_index] += dis[search_point[1]][search_index] + 1
                                                                                                    dis[search_point[1]][search_index] = 0
                                                    exact_coalitions[current_index].sort(key=lambda x:x[1]) 
                                                    if glut > 0 and len(exact_coalitions[search_index])>0:
                                                                    target_list = deepcopy(target_coalitions[current_index])
                                                                    move_flag=[-1]*num_rows
                                                                    mark=0
                                                                    for target_point in target_list:
                                                                                    stride = 1
                                                                                    if flag[target_point[1]][current_index] == 0:
                                                                                                    # seach toward down
                                                                                                    while target_point[1]-stride>= exact_coalitions[search_index][0][1]:
                                                                                                                    if flag[target_point[1]-stride][search_index]==1 and move_flag[target_point[1]-stride]== -1:
                                                                                                                                    if target_point[1]-stride+1 <= num_rows and flag[target_point[1]-stride+1][search_index] == 0:
                                                                                                                                                    flag[target_point[1]-stride][search_index] = 0
                                                                                                                                                    flag[target_point[1]-stride + 1][search_index] = 1
                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]-stride])
                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]-stride + 1])
                                                                                                                                                    dis[target_point[1]-stride + 1][search_index] += dis[target_point[1]-stride][search_index] + 1
                                                                                                                                                    dis[target_point[1]-stride][search_index]=0
                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                    move_flag[target_point[1]-stride + 1] = 1
                                                                                                                                                    mark = 1
                                                                                                                                                    break
                                                                                                                    stride += 1
                                                                                                    # search toward up
                                                                                                    if mark == 0:
                                                                                                                    while target_point[1]+stride<=exact_coalitions[search_index][-1][1]:
                                                                                                                                    if flag[target_point[1]+stride][search_index] == 1 and  move_flag[target_point[1]+stride] == -1:
                                                                                                                                                    if target_point[1]+stride - 1 >=0 and flag[target_point[1]+stride - 1][search_index]==0: 
                                                                                                                                                                    flag[target_point[1]+stride][search_index] = 0
                                                                                                                                                                    flag[target_point[1]+stride - 1][search_index] = 1
                                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]+stride])
                                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]+stride - 1])
                                                                                                                                                                    dis[target_point[1]+stride - 1][search_index] += dis[target_point[1]+stride][search_index] + 1
                                                                                                                                                                    dis[target_point[1]+stride][search_index]=0
                                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                    move_flag[target_point[1]+stride - 1] = 1
                                                                                                                                                                    mark = 1
                                                                                                                                                                    break
                                                                                                                                    stride += 1 
                                    glut = 0
                                    # compensate from the next coalitions to let demand = 0                                           
                                    if current_index + 1 < num_cols:
                                                    search_index = current_index + 1
                                                    search_list = deepcopy(exact_coalitions[search_index])
                                                    for search_point in search_list:
                                                                    if demand == 0:
                                                                                    break
                                                                    else:
                                                                                    if flag[search_point[1]][search_index] != 0 and flag[search_point[1]][current_index] == 0:
                                                                                                    flag[search_point[1]][search_index] = 0
                                                                                                    flag[search_point[1]][current_index] = 1
                                                                                                    demand -= 1
                                                                                                    exact_coalitions[search_index].remove([search_index,search_point[1]])
                                                                                                    exact_coalitions[current_index].append([current_index,search_point[1]])
                                                                                                    dis[search_point[1]][current_index] += dis[search_point[1]][search_point[0]] + 1
                                                                                                    dis[search_point[1]][search_point[0]] = 0           
                                                    exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                    if demand > 0 and len(exact_coalitions[search_index])>0:
                                                                    target_list = deepcopy(target_coalitions[current_index])
                                                                    move_flag=[-1]*num_rows
                                                                    mark=0
                                                                    for target_point in target_list:
                                                                                    stride = 1
                                                                                    if flag[target_point[1]][current_index] == 0:
                                                                                                    # seach toward down
                                                                                                    while target_point[1]-stride>= exact_coalitions[search_index][0][1]:
                                                                                                                    if flag[target_point[1]-stride][search_index]==1 and move_flag[target_point[1]-stride]== -1:
                                                                                                                                    if target_point[1]-stride+1 <= num_rows and flag[target_point[1]-stride+1][search_index] == 0:
                                                                                                                                                    flag[target_point[1]-stride][search_index] = 0
                                                                                                                                                    flag[target_point[1]-stride + 1][search_index] = 1
                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]-stride])
                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]-stride + 1])
                                                                                                                                                    dis[target_point[1]-stride + 1][search_index] += dis[target_point[1]-stride][search_index] + 1
                                                                                                                                                    dis[target_point[1]-stride][search_index]=0
                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                    move_flag[target_point[1]-stride + 1] = 1
                                                                                                                                                    mark = 1
                                                                                                                                                    break
                                                                                                                    stride += 1
                                                                                                    # search toward up
                                                                                                    if mark == 0:
                                                                                                                    while target_point[1]+stride<=exact_coalitions[search_index][-1][1]:
                                                                                                                                    if flag[target_point[1]+stride][search_index] == 1 and  move_flag[target_point[1]+stride] == -1:
                                                                                                                                                    if target_point[1]+stride - 1 >=0 and flag[target_point[1]+stride - 1][search_index]==0: 
                                                                                                                                                                    flag[target_point[1]+stride][search_index] = 0
                                                                                                                                                                    flag[target_point[1]+stride - 1][search_index] = 1
                                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]+stride])
                                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]+stride - 1])
                                                                                                                                                                    dis[target_point[1]+stride - 1][search_index] += dis[target_point[1]+stride][search_index] + 1
                                                                                                                                                                    dis[target_point[1]+stride][search_index]=0
                                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                    move_flag[target_point[1]+stride - 1] = 1
                                                                                                                                                                    mark = 1
                                                                                                                                                                    break
                                                                                                                                    stride += 1 
                    # only compensate from the next coalition
                    else: # glut==0
                                    # compensate from the next coalitons to let demand = 0
                                    demand += len2 -len1
                                    if current_index + 1 <= index_list[-1]:
                                                    search_index = current_index + 1
                                                    search_list = deepcopy(exact_coalitions[search_index])
                                                    for search_point in search_list:
                                                                    if demand == 0:
                                                                                    break
                                                                    else:
                                                                                    if flag[search_point[1]][search_index] != 0 and flag[search_point[1]][current_index] == 0:
                                                                                                    flag[search_point[1]][search_index] = 0
                                                                                                    flag[search_point[1]][current_index] = 1
                                                                                                    demand -= 1
                                                                                                    exact_coalitions[search_index].remove([search_index,search_point[1]])
                                                                                                    exact_coalitions[current_index].append([current_index,search_point[1]])
                                                                                                    dis[search_point[1]][current_index] += dis[search_point[1]][search_index] + 1
                                                                                                    dis[search_point[1]][search_index] = 0           
                                                    exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                    if demand > 0 and len(exact_coalitions[search_index])>0:
                                                                    target_list = deepcopy(target_coalitions[current_index])
                                                                    move_flag=[-1]*num_rows
                                                                    mark=0
                                                                    for target_point in target_list:
                                                                                    stride = 1
                                                                                    if flag[target_point[1]][current_index] == 0:
                                                                                                    # seach toward down
                                                                                                    while target_point[1]-stride>= exact_coalitions[search_index][0][1]:
                                                                                                                    if flag[target_point[1]-stride][search_index]==1 and move_flag[target_point[1]-stride]== -1:
                                                                                                                                    if target_point[1]-stride+1 <= num_rows and flag[target_point[1]-stride+1][search_index] == 0:
                                                                                                                                                    flag[target_point[1]-stride][search_index] = 0
                                                                                                                                                    flag[target_point[1]-stride + 1][search_index] = 1
                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]-stride])
                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]-stride + 1])
                                                                                                                                                    dis[target_point[1]-stride + 1][search_index] += dis[target_point[1]-stride][search_index] + 1
                                                                                                                                                    dis[target_point[1]-stride][search_index]=0
                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                    move_flag[target_point[1]-stride + 1] = 1
                                                                                                                                                    mark = 1
                                                                                                                                                    break
                                                                                                                    stride += 1
                                                                                                    # search toward up
                                                                                                    if mark == 0:
                                                                                                                    while target_point[1]+stride<=exact_coalitions[search_index][-1][1]:
                                                                                                                                    if flag[target_point[1]+stride][search_index] == 1 and  move_flag[target_point[1]+stride] == -1:
                                                                                                                                                    if target_point[1]+stride - 1 >=0 and flag[target_point[1]+stride - 1][search_index]==0: 
                                                                                                                                                                    flag[target_point[1]+stride][search_index] = 0
                                                                                                                                                                    flag[target_point[1]+stride - 1][search_index] = 1
                                                                                                                                                                    exact_coalitions[search_index].remove([search_index,target_point[1]+stride])
                                                                                                                                                                    exact_coalitions[search_index].append([search_index,target_point[1]+stride - 1])
                                                                                                                                                                    dis[target_point[1]+stride - 1][search_index] += dis[target_point[1]+stride][search_index] + 1
                                                                                                                                                                    dis[target_point[1]+stride][search_index]=0
                                                                                                                                                                    exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                    move_flag[target_point[1]+stride - 1] = 1
                                                                                                                                                                    mark = 1
                                                                                                                                                                    break
                                                                                                                                    stride += 1  
                else: #glut coalition: len1 > len2
                    if demand == 0:
                        glut += len1 - len2
                        # send out agents to the next coalition to let glut = 0
                        if current_index + 1 < num_cols:
                            search_index = current_index + 1
                            current_list = deepcopy(exact_coalitions[current_index])
                            for current_point in current_list:
                                if glut == 0 :
                                    break
                                else:
                                    if flag[current_point[1]][current_index] == 1 and flag[current_point[1]][search_index] == 0:
                                        flag[current_point[1]][search_index] = 1
                                        flag[current_point[1]][current_index] = 0
                                        glut -= 1
                                        exact_coalitions[search_index].append([search_index,current_point[1]])
                                        exact_coalitions[current_index].remove([current_index,current_point[1]])
                                        dis[current_point[1]][search_index] += dis[current_point[1]][current_index] + 1
                                        dis[current_point[1]][current_index] = 0           
                            exact_coalitions[search_index].sort(key=lambda x:x[1])
                    else:  # demand > 0 (glut == 0)
                        glut = len1 - len2
                        # only send out agents to the previous coalition
                        if demand >= glut:
                            demand -= glut
                            if current_index - 1 >=index_list[0]:
                                search_index = current_index - 1
                                current_list = deepcopy(exact_coalitions[current_index])
                                for current_point in current_list:
                                    if glut == 0 :
                                        break
                                    else:
                                        if flag[current_point[1]][current_index] == 1 and flag[current_point[1]][search_index] == 0:
                                            flag[current_point[1]][search_index] = 1
                                            flag[current_point[1]][current_index] = 0
                                            glut -= 1
                                            exact_coalitions[search_index].append([search_index,current_point[1]])
                                            exact_coalitions[current_index].remove([current_index,current_point[1]])
                                            dis[current_point[1]][search_index] += dis[current_point[1]][current_index] + 1
                                            dis[current_point[1]][current_index] = 0           
                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                            glut = 0    
                        # send out agents to the previous and next coalitions           
                        else:
                            glut -= demand
                            # send out agents to the previous coalition to let demand = 0
                            if current_index - 1 >=index_list[0]:
                                search_index = current_index - 1
                                current_list = deepcopy(exact_coalitions[current_index])
                                for current_point in current_list:
                                    if demand == 0 :
                                        break
                                    else:
                                        if flag[current_point[1]][current_index] == 1 and flag[current_point[1]][search_index] == 0:
                                            flag[current_point[1]][search_index] = 1
                                            flag[current_point[1]][current_index] = 0
                                            demand -= 1
                                            exact_coalitions[search_index].append([search_index,current_point[1]])
                                            exact_coalitions[current_index].remove([current_index,current_point[1]])
                                            dis[current_point[1]][search_index] += dis[current_point[1]][current_index] + 1
                                            dis[current_point[1]][current_index] = 0           
                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                            demand = 0
                            # send out agents to the next coalitions to let glut = 0
                            if current_index + 1 <=index_list[-1]:
                                search_index = current_index + 1
                                current_list = deepcopy(exact_coalitions[current_index])
                                for current_point in current_list:
                                    if glut == 0:
                                        break
                                    else:
                                        if flag[current_point[1]][current_index] == 1 and flag[current_point[1]][search_index] == 0:
                                            flag[current_point[1]][search_index] = 1
                                            flag[current_point[1]][current_index] = 0
                                            glut -= 1
                                            exact_coalitions[search_index].append([search_index,current_point[1]])
                                            exact_coalitions[current_index].remove([current_index,current_point[1]])
                                            dis[current_point[1]][search_index] += dis[current_point[1]][current_index] + 1
                                            dis[current_point[1]][current_index] = 0             
                                exact_coalitions[search_index].sort(key=lambda x:x[1])                                                                
            
            if exact == len(index_list):
                break
        exact = 0
        while exact != n:
            exact = 0
            timestep += 1
            max_dis = 0
            sum_dis = 0
            for index in index_list:
                if len(exact_coalitions[index]) > 0:
                    for j in range(0,len(target_coalitions[index])):
                        if exact_coalitions[index][j][1] == target_coalitions[index][j][1]:
                            exact += 1
                            max_dis = max(max_dis, dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]])
                            sum_dis += dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]]
                        elif exact_coalitions[index][j][1] < target_coalitions[index][j][1]:
                            dis[exact_coalitions[index][j][1]+1][exact_coalitions[index][j][0]] = dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] + 1
                            dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] = 0
                            exact_coalitions[index][j][1] += 1
                                        
                        else:
                            dis[exact_coalitions[index][j][1]-1][exact_coalitions[index][j][0]] = dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] + 1
                            dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] = 0
                            exact_coalitions[index][j][1] -= 1
        timesteps_list[n].append(timestep)
        max_distance_list[n].append(max_dis)
        sum_distance_list[n].append(sum_dis)
    file_data_timestep.write(str(timesteps_list[n])+'\n')
    file_data_max_dis.write(str(max_distance_list[n])+'\n')
    file_data_sum_dis.write(str(sum_distance_list[n])+'\n')                                                               
