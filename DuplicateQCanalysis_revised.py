### This script automates the QC of the output of the duplicate address script after QC by a geography staff member for BLQ listings


import pandas as pd
import os
import numpy as np

fps = ['Hancock_23009_Duplicates.csv',
       'Carroll_33003_Duplicates.csv',
       'Erie_36029_Duplicates_FT.csv',
       'Hancock_23009_Duplicates.csv',
       'Hartford_09003_Duplicates.csv',
       'Ocean_34029_Duplicates.csv',
       'Queens_36081_Duplicates.csv',
       'Oneida_36065_Duplicates_WA.csv',
       'Suffolk_36103_Duplicates.csv',
       'Worcester_25027_Duplicates_FT.csv'
       ]
for f in fps:
    print(f)
    fp = r'M:\08_Geography\Address Duplicate Script\QC\Analysis\{}'.format(f)
    QCfile = pd.read_csv(fp,dtype='object')
    QCfile['IN BLQ?'] = QCfile['IN BLQ?'].str.upper()
    QCfile['MAFID'] = QCfile.iloc[:,0]
    QCfile.ACTION.fillna('-',inplace=True)
    QCfile.drop_duplicates(subset=['MAFID'],inplace=True)

    allduplicates = QCfile.copy()
    total_county = len(allduplicates)
    #print('total duplicate records in county: {}'.format(total_county))

    QCfile = QCfile[pd.notnull(QCfile['IN BLQ?'])]
    qcedrecords = len(QCfile)
    qced_nolucadeletes = len(QCfile[QCfile.ACTION == '-'])
    
   # print('total records with a value in IN BLQ?: {}'.format(qcedrecords))

    print('****************************************************')
    QCtable = pd.DataFrame({'DuplicateCheck': pd.Series([], dtype='str'),
                            'County - Total Duplicate Addresses': pd.Series([], dtype='int'),
                            'County - % of Duplicate Addresses': pd.Series([], dtype='float'),
                            'QC - Total Addresses': pd.Series([], dtype='int'),
                            'QC - LUCA Deletes': pd.Series([], dtype='int'),
                            'QC - LUCA deletes in BLQ': pd.Series([], dtype='int'),
                            'QC - Addresses Not Duplicate (#)': pd.Series([], dtype='int'),
                            'QC - Addresses in BLQ': pd.Series([], dtype='int'),
                            'QC - Addresses in BLQ (%)': pd.Series([], dtype='float'),
                            'QC - Duplicate groups': pd.Series([], dtype='int'),
                            'QC - Duplicate groups - All addresses In BLQ': pd.Series([], dtype='int'),
                            'QC - Duplicate groups - All In BLQ (%)': pd.Series([], dtype='float'),
                            'QC - Duplicate groups - Only 1 Address in BLQ': pd.Series([], dtype='int'),
                            'QC - Duplicate groups - Only 1 Address in BLQ(%)': pd.Series([], dtype='float')})


    QCtable = QCtable[['DuplicateCheck',
                       'County - Total Duplicate Addresses',
                       'County - % of Duplicate Addresses',
                       'QC - Total Addresses',
                       'QC - LUCA Deletes',
                       'QC - LUCA deletes in BLQ',
                       'QC - Addresses Not Duplicate (#)',
                       'QC - Addresses in BLQ',
                       'QC - Addresses in BLQ (%)',
                       'QC - Duplicate groups',
                       'QC - Duplicate groups - All addresses In BLQ',
                       'QC - Duplicate groups - All In BLQ (%)',
                       'QC - Duplicate groups - Only 1 Address in BLQ',
                       'QC - Duplicate groups - Only 1 Address in BLQ(%)']]

    for typ in allduplicates['DuplicateCheck'].unique():
        print(typ)
        if isinstance(typ, basestring) == False:
            continue
        numonlyone = 0
        # this is dataframe of all addresses in county with this duplicate type regardless if they have been QC'd
        temp_all = allduplicates[allduplicates.DuplicateCheck == typ]
        # this is a dataframe of all address in county with this dupe type that have been QC'd
        temp_qcd = QCfile[QCfile['DuplicateCheck']==typ]
        # this is a dataframe of all the QC'd addresses that were not deleted in LUCA 
        temp_luca = temp_qcd[(temp_qcd.ACTION == '-') | ((temp_qcd['IN BLQ?']=='Y') & (temp_qcd.ACTION == 'D')) ]
        print('len temp_lucs:{}'.format(len(temp_luca)))
        #Col 1 is County - Total Duplicate Addresses for this type
        col1 = len(temp_all)
        #Col 2 is County - % of Duplicate Addresses in this type out of all duplicate addresses
        col2 = (float(col1)/float(total_county)) *100
        #col 3 is total QC'd addresses in this type
        col3 = len(temp_qcd)
        #col 4 is total luca deletes in this type
        col4 = len(temp_qcd[temp_qcd.ACTION  == 'D'])
        #col 5 is LUCA deletes that are still in BLQ in this type
        col5 = len(temp_qcd[(temp_qcd.ACTION == 'D') & (temp_qcd['IN BLQ?'] == 'Y')])
        #col 6 is for not duplicates (not duplicates, but no one seems to actually input this data in the QC sheet when there are thousands of addresses to check and little time to check the address detaisl)
        col6 = 0
        #col 7 is QC'd Addresses in BLQ
        col7 = len(temp_luca[temp_luca['IN BLQ?'].str.upper() == 'Y'])
        #col8 is % of addresses in this type within blq
        if col7 == 0:
              col8 = np.nan
        else:
            col8 = (float(col7)/float(len(temp_luca))) * 100 
        #col9 is QC - Unique Duplicate groups (#)
        col9 = len(temp_qcd.groupby(['Dupe_ID']))
        #create the crosstab table for the remainder of the calculations
        #this is a table where each row is a dupe group and columns are amount of 'Y' and 'N's within that group
        temp_luca = pd.crosstab(temp_luca.Dupe_ID,temp_luca['IN BLQ?'])
        #Col10 is Duplicate groups with all addresses in BLQ
        if 'N' in temp_luca.columns:
            col10 = len(temp_luca[temp_luca['N'] == 0])
        else:
            col10 = len(temp_luca)
        #Col 11 is Duplicate groups all in BLQ (%)
        if col9 == 0:
            col11 = np.nan
        else:
            col11 = float(col10)/float(col9) * 100
        print('length before duplicate groups removed with only 1 record: {}'.format(len(temp_luca)))
        #we will remove all isolated duplicate groups for now until we find a fix for the isolated duplicates
        if 'Y' in temp_luca.columns and 'N' in temp_luca.columns:
            temp_luca = temp_luca[~((temp_luca['Y'] == 1) & (temp_luca['N'] == 0))]
        elif 'Y' in temp_luca.columns:
            temp_luca = temp_luca[~temp_luca['Y'] == 1]
        elif 'N' in temp_luca.columns:
            temp_luca = temp_luca[~temp_luca['N'] == 1]
        print('length after duplicate groups removed with only 1 record: {}'.format(len(temp_luca)))
        #col 12 is duplicate groups only 1 address in BLQ
        if 'Y' in temp_luca.columns:
            col12 = len(temp_luca[temp_luca['Y']==1])
        else:
            col12 = np.nan
        #col 13 is percentage of col 12
        if col9 == 0:
            col13 = np.nan
        else:
            col13 = float(col12)/float(col9) * 100

        QCtable.loc[len(QCtable.index)] = [typ,col1,col2,col3,col4,col5,col6,col7,col8,col9,col10,col11,col12,col13]

    tot_1 = QCtable['County - Total Duplicate Addresses'].sum()
    tot_3 = QCtable['QC - Total Addresses'].sum()
    tot_4 = QCtable['QC - LUCA Deletes'].sum()
    tot_5 = QCtable['QC - LUCA deletes in BLQ'].sum()
    tot_6 = QCtable['QC - Addresses Not Duplicate (#)'].sum()
    tot_7 = QCtable['QC - Addresses in BLQ'].sum()
    tot_8 = float(tot_7)/float(tot_3) * 100
    tot_9 = QCtable['QC - Duplicate groups'].sum()
    tot_10 = QCtable['QC - Duplicate groups - All addresses In BLQ'].sum()
    tot_11 = float(tot_10)/float(tot_9) * 100
    tot_12 = QCtable['QC - Duplicate groups - Only 1 Address in BLQ'].sum()
    tot_13 = float(tot_12)/float(tot_9) * 100

    QCtable.loc[len(QCtable.index)] = ['Total',tot_1,'100',tot_3,tot_4,tot_5,tot_6,tot_7,tot_8,tot_9,tot_10,tot_11,tot_12,tot_13]
    

    QCtable.to_csv(r'M:\08_Geography\Address Duplicate Script\QC\Analysis\output\{}'.format(f))
