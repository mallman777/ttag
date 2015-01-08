# include <stdlib.h>
# include <string.h>

typedef struct{
    long * times;
    short * chans;
    int size;
} myStruct;

int myadder(int x, int y){
    return x + y;
}

/*
Function to create pointer to structure myStruct.  Creates two arrays that are arrSize in size. Uses an intermediate staging structure
and memcpys data over to bar.  This is to test my algorithm for coincidence times.
*/

myStruct * myFun (unsigned int arrSize){

    myStruct * stageStruct = (myStruct *) calloc (1,sizeof(myStruct));
    myStruct * bar = (myStruct *) calloc (1,sizeof(myStruct));

    stageStruct -> size = arrSize;
    stageStruct -> times = (long *) calloc(arrSize,sizeof(long));
    stageStruct -> chans = (short *) calloc(arrSize,sizeof(short));

    for (unsigned int i = 0; i != arrSize; ++i){
        stageStruct->times[i] = 1000*i;
        stageStruct->chans[i] = i;
    }

    bar -> times = (long *) calloc(arrSize,sizeof(long));
    bar -> chans = (short *) calloc(arrSize,sizeof(short));
    bar->size = stageStruct->size;

    memcpy(bar->times, stageStruct->times, arrSize*sizeof(long));
    memcpy(bar->chans, stageStruct->chans, arrSize*sizeof(short));

    free(stageStruct->times);
    free(stageStruct->chans);
//    free(&(stageStruct->size));
    free(stageStruct);

    return bar;
}

/*
Function that mimicks np.sum(arr) and a flat array.  Runs about 3 times faster than np.sum()
*/

int arrSum (int arr[], int arrSize){
    int sum = 0;
    for (int i = 0; i != arrSize; ++i){
        sum += arr[i];
    }
    return sum;
}
