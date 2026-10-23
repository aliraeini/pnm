
import os, sys;  "msRoot" in os.environ or sys.exit("Retry after `source .../src/bashrc`");  from msrc import *; DbgMsg('*** main, ignore ***')



# pnflow does not support single-pore network
#paint(sphere((I,J,K), R, InV))
nErrs=0
cmds=''
with open("spack4.mhd", 'w') as f1:
	f1.write("DimSize = 40 40 40\nVxlPy {\n")
	f1.write("  img.replace_range(0,255,0)\n  img.spacing = dbl3(1,1,1)\n")
	for kk in range(0,3,1):
		for jj in range(0,3,1):
			for ii in range(0,3,1):
				f1.write("  img.paint(sphere(("+str(ii*20)+","+str(jj*20)+","+str(kk*20)+"), 11, 1))\n")
	f1.write("  img.spacing = dbl3(2e-6,2e-6,2e-6)\n}\n")



with open("CAs.tsv", 'w') as f1:
	f1.write('''
0
0
30
30
30
30
30
40
30
40
'''); f1.close();

with open("input_pnflow.dat", 'w') as f1:
	f1.write('''// -*- C -*-
NETWORK: F spack4;
TITLE:       spack4Net;
cycle1:    0.      5.0E+05     0.05          T            T;
cycle2:    1.     -5.0E+05     0.05          T            T;
cycle3:    0.      5.0E+05     0.05          T            T;
cycle1_BC:   T     F       T     T       DP   1.  1.;
cycle2_BC:   T     F       T     T       DP   1.  1.;
cycle3_BC:   T     F       T     T       DP   1.  1.;
CALC_BOX:  0. 1.;
INIT_CONT_ANG:   1   0   10  -0.2    -3.   rand   0.;
//# EQUIL_CON_ANG:   4   30   50   -0.2   -3.   rand   0.;
READ_ALTR_CA:  CAs.tsv pore 4 90;
WaterOilInterface 0.03;
//#         xR  nTheta   init   Drainage  Imbibition  corners   all steps
visualize:  1.     10      T        F          F         T         F ;
visuaLight                  T        T          T         F         T ;
writeStatistics T;
''');

runSh('.', "pnextract spack4.mhd");
runSh('.', "pnflow    input_pnflow.dat");
runSh('.', "voxelImageProcPy spack4.mhd 'img.print_info()' dump_spack4.raw");
if fileFloatDiffersFrom("voxelImageProcPy.log","total_porosity:",0.32,0.05): nErrs+=1
if fileFloatDiffersFrom("pnflow.log","Absolute permeability:",1.5e-12,0.05): nErrs+=1


exit(nErrs)
