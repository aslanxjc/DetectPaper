#-*-coding:utf-8 -*-
from new_detect_image import Paper,AnsDetect

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


def rec_kaohao_str(ans_img_path=None):
    '''
    从答题卡识别出考号
    '''
    ansdetect = AnsDetect(ans_img_path)

    #考号区域标准信息提取
    kh_std_dct = ansdetect.findKaoHaoCnts()

    if kh_std_dct:
        kh_max_x = kh_std_dct.get('x') + kh_std_dct.get('w')

        #腐蚀操作
        ansdetect._erode()
        #膨胀操作
        ansdetect._erode_dilate()

        #提取填图的轮廓
        kh_cnts_lst,_ = ansdetect.findFillCnts(kh_max_x)

        #识别考号
        kh_str = ansdetect.recKaoHao(kh_std_dct)

        return kh_str

    return ''

def rec_shit_ans(ans_img_path=None,ans_th_rate=[],ans_xx_rate=[],std_quenos=[]):
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
        kh_max_x = kh_std_dct.get('x') + kh_std_dct.get('w')

        #腐蚀操作
        ansdetect._erode()
        #膨胀操作
        ansdetect._erode_dilate()

        #提取填图的答案区域轮廓
        _,ans_cnts_lst = ansdetect.findFillCnts(kh_max_x)

        #识别选择题答案
        shit_ans_lst = ansdetect.recAns(kh_std_dct,ans_th_rate,ans_xx_rate,std_quenos)

        return shit_ans_lst
    else:
        return []


if __name__ == "__main__": 
    img_path = '010114.jpg'
    #选择题题号
    std_quenos = [1,2,4,5,8,9,10,11,12,13,14]

    #标准题号比例
    ans_th_rate = [0.5682483889865261, 0.6080843585237259, 0.6461628588166374,\
                     0.6818980667838312, 0.7217340363210311, 0.760398359695372, \
                     0.7984768599882835, 0.8371411833626244, 0.8740480374926772,\
                      0.9138840070298769, 0.9502050380785003] 

    #标准选项比例
    ans_xx_rate = [0.3442028985507246, 0.5217391304347826, 0.6920289855072463, 0.8695652173913043]

    ans_img_path = get_ans_area(img_path)
    kh_str = rec_kaohao_str(ans_img_path)
    shit_ans_lst = rec_shit_ans(ans_img_path,ans_th_rate,ans_xx_rate,std_quenos)
    mylog(kh_str=kh_str)
    mylog(shit_ans_lst=shit_ans_lst)
