# function : transfor image content into well-divided points image and get all pixels location
# author : Zhang Zhehong
# date : 2020.11.13
# modify 1 : 2021.3.31

from cv2 import cv2
import numpy as np
import math

class Shape:
                def __init__(self,filename):
                                # properities 
                                self.cnt = 0 # the number of all pixels
                                self.min_width = 0 # the minimum width of the original shape
                                self.max_width = 0 # the maxmum width of the original shape
                                self.min_height = 0 # the minimum height of the original shape
                                self.max_height = 0 # the maxmum height of the original shape
                                self.originalShape_x = [] # store original pixels x location
                                self.originalShape_y = [] # store original pixels x location
                                self.targetShape = [] # store target pixels location
                                self.boundaryShape = [] # store boundary pixels
                                
                                # functions
                                self.getImage(filename) # get input image
                                self.getOriginalShape() # get original shape points
               
                # read a image
                # 读取图像
                def getImage(self, filename):
                                try :
                                                self.input = cv2.imread(filename)
                                except :
                                                print('IOError : fail to read image.')

                # scan image by cols and get pixels points location,warning that image axis is different from normal axis.
                # 此处进行列扫描，为了得到输入图像中像素点存在区域坐标的最大值和最小值
                def getOriginalShape(self): 
                                self.binaryImage = self.input.copy() # store the binary image
                                # find the region of interest
                                min_height = int(self.binaryImage.shape[0])
                                max_height = -1
                                min_width = int(self.binaryImage.shape[1])
                                max_width = -1
                                h = int(self.binaryImage.shape[0]) - 1
                                # topleft is (0,0)
                                for width in range(int(self.binaryImage.shape[1])):
                                                for height in range(int(self.binaryImage.shape[0])):
                                                                if self.binaryImage[height, width, 0] < 255:
                                                                                # count the number of black pixels
                                                                                self.cnt = self.cnt + 1 
                                                                                # store all black pixels
                                                                                self.originalShape_y.append(h - height)
                                                                                self.originalShape_x.append(width)
                                                                                # find coordinates range of ROI 
                                                                                if height > max_height:
                                                                                                max_height = height
                                                                                if height < min_height:
                                                                                                min_height = height 
                                                                                if width > max_width:
                                                                                                max_width = width
                                                                                if width < min_width:
                                                                                                min_width = width 
                                                                                self.binaryImage[height, width, 0] = 0
                                                                                self.binaryImage[height, width, 1] = 0
                                                                                self.binaryImage[height, width, 2] = 0
                                # store the ROI range
                                self.min_height = min_height
                                self.max_height = max_height                                                   
                                self.min_width = min_width
                                self.max_width = max_width             

                # get a new target shape with n  points
                # target:获取与目标像素个数相同的图像
                # method:给定的目标数值 n,
                #        先根据目标像素个数与原始像素个数的比例缩小图像
                #        再对缩小后的图像一层一层减少像素点，直到得到像素总数等于n的新的图像
                def getTargetShape(self,n):
                                #resize image before downzising it
                                #对图像按照比例进行缩小，ratio = sqrt(n/self.cnt)
                                tempImage = self.binaryImage.copy() # store updated shape
                                ratio = math.sqrt(n/self.cnt)# resize ratio
                                
                                tempImage = cv2.resize(tempImage,(0,0),fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA)# new size image
                                #update new count and ROI([min_width,max_width],[min_height,max_height])
                                #计算得到缩小后图像的兴趣区域的范围
                                #注意：更新计算ROI的范围能够极大减少不必要的遍历
                                min_height = int(tempImage.shape[0])
                                max_height = -1
                                min_width = int(tempImage.shape[1])
                                max_width = -1
                                h = int(tempImage.shape[0]) - 1
                                count = 0
                                for width in range(int(tempImage.shape[1])):
                                                for height in range(int(tempImage.shape[0])):
                                                                if tempImage[height, width, 0] < 255:
                                                                                # 使用resize缩放图像的时候，函数对原有的图像像素进行了修改，这里需要重新进行二值化图像
                                                                                tempImage[height,width,0] = 0
                                                                                tempImage[height,width,1] = 0
                                                                                tempImage[height,width,2] = 0
                                                                                # count the number of black pixels
                                                                                count = count + 1
                                                                                # find coordinates range of ROI 
                                                                                if height > max_height:
                                                                                                max_height = height
                                                                                if height < min_height:
                                                                                                min_height = height 
                                                                                if width > max_width:
                                                                                                max_width = width
                                                                                if width < min_width:
                                                                                                min_width = width 
                                targetImage = tempImage.copy()
                                #start to downsize
                                flag = 0
                                # each loop in a new range ROI in ([min_width,max_width],[min_height,max_height])
                                while True :
                                                for h in range(min_height, max_height + 1):
                                                                for w in range(min_width, max_width + 1):
                                                                                if tempImage[h,w,0] < 255:
                                                                                                if tempImage[h-1, w, 0] < 255 and tempImage[h + 1, w, 0] < 255 and tempImage[h, w + 1, 0] < 255 and tempImage[h, w-1, 0] < 255:
                                                                                                                continue
                                                                                                else:
                                                                                                                targetImage[h, w, 0] = 255
                                                                                                                targetImage[h, w, 1] = 255
                                                                                                                targetImage[h, w, 2] = 255
                                                                                                                count = count - 1
                                                                                                                if count == n :
                                                                                                                                flag = 1
                                                                                                                                break
                                                                if flag == 1:
                                                                                break
                                                if flag == 1:
                                                                break 
                                                min_width = min_width + 1
                                                min_height = min_height + 1
                                                max_width = max_width - 1
                                                max_height = max_height - 1                                                           
                                                tempImage = targetImage.copy()

                                # find current the range of ROI
                                min_height = int(targetImage.shape[0])
                                max_height = -1
                                min_width = int(targetImage.shape[1])
                                max_width = -1
                                for width in range(int(targetImage.shape[1])):
                                                for height in range(int(targetImage.shape[0])):
                                                                if targetImage[height, width, 0] < 255:
                                                                                # find coordinates range of ROI 
                                                                                if height > max_height:
                                                                                                max_height = height
                                                                                if height < min_height:
                                                                                                min_height = height 
                                                                                if width > max_width:
                                                                                                max_width = width
                                                                                if width < min_width:
                                                                                              min_width = width 
                                # store target shape points location
                                h = int(targetImage.shape[0])-1
                                for height in range(min_height, max_height + 1):
                                                for width in range(min_width, max_width + 1):
                                                                if targetImage[height,width,0] < 255:
                                                                                self.targetShape.append([width,h-height-1])

                                # update ROI range(topleft --> bottomleft)
                                self.min_height = h - max_height - 1
                                self.max_height = h - min_height - 1
                                self.min_width = min_width
                                self.max_width = max_width
                                self.targetImage = targetImage.copy()
                                # cv2.imwrite('../output/targetImage.png',self.targetImage)
                # get the pattern boundary points
                # 获取图像的边界点
                def getOriginalBoundary(self):
                                h = int(self.input.shape[0])-1
                                for height in range(self.min_height, self.max_height + 1):
                                                for width in range(self.min_width, self.max_width + 1):
                                                                if self.input[height,width,0] < 255:
                                                                                if (self.input[height-1,width,0] < 255) and (self.input[height+1,width,0] < 255) and (self.input[height,width-1,0] < 255) and (self.input[height,width+1,0] < 255):
                                                                                                continue
                                                                                else:
                                                                                                self.boundaryShape.append([width, h - height])

                                
