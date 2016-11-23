# -*- coding: utf-8 -*- 
import numpy as np
import math
import sys
import os

NUM_OF_GAUSS    = 3     # 足し合わせるガウス分布の数
NUM_OF_MOMENT   = 21
NUM_OF_MOMENTEQ = 15
NUM_OF_PARAM    = 10

OBJECTIVE_WEIGHT = [1.26, 0.66, 1.35, 3.18, 2.53, 2.85, 5.16, 7.25, 19.6, 11.5, 13.7, 18.3, 26.9, 27.9, 318.]

dx  = 0.01  # pdfpdfのX軸刻み幅

class Individual:
    u"""個体情報を格納
    メンバ: m[], o[], disp[], vel[], dPdf[], vPdf[], detailPrm[]
    Pythonでは，代入すれはメンバが生成される．元からメンバを明記しておくと識別子が同一として扱われてしまう．"""
    pass

class Simulation:
    u"""シミュレーション解の情報を格納
    メンバ: dispx[], dispy[], velx[], vely[]"""

class GWhiteNoise:
    u"""ガウス性ホワイトノイズ解の情報を格納
    メンバ: dispx[], dispy[]"""

#---- public ----
def drange(begin, end, step):
    u"""小数刻みでrangeできるように拡張
    【引数】begin: 開始の値，end: 終了の値，step: ステップ幅"""
    n = begin
    while n+step < end:
        yield n
        n += step

def culcIntegralPdf(pdf):
    u"""PDFの積分値を計算します．
    【引数】pdf: 確率分布の値リスト
    【戻り値】integration: 積分値"""
    integrantion    = 0.
    for i in range(len(pdf)):
        integrantion    += pdf[i]*dx
    return integrantion

def createLevelCrossingRate(xi, prm):
    u"""閾値通過率を計算します．
    【引数】xi: 閾値，prm: 詳細のパラメータ
    【戻り値】prob: 閾値通過率"""
    prob = 0.
    for i in range(0, NUM_OF_GAUSS):
        pp_c = prm['kappa'][i]/prm['sigma1'][i]/prm['sigma2'][i]
        pp_g = prm['mu2'][i] + pp_c*prm['sigma2'][i]*(xi - prm['mu1'][i])/prm['sigma1'][i]
        pp_sigma    = prm['sigma2'][i]*math.sqrt(1. - pp_c**2)
        # 閾値通過率
        prob += prm['a'][i]*math.exp(-1.*(pp_xi - prm['mu1'][i])**2/2./prm['sigma1'][i]**2)/2./math.pi/prm['sigma1'][i]/prm['sigma2'][i]/math.sqrt(1. - pp_c**2)* (pp_sigma**2*math.exp(-pp_g**2/2./pp_sigma**2)
                        + math.sqrt(math.pi/2.)*pp_g*pp_sigma*(1. + math.erf(pp_g/math.sqrt(2.)/pp_sigma)));
    return prob;

def getConstValue(name):
    if name == "NUM_OF_MOMENT":
        return NUM_OF_MOMENT
    elif name == "NUM_OF_MOMENTEQ":
        return NUM_OF_MOMENTEQ
    elif name == "NUM_OF_PARAM":
        return NUM_OF_PARAM
    elif name == "NUM_OF_GAUSS":
        return NUM_OF_GAUSS
    else:
        print("ERROR: 指定した定数は存在しません．")
        sys.exit()

def createDispPdf(x, prm):
    u"""パラメータから変位応答を計算します．
    【引数】x: はシミュレーションから取得，prm: 詳細のパラメータ
    【戻り値】pdf: 変位応答分布の値リスト"""
    pdf = []
    for i in range(0, len(x)):
        tmp_pdf = 0.
        for ii in range(0, NUM_OF_GAUSS):
            tmp_pdf += prm['a'][ii]*(1./math.sqrt(2.*math.pi)/prm['sigma1'][ii])*math.exp(-1.*(x[i]-prm['mu1'][ii])**2/2./prm['sigma1'][ii]**2)
        pdf.append(tmp_pdf)
    return pdf

def createVelPdf(x, prm):
    u"""パラメータから変位応答を計算します．
    【引数】x: はシミュレーションから取得，prm: 詳細のパラメータ
    【戻り値】pdf: 速度応答分布の値リスト"""
    pdf = []
    for i in range(0, len(x)):
        tmp_pdf = 0.
        for ii in range(0, NUM_OF_GAUSS):
            tmp_pdf += prm['a'][ii]*(1./math.sqrt(2.*math.pi)/prm['sigma2'][ii])*math.exp(-1.*(x[i]-prm['mu2'][ii])**2/2./prm['sigma2'][ii]**2)
        pdf.append(tmp_pdf)
    return pdf

def klDivergence(comp, true):
    u"""KLダイバージェンスを計算する．
    【引数】comp: 比較対象の確率分布の値リスト，true: 真値の確率分布の値リスト
    【戻り値】ret: KLダイバージェンスの値"""
    if len(comp) != len(true):
        print("KLダイバージェンス計算時のlistのサイズが異なります．")
        sys.exit()
    ret = 0.
    for i in range(len(true)):
        if (comp[i] == 0) or (true[i] == 0):
            continue
        else:
            ret += comp[i]*math.log(comp[i]/true[i])
    return ret

def getSimulationFromFile(arg_l, arg_a):
    u"""シミュレーションファイル読み込み
    【引数】arg_l: ラムダ，arg_a: アルファ
    【戻り値】sim: プロット用のシミュレーション解"""
    sim = Simulation()
    # 変位
    sim.dispx = []
    sim.dispy = []
    lineCount   = 0
    for line_s in open('/usr/local/src/master/dat/l='+str(arg_l)+'/a='+str(arg_a)+'/sim_y1pdf.dat'):
        if lineCount % 10 == 0:
            col_s   = line_s.strip().split(' ')
            sim.dispx.append(float(col_s[0]))
            sim.dispy.append(float(col_s[1]))
        lineCount   += 1

    # 速度
    sim.velx = []
    sim.vely = []
    lineCount = 0
    for line_s in open('/usr/local/src/master/dat/l='+str(arg_l)+'/a='+str(arg_a)+'/sim_y2pdf.dat'):
        if lineCount % 10 == 0:
            col_s   = line_s.strip().split(' ')
            sim.velx.append(float(col_s[0]))
            sim.vely.append(float(col_s[1]))
        lineCount += 1
    return sim

def getGWhiteNoiseFromFile():
    gwn = GWhiteNoise()
    # ホワイトノイズのみの厳密解ファイルの読み込み
    gwn.dispx = []
    gwn.dispy = []
    for line_s in open('/usr/local/src/master/dat/y1_Gpdf.dat'):
        col_s = line_s.strip().split(' ')
        gwn.dispx.append(float(col_s[0]))
        gwn.dispy.append(float(col_s[1]))
    return gwn

def getPopFromFile(arg_l, arg_a):
    # プロット用解析解X軸
    # for文の中で１回づつ読み込むのは無駄だから上で宣言しておく
    anaDispX = [i for i in drange(-6, 6, dx)]
    # anaVelX   = [i for i in drange(-12, 12, dx)]

    # 解析ファイル読み込み
    fileNum = _getFileNum('/usr/local/src/master/results/l='+str(arg_l)+'/dat_a='+str(arg_a)+'/')
    pop = []
    for i in range(0, fileNum):
        print('ana_gsay1pdf_' + str(i) + '.pdf is reading')
        for line_a in open('/usr/local/src/master/results/l='+str(arg_l)+'/dat_a='+str(arg_a)+'/ana_gsay1pdf_'+str(i)+'.dat'):
            col_a = line_a.strip().split(' ')
            ind = Individual()
            #--- モーメント値 ---
            ind.m = [float(col_a[i]) for i in range(NUM_OF_MOMENT)]
            #--- 目的関数値 ---
            ind.o = [float(col_a[i]) for i in range(NUM_OF_MOMENT, NUM_OF_MOMENT + NUM_OF_MOMENTEQ)]
            #--- パラメータ ---
            simplePrm = [float(col_a[i]) for i in range(NUM_OF_MOMENT + NUM_OF_MOMENTEQ, NUM_OF_MOMENT + NUM_OF_MOMENTEQ + NUM_OF_PARAM)]
            ind.detailPrm = _getDetailParameterFromSimpleNotation(simplePrm)
            #--- 変位 ---
            ind.disp = anaDispX
            #--- 速度 ---
            # ind.vel   = anaVelX
            #--- 変位応答分布 ---
            ind.dPdf  = createDispPdf(anaDispX, ind.detailPrm)
            #--- 速度応答分布 ---
            # vPdfForKL = createDispPdf(simVelX, detailPrm)
            # ind.dPdf  = createVelPdf(anaVelX, detailPrm)
            
            # PDFの積分がおかしいものを除去
            sumDispPdf = culcIntegralPdf(ind.dPdf)
            # if sumDispPdf > 1.00005 or sumDispPdf < 0.99995:
            if sumDispPdf > 1.05 or sumDispPdf < 0.95:
                continue

            pop.append(ind)
            del ind
    
    return pop

#---- private ----
def _getFileNum(path):
    u"""指定したディレクトリ配下のファイル数をカウント
    【引数】path: ディレクトリへのパス
    【戻り値】counter: ファイル数"""
    ch = os.listdir(path)
    counter = 0
    for i in ch:
        if (os.path.isdir(path + i)):
            checkFileNum(path + i + "/")
        else:
            counter += 1
    return counter

def _getDetailParameterFromSimpleNotation(simple):
    u"""パラメータの形式を変換します。
    【引数】simple: 簡易のパラメータ
    【戻り値】detail: 詳細のパラメータ"""
    detail  = {}
    # 重み
    detail['a'] = [0]*NUM_OF_GAUSS
    detail['a'][0]  = (1. - simple[0]) / 2.
    detail['a'][1]  = simple[0]
    detail['a'][2]  = (1. - simple[0]) / 2.
    # 変位
    detail['mu1']   = [0]*NUM_OF_GAUSS
    detail['mu1'][0]    = simple[1]
    detail['mu1'][1]    = 0.
    detail['mu1'][2]    = -1.*simple[1]
    detail['sigma1']    = [0]*NUM_OF_GAUSS
    detail['sigma1'][0] = simple[3]
    detail['sigma1'][1] = simple[5]
    detail['sigma1'][2] = simple[3]
    # 速度
    detail['mu2']   = [0]*NUM_OF_GAUSS
    detail['mu2'][0]    = simple[2]
    detail['mu2'][1]    = 0.
    detail['mu2'][2]    = -1.*simple[2]
    detail['sigma2']    = [0]*NUM_OF_GAUSS
    detail['sigma2'][0] = simple[4]
    detail['sigma2'][1] = simple[6]
    detail['sigma2'][2] = simple[4]
    # 共分散
    detail['kappa'] = [0]*NUM_OF_GAUSS
    detail['kappa'][0]  = simple[7]
    detail['kappa'][1]  = simple[8]
    detail['kappa'][2]  = simple[9]
    return detail

 







   # 主成分分析
    # pcaAnalysis(supPop)
    # sys.exit()
    ### for 中間発表<<ここから
    ## KLダイバージェンスと相関のあるモーメントを見つけよう
    # dKL   = []
    # obj   = np.zeros((NUM_OF_MOMENTEQ, len(pop)))
    # moment    = np.zeros((NUM_OF_MOMENT, len(pop)))
    # min_dKL   = 100
    # min_obj   = [100000]*NUM_OF_MOMENTEQ
    # minObjPop = [Individual()]*NUM_OF_MOMENTEQ
    # for i in range(0, len(pop)):
    #   # 散布図プロット用
    #   dKL.append(pop[i].dKL)
    #   for ii in range(0, NUM_OF_MOMENT):
    #       moment[ii, i]   = pop[i].m[ii]
    #   for ii in range(0, NUM_OF_MOMENTEQ):
    #       obj[ii, i]  = pop[i].o[ii]
    #   # KLダイバージェンス最小個体を見つける用
    #   if pop[i].dKL < min_dKL:
    #       min_dKL = pop[i].dKL
    #       minDKLPop   = pop[i]
    #   # 各目的関数を最小にしている個体を見つける
    #   for ii in range(0, NUM_OF_MOMENTEQ):
    #       if abs(pop[i].o[ii]) < min_obj[ii]:
    #           min_obj[ii] = abs(pop[i].o[ii])
    #           minObjPop[ii]   = pop[i]
    ## KLダイバージェンスが最小の個体
    # print("Min dKL = " + str(min_dKL))
    # for i in range(0, NUM_OF_MOMENTEQ):
    #   print("Moment No." + str(i) + " = " + str(minDKLPop.o[i]))
    ## dKLが上位の個体情報を表示
    # i = 0
    # supPop = []
    # while pop[i].dKL < 5.:
    #   if pop[i].dKL < 0:
    #       i += 1
    #       continue
    #   print("Pop No." + str(i) + ": dKL = " + str(pop[i].dKL))
    #   supPop.append(pop[i].o)
    #   plt.plot(range(0, NUM_OF_MOMENTEQ), pop[i].o, label=i)
    #   plt.xlabel("Number of MomentEQ")
    #   plt.ylabel("Value of MomentEQ")
    #   # plt.xticks(np.arange(0, NUM_OF_MOMENTEQ, 1))
    #   # plt.ylim([-140, 20])
    #   plt.grid(which='major',color='black',linestyle='--')
    #   plt.legend(loc='lower left')
    #   plt.savefig("/usr/local/src/master/fig/momentEQ.png")
    #   i += 1
#    plt.plot(range(0, NUM_OF_MOMENTEQ), pop[0].o, label=pop[0].dKL)
#    plt.xlabel("Number of MomentEQ")
#    plt.ylabel("Value of MomentEQ")
#    plt.xticks(np.arange(0, NUM_OF_MOMENTEQ, 1))
#    plt.grid(which='major',color='black',linestyle='--')
#    plt.legend(loc='lower left')
#    plt.savefig("/usr/local/src/master/fig/momentEQ.png")
#    plt.clf()

    ### for 中間発表>>ここまで
