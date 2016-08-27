#ifndef __RESEARCH_H_INCLUDE__
#define __RESEARCH_H_INCLUDE__

#define _USE_MATH_DEFINES
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <ctime>
#include <iostream>
#include <vector>

#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>
#include <gsl/gsl_statistics.h>
#include <gsl/gsl_sf.h>

#include "common.h"

using namespace std;


#ifndef __OSCILLATOR_AND_EXCITATION_PARAMETER__
#define __OSCILLATOR_AND_EXCITATION_PARAMETER__
/********** nÌWEüÍðisÏj**********/
#define PI M_PI
#define S0 1./(2.*PI)
#define EPSILON 0.3
#define ZETA 0.05
#endif // !__OSCILLATOR_AND_EXCITATION_PARAMETER__

/********** vZð **********/
#define SAMPLE_LENGTH 131072	// 131072,65536
#define NUM_OF_SAMPLES 100		// üÍÌW{
#define dt 0.01		// ÔÝ
#define dx 0.1		// pdfÌ¡²ÌÝ


class Simulation
{
private:
	double _lambda, _beta2, _alpha, _sigma;
	// pdfÌ¡²ÌÅ¬lCÅål
	double _y1min, _y1max, _y2max, _y2min;
	// QNb^Åg¤
	static double _f1(double force, double y1, double y2);
	static double _f2(double force, double y1, double y2);
	void _createExcitation(std::vector<double> &);

public:
	Simulation(double lambda, double beta2, double alpha);
	void culcRungeKutta(std::vector<double> &, std::vector< std::vector<double> > &, std::vector< std::vector<double> > &, std::vector<double> &);
	void createDispPdf(const std::vector< std::vector<double> > &, std::vector<double> &, std::vector<double> &);
	void createVelPdf(const std::vector< std::vector<double> > &, std::vector<double> &, std::vector<double> &);
	void exactSolutionOfGaussianWhiteNoise();
};

#endif // !__RESEARCH_H_INCLUDE_