
msSrc ?= ..

all:  ; $(MAKE) -f  ${msSrc}/script/Makefile.in  recurseMake USE_msRecurse=1
clean:; $(MAKE) -f  ${msSrc}/script/Makefile.in  recurseClean USE_msRecurse=1
test: ; $(MAKE) -f  ${msSrc}/script/Makefile.in  recurseTest USE_msRecurse=1
