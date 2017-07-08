#-*-coding:utf-8 -*-
import cv2
import numpy as np
from PIL import Image
import imutils
from imutils import contours
from imutils.perspective import four_point_transform
import os
import json


def mylog(**kargs):
    '''
    '''
    k = kargs.keys()[0]
    from pprint import pprint
    print '\n\n\n\n-----------------------beigin----------------'
    #pprint '{}s:{}'.format((k,kargs.get(k)))
    pprint('{}:'.format(k))
    pprint(kargs.get(k))
    print '----------------------end--------------------\n\n\n\n'


class Paper:
    def __init__(self,image_path="qingxie.png",quenos=None,std_ans_y=None):
        '''
        具体试卷处理
        从试卷中找出答案区域
        '''
        self.quenos = quenos
        self.std_ans_y = std_ans_y
        #图片路径
        self.image_path = image_path
        #腐蚀后的图像
        self.erode_image = None
        #膨胀后的图像
        self.dilate_image = None

        #腐蚀与膨胀核大小
        #腐蚀核大小
        self.edsize = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,20))
        #膨胀核大小
        self.dilsize = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
        
        #cv2图片对象
        self.image = cv2.imread(self.image_path)

        #图片的宽高度
        self.width = self.image.shape[1]
        self.height = self.image.shape[0]

        #图片转成灰度图
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        #做高斯模糊处理
        blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        #边缘检测后的图
        self.edged = cv2.Canny(self.gray, 75, 200)

        #对灰度图进行二值化处理
        ret,thresh = cv2.threshold(self.gray,0,250,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        #ret,thresh = cv2.threshold(self.gray,0,250,cv2.THRESH_BINARY)
        #ret,thresh = cv2.threshold(self.gray,0,250,cv2.THRESH_TRUNC)
        #ret,thresh = cv2.threshold(self.gray,0,250,cv2.THRESH_TOZERO)
        #ret,thresh = cv2.threshold(self.gray,0,250,cv2.THRESH_TOZERO_INV)
        self.thresh = thresh

        #输出边缘检测图像
        spt_lst = os.path.splitext(image_path)
        edged_path = spt_lst[0] + '_edged' + spt_lst[1]
        cv2.imwrite(edged_path,self.edged)
        #输出thresh二值图
        thresh_path = spt_lst[0] + '_thresh' + spt_lst[1]
        cv2.imwrite(thresh_path,self.thresh)

    def _erode(self):
        '''
        图像腐蚀操作
        '''
        self.erode_image = cv2.erode(self.thresh,self.edsize)
        #输出腐蚀后的图像
        spt_lst = os.path.splitext(self.image_path)
        erode_path = spt_lst[0] + '_erode' + spt_lst[1]
        cv2.imwrite(erode_path,self.erode_image)
        pass


    def _dilate(self):
        '''
        图像膨胀操作
        '''
        #self.dilate_image = cv2.erode(self.thresh,self.edsize)
        self.dilate_image = cv2.dilate(self.thresh,self.dilsize)
        #输出膨胀后的图像
        spt_lst = os.path.splitext(self.image_path)
        dilate_path = spt_lst[0] + '_dilate' + spt_lst[1]
        cv2.imwrite(dilate_path,self.dilate_image)

    def get_ans_point(self):
        '''
        从试卷中提取答案区域
        获取答案区域定位点
        '''
        #cnts = cv2.findContours(self.edged, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(self.edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(self.thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(self.thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(self.edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self._dilate()
        #cnts = cv2.findContours(self.thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cv2.findContours(self.dilate_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        all_attr = cnts[1]
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        #print cnts,33333333333333333

        if len(cnts) > 0:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

            all_c = []
            for c in cnts:
                peri = 0.01*cv2.arcLength(c, True)

                approx = cv2.approxPolyDP(c, peri, True)
                if len(approx)==4:
                    (x, y, w, h) = cv2.boundingRect(c)
                    #print 44444444444444444
                    #print x,y,w,h
                    #标识出识别出的机型轮廓并输出
                    #cv2.drawContours(self.image,c,-1,(255,0,255),3)
                    #spt_lst = os.path.splitext(self.image_path)
                    #draw_path = spt_lst[0] + '_draw' + spt_lst[1]
                    #cv2.imwrite(draw_path,self.image)
                    #break
                    if w > self.width*0.25 and x>50 and y>100:
                        #print 5555555555555555

                        #标识出识别出的机型轮廓并输出
                        cv2.drawContours(self.image,c,-1,(255,0,255),3)
                        spt_lst = os.path.splitext(self.image_path)
                        draw_path = spt_lst[0] + '_draw' + spt_lst[1]
                        cv2.imwrite(draw_path,self.image)

                        all_c.append({'x':x,'y':y,'w':w,'h':h})

            all_c = sorted(all_c,key=lambda x:x['w'],reverse=True)
            #print all_c,1111111111111
            for _c in all_c:
                x = _c.get('x')
                y = _c.get('y')
                w = _c.get('w')
                h = _c.get('h')
                return (x,y,x+w,y+h)
                return (x+5,y+5,x+w-5,y+h-10)

        else:
            return None

    def _line(self):
        '''
        '''
        minLineLength = 20
        maxLineGap = 10
        lines = cv2.HoughLinesP(self.edged,np.pi/180,118,minLineLength,maxLineGap)
        for x1,y1,x2,y2 in lines[0]:
            cv2.line(self.image,(x1,y1),(x2,y2),(0,255,0),1)
            #输出答题卡区域图像
            ans_lst = os.path.splitext(self.image_path)
            ans_path = ans_lst[0] + '_ansarea' + ans_lst[1]
            cv2.imwrite(ans_path,self.image)

    def cut_ans_area(self,cut_point=None):
        '''
        从试卷裁剪出答题卡区域图片
        '''
        #print cut_point,66666666666666666666666
        img = Image.open(self.image_path)
        region = img.crop(cut_point)

        spt_lst = os.path.splitext(self.image_path)
        cut_path = spt_lst[0] + '_cut' + spt_lst[1]

        region.save(cut_path)

        return cut_path



class AnsDetect:
    '''
    答题卡区域选项识别
    '''

    def __init__(self,image_path="mark.png",quenos=None,std_ans_y=None):
        '''
        '''

        self.quenos = quenos
        self.std_ans_y = std_ans_y

        self.image_path = image_path
        self.erode_image = None
        self.dilate_image = None
        self.kh_std_x = None
        self.kh_std_y = None
        self.kh_std_w = None
        self.kh_std_h = None
        #腐蚀与膨胀核大小
        #self.edsize = cv2.getStructuringElement(cv2.MORPH_CROSS,(8,8))
        #self.edsize = cv2.getStructuringElement(cv2.MORPH_RECT,(6,10))
        #腐蚀
        self.edsize = cv2.getStructuringElement(cv2.MORPH_RECT,(15,13))
        #膨胀为提取框
        self.cnts_dilsize = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
        #膨胀为提取答案
        self.ans_dilsize = cv2.getStructuringElement(cv2.MORPH_RECT,(15,10))

        self.image = cv2.imread(self.image_path)

        #图片的宽度
        self.width = self.image.shape[1]
        self.height = self.image.shape[0]

        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        #edged = cv2.Canny(blurred, 75, 200)
        self.edged = cv2.Canny(self.gray, 75, 200)
        #对灰度图进行二值化处理
        #self.thresh = cv2.threshold(self.gray,200,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        self.thresh = cv2.threshold(self.gray.copy(),200,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        #输出边缘检测图像
        spt_lst = os.path.splitext(image_path)
        edged_path = spt_lst[0] + '_edged' + spt_lst[1]
        cv2.imwrite(edged_path,self.edged)

        #输出thresh二值图
        thresh_path = spt_lst[0] + '_thresh' + spt_lst[1]
        cv2.imwrite(thresh_path,self.thresh)


    def _erode(self):
        '''
        图像腐蚀操作
        '''
        self.erode_image = cv2.erode(self.thresh,self.edsize)
        #输出腐蚀后的图像
        spt_lst = os.path.splitext(self.image_path)
        erode_path = spt_lst[0] + '_erode' + spt_lst[1]
        cv2.imwrite(erode_path,self.erode_image)
        pass


    def _dilate(self,cnts_dilsize=None):
        '''
        图像膨胀操作
        '''
        self.cnts_dilate_image = cv2.erode(self.thresh,self.cnts_dilsize)
        #self.dilate_image = cv2.dilate(self.erode_image,self.edsize1)
        #输出膨胀后的图像
        spt_lst = os.path.splitext(self.image_path)
        dilate_path = spt_lst[0] + '_dilate' + spt_lst[1]
        cv2.imwrite(dilate_path,self.cnts_dilate_image)

    def _erode_dilate(self,dilsize=None):
        '''
        图像膨胀操作
        '''
        #self.dilate_image = cv2.erode(self.thresh,self.edsize)
        self.dilate_image = cv2.dilate(self.erode_image,self.ans_dilsize)
        #输出膨胀后的图像
        spt_lst = os.path.splitext(self.image_path)
        dilate_path = spt_lst[0] + '_dilate' + spt_lst[1]
        cv2.imwrite(dilate_path,self.dilate_image)


    def findKaoHaoCnts(self):
        '''
        '''
        kh_std_lst = []

        #膨胀凸显外侧轮廓
        self._dilate()

        img,cnts,hierarchy = cv2.findContours(self.cnts_dilate_image.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #img,cnts,hierarchy = cv2.findContours(self.thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #img,cnts,hierarchy = cv2.findContours(self.edged.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            
            for i,c in enumerate(cnts):
                #轮廓逼近
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.01 * peri, True)
                (x, y, w, h) = cv2.boundingRect(c)

                #print self.width/3
                if i >10:
                    break
                #print w,h
                cv2.drawContours(self.image,c,-1,(255,0,255),5)
                spt_lst = os.path.splitext(self.image_path)
                kh_ans_std_path = spt_lst[0] + '_drawcnts' + spt_lst[1]
                cv2.imwrite(kh_ans_std_path,self.image)

                if h > self.height/3:
                    continue
                if w < self.width/8:
                    continue
                if x > self.width/3:
                    continue

                kh_std_lst.append({'x':x,'y':y,'w':w,'h':h})



            kh_std_lst = sorted(kh_std_lst,key=lambda x:x['y'])

            return kh_std_lst[0]
        else:
            return None

    
    def findFillCnts(self,kh_split_line_x=None):
        '''
        提取已经填图好的考号和答案轮廓,并进行区分
        '''
        #腐蚀操作
        self._erode()
        #膨胀操作
        self._dilate()

        #提取填图好的轮廓
        img,cnts,hierarchy = cv2.findContours(self.dilate_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        fill_cnts_lst = []
        kh_cnts_lst = []
        ans_cnts_lst = []
        if len(cnts) > 0:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

            for i,c in enumerate(cnts):
                #轮廓逼近
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.01 * peri, True)
                (x, y, w, h) = cv2.boundingRect(c)

                fill_cnts_lst.append({'x':x,'y':y,'w':w,'h':h})

            #将提取到的轮廓按照x排序
            fill_cnts_lst = sorted(fill_cnts_lst,key=lambda x:x['x'])
            for _cdct in fill_cnts_lst:
                if _cdct.get('x') < kh_split_line_x:
                    kh_cnts_lst.append(_cdct)
                else:
                    ans_cnts_lst.append(_cdct)

            #print u'考号:'
            #print kh_cnts_lst
            #print u'答案:'
            #print ans_cnts_lst

            return kh_cnts_lst,ans_cnts_lst

        return kh_cnts_lst,ans_cnts_lst







    def recKaoHao(self,kh_std_dct=None):
        '''
        识别考号
        kh_cnts:填图好的考号轮廓,考号区域标准轮廓信息
        '''
        #考号基准分割线
        kh_std_x = kh_std_dct.get('x')
        kh_std_w = kh_std_dct.get('w')

        kh_max_x = kh_std_x + kh_std_w 

        #获取考号和答案轮廓信息
        kh_cnts_lst,ans_cnts_lst = self.findFillCnts(kh_max_x)
        
        #卡号填图区域的平均宽度
        avg_w = sum([x['w'] for x in kh_cnts_lst])/len(kh_cnts_lst)
        
        #将考号区域X均分为10份
        each_w = kh_std_w/10

        #考号轮廓按Y排序
        kh_cnts_lst = sorted(kh_cnts_lst,key=lambda x:x['y'])

        kh_lst = []
        for _c_x in kh_cnts_lst:
            #print _c_x.get('x') - kh_std_x,222222222222222222222222
            dis_x = _c_x.get('x') - kh_std_x
            kh_no = dis_x/(avg_w+avg_w/2)
            #print kh_no,9999999999999999999

            kh_lst.append(kh_no)

        kh_str = ''.join([str(x) for x in kh_lst])

        return kh_str


    def recAns(self,kh_std_dct=None,ans_th_rate=[],ans_xx_rate=[],std_quenos=[]):
        '''
        识别选择题答案
        ans_th_rate:选项基准比例,ans_xx_rate:题号基准比例
        std_quenums:总提数
        '''
        ##选择题题号
        #std_quenos = [1,2,4,5,8,9,10,11,12,13,14]

        ##标准题号比例
        #ans_th_rate = [0.5682483889865261, 0.6080843585237259, 0.6461628588166374,\
        #                 0.6818980667838312, 0.7217340363210311, 0.760398359695372, \
        #                 0.7984768599882835, 0.8371411833626244, 0.8740480374926772,\
        #                  0.9138840070298769, 0.9502050380785003] 

        ##标准选项比例
        #ans_xx_rate = [0.3442028985507246, 0.5217391304347826, 0.6920289855072463, 0.8695652173913043]
        char_lst = ['A','B','C','D','E','F','G','H','I']

        #设置标准题号坑
        std_ans_queno = []
        for i,qn in enumerate(std_quenos):
            dct = {}
            dct['queno'] = std_quenos[i]
            dct['rate'] = ans_th_rate[i]
            dct['cnts'] = []
            std_ans_queno.append(dct)

        #是指标准选项标靶
        std_ans_xx = []
        for i,xx in enumerate(ans_xx_rate):
            dct = {}
            dct['rate'] = ans_xx_rate[i] 
            dct['xx'] = char_lst[i] 
            std_ans_xx.append(dct)
        
        #考号基准分割线
        kh_std_x = kh_std_dct.get('x')
        kh_std_w = kh_std_dct.get('w')

        kh_max_x = kh_std_x + kh_std_w 

        #获取考号和答案轮廓信息
        _,ans_cnts_lst = self.findFillCnts(kh_max_x)

        #把答案轮廓按x排序
        ans_cnts_lst = sorted(ans_cnts_lst,key=lambda x:x['x'])

        for std_que in std_ans_queno:
            th_rate = std_que.get('rate')
            
            #将提取到的答案轮廓循环与标准题号轮廓比例做比较
            for _ans_dct in ans_cnts_lst:
                _ans_rate = _ans_dct.get('x')/float(self.width)

                if _ans_rate > th_rate - 0.02 and _ans_rate < th_rate + 0.02:
                    std_que['cnts'].append(_ans_dct)

        #将匹配好的题号与轮廓进行处理,解析出选择的答案到底是A,B,C,D
        for que_cnt_dct  in std_ans_queno:

            que_cnt_dct['ans'] = []
            _cnts = que_cnt_dct.get('cnts')
            #如果有则按Y进行排序
            if _cnts:
                _cnts = sorted(_cnts,key=lambda x:x['y'])

                #将每个题号下的轮廓循环与标准选项比例做比较
                tmp_lst = []
                for _c in _cnts:
                    tu_rate = _c.get('y')/float(self.height)
                    #print que_cnt_dct.get('queno'),tu_rate,7777777777777777777

                    for _xx_dct in std_ans_xx:
                        xx_rate = _xx_dct.get('rate')
                        if tu_rate > xx_rate - 0.05 and tu_rate < xx_rate + 0.05:
                            xx = _xx_dct.get('xx')
                            tmp_lst.append(xx)
                if not tmp_lst:
                    tmp_lst.append('x')

                que_cnt_dct['ans'] = tmp_lst

            else:
                #如果没有则该题未填图,人为设置为x
                que_cnt_dct['ans'] = ['x']

        #返回识别出的答案
        shit_lst = []
        for _shit_dct  in std_ans_queno:
            _tmp_dct = {}
            _tmp_dct['queno'] = _shit_dct.get('queno')
            _tmp_dct['ans'] = _shit_dct.get('ans')
            shit_lst.append(_tmp_dct)


        #mylog(std_ans_queno=std_ans_queno)
        #mylog(shit_lst=shit_lst)

        return shit_lst


    def _line(self):
        '''
        直线检测
        '''
        minLineLength = 200
        maxLineGap = 100
        lines = cv2.HoughLinesP(self.thresh,1,np.pi/180,118,minLineLength,maxLineGap)
        for line in lines[:,:,:]:
            x1,y1,x2,y2 = line[0,:]
            #print x1,y1,x2,y2
            cv2.line(self.image,(x1,y1),(x2,y2),(0,255,0),1)
            #输出答题卡区域图像
            ans_lst = os.path.splitext(self.image_path)
            ans_path = ans_lst[0] + '_line' + ans_lst[1]
            cv2.imwrite(ans_path,self.image)



if __name__ == "__main__":
    #img_path = '010114.jpg'
    #img_path = '010102.jpg'
    #img_path = '010109.jpg'
    #img_path = '010110.jpg'
    #img_path = '010114.jpg'
    img_path = '010117.jpg'
    img_path = os.path.abspath(img_path)
    paper = Paper(img_path)
    #答案答题卡区域
    ans_area_point = paper.get_ans_point()
    if ans_area_point:
        ans_img_path = paper.cut_ans_area(ans_area_point)
        
        #检测和分析答题卡
        ansdetect = AnsDetect(ans_img_path)
        #腐蚀操作
        ansdetect._erode()
        #膨胀操作
        ansdetect._erode_dilate()
        ##直线检测
        #ansdetect._line()

        #考号区域标准信息提取
        kh_std_dct = ansdetect.findKaoHaoCnts()
        #print kh_std_dct,4444444444444444
        kh_max_x = kh_std_dct.get('x') + kh_std_dct.get('w')

        #提取填图的轮廓
        kh_cnts_lst,ans_cnts_lst = ansdetect.findFillCnts(kh_max_x)

        #识别考号
        kh_str = ansdetect.recKaoHao(kh_std_dct)

        #识别选择题答案
        ansdetect.recAns(kh_std_dct)


