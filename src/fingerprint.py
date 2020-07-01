import numpy as np
import cv2

#TODO: need to change the way we do matrix W generation from key
def gen_W (size, key):

    assert type(key) == int
    np.random.seed(key)
    return np.random.random(size)

def gen_fp (image, L, key):

    #color channel
    if len(image.shape) == 3:
        r,g,b = cv2.split(image)
        xr = np.concatenate([np.diagonal(r[::-1,:], i)[::(2*(i % 2)-1)] for i in range(1-r.shape[0], r.shape[0])])
        xg = np.concatenate([np.diagonal(g[::-1,:], i)[::(2*(i % 2)-1)] for i in range(1-g.shape[0], g.shape[0])])
        xb = np.concatenate([np.diagonal(b[::-1,:], i)[::(2*(i % 2)-1)] for i in range(1-b.shape[0], b.shape[0])])

        Wr = gen_W((L, xr.shape[0]), key)
        Wg = gen_W((L, xg.shape[0]), key)
        Wb = gen_W((L, xb.shape[0]), key)

        wtxr = np.matmul(xr, Wr.T)
        wtxg = np.matmul(xg, Wg.T)
        wtxb = np.matmul(xb, Wb.T)

        wtxr[wtxr < np.mean(wtxr)] = 0
        wtxr[wtxr > np.mean(wtxr)] = 1
        wtxg[wtxg < np.mean(wtxg)] = 0
        wtxg[wtxg > np.mean(wtxg)] = 1
        wtxb[wtxb < np.mean(wtxb)] = 0
        wtxb[wtxb > np.mean(wtxb)] = 1

        #TODO: evaluate what to do with color channel fingerprints, concatenate?
        return wtxr #, wtxg, wtxb

    #black white channel
    else:
        x = np.concatenate([np.diagonal(image[::-1,:], i)[::(2*(i % 2)-1)] for i in range(1-image.shape[0], image.shape[0])])
        matW = gen_W((L, x.shape[0], key))
        wtx = np.matmul(x, matW.T)
        wtx[wtx < np.mean(wtx)] = 0
        wtx[wtx > np.mean(wtx)] = 1

        return wtx

def fp2text (fingerprint):

    return fingerprint.tostring()

def text2fp (text):

    return np.fromstring(text)
