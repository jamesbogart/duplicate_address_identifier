###this file can be used to re-assign addresses which were caught as duplicates in separate tests
### and therefore assigned different IDs. This script will re-assign the lone duplicate so that it is associated
### with the other duplicates that point to that specific address



import pandas as pd
testfile = r'M:\08_Geography\Address Duplicate Script\output\33003_finaltable_QC.csv'

finaltable = pd.read_csv(testfile,dtype='object')
finaltable.set_index('MAFID',inplace=True)
print(len(finaltable.drop_duplicates(subset=['Dupe_ID'],keep=False)))
unique = finaltable.drop_duplicates(subset=['Dupe_ID'], keep=False)
unique['MAFID'] = unique.index
unique = unique[['MAFID','LinkedMAFIDs','Dupe_ID']]
def reassignID(row):
    mafs = row.LinkedMAFIDs.split(',')
    for m in mafs:
        if row.MAFID == m:
            continue
        else:
            return m

unique['MAFLINK'] = unique.apply(reassignID,axis=1)
print(len(unique[unique.MAFID == unique.MAFLINK]))
print('***********')
unique.rename(columns={'MAFID':'MAFID_orig','MAFLINK':'MAFID'}, inplace=True)
unique.set_index('MAFID',inplace=True)
unique.update(finaltable.Dupe_ID)
unique.reset_index(inplace=True,drop=True)
unique.rename(columns={'MAFID_orig':'MAFID'},inplace=True)
unique = unique[['MAFID','Dupe_ID']]
unique.set_index('MAFID',inplace=True)
finaltable.update(unique)
print(unique)
print(len(finaltable.drop_duplicates(subset=['Dupe_ID'],keep=False)))

    

loneDupes = finaltable.drop_duplicates(subset=['Dupe_ID'], keep=False)
if len(loneDupes) > 0:
    loneDupes['MAFID'] = loneDupes.index
    loneDupes = loneDupes[['MAFID','LinkedMAFIDs','Dupe_ID']]
    def reassignID(row):
        mafs = row.LinkedMAFIDs.split(',')
        for m in mafs:
            if row.MAFID == m:
                continue
            else:
                return m

    loneDupes['MAFLINK'] = loneDupes.apply(reassignID,axis=1)
    loneDupes.rename(columns={'MAFID':'MAFID_orig','MAFLINK':'MAFID'}, inplace=True)
    loneDupes.set_index('MAFID',inplace=True)
    loneDupes.update(finaltable.Dupe_ID)
    loneDupes.reset_index(inplace=True,drop=True)
    loneDupes.rename(columns={'MAFID_orig':'MAFID'},inplace=True)
    loneDupes = loneDupes[['MAFID','Dupe_ID']]
    loneDupes.set_index('MAFID')
    finaltable.update(loneDupes)
