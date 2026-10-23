#ifndef ONDEMANDSTREAM_H
#define ONDEMANDSTREAM_H
// output stream to write both to std::cout and the .prt file, used by pnflow
// (moved here from the former src/include/InputFile.h)
#include <fstream>
#include <iostream>
#include <iomanip>
#include <string>

#define defaultFloat  std::resetiosflags(std::ios_base::floatfield)<<std::setprecision(6)

/// output stream to write both to std::cout, and .prt file
class mstream  {
 public:
	enum: short { PRTF = 1, STDO = 2 }; // .prt and stdout

	thread_local
		static std::ofstream  dbgFile; /// output stream to write .dbg  file for debugging

	mstream(std::string fnam, unsigned char po=PRTF|STDO)
	:	outps(po) { if (!fnam.empty() && outps&PRTF) prt_.open(fnam); if(!prt_) outps&=~PRTF; };

	mstream& operator<<(std::ostream& (*fn)(std::ostream&))  {
		if(outps&PRTF) { fn(prt_);  }  if(outps&STDO) { fn(std::cout); std::cout.flush(); }  return *this;  }

	template <class T>  mstream& operator<< (T val)  {
		if(outps&PRTF) { prt_<<val; }  if(outps&STDO) { std::cout<< val; }   return *this;  }

	std::ofstream& fileStream() { return prt_; }

 private:
	std::ofstream prt_;
	unsigned char outps; /// output .prt std::out
};


#define outD mstream::dbgFile


#endif
