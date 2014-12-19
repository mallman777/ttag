#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include "./CTimeTag/Include/CTimeTag.h"
#include "./CTimeTag/Include/CLogic.h"
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <iomanip>
using namespace std;
using namespace TimeTag;

int volatile runAcq = 1;

static void exitsignal(int signal){
    cout << "stopping tagger" << endl;
    runAcq = 0;
}

void IdTest(CTimeTag &timetag)
{
    unsigned char *chan;
    long long *time;
    long long count = 0;
    bool reference = false;
    int ledbrightness = 100;
    int delay = 70;
    double res = timetag.GetResolution();
    int sizeLast = 0;
    bool useEdgeGate = false;
    int gateDuration = 1000;

    cout << "> FPGA: " << timetag.GetFpgaVersion() << " Channels: " << timetag.GetNoInputs() << " Resolution: " << timetag.GetResolution() << endl;

    cout << "> Setting LED brightness" << endl;
    timetag.SetLedBrightness(ledbrightness);

    cout << "> Using Edge Gate" << endl;
    timetag.UseTimetagGate(useEdgeGate);
 
    cout << "> Setting Gate Duration" << endl;
    timetag.SetGatingTime(gateDuration);

    cout << "> Setting Channel Voltages" << endl;
    for (int i=0;i<16;i++) {
        timetag.SetInputThreshold(i+1,.100);
    }
    cout << "> Setting Reference value" << endl;
    timetag.Use10MHz(reference);

//    cout << "> Set Ch8 Delay" << endl;
//    timetag.SetDelay(8, delay);

    cout << "> Set Ch1 Delay" << endl;
    timetag.SetDelay(1, delay);

    timetag.StartTimetags();
    while (runAcq < 100){
        sizeLast = timetag.ReadTags(chan, time);
        count += sizeLast;
        cout << "Acquisitions: " << runAcq << endl;
        cout << "Total Counts: " << count << endl;
        cout << "Size Last Read: " << sizeLast << endl;
        runAcq++;
    }
    timetag.StopTimetags();
    cout << "exiting" << endl;

    cout << "Chan: ";
    for (int i = 0; i != 7; ++i){
        cout  << (int)chan[i] <<" ";
    }
    cout << endl;

    cout << "Time(ns): ";
    for (int i = 0; i != 7; ++i){
        cout << std::fixed;
        cout << std::setprecision(2);
        cout << time[i]*res*1e9 << " ";
    }
    cout << endl;
    cout << "Last time(ns): " << time[sizeLast-1]*res*1e9 << endl;
    cout << "Last Chan: " << (int)chan[sizeLast-1] << endl;
}

void SimpleTest(CTimeTag &timetag)
{
		unsigned char *chan;
		long long *time;
		int count= timetag.ReadTags(chan, time);
		int count2;
		long long old = 0;

		timetag.StartTimetags();
		usleep(2000000);
		count= timetag.ReadTags(chan, time);
		timetag.StopTimetags();

        if (0){
		    //save as text
		    ofstream testfile;
		    testfile.open("testfile.txt");
		    printf ("count %d\n", count);
		    count2 = count;
		    if (count > 5)
			    count2 = 5;
		    for (int j= 0; j<count2; j++)
		    {
			    printf ("chan %d time %lu diff %d\n", (int)chan[j], time[j], (int)(time[j]-old));
			    printf ("chan %d time %lx diff %d\n", (int)chan[j], time[j], (int)(time[j]-old));
			    testfile << (int)chan[j] << "\t" << time[j] << "\t" << time[j]-old <<"\n";
			    old= time[j];
		    }
		    printf ("chan %d time %d diff %d\n", (int)chan[count-1], (int)time[count-1], (int)(time[count-1]-old));
		    old  = time[count-1];
		    testfile.close();

		    //save as binary
		    ofstream outbin ("testfile.bin", ios::binary);
		    outbin.write((const char *)time,count*sizeof(*time));
		    outbin.close();
        }
}

void TomTest(CTimeTag &timetag)
{
	printf ("Tom Special Test\n");
	
	
	ChannelType *chan;
	TimeType *time;
	double res= timetag.GetResolution();
	

for(int test= 0;;test++)
	{
	timetag.StartTimetags();	
	double  min= 1E9;
	double max= -1E9;
	printf ("\n");
	long long old= 0;
	int extra= 10;
	for (int i= 0;i<1000*extra;i++)
	{
		int count= timetag.ReadTags(chan, time);
		
		for (int j= 0; j<count; j++)
		{
			if (chan[j] == 30)
			{
				printf ("\nOverflow %d\n", time[j]);
			}
			else
			{

			long long diff= time[j]-old;
			double dtime = diff* res;
			if (old == 0)
			{
				old= time[j];
				continue;
			}
			old= time[j];
			int x;
			if (diff <= 0)
			{
				printf ("\nErr !!! Flags= %x, i= %d, j= %d" ,timetag.ReadErrorFlags(), i, j);
				printf ("diff= %ld",diff);
				printf ("= %lx",diff);
				printf ("= %f\n",diff*timetag.GetResolution());
				x= 8;
			}
			if (dtime < min)
				min= dtime;
			if (dtime > max)
				max = dtime;
			}

			
		}
		
		printf ("test %4d tags %8d min %10.4f us max %10.4f us    \r", test, count, min*1e6, max*1e6);
	}
	timetag.StopTimetags();
	int flags= timetag.ReadErrorFlags();
	if (flags)
		printf ("\nFlag check= %x", flags);
}

}

void SpeedTest(CTimeTag &timetag)
{
	printf ("Timetag Speed Test\n");
	printf ("Increase rate until error goes on\n\n");  

	timetag.StartTimetags();
	ChannelType *chan;
	TimeType *time;
	double res= timetag.GetResolution();
	long long old= 0;
	double  min= 1E6;
	double max= -1E6;

	for (int i= 0;;i++)
	{
		if (i %1000== 0)
		{
			printf ("\n");
			min= 1E6;
		    max= -1E6;
		}
		int count= timetag.ReadTags(chan, time);
		
		for (int j= 0; j<count; j++)
		{
			if (chan[j] == 30)
			{
				printf ("\nOverflow\n");
			}
			else
			{

			long long diff= time[j]-old;
			double dtime = diff* res;
			old= time[j];
			if (dtime < min)
				min= dtime;
			if (dtime > max)
				max = dtime;
			}

			
		}
		
		printf ("tags %8d min %10.4f us max %10.4f us           \r", count, min*1e6, max*1e6);
	}
	timetag.StopTimetags();

}

void LogicTest(CTimeTag &timetag)
{
	printf ("Please note: Logic test ist only possible, when logic feature is enabled in device\n");
	CLogic logic(&timetag);
	logic.SwitchLogicMode();

	int delayTicks= (int)(66e-9/timetag.GetResolution());
	logic.SetDelay(1, delayTicks);
	logic.SetDelay(3, 0);

	logic.SetWindowWidth((int)(1e-9 /timetag.GetResolution()));

	printf ("\n");
	for (int i= 0; i<1000; i++)
	{
		logic.ReadLogic();
		double time= logic.GetTimeCounter()*5e-9;
		double single1= logic.CalcCountPos(1)/time/1000;
		double single3= logic.CalcCountPos(4)/time/1000;
		double pattern= logic.CalcCountPos(5)/time/1000;
		printf ("\r s1: %8.3f s3:%8.3f both:%8.3f", single1, single3, pattern);

	}
	printf ("\nready\n");
	
}
void Help()
{
	printf ("\n\nCommands\n");
	printf ("--------\n");
	printf ("H Help (this text)\n");
	printf ("C Calibrate\n");
	printf ("L LogicTest\n");
	printf ("S SpeedTest\n");
	printf ("R ReadTags\n");
	printf ("Q Quit\n");

	printf ("\n");


}
void Menue(CTimeTag &timetag)
{
	printf ("\n:");
	char c= getchar();
	switch (toupper(c))
	{
		case 'H': 
			Help(); 
			break;
		case 'C': 
			printf ("Calibrating.....");
			fflush(stdout);
			timetag.Calibrate();
			printf ("ok !\n");
			break;
		case 'L': 
			LogicTest(timetag);
			break;
		case 'S': 
			SpeedTest(timetag);
			break;
		case 'R': 
			SimpleTest(timetag);
			break;
		case 'T': 
			TomTest(timetag);
			break;

		case 'Q':
			timetag.Close();
			exit(0);
	}

}
void MenueLoop(CTimeTag &timetag)
{
	Help();
	for (;;)
	{
		
		try 
		{
			Menue(timetag);
		}
		catch (TimeTag::Exception ex)
		{
			printf ("\nErr: %s\n", ex.GetMessageText().c_str());
		}

		catch (std::exception ex)
		{
			printf ("\nErr: %s\n", ex.what());
		}

	}
}

int main(int argc, char* argv[])
{ 

	printf ("\nPointer size = %d, seems I am running in %d bit mode\n\n", (int)sizeof(int*), 8*(int)sizeof(int*));

	printf ("Opening timetag device...\n");  
	
	
	CTimeTag timetag; 
	try
	{
		timetag.Open();
//		timetag.SetInputThreshold(1, 0.1);
		IdTest(timetag);
        timetag.Close();
	}
	catch (TimeTag::Exception ex)
	{
		printf ("\nErr: %s\n", ex.GetMessageText().c_str());
		printf ("Press enter\n");
		getchar();
	}
	return 0;
}

