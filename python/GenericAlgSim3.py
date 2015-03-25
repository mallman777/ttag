import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fftshift, ifftshift, fft2
from numpy.random import rand
from numpy import round
pi = np.pi

res = 256;   # wavefront / SLM resolution
abberationRes = res/4;   # resolution of scrambling operation
poi = res/2+1; # point of interest

phase = np.zeros((res,res));

#rng(1500);  # introduce an abberation to the wavefront
#abb = double(rand(abberationRes)<.5);
# create a matrix abb with random 0 and pi's 
abb = rand(abberationRes, abberationRes)
abb[abb<0.5]=0
abb[abb>0]=np.pi

abb = np.kron(abb,np.ones((res/abberationRes,res/abberationRes)));

field = np.exp(1j*(phase+abb))/res
farfield = abs(fftshift(fft2(ifftshift(field))/res**2))**2; # should be blurred
#figure(2);imagesc(farfield.**.5)
plt.figure(2)
ax = plt.gca()
ax.imshow(farfield**0.5)
plt.show(block=False)

# begin with making 
R0 = .1;                    # percent of pixels to change at beginning
REND = .01;                # percent of pixels to chang eat end
population = 100;           # number of trials per iteration
optRes = abberationRes;     # super-pixel resolution
n = 2000;                   # total number of iterations
lmbda = 300;               # dropoff of exponential to determine R
cost = np.zeros((population));            # initialize cost array for speed
randTseeds = np.round((res**4)*rand(n));  # creat random 'Breeder' seeds
randpopseeds =np.round((res**4)*rand(population)); # create seeds for population
initial = np.zeros((optRes,optRes));                    # initial guess replaced with offspring
ratio = .03;               # ratio of best population samples to cho0se from
for i in range(n): #= 1:n
    print i
    #rng(randTseeds(i))                  # seed random number generator
    np.random.seed(seed = int(randTseeds[i])) 
    #Ton = double(rand(optRes)<.5);      # Make binary breeder function T
    Ton = np.where(rand(optRes,optRes)<.5,1,0);      # Make binary breeder function T
    Toff = np.ones((optRes,optRes)) - Ton;
    start_idx = int ( ratio*population )
    randpopseeds[start_idx:] = np.round(res**2.*rand(population-start_idx)); # replace worst population with new tries
    R = (R0-REND)*np.exp(-1j/lmbda)+REND;  
    for j in range(population):# = 1:population
        # use seed to make pupulation patterns
        #print 'seed',randpopseeds[j]
        np.random.seed(seed=int(randpopseeds[j]));
        randpixels = np.floor((optRes**2)*rand(np.round(R*optRes**2)));
        randpixvals = 2*pi*rand(len(randpixels));
        np.random.seed(seed=int(randpopseeds[j]))
        randpat = initial;
        sh = randpat.shape
        randpat.shape = (1, randpat.size)
        #print type(randpat),randpat.shape, randpixvals.shape, randpixels.shape
        #randpat[1] = 0  
        randpat[0,randpixels.astype(int)] = randpixvals;
        randpat.shape=sh
        # test the population pattern
        randpat = np.kron(randpat,np.ones((res/optRes,res/optRes)));      
        randfield = np.exp(1j*(randpat+phase+abb));
        farfield = abs(fftshift(fft2(ifftshift(randfield))/res**2))**2;
        # assign a cost value to that pattern
        #cost(j) = sum(sum(farfield(poi-3:poi+3,poi-3:poi+3)));  ## using an 11x11 area as the target
        cost[j] = farfield[poi,poi];  ## using an 11x11 area as the target
        
    # sort the cost values for this population and keep pick a fraternal
    # and maternal setting from the best ones

    sortedcost = np.sort(cost);
    sortedcost[:]= sortedcost[::-1]
    index = np.argsort(cost)
    index[:]=index[::-1]
    #print sortedcost
    #print index
    #sortedcost
#     if sortedcost(1) > .95;
#         rng(randpopseeds(index(1)));
#         randpixels = round(1+(optRes**2-1)*rand(round(R*optRes**2),1));
#         randpixvals = 2*pi*rand(length(randpixels),1);
#         rng(randpopseeds(index(1)))
#         randpat = initial;
#         randpat(randpixels) = randpixvals;
#         randpat = kron(randpat,ones(res/optRes));
#         initial = randpat;
#         break
#     end
    # randomly choose from top ratio*100#
    k = 1;
    #newMother = index(k);
    #newFather = index(k+1);
    newMother = index[np.floor(round(ratio*population)*rand(1)).astype(int)];
    newFather = index[np.floor(round(ratio*population)*rand(1)).astype(int)];
#     if newMother==newFather
#         newFather = index(round(1+(round(ratio*population)-1)*rand(1)));
#     end
    while(randpopseeds[newMother]==randpopseeds[newFather]):
        k = k+1;
        newFather = index[k];

    
    print [sortedcost[newMother], sortedcost[newFather]]
    
    # generate the maternal and paternal patterns from the seed
    np.random.seed(seed=int(randpopseeds[newMother]));
    randpixels = np.floor((optRes**2)*rand(round(R*optRes**2)));
    randpixvals = 2*pi*rand(len(randpixels));
    np.random.seed(seed=int(randpopseeds[newMother]))
    randpat = initial;
    randpat.ravel()[randpixels.astype(int)] = randpixvals;
    # use the binary breeder matrix T_on to take a linear subset of the maternal
    # pattern
    MotherPat = Ton*randpat;
    
    np.random.seed(seed=int(randpopseeds[newFather]));
    randpixels = np.floor((optRes**2)*rand(round(R*optRes**2)));
    randpixvals = 2*pi*rand(len(randpixels));
    np.random.seed(seed=int(randpopseeds[newFather]))
    randpat = initial;
    randpat.ravel()[randpixels.astype(int)] = randpixvals;
    # use the binary  breeder matrix T_off to take a linear subset of the maternal
    # pattern
    FatherPat = Toff*randpat;
    
    #move best random population seeds to front. The latter will be
    #replaced with new guesses
    bestrandseeds = randpopseeds[index[:round(ratio*population)]];
    randpopseeds[:len(bestrandseeds)] = bestrandseeds;
    
    # replace the initial guess with the offspring
    initial = FatherPat+MotherPat;
    progress_pat = np.kron(initial,np.ones((res/optRes,res/optRes)));      
    field = np.exp(1j*(progress_pat+phase+abb))
    field = (abs(fftshift(fft2(ifftshift(field))/res**2))**2)
    plt.figure(1)
    ax = plt.gca()
    ax.imshow(field)
    plt.title('i: %d'%i)
    plt.show(block=False)
    plt.draw()

finalField = np.exp(1j*(np.kron(initial,np.ones((res/optRes,res/optRes)))+phase+abb));
imagesc(abs(fftshift(fft2(ifftshift(finalField))/res**2))**2)
plt.figure(1)
ax = plt.gca()
ax.imshow(finalField**0.5)
plt.show()
