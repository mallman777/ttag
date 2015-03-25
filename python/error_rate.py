import numpy as np
import operator as op
def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

# n is length of message
# e is error rate
err_list = [0.8, 0.08, 0.04, 0.03, 0.02, 0.01, 0.001]
# 2 photons, up to 2 errors
err2 = err_list[0]**2 + \
       2*err_list[0]*err_list[1] + \
       2*err_list[0]*err_list[2] + err_list[1]*err_list[1]

err3 = err_list[0]**3 + \
       3*err_list[0]*err_list[1] + \
       3*err_list[0]**2 *err_list[2] + 3 * err_list[0]*err_list[1]**2 + \
       err_list[1]**3 + 6 * err_list[0]*err_list[1]*err_list[2]
       
def calc_error(bits_symbol,e,redundancy):
    #print e
    n=2**bits_symbol - 1
    #  6*k = n/k * redundancy * 2 * n   
    k = n*(redundancy / 3.)**0.5
    err_thresh = int( (n-k)/2.)
    prev = (1.-e)**n
    #print 'prev',prev
    success = [prev]
    for r in range(n+1):
        prev = prev * (n-r)/(r+1) * e / (1.-e)
        success.append(prev)
    success = np.array(success)
    err = 1-success.cumsum()[0:(n+1)/2]
    return err,err_thresh

#print calc_error(7,0)
plt.clf()
for loop in range(5,6):
    errors = []
    for e in np.arange(0,0.21,0.01):
        err,err_thresh = calc_error(loop,e,redundancy = 1)
        errors.append([e, err[err_thresh]])
    errors = np.array(errors)
    plt.plot(errors[:,0],errors[:,1],label='%d'%loop)

err,err_thresh=calc_error(6,0.2, redundancy = 1)    
"""
#  look at success at sending 1 symbol
for n in range(1,64,2):
    plist = []
    for r in range(n+1):
        plist.append( ncr(n,r) * (e**(n-r)) * (1.-e)**(r))
    plist2=[]
    for r in range(n+1):
        plist2.append( ncr(n,r) * (e**(r)) * (1.-e)**(n-r))

    plist = np.array(plist)
    plist2 = np.array(plist2)

    #print plist 
    #print 0.3*63*(0.7)**62
    print n,plist.cumsum()[(n-1)/2]
    print n,plist2.cumsum()[(n-1)/2]
"""
# 5bit errors:
err_list =  [0.853, 0.077, 0.0296]
