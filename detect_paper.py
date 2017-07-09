#-*-coding:utf-8 -*-
from new_detect_image import Paper,AnsDetect
import cv2

def mylog(**kargs):
    '''
    格式化打印数据
    '''
    k = kargs.keys()[0]
    from pprint import pprint
    print '\n\n-----------------------beigin----------------'
    #pprint '{}s:{}'.format((k,kargs.get(k)))
    pprint('{}:'.format(k))
    pprint(kargs.get(k))
    print '----------------------end--------------------\n\n'

def get_ans_area(img_path=None):
    '''
    从试卷中分离出答题卡
    '''
    paper = Paper(img_path)
    #答案答题卡区域
    ans_area_point = paper.get_ans_point()
    print u'答案区域:'
    print ans_area_point
    if ans_area_point:
        ans_img_path = paper.cut_ans_area(ans_area_point)
        return ans_img_path
    return None


def rec_kaohao_str(ans_img_path=None,std_point=None):
    '''
    从答题卡识别出考号
    '''
    ansdetect = AnsDetect(ans_img_path)

    #考号区域标准信息提取
    kh_std_dct = ansdetect.findKaoHaoCnts()

    #腐蚀核计算方法std_w/2,std_h/3,链接核计算方法std_w/6,std_h/6
    std_w = std_point.get('w')
    std_h = std_point.get('h')
    
    #腐蚀核大小
    edsize = cv2.getStructuringElement(cv2.MORPH_RECT,(std_w/2,std_h/3))

    dilsize = cv2.getStructuringElement(cv2.MORPH_RECT,(std_w/2,std_h/3))

    dilsize_join = cv2.getStructuringElement(cv2.MORPH_CROSS,(std_w/6,std_w/6))

    if kh_std_dct:

        #识别考号
        kh_str = ansdetect.recKaoHao(kh_std_dct,edsize,dilsize)

        return kh_str

    return ''

def rec_shit_ans(ans_img_path=None,ans_th_rate=[],ans_xx_rate=[],std_quenos=[],std_point=None):
    '''
    从答题卡识别出选择题答案
    ans_th_rate:题号标准比率
    ans_xx_rate:选项标准比率
    std_quenos:选择题题号
    '''
    ansdetect = AnsDetect(ans_img_path)

    #考号区域标准信息提取
    kh_std_dct = ansdetect.findKaoHaoCnts()

    if kh_std_dct:

        #腐蚀核计算方法std_w/2,std_h/3,链接核计算方法std_w/6,std_h/6
        std_w = std_point.get('w')
        std_h = std_point.get('h')
        
        #腐蚀核大小
        edsize = cv2.getStructuringElement(cv2.MORPH_RECT,(std_w/2,std_h/3))

        dilsize = cv2.getStructuringElement(cv2.MORPH_RECT,(std_w/2,std_h/3))

        dilsize_join = cv2.getStructuringElement(cv2.MORPH_CROSS,(std_w/8,std_w/8))

        #识别选择题答案
        shit_ans_lst = ansdetect.recAns(kh_std_dct,ans_th_rate,ans_xx_rate,std_quenos,edsize,dilsize,dilsize_join)

        return shit_ans_lst
    else:
        return []


if __name__ == "__main__": 
    #img_path = '010114.jpg'
    #img_path = '010118.jpg'
    #img_path = '010121.jpg'
    #img_path = '062201.jpg'
    img_path = '062202.jpg'
    #img_path = '062203.jpg'
    #img_path = '010118.jpg'
    #选择题题号
    #std_quenos = [1,2,3,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20]
    std_quenos = [1,2,3,4,5,6,7,8,9,10]
    #std_quenos = [1,2,4,5,8,9,10,11,12,13,14]

    #标准题号比例
    #ans_th_rate = [0.4171180931744312, 0.4452871072589382, 0.4723726977248104, 0.49837486457204766, 0.5265438786565547, 0.5644637053087758, 0.5915492957746479, 0.6175514626218852, 0.647887323943662, 0.6771397616468039, 0.7085590465872156, 0.7388949079089924, 0.7670639219934995, 0.7952329360780065, 0.8255687973997833, 0.8559046587215602, 0.8840736728060672, 0.9154929577464789, 0.942578548212351, 0.9685807150595883]
    #物理
    ans_th_rate = [0.6188679245283019, 0.6553459119496855, 0.6930817610062893, 0.730817610062893, 0.7660377358490567, 0.8188679245283019, 0.8566037735849057, 0.8930817610062893, 0.9308176100628931, 0.9685534591194969]
    #山东
    #ans_th_rate = [0.5682483889865261, 0.6080843585237259, 0.6461628588166374, 0.6818980667838312, 0.7217340363210311, 0.760398359695372, 0.7984768599882835, 0.8371411833626244, 0.8740480374926772, 0.9138840070298769, 0.9502050380785003]

    #标准选项比例
    #ans_xx_rate = [0.3442028985507246, 0.5217391304347826, 0.6920289855072463, 0.8695652173913043] 
    ans_xx_rate = [0.3515625, 0.5390625, 0.734375, 0.9375]
    #ans_xx_rate = [0.3442028985507246, 0.5217391304347826, 0.6920289855072463, 0.8695652173913043]
    

    #开始
    ans_img_path = get_ans_area(img_path)

    #std_point = {"y": 171, "x": 180, "w": 36, "h": 36}
    std_point = {"y": 171, "x": 180, "w": 64, "h": 88}

    kh_str = rec_kaohao_str(ans_img_path,std_point)

    shit_ans_lst = rec_shit_ans(ans_img_path,ans_th_rate,ans_xx_rate,std_quenos,std_point)
    mylog(kh_str=kh_str)
    mylog(shit_ans_lst=shit_ans_lst)
