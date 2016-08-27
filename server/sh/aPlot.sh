#!/bin/bash
RESULT_PATH="/usr/local/src/master/aResults"

##### Handling whether argument exists. #############
if [ $# -ne 3 ]; then
  echo "指定された引数は$#個です。" 1>&2
  echo "実行するには3個の引数が必要です。" 1>&2
  exit 1
fi

lambda=$1
alpha=$2
num=$3

##### Declare variables ################
params="l=${lambda}"
dat="dat_a=${alpha}"
eps="eps_a=${alpha}"

##### Handling whether directory exists. #############
if [ ! -e ${RESULT_PATH}/${params}/${dat} ]; then
	echo "指定されたアルファの結果が存在しません。" 1>&2
	exit 1
fi

##### Handlings if a directry "eps" exists. ######
if [ -e ${RESULT_PATH}/${params}/${eps} ]; then
	rm -rf ${RESULT_PATH}/${params}/${eps}/*
else
	mkdir ${RESULT_PATH}/${params}/${eps}
fi

##### Handling if "plot.plt" exists. #############
plot="plot.plt"

if [ -e ${plot} ]; then
	cp /dev/null ${plot}
else
	touch ${plot}
fi

# 初期設定
cat <<EOF >${plot}
set terminal postscript eps enhanced color
set xlabel font "Times New Roman"
set ylabel font "Times New Roman"
unset key
EOF

# plot first-cross pdf
if [ -e ${RESULT_PATH}/${params}/${dat}/"firstcross_${num}.dat" ]; then
cat <<EOF >>${plot}
set output "${RESULT_PATH}/${params}/${eps}/firstcross_${num}.eps"
set size 0.45,0.55
set xlabel "threshold {/Symbol x}"
set ylabel "up-clossing rate"
set xtics 2
set ytics 0.2
p [0:8][0:0.6] "${RESULT_PATH}/${params}/${dat}/firstcross_${num}.dat" with l lt 1 lw 4 lc rgb "blue"
EOF
fi

# plot distribution pdf
if [ -e ${RESULT_PATH}/${params}/${dat}/"gsay1pdf_${num}.dat" ]; then
cat <<EOF >>${plot}
set output "${RESULT_PATH}/${params}/${eps}/gsay1pdf_${num}.eps"
set size 0.45,0.55
set xlabel "displacement {/Italic-Times y_1}"
set ylabel "probability density {/Italic-Times p_{Y_1}}"
set xtics 2
set ytics 0.2
p [-6:6][0.:1.0] "${RESULT_PATH}/${params}/${dat}/gsay1pdf_${num}.dat" with l lt 1 lw 4 lc rgb "blue"
EOF

cat <<EOF >>${plot}
set output "${RESULT_PATH}/${params}/${eps}/log_gsay1pdf_${num}.eps"
set size 0.45,0.55
set xlabel "displacement {/Italic-Times y_1}"
set ylabel "probability density {/Italic-Times p_{Y_1}}"
set xtics 2
set ytics 0.1
set logscale y
set format y "10^{%L}"
p [-6:6][0.00001:1.0] "${RESULT_PATH}/${params}/${dat}/gsay1pdf_${num}.dat" with l lt 1 lw 4 lc rgb "blue"
EOF
fi

gnuplot ${plot}

rm ${plot}