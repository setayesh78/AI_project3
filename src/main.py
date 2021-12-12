import math
import copy
import time

res = []
rowsDomains={}
colsDomains={}
n=0
rowsAssignment={}
colsAssignment={}


##CONFIG
PROPAGATION = 'MAC' # FC or MAC
st='puzzle5'

##


class Tuple:
    def __init__(self, content):
        self.content = content
    

    def __eq__(self, other): 
        return self.content == other.content

    def EqualityOfZO(self):
        return self.content.count('1') == self.content.count('0')
    
    def ValidationOfPositionsZO(self):
        return not(self.content.count('111')!=0 or self.content.count('000')!=0)
        

    
def genBin(s):
    if '-' in s:
        s1 = s.replace('-','0',1) #only replace once
        s2 = s.replace('-','1',1) #only replace once
        genBin(s1)
        genBin(s2)
    else:
        t = Tuple(s)
        if t.ValidationOfPositionsZO() and t.EqualityOfZO():
            res.append(t)
    

def revise(Xi,Xj,rowDict,colDict):
    revised = False
    XjDomains = copy.deepcopy(rowsDomains[Xj[1]])
    if Xj[0]==1:
        if Xj[1] in rowsAssignment:
            XjDomains = copy.deepcopy([rowsAssignment[Xj[1]]])
        elif Xj[1] in rowDict:
            for item in rowDict[Xj[1]]:
                XjDomains.remove(item)
    if Xj[0]==0:
        XjDomains = copy.deepcopy(colsDomains[Xj[1]]) 
        if Xj[1] in colsAssignment:
            XjDomains = copy.deepcopy([colsAssignment[Xj[1]]])
        elif Xj[1] in colDict:
            for item in colDict[Xj[1]]:
                XjDomains.remove(item)        
    if Xi[0]==1:
        for item in rowsDomains[Xi[1]]:
            flag = False
            if Xj[0]==1:
                for jitem in XjDomains:
                    if item != jitem:
                        flag = True
            elif Xj[0]==0:
                for jitem in XjDomains:
                    if item.content[Xj[1]] == jitem.content[Xi[1]]:
                        flag=True
            if not flag:
                if Xi[1] in rowDict:
                    if item not in rowDict[Xi[1]]:
                        rowDict[Xi[1]].append(item)
                else:
                    rowDict[Xi[1]] = [item]
                revised = True
    
    else:
        for item in colsDomains[Xi[1]]:
            flag = False
            if Xj[0]==0:
                for jitem in XjDomains:
                    if item != jitem:
                        flag = True
            elif Xj[0]==1:
                for jitem in XjDomains:
                    if item.content[Xj[1]] == jitem.content[Xi[1]]:
                        flag=True
            if not flag:
                if Xi[1] in colDict:
                    if item not in colDict[Xi[1]]:
                        colDict[Xi[1]].append(item)
                else:
                    colDict[Xi[1]] = [item]     
                revised = True
    return revised,rowDict,colDict



def AC3(queue):
    rowDict={}
    colDict={}
    while len(queue)!=0:
        lst = queue.pop(0)
        Xj = lst[1]
        Xi = lst[0]
        revised,rowDict,colDict = revise(Xi,Xj,rowDict,colDict)
        if revised:
            if Xi[0]==1:
                if len(rowsDomains[Xi[1]]) == len(rowDict[Xi[1]]):
                    return False,rowDict,colDict
            if Xi[0]==0:
                if len(colsDomains[Xi[1]]) == len(colDict[Xi[1]]):
                    return False,rowDict,colDict
            if Xi[0] == 1:
                for item in rowsDomains:
                    if item not in rowsAssignment:
                        if Xj[0]!=1 and Xj[1]!=item: 
                            tempTuple=(1,item)
                            if tempTuple != Xi:
                                queue.append([tempTuple,Xi])
                for item in colsDomains:
                    if item not in colsAssignment: 
                        if Xj[0]!=0 and Xj[1]!=item: 
                            tempTuple=(0,item)
                            if tempTuple != Xi:
                                queue.append([tempTuple,Xi])                    
            elif Xi[0] == 0:
                for item in colsDomains:
                    if item not in colsAssignment: 
                        if Xj[0]==1 and Xj[1]!=item: 
                            tempTuple=(0,item)
                            if tempTuple != Xi:
                                queue.append([tempTuple,Xi]) 
                for item in rowsDomains:
                    if item not in rowsAssignment:
                        if Xj[0]==0 and Xj[1]!=item: 
                            tempTuple=(0,item)
                            if tempTuple != Xi:
                                queue.append([tempTuple,Xi]) 
    return True,rowDict,colDict


def selectUnassignedVariable():
    #just using MRV
    if (len(rowsDomains)!=n) or (len(colsDomains)!=n): 
        return -1,-1
    minDomain=math.inf
    row=-1
    selected=0
    for item in rowsDomains:
        if item not in rowsAssignment:
            if len(rowsDomains[item])< minDomain:
                selected = item
                minDomain = len(rowsDomains[item])
                row = 1
    for item in colsDomains:
        if item not in colsAssignment:
            # i+=1
            if len(colsDomains[item])< minDomain :
                selected = item
                minDomain = len(colsDomains[item])
                row = 0
    return row,selected



def isSafe(row,item):
    return item.ValidationOfPositionsZO() and item.EqualityOfZO()

    
def inference(row,selected,value):
    flag = False
    colDict = {} #must delete from domain
    rowDict = {} #must delete from domain   
    if PROPAGATION == 'FC':
        if row ==1:
            for item in rowsDomains:
                lst=[]
                if item not in rowsAssignment:
                    for val in rowsDomains[item]:
                        #append item that is not assign and is equal to others 
                        if value == val:
                            lst.append(val)
                    if len(lst)!=0:
                        rowDict[item] = lst
        elif row ==0:
            for item in colsDomains:
                lst=[]
                if item not in colsAssignment:
                    for val in colsDomains[item]:
                        #append item that is not assign and is equal to others 
                        if value == val:
                            lst.append(val)
                    if len(lst)!=0:
                        colDict[item] = lst

        #if we select one row we must update cols values and vice versa
        if row == 1:
            for item in colsDomains:
                if item not in colsAssignment: 
                    for val in colsDomains[item]:
                        if val.content[selected] != value.content[item]:
                            if item in colDict:
                                colDict[item].append(val)
                            else:
                                colDict[item] = [val]
        if row == 0:
            for item in rowsDomains:
                if item not in rowsAssignment: 
                    for val in rowsDomains[item]:
                        if val.content[selected] != value.content[item]:
                            if item in rowDict:
                                rowDict[item].append(val)
                            else:
                                rowDict[item] = [val]
        if len(colDict)==0 and len(rowDict)==0:
            flag = False
        else:
            flag = True


    elif PROPAGATION == 'MAC':
        queue = []
        t=(row,selected)
        if row == 1:
            for item in rowsDomains:
                if item not in rowsAssignment:
                    tempTuple=(1,item)
                    queue.append([tempTuple,t])
            for item in colsDomains:
                if item not in colsAssignment: 
                    tempTuple=(0,item)
                    queue.append([tempTuple,t])                    
        elif row == 0:
            for item in colsDomains:
                if item not in colsAssignment: 
                    tempTuple=(0,item)
                    queue.append([tempTuple,t])  
            for item in rowsDomains:
                if item not in rowsAssignment:
                    tempTuple=(1,item)
                    queue.append([tempTuple,t])
        flag,rowDict,colDict = AC3(queue)
        if len(colDict)==0 and len(rowDict)==0:
            flag = False
        else:
            flag = True        
    return flag,rowDict,colDict
        


def backTrack():

    if len(colsAssignment)==n and len(rowsAssignment)==n:
        return True
    row,selected = selectUnassignedVariable()    
    values=[]
    rowDict = {}
    colDict = {}
    if row==1:
        values = rowsDomains[selected]
    elif row==0:
        values = colsDomains[selected]
    for item in values:
        if row==1:
            rowsAssignment[selected] = item
            print("+assign to row "+str(selected)+": "+item.content)
        else:
            colsAssignment[selected] = item
            print("+assign to col "+str(selected)+": "+item.content)

        #forwardChecking and MAC
        # (inference)    
        infer,rowDict,colDict = inference(row,selected,item)        
        if infer:
            for delItem in rowDict:
                for valueItem in rowDict[delItem]:
                    rowsDomains[delItem].remove(valueItem)
                    print("removing value from row domain "+str(delItem)+": "+valueItem.content)
                if len(rowsDomains[delItem])==0:
                    rowsDomains.pop(delItem)
                
            for delItem in colDict:
                for valueItem in colDict[delItem]:
                    colsDomains[delItem].remove(valueItem)
                    print("removing value from col domain "+str(delItem)+": "+valueItem.content)
                if len(colsDomains[delItem])==0:
                    colsDomains.pop(delItem)   
        result = backTrack()
        if result:
            return result

        if row==1:
            rowsAssignment.pop(selected)
            print("-removing assigned value from row "+str(selected))

        elif row==0:
            colsAssignment.pop(selected) 
            print("-removing assigned value from col "+str(selected))

        
        for delItem in rowDict:
            for valueItem in rowDict[delItem]:
                print("adding value to row domain "+str(delItem)+": "+valueItem.content)
                if delItem not in rowsDomains:
                    rowsDomains[delItem] = [valueItem]
                else:    
                    rowsDomains[delItem].append(valueItem)
        for delItem in colDict:
            for valueItem in colDict[delItem]:
                print("adding value to col domain "+str(delItem)+": "+valueItem.content)
                if delItem not in colsDomains:
                    colsDomains[delItem] = [valueItem]
                else:    
                    colsDomains[delItem].append(valueItem)            
    return False


##
file1 = open('.\\Input\\'+st+'.txt', 'r')
##
Lines = file1.readlines()
grid = []
i=0
row=0
col=0


for line in Lines:
    l=line.strip().split()
    if i==0:
        row = int(l[0])
        col = int(l[1])
        n=row
        i+=1
    else:
        grid.append(l)
        res = []
        str1 = ""
        str1 = str1.join(l)
        genBin(str1)
        rowsDomains[i-1]=res
        i+=1

file1.close()


for i in range(0,col):
    temp=""
    for j in range(0,row):
        temp+=grid[j][i]
    res = []
    str1 = ""
    str1 = str1.join(temp)

    genBin(str1)
    colsDomains[i]=res


for item in grid:
    print(item)
    
start = time.time()    
status = backTrack()
end = time.time()
print("\n\n time")
print(end-start)
print("\n\n")
print('***************')
if status:
    if len(rowsAssignment)==n:
        for item in sorted(rowsAssignment.keys()):
            print(item,rowsAssignment[item].content) 
        print("+++++")
        for item in sorted(colsAssignment.keys()):
            print(item,colsAssignment[item].content)
else:
    print('Impossible')
