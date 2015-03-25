import numpy


filename = 'data.txt'

def load(filename, width):
    # loop to check if the file loads properly
    cnt_data=0
    bad_width=True
    while bad_width:
        # loop to check if file exists
        cnt = 0
        bad = True
        while bad:
            try:
                data = np.loadtxt(filename)
                bad = False
            except:
                cnt = cnt+1
                if cnt>10:
                    send_msg('Can not load %s'%filename)
                    return False
                else:
                    bad = True
        if data.shape[1] != width
            cnt_width = cnt_width + 1
            if cnt_width>10:
                send_msg('Can not load data from  %s with width %d'%(filename,width))
                return False
        else:
            bad_width = True

    return data

def check():
    data = load(filename,11)
    cutbool = (data[-1,0] - data [:,0])<1.0
    counts = data[cutbool,:].sum(axis=0)
    bad_list = np.where(counts[3,:]==0, np.arange(8))
    return bad_list
