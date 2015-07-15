all: start64

CppDemo32: CppDemo.cpp  makefile ../CTimeTag/Include/*.h ../CTimeTag/Linux/libtimetag32.so
	gcc  -m32 CppDemo.cpp -oCppDemo32 -lpthread -lstdc++ -ICTimeTagLib -L ../CTimeTagSource -L../CTimeTag/Linux -lusb-1.0 -ltimetag32 

CppDemo64: CppDemo.cpp  makefile ../CTimeTag/Include/*.h ../CTimeTag/Linux/libtimetag64.so
	gcc  -m64 CppDemo.cpp -oCppDemo64 -lpthread -lstdc++ -ICTimeTagLib -L../CTimeTag/Linux -lusb-1.0 -ltimetag64 


start64:CppDemo64
	sudo ./CppDemo64
	
start32:CppDemo32
	sudo ./CppDemo32

