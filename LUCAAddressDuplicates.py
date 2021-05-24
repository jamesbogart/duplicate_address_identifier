from xlrd import XLRDError
import pandas as pd
import csv
import numpy as np
import Tkinter
import tkFileDialog
import os
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)

#this turns off the 'set_copy_warning' bug that occurs when assigning a column from a selection of data using a function
pd.set_option('mode.chained_assignment', None)

#simple GUI window for selection folder paths
root = Tkinter.Tk()
root.withdraw() #use to hide tkinter window

currdir = os.getcwd()
while True:
    lucasubmissions = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select directory to LUCA participant returns folder (likely L:/incoming/ but your LUCA drive may be mapped to a different letter)')
    if lucasubmissions == '':
        print('Please select a directory for your LUCA returns')
    else:
        break

while True:
    lucalists = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select where your LUCA state address lists are located')
    if lucalists == '':
        print('Please select a directory for your LUCA address lists')
    else:
        break
lucalists = r'M:/08_Geography/Address Duplicate Script/raw state files'
while True:
    outputfolder = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select where you would like your output located')
    if outputfolder == '':
        print('Please select a directory for your output folder')
    else:
        break





#ensure selected input location contains the correct LUCA list for that state
states = ['34']
for state in states:
    statefile = lucalists+'/2020LUCA_ST{}_address_list.csv'.format(state)


        
    #This section iterates through the LUCA drive 'incoming' folder for the given state,
    #attempts to find any CSVs or XLSX files with 'changes addresses' (the instructed requirment for LUCA participants when submitting, there may be address lists submitted without this phrase in the filename)
    #if the file is password protected, this would require an additional library to handle, we in the regions do not have the permissions to install new python libraries
    #if the file is able to be opened, it will check for the 'MAFID' and 'ACTION' headers,
    #if these headers are present, these columns are appeneded to a pandas dataframe and then queried so that only the MAFID's with a 'D' or 'd' action code remain.
    #this will be used later in the code to join to the duplicate results so the user will understand which duplicate records were removed from the decennial universe in the LUCA operation
    folders = os.listdir(lucasubmissions+'\st{}'.format(state))
    ##
    print('building spreadsheet of MAFIDs with D action code in LUCA submissions for state {}...'.format(state))
    deletes_df = pd.DataFrame()
    entitiesnotincluded = []
    filesnotincluded = []
    passwordfiles = []
    entitiesadded = 0
    entitiesnotadded = 0
    for folder in folders:
        entityadded = False
        directory = lucasubmissions+'/st{}/{}/'.format(state,folder)
        for f in os.listdir(directory):
            fileadded = False
            if ('changes_address' in f)and ((f.lower().endswith('.xlsx'))or(f.lower().endswith('.xls'))):
                try:
                    df = pd.read_excel(directory+'\\'+f)
                    fileadded = True
                    entityadded = True
                except XLRDError:
                    ('NOT ADDED: entity: {}, file: {} is password protected'.format(folder,f))
                    passwordfiles.append((folder,f))
                    pass
            elif ('changes_address' not in f)and((f.lower().endswith('.xlsx'))or(f.lower().endswith('.xls'))):
                try:
                    df = pd.read_excel(directory+'\\'+f)
                    headers=list(df.columns.values)
                    headers=[str(x).lower() for x in headers]
                    headers=filter(lambda x: ('action' in str(x).lower()) or ('mafid' in str(x).lower()), headers)
                    if len(headers) > 1:
                        fileadded = True
                        entityadded = True
                    else:
                        print('NOT ADDED: entity: {}, file: {} doesnt have neccessary headers (MAFID, ACTION)'.format(folder,f))
                except XLRDError:
                    print('NOT ADDED: entity: {}, file: {} is password protected'.format(folder,f))
                    passwordfiles.append((folder,f))
                    pass

            elif ('changes_address' in f)and (f.lower().endswith('.csv')):
                fileadded = True
                entityadded = True
                df = pd.read_csv(directory+'\\'+f,dtype='object')
            elif f.lower().endswith('.csv'):
                with open(directory+'\\'+f) as c:
                    reader = csv.reader(c)
                    headers = next(reader)
                    headers=[str(x).lower() for x in headers]
                    headers=filter(lambda x: ('action' in x) or ('mafid' in x), headers)
                    if len(headers) > 1:
                        fileadded = True
                        entityadded = True
                        df = pd.read_csv(directory+'\\'+f,dtype='object')
                    else:
                        print('NOT ADDED: entity: {}, file: {} doesnt have neccessary headers (MAFID, ACTION)'.format(folder,f))
            if fileadded:
                headers = list(df.columns.values)
                cleaned_headers = []
                for i in headers:
                    if 'action' in i.lower():
                        cleaned_headers.append(i)
                    if 'mafid' in i.lower():
                        cleaned_headers.append(i)
                if len(cleaned_headers) < 2:
                    print('NOT ADDED: entity: {}, file: {} doesnt have neccessary headers (MAFID, ACTION)'.format(folder,f))
                    pass
                else:
                    df = df[cleaned_headers]
                    df.rename(columns = {cleaned_headers[0]:'MAFID',cleaned_headers[1]:'ACTION'}, inplace = True)
                    df['MAFID'] = df['MAFID'].astype(str).replace('\.0', '', regex=True)
                    df = df.replace(np.nan,'',regex=True)
                    df = df.loc[(df.ACTION == 'd') | (df.ACTION == 'D')]
                    print('added entity: {}, file: {}'.format(folder,f))
                    deletes_df = deletes_df.append(df,ignore_index=False)

            else:
                filesnotincluded.append((folder,f))
        if entityadded == False:
            entitiesnotadded += 1
            entitiesnotincluded.append(folder)
        else:
            entitiesadded += 1

    deletes_df.to_csv(outputfolder+'/{}LUCADeletes'.format(state))
    del deletes_df
    del df

    print('entities which did not have a valid or un-password protected file and therefore not included:')
    pp.pprint(entitiesnotincluded)
    print('')
    print('password protected files:')
    pp.pprint(passwordfiles)
    print('')
    print('{} total participating entities in incoming folder for state {}, {} entities were successfullu added to compiled LUCA delete action table, {} entities could not be added (see list above)'.format(entitiesnotadded+entitiesadded,state,entitiesadded,entitiesnotadded))
    print('')
    print('LUCA submissions loaded. Generating duplicate tables...') 
##

    ###below functions are used to format address strings to keep them uniform for duplicate comparison purposes
    def textreplace(x):
        #matches in MatchesCase1 are checked for presence at beginning of streetname or in the middle with spaces on either side 
        #matches in MatchesCase2 are checked for only at the end of a street name
        MatchesCase1 = {'FIRST':'1ST',
                   'SECOND':'2ND',
                   'THIRD':'3RD',
                   'FOURTH':'4TH',
                   'FIFTH':'5TH',
                   'SIXTH':'6TH',
                   'SEVENTH':'7TH',
                   'EIGTH':'8TH',
                   'NINTH':'9TH',
                   'TENTH':'10TH',
                   'SAINT':'ST',
                   'HIGHWAY':'HWY',
                   'STATE HWY':'',
                   'STATE RD':'',
                   'CO RD':'',
                   'ROUTE':'RTE',
                   'RTE':'',
                   'HWY':'',
                   'US':''}
        for key,value in MatchesCase1.items():
            x = re.sub(r'(?<!\S)'+key+r'(?!\S)', value, x)
            
        MatchesCase2 = {'COVE':'CV','RIDGE':'RDG'}
        
        for key,value in MatchesCase2.items():
            x = re.sub(key+r'$', value, x)
            
        return x

    ##
    ##def replaceandcorrect(row):
    ##    """
    ##       similar to the function above, however also returns a value for the 'corrections' column which would allow the user
    ##       optionally output a table of all the records that have been corrected with the following replacements to QC.
    ##    """
    ##    
    ##    if row['STREET REFORMAT'].endswith(' COVE'):
    ##        return pd.Series((row['STREET REFORMAT'].replace(' COVE',' CV'),1))
    ##    if row['STREET REFORMAT'].endswith(' RIDGE'):
    ##        return pd.Series((row['STREET REFORMAT'].replace(' RIDGE',' RDG'),1))
    ##    else:
    ##        return pd.Series((row['STREET REFORMAT'],0))

    def nospace(row):
        if pd.isnull(row.HOUSENUMBER):
            if pd.isnull(row['APARTMENT UNIT']):
                addnospace = row.STREETNAME + row.ZIP + "_" + row.GEOID
            else:
                addnospace = row.STREETNAME + row['APARTMENT UNIT'] + row.ZIP + "_" + row.GEOID
        elif pd.notnull(row['APARTMENT UNIT']):
            if re.search(r'[0-9]$',row.HOUSENUMBER) and re.search(r'^[0-9]',row.STREETNAME):
                addnospace = row.HOUSENUMBER +'|'+ row.STREETNAME + row['APARTMENT UNIT'] + row.ZIP + "_" + row.GEOID
            else:
                addnospace = row.HOUSENUMBER + row.STREETNAME + row['APARTMENT UNIT'] + row.ZIP + "_" + row.GEOID
        else:
            if pd.notnull(row.HOUSENUMBER) and re.search(r'[0-9]$',row.HOUSENUMBER) and re.search(r'^[0-9]',row.STREETNAME):
                addnospace = row.HOUSENUMBER +'|'+  row.STREETNAME + row.ZIP + "_" + row.GEOID
            else:
                addnospace = row.HOUSENUMBER + row.STREETNAME  + row.ZIP + "_" + row.GEOID
        addnospace = addnospace.replace(' ','')
        return addnospace
        
    def apartmentcorrect(x):
        """
            replaces apartment designator prefixes with an empty string
        """
            
        for designator in ['APT','LOT','UNIT','STE','TRLR']:
            if pd.notnull(x) and x.startswith('_'+designator):
                x = x.replace(designator,'')
                return x
        return x
    
    ###we want a pipe delimter between records that end with numbers in the housenumber and start with numbers in the streetname
    def aptnospace(row):
        if pd.notnull(row['APARTMENT UNIT']):
            if re.search(r'[0-9]$',row.HOUSENUMBER) and re.search(r'^[0-9]',row.STREETNAME):
                addnospace = row.HOUSENUMBER +'|' + row.STREETNAME + row.APT_REFORMAT + row.ZIP + "_" + row.GEOID
            else:
                addnospace = row.HOUSENUMBER +  row.STREETNAME + row.APT_REFORMAT + row.ZIP + "_" + row.GEOID
        else:
            if re.search(r'[0-9]$',row.HOUSENUMBER) and re.search(r'^[0-9]',row.STREETNAME):
                addnospace = row.HOUSENUMBER +'|' + row.STREETNAME + row.ZIP + "_" + row.GEOID
            else:
                addnospace = row.HOUSENUMBER + row.STREETNAME + row.ZIP + "_" + row.GEOID
        addnospace = addnospace.replace(' ','')
        return addnospace

    def characterduplicate(row):
        if re.search(r'\d',row.STREETNAME):
            charaddress = np.nan
        else:
            if pd.isnull(row.HOUSENUMBER) and pd.isnull(row.APT_REFORMAT):
                charaddress = sorted(row.STREETNAME.replace(' ','').replace('_','').replace('|',''))
            elif pd.isnull(row.HOUSENUMBER):
                charaddress = sorted(row.STREETNAME + row.APT_REFORMAT).replace(' ','').replace('_','').replace('|','')
            elif pd.notnull(row.APT_REFORMAT):
                charaddress = ''.join(sorted((row.HOUSENUMBER + row.STREETNAME + row.APT_REFORMAT).replace(' ','').replace('_','').replace('|','')))
                #charaddress = ''.join(sorted(row.APT_NOSPACE.replace('_','')))
            else:
                charaddress = ''.join(sorted((row.HOUSENUMBER + row.STREETNAME ).replace(' ','').replace('_','').replace('|','')))
                #charaddress = ''.join(sorted(row.ADD_NOSPACE.replace('_','')))
        return charaddress


    def createduplicatetable(column):
        """
            input paramter is a column of the dataframe to be checked for duplicate values.
            Creates a temp dataframe that selects the rows with values that appear more than once (are duplicates)
            Adds a column ('COUNT') to the dataframe that contains the number of occurances of that value
        """   
            
        temp = data.loc[data[column].map(data[column].value_counts()) > 1]
        temp['COUNT']= temp[column].map(temp[column].value_counts())
        #temp = temp[[column,'COUNT','MAFID']]
        temp.sort_values(by=column, inplace=True)
        temp.to_csv('{}/{}duplicatetable{}{}.csv'.format(outputfolder,column,state,county))
        return temp

    #read through the LUCA list and build python list of all unique counties in COUNTYFP column for iterating
    print('Creating list of counties within state:{} '.format(state))
##    counties_list = set()
##
##    chunks = pd.read_csv(statefile,chunksize=100000,usecols=['STATEFP','COUNTYFP'],dtype='object')
##    for chunk in chunks:
##        chunk = chunk[(chunk['STATEFP'] == state) & chunk['COUNTYFP'].notnull()]
##        counties =  list(chunk.COUNTYFP.unique())
##        for county in counties:
##            counties_list.add(county)
##
##    counties_list = sorted(counties_list)
    counties_list = ['027']
        




       
    ## this section loops through the counties in the compiled list (neccessary because most states address lists' are too big to load fully into memory)
    ## 'STREET REFORMAT' and 'APT REFORMAT' columns are created to hold the street name and apartment unit designation after they have been formatted for unifomrity
    statedf = pd.DataFrame()
    for county in counties_list:
        print('Begin Gathering duplicates for county number {}'.format(county))
        datacolumns = ['COUNTYFP','GQ_FLAG','MAFID','CITY_STYLE','GEOID','HOUSENUMBER','STREETNAME','APARTMENT UNIT','ZIP','LAT','LONG']
        chunks = pd.read_csv(statefile,chunksize=100000,dtype='object',usecols=datacolumns)
        data = []
        print('loading address list for county: {}'.format(county))
        for chunk in chunks:
            data.append(chunk[(chunk.COUNTYFP == county) & (chunk.GQ_FLAG.isnull()) & (chunk.CITY_STYLE == 'Y')])
        data = pd.concat(data)
        data.drop(['COUNTYFP','GQ_FLAG','CITY_STYLE'],inplace=True,axis=1)
        print('address list loaded...')
        print('formatting columns...')
        print('')
        data = data[data['STREETNAME'] != 'NO KNOWN ADDRESSES IN THIS BLOCK']
        data.HOUSENUMBER = data.HOUSENUMBER.fillna('')
        data[['APARTMENT UNIT','HOUSENUMBER' ,'STREETNAME']] = data[['APARTMENT UNIT','HOUSENUMBER' ,'STREETNAME']].apply(lambda x : x.str.upper()) 
        #data['CORRECTION'] = 0
        data['FULLADDRESS'] = data.HOUSENUMBER.fillna('') + " " + data.STREETNAME.fillna('') + " " + data['APARTMENT UNIT'].fillna('') + " " + data.ZIP.fillna('') + "_" + data.GEOID.fillna('')
        data['ADD_NOSPACE'] = data.apply(nospace, axis=1)    
        data['STREET REFORMAT'] = data['STREETNAME'].apply(textreplace)
        data['STREET REFORMAT'] = data['STREET REFORMAT'].apply(lambda x: x.lstrip())
        #data[['STREET REFORMAT','CORRECTION']] = data[['STREET REFORMAT','CORRECTION']].apply(replaceandcorrect, axis=1)
        #unique_street = data[~data['STREET REFORMAT'].duplicated(keep=False)]
        #corrections = data.loc[data['CORRECTION'] == 1,['MAFID','CORRECTION']]
        data['APT_REFORMAT'] = data['APARTMENT UNIT'].apply(lambda x: '_'+(x) if pd.notnull(x) else x)
        data['APT_REFORMAT'] = data['APT_REFORMAT'].apply(apartmentcorrect)
        data['APT_NOSPACE'] = np.nan
        data.loc[pd.notnull(data['APARTMENT UNIT']),'APT_NOSPACE'] = data[pd.notnull(data['APARTMENT UNIT'])].apply(aptnospace,axis=1)
        data['FULLCHARS'] = data.apply(characterduplicate,axis=1)
        data['HNLEN'] = data.HOUSENUMBER.apply(lambda x: len(x))

    ### there are 6 separate formatting checks for duplicate values, each resulting in its own dataframe:
    ### 1. Full Address and GEOID without formatting = HOUSENUMBER + " " + STREETNAME + " " +APARTMENT UNIT+ " " + ZIP + "_" + GEOID
    ### 2. The same address string above but with all spaces removed (If there was Apple Tree Ln. and Appletree Ln, they will be found as duplicates)
    ### 3. Apartment duplcates with unit prefixes removed ('UNIT 1' and 'APT 1' at the same address would be found as duplicate)= HOUSENUMBER + STREETNAME + APT_REFORMAT + ZIP + "_" + GEOID
    ### 4. Address duplicates that may have diff zip but same Geocode = HOUSENUMBER + STREETNAME + APT_REFORMAT + "_"+GEOID
    ### 5. Address duplicates that may have diff geocode = HOUSENUMBER + STREETNAME + APT_REFORMAT + ZIP
    ### 6. Check columns that come out of reformatting functions above (use 'reformat' columns) =  HOUSENUMBER + STREET REFORMAT + APT_REFORMAT+ ZIP
        
        print('generating duplicate tables...')
        print('')
        if 'DupeID_Increment' not in locals():
            DupeID_Increment = 1
        fulladdressduptable = createduplicatetable('FULLADDRESS')
        fulladdressduptable['DuplicateCheck'] = 'Full Address'
        fulladdressduptable['Dupe_ID'] = fulladdressduptable.groupby('FULLADDRESS', sort=False).grouper.group_info[0] + DupeID_Increment
        fulladdressduptable['LinkedMAFIDs'] = fulladdressduptable.groupby('FULLADDRESS')['MAFID'].transform(lambda x: ','.join(x))
        DupeID_Increment += len(fulladdressduptable)

        nospacetable = createduplicatetable('ADD_NOSPACE')
        nospacetable['DuplicateCheck'] = 'Address NoSpace'
        nospacetable['Dupe_ID'] = nospacetable.groupby('ADD_NOSPACE', sort=False).grouper.group_info[0] + DupeID_Increment
        nospacetable['LinkedMAFIDs'] = nospacetable.groupby('ADD_NOSPACE')['MAFID'].transform(lambda x: ','.join(x))
        DupeID_Increment += len(nospacetable)    

        aptduptable = createduplicatetable('APT_NOSPACE')
        aptduptable['DuplicateCheck'] = 'Apartment Prefix'
        aptduptable['Dupe_ID'] = aptduptable.groupby('APT_NOSPACE', sort=False).grouper.group_info[0] + DupeID_Increment
        aptduptable['LinkedMAFIDs'] = aptduptable.groupby('APT_NOSPACE')['MAFID'].transform(lambda x: ','.join(x))
        DupeID_Increment += len(aptduptable)

        data['WRONG ZIP'] = data.HOUSENUMBER.fillna('')+data.STREETNAME.fillna('')+data.APT_REFORMAT.fillna('')+ "_"+data.GEOID.fillna('')
        data['WRONG ZIP'] = data['WRONG ZIP'].str.replace(' ','')
        wrongziptable = createduplicatetable('WRONG ZIP')
        wrongziptable['DuplicateCheck'] = 'Different Zip'
        wrongziptable['Dupe_ID'] = wrongziptable.groupby('WRONG ZIP', sort=False).grouper.group_info[0] + DupeID_Increment
        wrongziptable['LinkedMAFIDs'] = wrongziptable.groupby('WRONG ZIP')['MAFID'].transform(lambda x: ','.join(x))
        DupeID_Increment += len(wrongziptable)
        
        data['WRONG BLOCK'] = data.HOUSENUMBER.fillna('') +data.STREETNAME.fillna('') + data.APT_REFORMAT.fillna('') + data.ZIP.fillna('')
        data['WRONG BLOCK'] = data['WRONG BLOCK'].str.replace(' ','')
        wrongblocktable = createduplicatetable('WRONG BLOCK')
        wrongblocktable['Dupe_ID'] = wrongblocktable.groupby('WRONG BLOCK', sort=False).grouper.group_info[0] + DupeID_Increment
        wrongblocktable['LinkedMAFIDs'] = wrongblocktable.groupby('WRONG BLOCK')['MAFID'].transform(lambda x: ','.join(x))
        wrongblocktable['DuplicateCheck'] = 'Different Block'
        DupeID_Increment += len(wrongblocktable)    

        data['WRONGSTREETFORMAT'] = data.HOUSENUMBER.fillna('') + data['STREET REFORMAT'].fillna('') + data.APT_REFORMAT.fillna('') + data.ZIP.fillna('')
        data['WRONGSTREETFORMAT'] = data['WRONGSTREETFORMAT'].str.replace(' ','')
        streetformattable = createduplicatetable('WRONGSTREETFORMAT')
        streetformattable['Dupe_ID'] = streetformattable.groupby('WRONGSTREETFORMAT', sort=False).grouper.group_info[0] + DupeID_Increment    
        streetformattable['DuplicateCheck'] = 'Different Formatting'
        streetformattable['LinkedMAFIDs'] = streetformattable.groupby('WRONGSTREETFORMAT')['MAFID'].transform(lambda x: ','.join(x))
        DupeID_Increment += len(streetformattable)

        data['HN_NUM'] = data['HOUSENUMBER'].str.replace(r'\D|\s', '')
        charformattable1 = data.groupby(['FULLCHARS','GEOID','HN_NUM']).filter(lambda x: len(set(x['HNLEN']))>1 and x.HOUSENUMBER.str.contains('[A-Z]').any() and (len(set(x.ZIP))==1))
        charformattable1['Dupe_ID'] = charformattable1.groupby('FULLCHARS', sort=False).grouper.group_info[0] + DupeID_Increment
        DupeID_Increment += len(charformattable1)
        charformattable1['LinkedMAFIDs'] = charformattable1.groupby('FULLCHARS')['MAFID'].transform(lambda x: ','.join(x))
        charformattable1['DuplicateCheck'] = 'CharMatch'
        charformattable2 = data.groupby(['FULLCHARS','GEOID','HN_NUM']).filter(lambda x:len(set(x['HNLEN']))>1 and x.HOUSENUMBER.str.contains('[A-Z]').any())
        charformattable2['Dupe_ID'] = charformattable2.groupby('FULLCHARS', sort=False).grouper.group_info[0] + DupeID_Increment
        charformattable2['LinkedMAFIDs'] = charformattable2.groupby('FULLCHARS')['MAFID'].transform(lambda x: ','.join(x))

        DupeID_Increment += len(charformattable2)
        charformattable2['DuplicateCheck'] = 'CharMatch DiffZip'
        charformattable3 = data.groupby(['FULLCHARS','ZIP','HN_NUM']).filter(lambda x: len(set(x['HNLEN']))>1 and x.HOUSENUMBER.str.contains('[A-Z]').any())
        charformattable3['Dupe_ID'] = charformattable3.groupby('FULLCHARS', sort=False).grouper.group_info[0] + DupeID_Increment
        charformattable3['LinkedMAFIDs'] = charformattable3.groupby('FULLCHARS')['MAFID'].transform(lambda x: ','.join(x))

        DupeID_Increment += len(charformattable3)
        charformattable3['DuplicateCheck'] = 'CharMatch DiffGEOID'
        
        cols1 = ['MAFID','GEOID','HOUSENUMBER','STREETNAME','APARTMENT UNIT','APT_REFORMAT','ZIP','LAT','LONG']
        data = data[cols1]
        
        duplicatetables = [fulladdressduptable, nospacetable, aptduptable, wrongziptable, wrongblocktable, streetformattable, charformattable1, charformattable2, charformattable3]

        print('joining duplicate tables...')
        finaltable = reduce(lambda df, dupetable: df.combine_first(dupetable.set_index('MAFID')),
                            duplicatetables,
                            data.set_index('MAFID')).reset_index()

        finaltable = finaltable[finaltable.DuplicateCheck.notnull()]

        for table in duplicatetables:
            del table
        del data

        finaltable.set_index('MAFID',inplace=True)
        deletes_df = pd.read_csv(outputfolder+'/{}LUCADeletes'.format(state),dtype='object',usecols=['MAFID','ACTION'])
        deletes_df.set_index('MAFID',inplace=True)
        finaltable = finaltable.join(deletes_df, how='left')
        del deletes_df    


        finaltable = finaltable[['GEOID','HOUSENUMBER','STREETNAME','APARTMENT UNIT','APT_REFORMAT','ZIP','LAT','LONG','ACTION','DuplicateCheck','Dupe_ID','LinkedMAFIDs']]
        finaltable.sort_values(by=['HOUSENUMBER','STREETNAME','APT_REFORMAT'],inplace=True)
        finaltable.drop('APT_REFORMAT',inplace=True, axis=1)
        finaltable.Dupe_ID = finaltable.Dupe_ID.astype(str).replace('\.0', '', regex=True)
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
            loneDupes.set_index('MAFID',inplace=True)
            finaltable.update(loneDupes)
        finaltable.drop('LinkedMAFIDs',inplace=True, axis=1)
        #finaltable.to_csv(outputfolder+'/{}_finaltable_QC.csv'.format(state+county))
        
        print('County: {} duplicate table exported to {}/{}_finaltable.csv'.format(county,outputfolder,state+county) )
        print('*******************************************************************************')
        print('')
        statedf = statedf.append(finaltable)

        charformattable1.to_csv('{}/{}duplicatetable{}{}.csv'.format(outputfolder,'charformat1',state,county))
        charformattable2.to_csv('{}/{}duplicatetable{}{}.csv'.format(outputfolder,'charformat2',state,county))
        charformattable3.to_csv('{}/{}duplicatetable{}{}.csv'.format(outputfolder,'charformat3',state,county))

    print('Generating statewide duplicate list...')    
    #statedf.to_csv(outputfolder+'/{}_finaltable.csv'.format(state))
    print('Duplicate tables for state: '+state+' completed. Press ENTER to exit...')








    

    
    
    
    



    

    
    
    
    
