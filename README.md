# duplicate_address_identifier
Project for detecting address duplicates in the Census Bureau's LUCA address lists
This project was developed while working as a Geographer for the Census Bureau. The task was to determine if there was a way to find duplicate address records without using spatial data, as many address duplicates we due to incorrect geocoding issues and therefore placed in different census blocks or tracts. 

NOTE: CENSUS BUREAU ADDRESS DATA IS CONFIDENTIAL, THEREFORE, THIS APPLICATION WILL NOT WORK WHEN DOWNLOADED LOCALLY OFF OF THE CENSUS BUREAU NETWORK. THE SCRIPT REQUIRES SPECIFIC INPUTS WHICH I COULD NOT INCLUDE IN THE REPO DUE TO THE CONFIDENTIALITY OF THE DATA. THE SCRIPT ALSO REQUIRES ACCESS TO SPECIFIC DRIVES ON THE CENSUS NETWORK IN ORDER TO COMPILE THE LUCA DELETES FROM FILES ON THE NETWORK. THIS PROJECT IS POSTED SPECIFICALLY FOR PORTFOLIO PURPOSES ONLY AND IS NOT INTENDED TO BE FUNCTIONAL WHEN CLONED.

LUCA ADDRESS LIST DUPLICATE PROCESSING SCRIPT

Background :

The Census Bureau maintains the entirety of its address data within a single master database referred to as the Master Address File (MAF). This database accounts for all addresses known to the Census Bureau since the 2000 Decennial Census. While comprehensive, there is a large amount of ‘bad’ addresses in the database, such as those which have since been verified to no longer exist, or addresses which had incorrect information. To ensure the 2020 Decennial Census enumeration operation is as efficient as possible, the Census Bureau creates the enumeration universe for the decennial census from the addresses in the MAF by implementing the Decennial Filter to filter out those ‘bad’ addresses and to remove duplicate address records that refer to the same housing unit. It is important that the enumeration universe is as accurate as possible, as there are numerous operational phases that go into counting each non-responding household

The Census Bureau invites local governments to assist with their effort in developing the 2020 Decennial Census enumeration universe through geographic partnership programs. One such program is the Local Update of Census Addresses (LUCA) operation. Entities who participate in this program receive a list of the most updated addresses known to the Census Bureau within their jurisdiction, and their task is to review the addresses and make corrections as needed. Valid correction types include adding an address the Census Bureau doesn’t have, correcting an address’ attributes to be more accurate, or deleting an address from the LUCA list that is either a duplicate record or an address that no longer exists.

The LUCA address list duplicate processing script was written to measure how many duplicate addresses exist within the LUCA address lists and to measure the effectiveness of the Decennial Filter in removing duplicate addresses from the enumeration universe. 

LUCA ADDRESSS LIST DUPLICATE PROCESSING SCRIPT OVERVIEW
The script loads in all the addresses from the LUCA list for a user-specified county and runs a series of formatting operations which identify duplicate records, these are 2 or more address records which may have identical or differing attributes and refer to the same housing unit. This application contains a python script written  to identify duplicate addresses within LUCA address lists the Census Bureau had provided to LUCA participants prior to performing their LUCA review . The python script also compiles a table of MAFIDs which were submitted to be deleted by participants as part of their LUCA submission. The duplicates and LUCA deletes are joined, and the final output includes a column to indicate which address duplicates were deleted by the participant through LUCA program. There are 7 tests  performed within the script to catch variations of duplicate types which are described in detail in the LUCA Address List Duplicate section of this document: 
1. Full address comparison 
2. Full address comparison with all spaces removed from the address string
3. Alternative apartment unit designator duplicates
4. Duplicate addresses that have different GEOID values
5. Duplicate addresses that have different zipcode values
6. Duplicate addresses matched after reformatting the street name
7. Duplicate addresses where the apartment designator is included in the house number field
The final Ooutput tables indicate which test is associated withidentified each duplicate address. Each duplicateAll duplicates which refer to the same unit are assigned a  group is assigned a unique duplicate  ID, so output can be sorted, and duplicate groups kept together in order. NYRCC geography staff reviewed and analyzed a selection of county duplicate outputs to determine how many duplicates were included in the final decennial enumeration universe.

Building the LUCA return DELETE table:
The first step of the application is to compile a list of all MAFIDs which have a ‘D’ (delete) action code in the LUCA return files . The LUCA return files are the submissions from LUCA participants indicating suggested changes to the Census Bureaus address list, and those with the ‘D’ action code are indicating to the Census Bureau that that particular address should be deleted from the Decennial enumeration universe. It is important to indicate which address duplicates had a ‘D’ action code in LUCA so that we can remove these when testing the effectiveness of the Decennial Filter. It is also important we compile this list as the first step in the script so that the list can be compiled only once for the entire state and then joined to each county duplicate table that is processed within that state.  

Each state has its own folder in the LUCA drive’s ‘incoming’ folder, and within each state’s folder is a sub-folder for each entity within that state which that participated in the LUCA program. Within each of these participating entity’s folder is a series of assorted files associated to the LUCA operation. Some of the files are associated with their address list updates, and these are the files that are used to build the table of MAFIDs with LUCA delete codes that are joined to the final script output. LUCA participants were instructed to name their submittedssion address updates file with to include the phrase ‘changes_addresses’, however this was not always the case. This script looks inside each participating entity’s folder and scans each filename to see if it is a csv or xlsx file type and if ‘changes_address’ is included in the filename. If these conditions are met, the script loads the file into a table (Pandas dataframe)  and queries out MAFIDs with only the ‘D’ or ‘d’ value in the ACTION column. This result is then appended to a cumulative table for the state which will be used to join the duplicate address tableses compiled later in the script. If a file in the entity’s folder is a .csv or .xlsx and does not have ‘changes addresses’ in the name, the program script will then attempt to read it into a table, and if successful, will then check if there is a column for ‘MAFID’ and a column for ‘ACTION’. If it cannot be read in as a table or, after being read into a table, it does not contain these columns, it will not append the file to the cumulative table for the state.  

LUCA participants were also required to password protect their files; however, the returns seem to overwhelmingly not be password protected. If the application does encounter a password protected file, it will simply ignore the file and move on*. A message is printed to the screen to let the user know the file was password protected and could not be accessed , and once this section of the script completes, a list of all entities which did not contain one valid LUCA return file in their sub-folder is printed to the console. For all states in the NYRCC region there were 571 total participating entities in the LUCA drive, 521 entities were successfully added to a compiled LUCA deletes table, 50 entities could not be added as they only had password protected or invalid files within their sub-folder.. Once the cumulative state deletes file is compiled, the table is saved as a CSV and the program continues to the next section compiling duplicates from the LUCA address list.

* The passwords were required to follow a standard format, and therefore, the script could be easily automated to unlock the file and incorporate the data into the cumulative state deletes table. This, however, requires the installation of an additional python library (pywin32). Access to install new python packages is beyond the privileges of the geography team which developed the application.

LUCA ADDRESS LIST DUPLICATE TESTS:
The script initializes a list of counties within the user-provided  state by scanning   the state address list and finding unique values within the ‘COUNTYFP’ column, which are compiled into a python list. The compiled county list is iterated so that duplicate processing is only performed on one county at a time, as the state list is too large to load into memory and process at once. 

For each county in the county list, 7 tests are performed that each identify duplicate addresses and then assigns to them  1.) a unique duplicate ID to associate the duplicate addressesaddress records that refer to the same housing unit to a duplicate pair or to each other as a duplicate group correlate duplicates together and 2.) the value of the test  in which they were caught. Tests are performed in the following order:
1.	Full Address Duplicate: Addresses are compared against each other using their unedited HOUSENUMBER, STREETNAME, APARTMENT UNIT, ZIP and GEOID columns with spaces separating the fields. Addresses where all ofall the above fields exactly match are flagged. These aAddresses that match this condition are “true” duplicates in that each of these unedited columns in the address list match completely. 
2.	Full Address – No Space Duplicate Addresses are compared against each other using their unedited HOUSENUMBER, STREETNAME, APARTMENT UNIT, ZIP and GEOID columns (the same as Full Address Duplicate): The columns used in this test  are the same columns used in the previous test, but with no spaces separating between the fields and all spaces removed from within each field as well. For example, addresses with the same house number on Bay View St. and Bayview St. will be caught as duplicates (if they are within the same ZIP and GEOID). 
HOUSENUMBER	STREETNAME
15	Bay View St.
15	Bayview St.

Another common condition that is caught in this test is when a directional character from the street name is included in the house number field. Such as:
HOUSENUMBER	STREETNAME
46	W PINE ST
46 W 	PINE ST

An exceptionEXCEPTION: when an address has a numeric character at the end of the HOUSENUMBER and beginning of STREETNAME, to this test is that   a ‘|’ character is added to the space-removed string to separate those fields. any address that has a numeric character at the end of the HOUSENUMBER and beginning of STREETNAME. This prevents common false duplicates being caught, such as:
HOUSENUMBER	STREETNAME
60	15TH ST
601	5TH ST


3.	Apartment Prefix Formatting Duplicate: Duplicate matches are performed only on addresses that have a value in the APARTMENT UNIT field. If the strings 'APT','LOT','UNIT','STE' or 'TRLR' are present in the APARTMENT UNIT field, they are removed. Addresses are then comparedtested using the HOUSENUMBER, STREETNAME, APARTMENT UNIT, ZIP and GEOID fieldsagain with all spaces removed in the address string . 
4.	Different Zip Duplicates: Some address records in the LUCA address list refer to the same unit but contain different ZIP values.  This duplicate test is performed with the HOUSENUMBER, STREETNAME, formatted APARTMENT UNIT (see test 3) and GEOID fields with all spaces removed.
5.	Different Block Duplicate: Some address records in the LUCA address list refer to the same unit but contain different GEOID values. Often this occurs to units which are near a census tract or block boundary. This duplicate test is performed with the HOUSENUMBER, STREETNAME, formatted APARTMENT UNIT (see test 3) and ZIP fields with all spaces removed. 
6.	Streetname Formatting Duplicate: This test compares addresses after reformatting the STREETNAME column with a series of text replacements to normalize words that have common alternative spellings and to remove terms that can interchangeably be used or omitted in an address*.  Text replacements are performed in two steps:
1.	
i.	The following is a list of terms which have common alternative spellings and are replaced with the term that follows the colon: 'FIRST':'1ST', 'SECOND':'2ND', 'THIRD':'3RD', 'FOURTH':'4TH', 'FIFTH':'5TH', 'SIXTH':'6TH', 'SEVENTH':'7TH', 'EIGTH':'8TH', 'NINTH':'9TH', 'TENTH':'10TH','SAINT':'ST'. These terms are replaced only if they are found at the beginning of the STREETNAME field or found as an isolated word with spaces on either side. They will not be replaced if in the middle of a word or at the end of a streename.
ii.	The  following are rare suffixes that are replaced if they are found only at the end of the STREETNAME field and with a space before their term (‘COVE’:’CV’),(‘RIDGE’:’RDG’). It appears the MAF handles standardizing address suffixes well, but it misses at least these two. 
	
2.	The following terms are interchangeably used or omitted in addresses and are replaced with empty strings to standardize the street name prefix: ‘HIGHWAY', 'STATE HWY',’STATE RD’,’CO RD’,’ROUTE’,’RTE’,’HWY’,’US’

*This script was written for the addresses in the NY Regional Census Office Area, and specifically, those in NY State and Mass. were the focus of QC. It is likely there are common terms and words used in street names in other geographic regions of the country which have not been accounted for in this version of the script and should be considered when looking for duplicates in other regions. There are also possible other suffixes that are particular to a region which may not be standardized by the MAF. A user can simply add more text replacement pairs to the dictionary used in the ‘textreplace’ function in the python script. 

7.	Character Match Duplicate: This test takes all the alphanumeric characters in the HOUSENUMBER, formatted STREETNAME (see test 6), and formatted APARTMENT UNIT columns (see test 3), sorts them in alphabetical order, and then concatenates them into one long, unspaced string. This string is used to match duplicates. The goal of this test is to catch addresses which include the unit designator in the HOUSENUMBER column 
HOUSENUMBER	STREETNAME	APARTMENT UNIT
100 A	FRONT ST	
100	FRONT ST 	APT A
After formatting and sorting, both above records above become '001AFNORSTT' and will be matched as duplicates. This test is not performed on any addresses with a STREENAME value that contains one or more numeric characters due to the high number of false duplicates which arise with interchangeable numbers. 
	A hypothetical example of a duplicate group resulting from this test (FULLCHARS column):



ROW	GEOID	HOUSE
NUMBER	STREETNAME	APARTMENT UNIT	ZIP	FULLCHARS	HNLEN	HN_NUM
1	361119502002017	125 A	MAIN ST		12477	125AAIMNST	4	125
2	361119502002028	215	MAINA ST		12477	125AAIMNST	3	215
3	361119515002017	125	MAIN ST	APT A	12449	125AAIMNST	3	125
4	361119515002029	215	MAINA ST		12449	125AAIMNST	3	215
5	361119522002017	152	MAINA ST		12477	125AAIMNST	3	152
6	361119524001019	21	MAINA ST	APT 5	12401	125AAIMNST	2	21

In the above table, the column FULLCHARS represents the sorted string which is used to group the address records together. There is also an HNLEN column containing the length of characters in the HOUSENUMBER field and the HN_NUM which is the house number without any letter characters. Additional subgroupings are needed to pullout the correct duplicate rows, which are on row 1 and 3 , and prevent false duplicates. Because it is likely that there are multiple occurrences of the same street name within a county, and the likelihood of false duplicates this may cause in this test, aAdditional subgroupings are needed to pullout the correct duplicate rows, which are on row 1 and 3 , and prevent false duplicates.  tThe above duplicate rows are then sub-grouped 3 more times , each resulting in its own table: 
1.	The address list is grouped into duplicate groups by both this sorted address string (FULLCHARS, seen above) and then further grouped by Subgrouped based upon similar GEOID values within each of these groupsthe FULLCHAR duplicate table. These FULLCHARS-GEOID subgroups are tested for a singular unique ZIP value. Duplicate groups that pass this test will get the value of ‘CharMatch’ as their duplicate type. 
2.	Using the FULLCHARS-GEOID subgroup in the above test, if there is more than one unique zip value, duplicates will be assigned ‘CharMatch DiffZip’ value as their duplicate type.
3.	To test for the duplicates which may have different GEOIDs, the address list is grouped into duplicate groups by both this sorted address string (FULLCHARS, seen above) and then further grouped by ZIP values within each of these groups. The GEOID-ZIP subgroups are tested for a singular unique GEOID value. Duplicate groups that pass this test will get the value of ‘CharMatch DiffGEOID’ as their duplicate type. 
For example: After grouping the above duplicates by their GEOID the following table  results:
ROW	GEOID	HOUSE
NUMBER	STREETNAME	APARTMENT UNIT	ZIP	FULLCHARS	HNLEN	HN_NUM
1	361119502002017	125 A	MAIN ST		12477	125AAIMNST	4	125
2	361119515002017	125	MAIN ST	APT A	12449	125AAIMNST	3	125
3	361119522002017	152	MAINA ST		12477	125AAIMNST	3	152

Additional conditions must be applied to this FULLCHARS-GEOID subgroup to identify the duplicate addresses. This table is then grouped once more by the HN_NUM column, resulting in a subgroup of the first two rows of the above table. Finally, these groups are tested for the presence of a letter character in at least one of the rows, and for at least two different HNLEN values. The final result of these various groupings and tests filters down to only the address duplicates where one record contains the apartment unit in the HOUSE NUMBER field. The matching records (rows 1 and 2) would be assigned the Duplicate Type value of ‘CharMatch DiffZip’.  

Each of the 7 duplicate tests above results in its own table. These tables contain all occurrences of duplicates within the county that are identified through that particular test, and many addresses will appear on multiple tables. Each record in a particular table has the same value in the ‘Dupe_Type’ field, which is used to identify which table it came from when joined back to the LUCA address list in the next step. 
After these tables have been generated for each duplicate test, they are then joined back to the original LUCA address list by the MAFID column. After the join, the address at a particular MAFID will contain values for the ‘Dupe_ID’ and ‘DuplicateType’. The order in which the tables are joined back is important because each subsequent table -join will only consider records on the LUCA address list that have not already been joined to a duplicate table. This allows for only one value in the ‘Dupe_Type’ field. The order of table-joins is also important because the duplicate tests get more specific in the order that they are joined. For example, if a record would be considered a duplicate in the ‘Full Address Duplicate’ test, it will likely also be considered a duplicate for the other subsequent 6 tests as well. This means a record should only be considered as ‘Different Block’ duplicate (test 4) if the address was not already caught in the ‘Full Address Duplicate’ test (test 1), the ‘Full Address – No Space’ test (test 2)  or the ‘Apartment Prefix Formatting’ test (test 3).  
These temporary duplicate tables are simply held in memory while the script runs and are then deleted after being joined, but the code can be modified so that each table can be individually output as a csv if needed. This can be achieved by simply uncommenting the ‘pd.to_csv()’ line in the createduplicatetable function. This will create a csv for each duplicate test for each county in the state in the output location specified by the user at the beginning of the script.

Application Output QC
Duplicate address tables for various counties were analyzed to gather statistics on duplicate address occurrence and to determine how many of the duplicates made it into the 2020 Decennial Census universe. Counties were selected to cover rural and metropolitan areas within New York State and Massachusetts. 

RESULTS
Total addresses in luca lists in region 18870798
Total duplicate records in region 64724 or .34% of addresses are duplicate records
- how bad is the issue of address duplicates ( can I get a number of the total addresses within the filter for a county or state or region?)
- how effective was the filter in general?(what percentage of address duplicates made it through the decennial filter and what percentage was properly resolved by the filter(only 1 record in maf in a duplicate group))
- which duplicate type is most common?
-which duplicate type was most likely to not be caught by filter?
-is there a spatial component to where duplicates are caught (not sure how to go about this yet, will be a secondary analysis if there is enough time)
- *not crucial to testing filter but interesting to find out* how many duplicates were re-added to the universe after being deleted in LUCA?


Things To Consider:
•	 This application will not match addresses duplicates that refer to the same unit but have different values for both the ZIP and GEOID field.  A match between oOne of these two fields isare needed as a control to prevent the likelihood of false duplicate occurring if searching within the entire county . (if there is more than one ‘Main st’ in a county, which is very likely, we will need to search within a secondary sub-geography in order to ensure we are referring to the same ‘Main st’, as it is almost 100% unlikely there would be more than one ‘main st’ in the same zipcode or block.)However, It would be possible to use tract as the secondary geo in further revisions of the script by slicing it from the GEOID, which would allow for a duplicate address within the same tract that has a different block and different zipcode, as it is again unlikely for there to be more than one street within a tract with the same name.
