#include "../include/research.h"

Simulation::Simulation(double lambda, double beta2, double alpha)
{
	this->_lambda	= lambda;
	this->_beta2	= beta2;
	this->_alpha	= alpha;
}

/**
 * @fn 入力を生成する
 * @param std::vector<double> &force 入力を格納（領域確保済み）
 **/
void Simulation::_createExcitation(std::vector<double> &force)
{
	unsigned int i;

	// ランダム変数
	gsl_rng* r	= gsl_rng_alloc(gsl_rng_default);
	gsl_rng_set(r, time(NULL)+clock());
	gsl_rng* rp	= gsl_rng_alloc(gsl_rng_default);
	gsl_rng_set(rp, time(NULL)+clock()+1);

	// 入力強度
	double wSt = sqrt(_alpha);
	double pSt = sqrt(1 - _alpha);

	// ホワイトノイズの分散
	double sigma	= sqrt(2.*M_PI*S0 / dt);

	for (i = 0; i < SAMPLE_LENGTH; ++i)
		force[i]	= wSt*gsl_ran_gaussian(r, sigma) + pSt*gsl_ran_bernoulli(r, dt*_lambda)*gsl_ran_gaussian(rp, sqrt(_beta2)) / dt;
}

/**
 * @fn 運動方程式を4次のルンゲクッタで解く
 * @param std::vector<double> &x 時間を格納
 * @param std::vector<double> &y 応答変位を格納
 * @param std::vector<double> &force 入力
 **/
void Simulation::culcRungeKutta(std::vector<double> &t, std::vector< std::vector<double> > &v_y1, std::vector< std::vector<double> > &v_y2, std::vector<double> &force)
{
	std::cout << "Start solving equation of motion using 4th-Runge-Kutta.\n" << std::endl;

	unsigned int i, ii;


	t.resize(SAMPLE_LENGTH);
	Common::resize2DemensionalVector(v_y1, NUM_OF_SAMPLES, SAMPLE_LENGTH);
	Common::resize2DemensionalVector(v_y2, NUM_OF_SAMPLES, SAMPLE_LENGTH);
	// ルンゲクッタの諸変数
	double DY1[4], DY2[4];
	for (i = 0; i < NUM_OF_SAMPLES; ++i)
	{
		/* 入力を生成 */
		force.resize(SAMPLE_LENGTH);
		this->_createExcitation(force);

		// 初期値
		double y1 = 0., y2 = 0.;

		for (ii = 0; ii < SAMPLE_LENGTH; ++ii)
		{
			DY1[0] = dt*_f1(force[ii], y1, y2);
			DY2[0] = dt*_f2(force[ii], y1, y2);

			DY1[1] = dt*_f1(force[ii], y1 + DY1[0] / 2.0, y2 + DY2[0] / 2.0);
			DY2[1] = dt*_f2(force[ii], y1 + DY1[0] / 2.0, y2 + DY2[0] / 2.0);

			DY1[2] = dt*_f1(force[ii], y1 + DY1[1] / 2.0, y2 + DY2[1] / 2.0);
			DY2[2] = dt*_f2(force[ii], y1 + DY1[1] / 2.0, y2 + DY2[1] / 2.0);

			DY1[3] = dt*_f1(force[ii], y1 + DY1[2], y2 + DY2[2]);
			DY2[3] = dt*_f2(force[ii], y1 + DY1[2], y2 + DY2[2]);

			y1 = y1 + (DY1[0] + 2.*DY1[1] + 2.*DY1[2] + DY1[3]) / 6.0;
			y2 = y2 + (DY2[0] + 2.*DY2[1] + 2.*DY2[2] + DY2[3]) / 6.0;

			// 変位と速度の最小値・最大値を決定
			if (y1>_y1max) _y1max = y1;
			if (y1<_y1min) _y1min = y1;
			if (y2>_y2max) _y2max = y2;
			if (y2<_y2min) _y2min = y2;


			// cout << "y1min:" << _y1min << ", y1:" << y1 << endl;
			v_y1[i][ii] = y1;
			v_y2[i][ii] = y2;

			if (i == 0)
				t[ii]	= ii*dt;
		}
	}
}

/**
 * @fn 変位の確率密度関数を生成
 * @param std::vector< std::vector<double> > &y1 応答変位が格納された２次元配列
 * @param std::vector<double> &x X軸の情報を保存
 * @param std::vector<double> &y Y軸の情報を保存
 **/
void Simulation::createDispPdf(const std::vector< std::vector<double> > &y1, std::vector<double> &x, std::vector<double> &y)
{
	cout << "Creating a file of the displacement pdf(.dat).\n" << endl;

	int i, ii, iii;

	int n_dx1, size = 0;
	double pdf_y1, integral_y1 = 0.;
	std::vector< std::vector<double> > pdf_buffer;
	Common::resize2DemensionalVector(pdf_buffer, NUM_OF_SAMPLES, 3000);

	for (i = 0; i < NUM_OF_SAMPLES; ++i)
	{
		for (ii = 0; (_y1min + ii*dx) <= _y1max; ++ii)
		{
			// vectorのresize用
			if (i == 0) size++;

			// 幅dxに含まれる回数
			// TODO:バッファに追加した値を除外することで速度向上
			n_dx1 = 0;
			for (iii = 0; iii < SAMPLE_LENGTH; ++iii)
				if ((y1[i][iii] < (_y1min + (ii + 1)*dx)) && (y1[i][iii] >= (_y1min + ii*dx)))
					n_dx1++;
			
			pdf_buffer[i][ii] = (double)n_dx1 / SAMPLE_LENGTH / dx;
		}
	}

	x.resize(size);
	y.resize(size);
	for (i = 0; (_y1min + i*dx) <= _y1max; ++i)
	{
		pdf_y1 = 0.;
		for (ii = 0; ii < NUM_OF_SAMPLES; ++ii)
			pdf_y1 += pdf_buffer[ii][i];
		pdf_y1 = (double)pdf_y1 / NUM_OF_SAMPLES;

		x[i]	= _y1min + i*dx;
		y[i]	= pdf_y1;

		integral_y1 += pdf_y1*dx;
	}

	std::cout << "integral of pdf_y1 = " << integral_y1 << ".\n" << std::endl;
}

/**
 * @fn 速度の確率密度関数を生成
 * @param std::vector< std::vector<double> > &y2 応答速度が格納された２次元配列
 * @param std::vector<double> &x X軸の情報を保存
 * @param std::vector<double> &y Y軸の情報を保存
 **/
void Simulation::createVelPdf(const std::vector< std::vector<double> > &y2, std::vector<double> &x, std::vector<double> &y)
{
	cout << "Creating a file of the velocity pdf(.dat).\n" << endl;

	int i, ii, iii;

	int n_dx, size = 0;
	double pdf_y2, integral_y2 = 0.;
	std::vector< std::vector<double> > pdf_buffer;
	Common::resize2DemensionalVector(pdf_buffer, 3000, NUM_OF_SAMPLES);

	for (i = 0; i<NUM_OF_SAMPLES; ++i)
	{
		for (ii = 0; (_y2min + ii*dx) <= _y2max; ++ii)
		{
			// vectorのresize用
			if (i == 0) size++;

			// 幅dxに含まれる回数
			n_dx = 0;
			for (iii = 0; iii<SAMPLE_LENGTH; ++iii)
				if ((y2[i][iii] < (_y2min + (ii + 1)*dx)) && (y2[i][iii] >= (_y2min + ii*dx)))
					n_dx++;

			pdf_buffer[ii][i] = (double)n_dx / SAMPLE_LENGTH / dx;
		}
	}

	x.resize(size);
	y.resize(size);
	for (i = 0; (_y2min + i*dx) <= _y2max; ++i) {
		pdf_y2 = 0.;
		for (ii = 0; ii<NUM_OF_SAMPLES; ++ii)
		{
			pdf_y2 += pdf_buffer[i][ii];
		}
		pdf_y2 = (double)pdf_y2 / NUM_OF_SAMPLES;

		x[i]	= _y2min + i*dx;
		y[i]	= pdf_y2;

		integral_y2 += pdf_y2*dx;
	}

	std::cout << "integral of pdf_y2 = " << integral_y2 << ".\n" << std::endl;
}

/* ガウス性ホワイトノイズを受ける系の厳密解 */
void Simulation::exactSolutionOfGaussianWhiteNoise()
{
	cout << "Culculate exact solution excited Gaussian white noise." << endl;

	// カウント変数
	size_t tmp;

	FILE *x_Gpdf;
	x_Gpdf = fopen("y1_Gpdf.dat", "w");

	// 第二修正ベッセル関数
	double K_nu;
	double bessel_p, bessel_q;
	double bessel_C, bessel_arg;

	// 確率密度関数の厳密解epsilon
	double exact_gauss_pdf;
	double integral_gauss_pdf;

	bessel_p = 2.*ZETA;
	bessel_q = ZETA*EPSILON;
	bessel_arg = pow(bessel_p, 2) / (8.*bessel_q);

	K_nu = gsl_sf_bessel_Knu(0.25, bessel_arg);
	bessel_C = 2.*sqrt(bessel_q / bessel_p)*exp(-bessel_arg) / K_nu;

	for (tmp = 0; (_y1min + tmp*dx) <= _y1max; tmp++)
	{
		exact_gauss_pdf = bessel_C*exp(-bessel_p*pow(_y1min + tmp*dx, 2) - bessel_q*pow(_y1min + tmp*dx, 4));
		integral_gauss_pdf += exact_gauss_pdf*dx;
		// 厳密解の記録
		fprintf(x_Gpdf, "%lf %lf\n", (_y1min + tmp*dx), exact_gauss_pdf);
	}

	std::cout << "integral of exact_gauss_pdf = " << integral_gauss_pdf << ".\n" << std::endl;

	fclose(x_Gpdf);
}

double Simulation::_f1(double force, double y1, double y2)
{
	return y2;
}

double Simulation::_f2(double force, double y1, double y2)
{
	return force - 2.*ZETA*y2 - y1 - EPSILON*y1*y1*y1;
}
