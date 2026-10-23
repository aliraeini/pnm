
import os; ''' ========== set up paths  =========== '''
if not ("msRoot" in os.environ):
  print("try again after running:\nsource .../src/bashrc"); exit(-1);
from msrc  import *



nErrs=0


with open("spack_in.mhd", 'w') as f1:
	f1.write("""DimSize = 20 20 20
				Offset =      0  0  0
				VxlPy {
				  img.replace_range(0,255,0)   # everything set to 0
				  img.spacing = dbl3(1,1,1)
				  for c in [(0,0,0), (0,20,0), (0,20,20), (0,0,20), (20,0,0), (20,20,0), (20,20,20), (20,0,20)]:
				    img.paint(sphere(c, 12, 1))   # centre, radius, inside-value
				  img.spacing = dbl3(5e-6,5e-6,5e-6)
				}
				""");

runSh('.', "voxelImageProcPy spack_in.mhd -o spack.mhd");
runSh('.', "pnextract spack.mhd");
if fileFloatDiffersFrom("pnextract.log","nElems:",5.,0.01): nErrs+=1

exit(nErrs)
