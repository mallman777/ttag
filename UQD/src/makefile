all: start64

CppDemo64: CppDemo.cpp  makefile ../CTimeTag/Include/*.h ../CTimeTag/Linux/libtimetag64.so
	gcc  -m64 CppDemo.cpp -oCppDemo64 -lpthread -lstdc++ -ICTimeTagLib -L../CTimeTag/Linux -lusb-1.0 -ltimetag64 

CppDemo64_msa: CppDemo_msa.cpp  makefile ./CTimeTag/Include/*.h ./CTimeTag/Linux/libtimetag64.so
	g++  -m64 CppDemo_msa.cpp -oCppDemo64_msa -lpthread -lstdc++ -ICTimeTagLib -L../CTimeTag/Linux -lusb-1.0 -ltimetag64 

UQDinterface: uqd.cpp  makefile ./CTimeTag_Version_2_18_9/CTimeTag/Include/*.h ./CTimeTag_Version_2_18_9/CTimeTag/Linux/libtimetag64.so
	g++  -m64 buffer.c uqd.cpp -oUQDinterface -lpthread -lstdc++ -ICTimeTagLib -L./CTimeTag_Version_2_18_9/CTimeTag/Linux -lusb-1.0 -ltimetag64 -lm -lrt -lboost_program_options -lboost_thread 

start64: UQDinterface
#	sudo ./UQDinterface
	
oldstart:
	sudo /lib/ld-linux.so.2 --library-path ../CTimeTag/Linux/ ./CppDemo64
