# vein-based structure for formation task
# function: vein-based pattern formation where slope k = 3pi/4
# author : zhehong
# date : 2022.6.1

import numpy as np
import matplotlib.pyplot as plt
import random
from copy import deepcopy
import time

from Preprocess import Shape
from RandomPoints import RandomPoints
from VeinCoalitions import VeinCoalitions

timesteps_list = {}
max_distance_list = {}
sum_distance_list = {}

data_timestep = []
data_max_dis = []
data_sum_dis = []

file_data_timestep = open('../../../output/veinbasedformation/formation3/VB4_timestep_1.txt','w')
file_data_max_dis = open('../../../output/veinbasedformation/formation3/VB4_max_dis_1.txt','w')
file_data_sum_dis = open('../../../output/veinbasedformation/formation3/VB4_sum_dis_1.txt','w')

labels = []
img_index = 3
vein_type = 4 #1: k=0,y=0; 2: y=x, k=pi/4; 3:y-x=c k=pi/2; 4:x+y=c, k=3pi/4
size_list=[100,400,900,1500,2000]
# n=100
# shape_index = 9
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
                                file = '../../../input/data2/shape'+str(shape_index)+'/img'+str(img_index)+'.png'   # the filename of the input
                                print("size = ",n, "shape :",file)
                                img = Shape(file)      # get the image by the filename
                                img.getTargetShape(n)  # get the set of original target locations from the input
                                target_points=[]      #store target points
                                for p in img.targetShape:
                                                target_points.append([p[0] - img.min_width,p[1] - img.min_height])  #get the set of target locations after somve shifts
                                                
                                #########################################################################
                                ################ step 2 : get original shape locations ##################
                                #########################################################################
                                num_rows = img.max_height - img.min_height + 1   # get the height of the target locations
                                num_cols = img.max_width - img.min_width + 1     # get the width of the target locations
                                print("map:",num_rows,"X",num_cols)
                                R =  RandomPoints()  # intialize a RandomPoints class R
                                original_points = R.generateRandomPoints2(num_rows,num_cols,n) # get a set of original dot locations

                                #########################################################################################
                                ##### step 3 : get vein-based coalitions on target locations and original locations #####
                                #########################################################################################
                                t_coalition = VeinCoalitions(vein_type,target_points,num_rows,num_cols)
                                target_coalitions = t_coalition.veinBasedPartioning() # get the vein-based decomposition on target locations
                                o_coalition = VeinCoalitions(vein_type,original_points,num_rows,num_cols)
                                original_coalitions = o_coalition.veinBasedPartioning() # get vein-based coalitions on original locations
                                index_list = o_coalition.getIndexList()

                                #########################################################################
                                ############################ step 4 : rectify ###########################
                                #########################################################################                                
                                exact_coalitions = deepcopy(original_coalitions)  # the optimal coalition
                                exact = 0
                                glut = 0  #record extra agents in the glut coalition
                                demand = 0 # record understaffed agents in the shortage coalition
                                timestep = 0

                                flag = {}
                                dis = {}
                                row_hash = {}
                                row_binary_list = np.arange(0,num_rows,0.5)
                                col_binary_list = np.arange(0,num_cols,0.5)
                                cnt =0
                                for i in row_binary_list:
                                                flag[i]={}
                                                dis[i]={}
                                                row_hash[i]=cnt
                                                cnt += 1
                                                for j in col_binary_list:
                                                                flag[i][j]=0
                                                                dis[i][j]=0

                                for p in original_points:
                                                flag[p[1]][p[0]] = 1
                                                dis[p[1]][p[0]] = 0

                                # compensate from glut coalitions
                                while True:
                                                timestep += 1
                                                demand = 0
                                                glut = 0
                                                exact = 0
                                                for current_index in index_list:
                                                                len1 = len(exact_coalitions[current_index])
                                                                len2 = len(target_coalitions[current_index])
                                                                # print("current_index:",current_index,"now_len: ",len1, "target_len: ", len2)
                                                                if len1 == len2:
                                                                                # print("mode 1, demand: ", demand, "glut: ",glut)
                                                                                exact += 1
                                                                # understaffed coalition
                                                                elif  len1 < len2:
                                                                                if glut >= (len2 - len1):
                                                                                                demand = len2 - len1
                                                                                                #only compensate from the previous coalition
                                                                                                glut -= demand
                                                                                                # print("in-mode 2-1, demand: ", demand, "glut: ",glut)
                                                                                                if current_index - 1 >=index_list[0]:
                                                                                                                search_index = current_index - 1
                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                for search_point in search_list:
                                                                                                                                if demand == 0:
                                                                                                                                                break
                                                                                                                                else:
                                                                                                                                                # current coalition gets agents from the search(previous) coalition
                                                                                                                                                if flag[search_point[1]][search_point[0]] == 1 :
                                                                                                                                                                if search_point[1]+0.5 < num_rows and search_point[1]+0.5 >=0 and current_index-(search_point[1]+0.5) >= 0 and current_index-(search_point[1]+0.5)<num_cols: 
                                                                                                                                                                                if flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)]== 0:
                                                                                                                                                                                                flag[search_point[1]][search_point[0]] = 0
                                                                                                                                                                                                flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)] = 1
                                                                                                                                                                                                demand -= 1
                                                                                                                                                                                                exact_coalitions[search_index].remove([search_point[0],search_point[1]])
                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(search_point[1]+0.5),search_point[1]+0.5])
                                                                                                                                                                                                dis[search_point[1]+0.5][current_index-(search_point[1]+0.5)] += dis[search_point[1]][search_point[0]] + 1
                                                                                                                                                                                                dis[search_point[1]][search_point[0]]= 0
                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                # adjust
                                                                                                                if demand > 0 and len(exact_coalitions[search_index]) >0:
                                                                                                                                target_list = deepcopy(target_coalitions[current_index])
                                                                                                                                move_flag=[-1]*len(row_binary_list)
                                                                                                                                mark = 0
                                                                                                                                for target_point in target_list:
                                                                                                                                                stride = 0.5
                                                                                                                                                if flag[target_point[1]][target_point[0]] == 0:
                                                                                                                                                                # search toward down
                                                                                                                                                                while target_point[1]-0.5-stride >= exact_coalitions[search_index][0][1]:
                                                                                                                                                                                if flag[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] == 1 and move_flag[row_hash[target_point[1]-0.5-stride]] == -1:
                                                                                                                                                                                                if search_index-(target_point[1]-0.5-stride+0.5)>=0 and flag[target_point[1]-stride][search_index-(target_point[1]-stride)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]-stride][search_index-(target_point[1]-stride)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]-0.5-stride),target_point[1]-0.5-stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]-stride),target_point[1]-stride])
                                                                                                                                                                                                                                dis[target_point[1]-stride][search_index-(target_point[1]-stride)] += dis[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]-stride]] = 1
                                                                                                                                                                                                                                mark = 1
                                                                                                                                                                                                                                break
                                                                                                                                                                                stride += 0.5
                                                                                                                                                                if mark == 0:
                                                                                                                                                                                # search toward up
                                                                                                                                                                                while target_point[1]-0.5+stride <= exact_coalitions[search_index][-1][1]:
                                                                                                                                                                                                if flag[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] == 1 and move_flag[row_hash[target_point[1]-0.5+stride]] == -1:
                                                                                                                                                                                                                if target_point[1]-0.5+stride-0.5 >=0 and search_index-(target_point[1]-0.5+stride-0.5)>=0 and flag[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]-0.5+stride),target_point[1]-0.5+stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]-0.5+stride-0.5),target_point[1]-0.5+stride-0.5])
                                                                                                                                                                                                                                dis[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)] += dis[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]-0.5+stride-0.5]] = 1
                                                                                                                                                                                                                                mark = 1
                                                                                                                                                                                                                                break
                                                                                                                                                                                                stride += 0.5  
                                                                                                                                if mark == 0 and len(exact_coalitions[current_index])>0:
                                                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                                                for current_point in current_list:
                                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1:
                                                                                                                                                                                if current_point[1]-0.5 >= 0 and current_index - (current_point[1]-0.5) >=0 and current_index - (current_point[1]-0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]-0.5)>=0 and  search_index-(current_point[1]-0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]==0 and flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]-0.5),current_point[1]-0.5])
                                                                                                                                                                                                                                dis[current_point[1]-0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break
                                                                                                                                                                                if current_point[1]+0.5 < num_rows and current_index - (current_point[1]+0.5) >=0 and current_index - (current_point[1]+0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]+0.5)>=0 and  search_index-(current_point[1]+0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]==0 and flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]+0.5),current_point[1]+0.5])
                                                                                                                                                                                                                                dis[current_point[1]+0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break

                                                                                                                                                                                
                                                                                                demand = 0
                                                                                                # print("out-mode 2-1, demand: ", demand, "glut: ",glut)
                                                                                elif glut > 0 and glut <  (len2 - len1):
                                                                                                # first, compensate from the previous coalition
                                                                                                demand = len2- len1
                                                                                                demand -= glut 
                                                                                                # print("in-mode 2-2, demand: ", demand, "glut: ",glut)
                                                                                                if current_index - 1 >=index_list[0]:
                                                                                                                search_index = current_index - 1
                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                for search_point in search_list:
                                                                                                                                if glut == 0 :
                                                                                                                                                break
                                                                                                                                else:
                                                                                                                                                # the search(previous) coalition sends agents to the current coalition
                                                                                                                                                if flag[search_point[1]][search_point[0]] != 0 and search_point[1]+0.5>=0 and search_point[1]+0.5<num_rows and current_index-(search_point[1]+0.5)<num_cols and current_index-(search_point[1]+0.5) >= 0 and flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)] == 0:
                                                                                                                                                                flag[search_point[1]][search_point[0]] = 0
                                                                                                                                                                flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)] = 1
                                                                                                                                                                glut -= 1
                                                                                                                                                                exact_coalitions[search_index].remove([search_point[0],search_point[1]])
                                                                                                                                                                exact_coalitions[current_index].append([current_index-(search_point[1]+0.5),search_point[1]+0.5])
                                                                                                                                                                dis[search_point[1]+0.5][current_index-(search_point[1]+0.5)] += dis[search_point[1]][search_point[0]] + 1
                                                                                                                                                                dis[search_point[1]][search_point[0]] = 0
                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1]) 
                                                                                                                # adjust
                                                                                                                if glut > 0 and len(exact_coalitions[search_index])>0:
                                                                                                                                target_list = deepcopy(target_coalitions[current_index])
                                                                                                                                move_flag=[-1]*len(row_binary_list)
                                                                                                                                mark = 0
                                                                                                                                # adjust search(previous) coalition
                                                                                                                                for target_point in target_list:
                                                                                                                                                stride = 0.5
                                                                                                                                                if flag[target_point[1]][target_point[0]] == 0:
                                                                                                                                                                # search toward down
                                                                                                                                                                while target_point[1]-0.5-stride >= exact_coalitions[search_index][0][1]:
                                                                                                                                                                                if flag[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] == 1 and move_flag[row_hash[target_point[1]-0.5-stride]] == -1:
                                                                                                                                                                                                if search_index-(target_point[1]-0.5-stride+0.5)>=0 and flag[target_point[1]-stride][search_index-(target_point[1]-stride)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]-stride][search_index-(target_point[1]-stride)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]-0.5-stride),target_point[1]-0.5-stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]-stride),target_point[1]-stride])
                                                                                                                                                                                                                                dis[target_point[1]-stride][search_index-(target_point[1]-stride)] += dis[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]-0.5-stride][search_index-(target_point[1]-0.5-stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]-stride]] = 1
                                                                                                                                                                                                                                mark = 1
                                                                                                                                                                                                                                break
                                                                                                                                                                                stride += 0.5
                                                                                                                                                                if mark == 0:
                                                                                                                                                                                # search toward up
                                                                                                                                                                                while target_point[1]-0.5+stride <= exact_coalitions[search_index][-1][1]:
                                                                                                                                                                                                if flag[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] == 1 and move_flag[row_hash[target_point[1]-0.5+stride]] == -1:
                                                                                                                                                                                                                if target_point[1]-0.5+stride-0.5 >=0 and search_index-(target_point[1]-0.5+stride-0.5)>=0 and flag[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]-0.5+stride),target_point[1]-0.5+stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]-0.5+stride-0.5),target_point[1]-0.5+stride-0.5])
                                                                                                                                                                                                                                dis[target_point[1]-0.5+stride-0.5][search_index-(target_point[1]-0.5+stride-0.5)] += dis[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]-0.5+stride][search_index-(target_point[1]-0.5+stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]-0.5+stride-0.5]] = 1
                                                                                                                                                                                                                                mark = 1
                                                                                                                                                                                                                                break
                                                                                                                                                                                                stride += 0.5  
                                                                                                                                # adjust current coalition 
                                                                                                                                if mark == 0 and len(exact_coalitions[current_index])>0:
                                                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                                                for current_point in current_list:
                                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1:
                                                                                                                                                                                if current_point[1]-0.5 >= 0 and current_index - (current_point[1]-0.5) >=0 and current_index - (current_point[1]-0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]-0.5)>=0 and  search_index-(current_point[1]-0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]==0 and flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]-0.5),current_point[1]-0.5])
                                                                                                                                                                                                                                dis[current_point[1]-0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break
                                                                                                                                                                                if current_point[1]+0.5 < num_rows and current_index - (current_point[1]+0.5) >=0 and current_index - (current_point[1]+0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]+0.5)>=0 and  search_index-(current_point[1]+0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]==0 and flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]+0.5),current_point[1]+0.5])
                                                                                                                                                                                                                                dis[current_point[1]+0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break
                                                                                                                
                                                                                                                
                                                                                                glut = 0
                                                                                                #second, compensate from the next coalition                                           
                                                                                                if current_index + 1 <= index_list[-1]:
                                                                                                                search_index = current_index + 1
                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                for search_point in search_list:
                                                                                                                                if demand == 0:
                                                                                                                                                break
                                                                                                                                else:
                                                                                                                                                # current coalition gets agents from the search(next) coalition
                                                                                                                                                if flag[search_point[1]][search_point[0]] != 0 and search_point[1]-0.5>=0 and search_point[1]-0.5<num_rows and current_index-(search_point[1]-0.5)>=0 and current_index-(search_point[1]-0.5)<num_cols and flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] == 0:
                                                                                                                                                                flag[search_point[1]][search_point[0]] = 0
                                                                                                                                                                flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] = 1
                                                                                                                                                                demand -= 1
                                                                                                                                                                exact_coalitions[search_index].remove([search_point[0],search_point[1]])
                                                                                                                                                                exact_coalitions[current_index].append([current_index-(search_point[1]-0.5),search_point[1]-0.5])
                                                                                                                                                                dis[search_point[1]-0.5][current_index-(search_point[1]-0.5)] += dis[search_point[1]][search_point[0]] + 1
                                                                                                                                                                dis[search_point[1]][search_point[0]] = 0           
                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                if demand > 0 and len(exact_coalitions[search_index])>0:
                                                                                                                                target_list = deepcopy(target_coalitions[current_index])
                                                                                                                                move_flag=[-1]*len(row_binary_list)
                                                                                                                                mark = 0
                                                                                                                                # adjust search(next) coalition
                                                                                                                                for target_point in target_list:
                                                                                                                                                stride = 0.5
                                                                                                                                                if flag[target_point[1]][target_point[0]] == 0:
                                                                                                                                                                # search toward down
                                                                                                                                                                while target_point[1]+0.5-stride >= exact_coalitions[search_index][0][1]:
                                                                                                                                                                                if flag[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] == 1 and move_flag[row_hash[target_point[1]+0.5-stride]] == -1:
                                                                                                                                                                                                if target_point[1]+0.5-stride+0.5<num_rows and search_index-(target_point[1]+0.5-stride+0.5)>=0 and flag[(target_point[1]+0.5-stride+0.5)][search_index-(target_point[1]+0.5-stride+0.5)]==0:
                                                                                                                                                                                                                flag[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] = 0
                                                                                                                                                                                                                flag[target_point[1]+0.5-stride+0.5][search_index-(target_point[1]+0.5-stride+0.5)] = 1
                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]+0.5-stride),target_point[1]+0.5-stride])
                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]+0.5-stride+0.5),target_point[1]+0.5-stride+0.5])
                                                                                                                                                                                                                dis[target_point[1]+0.5-stride+0.5][search_index-(target_point[1]+0.5-stride+0.5)] += dis[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] + 1
                                                                                                                                                                                                                dis[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)]=0
                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                move_flag[row_hash[target_point[1]+0.5-stride+0.5]] = 1
                                                                                                                                                                                                                mark =1
                                                                                                                                                                                                                break
                                                                                                                                                                                stride += 0.5
                                                                                                                                                                if mark == 0:
                                                                                                                                                                                # search toward up
                                                                                                                                                                                while target_point[1]+0.5+stride <= exact_coalitions[search_index][-1][1]:
                                                                                                                                                                                                if flag[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] == 1 and move_flag[row_hash[target_point[1]+0.5+stride]] == -1:
                                                                                                                                                                                                                if search_index-(target_point[1]+stride)>=0 and flag[target_point[1]+stride][search_index-(target_point[1]+stride)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]+stride][search_index-(target_point[1]+stride)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]+0.5+stride),target_point[1]+0.5+stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]+stride),target_point[1]+stride])
                                                                                                                                                                                                                                dis[target_point[1]+stride][search_index-(target_point[1]+stride)] += dis[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]+stride]] = 1
                                                                                                                                                                                                                                mark=1
                                                                                                                                                                                                                                break
                                                                                                                                                                                                stride += 0.5  
                                                                                                                                # adjust current coalition
                                                                                                                                if mark == 0 and len(exact_coalitions[current_index])>0:
                                                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                                                for current_point in current_list:
                                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1:
                                                                                                                                                                                if current_point[1]-0.5 >= 0 and current_index - (current_point[1]-0.5) >=0 and current_index - (current_point[1]-0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]-0.5)>=0 and  search_index-(current_point[1]-0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]==0 and flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]-0.5),current_point[1]-0.5])
                                                                                                                                                                                                                                dis[current_point[1]-0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break
                                                                                                                                                                                if current_point[1]-0.5 < num_rows and current_index - (current_point[1]+0.5) >=0 and current_index - (current_point[1]+0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]+0.5)>=0 and  search_index-(current_point[1]+0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]==0 and flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]+0.5),current_point[1]+0.5])
                                                                                                                                                                                                                                dis[current_point[1]+0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break                                                
                                                                                                                                
                                                                                                # print("out-mode 2-2, demand: ", demand, "glut: ",glut)                                                                                              
                                                                                else: # glut==0
                                                                                                
                                                                                                #only compensate from the next coaliton
                                                                                                demand += len2 -len1
                                                                                                # print("in-mode 2-3, demand: ", demand, "glut: ",glut)
                                                                                                if current_index + 1 <= index_list[-1]:
                                                                                                                search_index = current_index + 1
                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                for search_point in search_list:
                                                                                                                                if demand == 0:
                                                                                                                                                break
                                                                                                                                else:
                                                                                                                                                # current coalition gets agents from the search(next) coalition
                                                                                                                                                if flag[search_point[1]][search_point[0]] == 1:
                                                                                                                                                                if search_point[1]-0.5>=0 and search_point[1]-0.5<num_rows and current_index-(search_point[1]-0.5)>=0 and current_index-(search_point[1]-0.5)<num_cols and flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] == 0:
                                                                                                                                                                                flag[search_point[1]][search_point[0]] = 0
                                                                                                                                                                                flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] = 1
                                                                                                                                                                                demand -= 1
                                                                                                                                                                                exact_coalitions[search_index].remove([search_point[0],search_point[1]])
                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(search_point[1]-0.5),search_point[1]-0.5])
                                                                                                                                                                                dis[search_point[1]-0.5][current_index-(search_point[1]-0.5)] += dis[search_point[1]][search_point[0]] + 1
                                                                                                                                                                                dis[search_point[1]][search_point[0]] = 0           
                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                if demand > 0 and len(exact_coalitions[search_index]) >0:
                                                                                                                                target_list = deepcopy(target_coalitions[current_index])
                                                                                                                                move_flag=[-1]*len(row_binary_list)
                                                                                                                                mark = 0
                                                                                                                                # adjust search(next) coalition
                                                                                                                                for target_point in target_list:
                                                                                                                                                stride = 0.5
                                                                                                                                                if flag[target_point[1]][target_point[0]] == 0:
                                                                                                                                                                # search toward down
                                                                                                                                                                while target_point[1]+0.5-stride >= exact_coalitions[search_index][0][1]:
                                                                                                                                                                                if flag[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] == 1 and move_flag[row_hash[target_point[1]+0.5-stride]] == -1:
                                                                                                                                                                                                if target_point[1]+0.5-stride+0.5<num_rows and search_index-(target_point[1]+0.5-stride+0.5)>=0 and flag[(target_point[1]+0.5-stride+0.5)][search_index-(target_point[1]+0.5-stride+0.5)]==0:
                                                                                                                                                                                                                flag[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] = 0
                                                                                                                                                                                                                flag[target_point[1]+0.5-stride+0.5][search_index-(target_point[1]+0.5-stride+0.5)] = 1
                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]+0.5-stride),target_point[1]+0.5-stride])
                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]+0.5-stride+0.5),target_point[1]+0.5-stride+0.5])
                                                                                                                                                                                                                dis[target_point[1]+0.5-stride+0.5][search_index-(target_point[1]+0.5-stride+0.5)] += dis[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)] + 1
                                                                                                                                                                                                                dis[target_point[1]+0.5-stride][search_index-(target_point[1]+0.5-stride)]=0
                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                move_flag[row_hash[target_point[1]+0.5-stride+0.5]] = 1
                                                                                                                                                                                                                mark =1
                                                                                                                                                                                                                break
                                                                                                                                                                                stride += 0.5
                                                                                                                                                                if mark == 0:
                                                                                                                                                                                # search toward up
                                                                                                                                                                                while target_point[1]+0.5+stride <= exact_coalitions[search_index][-1][1]:
                                                                                                                                                                                                if flag[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] == 1 and move_flag[row_hash[target_point[1]+0.5+stride]] == -1:
                                                                                                                                                                                                                if search_index-(target_point[1]+stride)>=0 and flag[target_point[1]+stride][search_index-(target_point[1]+stride)]==0 :
                                                                                                                                                                                                                                flag[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] = 0
                                                                                                                                                                                                                                flag[target_point[1]+stride][search_index-(target_point[1]+stride)] = 1
                                                                                                                                                                                                                                exact_coalitions[search_index].remove([search_index-(target_point[1]+0.5+stride),target_point[1]+0.5+stride])
                                                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(target_point[1]+stride),target_point[1]+stride])
                                                                                                                                                                                                                                dis[target_point[1]+stride][search_index-(target_point[1]+stride)] += dis[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)] + 1
                                                                                                                                                                                                                                dis[target_point[1]+0.5+stride][search_index-(target_point[1]+0.5+stride)]=0
                                                                                                                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                move_flag[row_hash[target_point[1]+stride]] = 1
                                                                                                                                                                                                                                mark=1
                                                                                                                                                                                                                                break
                                                                                                                                                                                                stride += 0.5  
                                                                                                                                # adjust current coalition
                                                                                                                                if mark == 0 and len(exact_coalitions[current_index])>0:
                                                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                                                for current_point in current_list:
                                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1:
                                                                                                                                                                                if current_point[1]-0.5 >= 0 and current_index - (current_point[1]-0.5) >=0 and current_index - (current_point[1]-0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]-0.5)>=0 and  search_index-(current_point[1]-0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]==0 and flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]-0.5][current_index-(current_point[1]-0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]-0.5),current_point[1]-0.5])
                                                                                                                                                                                                                                dis[current_point[1]-0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break
                                                                                                                                                                                if current_point[1]-0.5 < num_rows and current_index - (current_point[1]+0.5) >=0 and current_index - (current_point[1]+0.5) < num_cols:
                                                                                                                                                                                                if search_index-(current_point[1]+0.5)>=0 and  search_index-(current_point[1]+0.5)<num_cols:
                                                                                                                                                                                                                if flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]==0 and flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)]==1:
                                                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                                                flag[current_point[1]+0.5][current_index-(current_point[1]+0.5)]=1
                                                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                                                exact_coalitions[current_index].append([current_index-(current_point[1]+0.5),current_point[1]+0.5])
                                                                                                                                                                                                                                dis[current_point[1]+0.5][current_index-(current_point[1]-0.5)] = dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                                                dis[current_point[1]][current_point[0]]=0
                                                                                                                                                                                                                                exact_coalitions[current_index].sort(key=lambda x:x[1])
                                                                                                                                                                                                                                break 
                                                                                                                                
                                                                                                # print("out-mode 2-3, demand: ", demand, "glut: ",glut)                                                                                               
                                                                # glut coalition
                                                                else: #len1 > len2
                                                                                # only send out agents to next coalition
                                                                                if demand == 0:
                                                                                                glut += len1 - len2
                                                                                                # print("in-mode 3-1, demand: ", demand, "glut: ",glut)
                                                                                                # current coalition sends out agents to the search(next) coalition
                                                                                                if current_index + 1 <= index_list[-1]:
                                                                                                                search_index = current_index + 1
                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                for current_point in current_list:
                                                                                                                                if glut == 0 :
                                                                                                                                                break
                                                                                                                                else:
                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1: 
                                                                                                                                                                if current_point[1]+0.5<num_rows and search_index-(current_point[1]+0.5)>=0 and search_index-(current_point[1]+0.5)<num_cols and flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)] == 0:
                                                                                                                                                                                flag[current_point[1]+0.5][search_index-(current_point[1]+0.5)] = 1
                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                glut -= 1
                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(current_point[1]+0.5),current_point[1]+0.5])
                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                dis[current_point[1]+0.5][search_index-(current_point[1]+0.5)] += dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                dis[current_point[1]][current_point[0]] = 0           
                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                # print("out-mode 3-1, demand: ", demand, "glut: ",glut)
                                                                                else:
                                                                                                glut += len1 - len2
                                                                                                # only send out to the previous coalition
                                                                                                if demand >= glut:
                                                                                                                # print("in-mode 3-2, demand: ", demand, "glut: ",glut)
                                                                                                                demand -= glut
                                                                                                                # send out agents to the previous coalition to let glut = 0
                                                                                                                if current_index - 1 >=index_list[0]:
                                                                                                                                search_index = current_index - 1
                                                                                                                                current_list = deepcopy(exact_coalitions[current_index])
                                                                                                                                for current_point in current_list:
                                                                                                                                                if glut == 0:
                                                                                                                                                                break
                                                                                                                                                else:
                                                                                                                                                                if flag[current_point[1]][current_point[0]] == 1:
                                                                                                                                                                                if current_point[1]-0.5>=0 and search_index-(current_point[1]-0.5) >=0 and search_index-(current_point[1]-0.5) < num_cols and flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)] == 0:
                                                                                                                                                                                                flag[current_point[1]-0.5][search_index-(current_point[1]-0.5)] = 1
                                                                                                                                                                                                flag[current_point[1]][current_point[0]] = 0
                                                                                                                                                                                                glut -= 1
                                                                                                                                                                                                exact_coalitions[search_index].append([search_index-(current_point[1]-0.5),current_point[1]-0.5])
                                                                                                                                                                                                exact_coalitions[current_index].remove([current_point[0],current_point[1]])
                                                                                                                                                                                                dis[current_point[1]-0.5][search_index-(current_point[1]-0.5)] += dis[current_point[1]][current_point[0]] + 1
                                                                                                                                                                                                dis[current_point[1]][current_point[0]] = 0           
                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                glut = 0   
                                                                                                                # print("out-mode 3-2, demand: ", demand, "glut: ",glut)
                                                                                                # send out to the previous and next coalitions            
                                                                                                else:
                                                                                                                # print("in-mode 3-3, demand: ", demand, "glut: ",glut)
                                                                                                                glut -= demand
                                                                                                                # send out agents to the previous coalition to let demand = 0
                                                                                                                if current_index - 1 >=index_list[0]:
                                                                                                                                search_index = current_index - 1
                                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                                for search_point in search_list:
                                                                                                                                                if demand == 0 :
                                                                                                                                                                break
                                                                                                                                                else:
                                                                                                                                                                if flag[search_point[1]][search_point[0]] == 0: 
                                                                                                                                                                                if search_point[1]+0.5<num_rows and current_index-(search_point[1]+0.5) >= 0 and current_index-(search_point[1]+0.5) < num_cols and flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)] == 1:
                                                                                                                                                                                                flag[search_point[1]][search_point[0]] = 1
                                                                                                                                                                                                flag[search_point[1]+0.5][current_index-(search_point[1]+0.5)] = 0
                                                                                                                                                                                                demand -= 1
                                                                                                                                                                                                exact_coalitions[search_index].append([search_point[0],search_point[1]])
                                                                                                                                                                                                exact_coalitions[current_index].remove([current_index-(search_point[1]+0.5),search_point[1]+0.5])
                                                                                                                                                                                                dis[search_point[1]][search_point[0]] += dis[search_point[1]+0.5][current_index-(search_point[1]+0.5)] + 1
                                                                                                                                                                                                dis[search_point[1]+0.5][current_index-(search_point[1]+0.5)] = 0           
                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                demand = 0
                                                                                                                # send out agents to the seach(next) coalitions
                                                                                                                if current_index + 1 <= index_list[-1]:
                                                                                                                                search_index = current_index + 1
                                                                                                                                search_list = deepcopy(exact_coalitions[search_index])
                                                                                                                                for search_point in search_list:
                                                                                                                                                if glut == 0:
                                                                                                                                                                break
                                                                                                                                                else:
                                                                                                                                                                if flag[search_point[1]][search_point[0]] == 0:
                                                                                                                                                                                if search_point[1]-0.5>=0 and current_index-(search_point[1]-0.5) >=0 and current_index-(search_point[1]-0.5) < num_cols and flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] == 1:
                                                                                                                                                                                                flag[search_point[1]][search_point[0]] = 1
                                                                                                                                                                                                flag[search_point[1]-0.5][current_index-(search_point[1]-0.5)] = 0
                                                                                                                                                                                                glut -= 1
                                                                                                                                                                                                exact_coalitions[search_index].append([search_point[0],search_point[1]])
                                                                                                                                                                                                exact_coalitions[current_index].remove([current_index-(search_point[1]-0.5),search_point[1]-0.5])
                                                                                                                                                                                                dis[search_point[1]][search_point[0]] += dis[search_point[1]-0.5][current_index-(search_point[1]-0.5)] + 1
                                                                                                                                                                                                dis[search_point[1]-0.5][current_index-(search_point[1]-0.5)] = 0             
                                                                                                                                exact_coalitions[search_index].sort(key=lambda x:x[1])
                                                                                                                # print("out-mode 3-3, demand: ", demand, "glut: ",glut)                                                                
                                                # draw_x = []
                                                # draw_y = []
                                                # for index in index_list:
                                                #                 if len(exact_coalitions[index]) > 0:
                                                #                                 for p in exact_coalitions[index]:
                                                #                                                 draw_x.append(p[0])
                                                #                                                 draw_y.append(p[1])

                                                # plt.clf()
                                                # plt.axis("off")
                                                # plt.scatter(draw_x,draw_y,s=8,alpha=0.8,marker='.',edgecolors='black')
                                                # plt.pause(0.3)
                                                if exact == len(index_list):
                                                                break
                                                # print("exact: ",exact)

                                exact = 0
                                while exact != n:
                                                exact = 0
                                                timestep += 1
                                                # exact_points_x=[]
                                                # exact_points_y=[]
                                                sum_dis = 0
                                                max_dis = 0
                                                for index in index_list:
                                                                if len(exact_coalitions[index]) > 0:
                                                                                for j in range(0,len(target_coalitions[index])):
                                                                                                if exact_coalitions[index][j][0] == target_coalitions[index][j][0]:
                                                                                                                exact += 1
                                                                                                                max_dis = max(max_dis,dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]])
                                                                                                                sum_dis += dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]]
                                                                                                elif exact_coalitions[index][j][0] < target_coalitions[index][j][0]:
                                                                                                                dis[index - (exact_coalitions[index][j][0]+0.5)][exact_coalitions[index][j][0]+0.5] =  dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] + 1
                                                                                                                dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] = 0
                                                                                                                exact_coalitions[index][j][0] += 0.5
                                                                                                                exact_coalitions[index][j][1] = index - exact_coalitions[index][j][0]
                                                                                                else:
                                                                                                                dis[index - (exact_coalitions[index][j][0]-0.5)][exact_coalitions[index][j][0]-0.5] =  dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] + 1
                                                                                                                dis[exact_coalitions[index][j][1]][exact_coalitions[index][j][0]] = 0
                                                                                                                exact_coalitions[index][j][0] -= 0.5
                                                                                                                exact_coalitions[index][j][1] = index - exact_coalitions[index][j][0]
                                                                                
                                timesteps_list[n].append(timestep)
                                max_distance_list[n].append(max_dis)
                                sum_distance_list[n].append(sum_dis)
                file_data_timestep.write(str(timesteps_list[n])+'\n')
                file_data_max_dis.write(str(max_distance_list[n])+'\n')
                file_data_sum_dis.write(str(sum_distance_list[n])+'\n')
