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

/*
Function that histograms data with single-interger bin size, so no need for division.
*/

uint64_t * myHist(uint64_t * arr, uint64_t * range){
  uint64_t binNum = (range[1] - range[0]) + 1;
  uint64_t * y = (uint64_t*)calloc(2*binNum, sizeof(uint64_t)); // y holds the hist and the bin array
  for (uint32_t i = 0; arr[i] >= range[0] && arr[i] <= range[1]; ++i){
    binIndex = arr[i] - range[0];
    y[binIndex]++;
  }
  for (uint32_t i = 0; i != binNum; ++i){
    y[binSize + i] = range[0] + i;
  }
  return y;
}
