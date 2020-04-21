class Object(object):
    pass

def splitUsers(users):  #here api support max start 15
    k, modK = divmod(len(users), 15)
    uSplits = []
    uTab = users.to_numpy()

    for i in range(k):
        iStart = 15 * i
        iEnd = (15 * (i + 1))
        uSplits.append(uTab[iStart:iEnd])
    if (modK > 0):
        iStart = len(users) - modK
        iEnd = len(users)
        uSplits.append(uTab[iStart:iEnd])

    return uSplits

def splitParkings(dataframe): #max dest  is 100 in request
    k2, modK2 = divmod(len(dataframe), 100)
    pSplits = []
    pTab = dataframe.to_numpy()
    for i in range(k2):
        iStart = 100 * i
        iEnd = (100 * (i + 1))
        pSplits.append(pTab[iStart:iEnd])
    if (modK2 > 0):
        iStart = len(dataframe) - modK2
        iEnd = len(dataframe)
        pSplits.append(pTab[iStart:iEnd])
    return  pSplits