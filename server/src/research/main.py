# -*- coding: utf-8 -*-
u"""メインの処理を実行します．"""
import common as cmn
import analysis as ana
import plotFig as fig
import sys

if __name__ == "__main__":
    # コマンドライン引数読み込み
    arg_l   = float(sys.argv[1])
    arg_a   = float(sys.argv[2])
    
    sim = cmn.getSimulationFromFile(arg_l, arg_a)
    gwn = cmn.getGWhiteNoiseFromFile()
    pop = cmn.getPopFromFile(arg_l, arg_a)

    cmn.getKurtosisValue(gwn.dispx, gwn.dispy, 0.01)

    pop = sorted(pop, key=lambda x: cmn.klDivergence([cmn.createDispPdf(sim.dispx[i], x.detailPrm) for i in range(len(sim.dispx))], sim.dispy))
    _pop = ana.getAroundSpecifiedSquareObjectValue(pop, 0, 10.)
#    for i in range(cmn.getConstValue('NUM_OF_MOMENTEQ')):
#        fig.plotSpecificObjectValue(_pop, i, '/usr/local/src/master/fig/a' + str(i) + '.eps')
#    for i in range(len(_pop)):
#        filename    = "_Obj=" + str(round(cmn.getSquareObjectiveValue(_pop[i], cmn.getStandardDeviationList(pop)), 5)) + ".eps"
#        fig.plotDispPdf_Ana_Sim_Gauss(_pop[i], sim, gwn, '/usr/local/src/master/fig/' + filename)

    meanSdList = cmn.getStandardDeviationList(pop)
    minSquareInd = ana.getMinSquareObjectInd(pop)
#    fig.plotDispPdf_Ana_Sim_Gauss(minSquareInd, sim, gwn, "/usr/local/src/master/fig/aaa.eps")
    
    print(pop[0].detailPrm)
    selectedInd = ana.culcEquivalentLinearizationMethod(_pop, arg_l, arg_a)
    fig.plot3DDispPdf_Ana(pop[0], sim, "/usr/local/src/master/fig/ccc_ana.eps")
    fig.plot3DDispPdf_Sim(sim, "/usr/local/src/master/fig/ccc_sim.eps")
    fig.plotDispPdf_Ana_Sim_Gauss(selectedInd, sim, gwn, "/usr/local/src/master/fig/aaa.eps")
    fig.plotDispPdf_Ana_Sim_Gauss(pop[0], sim, gwn, "/usr/local/src/master/fig/bbb.eps")
    fig.plotVelPdf_Ana_Sim(pop[0], sim, "/usr/local/src/master/fig/ddd.eps")
    fig.plotRelation_KLDivergence_Objective(pop, sim, "/usr/local/src/master/fig/Relation_of_KLDivergence-SquareObjectiveValue_" + str(arg_l) + "_" + str(arg_a) + ".eps")

    fig.plotIndObjectiveValue(pop[0], meanSdList, "/usr/local/src/master/fig/ObjectiveValue_" + str(arg_l) + "_" + str(arg_a) + ".eps")
#    fig.plotMomentValue(pop[0], "/usr/local/src/master/fig/MomentValue_" + str(arg_l) + "_" + str(arg_a) + ".eps")
#    fig.plotPopObjectiveValue(pop, meanSdList, 10, "/usr/local/src/master/fig/10_ObjectiveValue_" + str(arg_l) + "_" + str(arg_a) + ".eps")
