# asic_bulk_extract

This README gives a detailed description of the table `asic.asic_bulk_extract`. This table is formed from the data contained in the weekly updated `Company Dataset` supplied by ASIC on `data.gov.au`, a guide to which can be found [here](company-dataset-help-file.pdf). 

The csv file for ASIC's Company Dataset for any given update contains information on all companies currently registered with ASIC, as well as information on all deregistered companies for the last year. Hence, this file does not give a full dataset of the companies and entities that appear on the ASIC Connect website when searching under `Organizations and Business Names`. Furthermore, as the file is updated weekly, some data is deleted, since some deregistered companies then fall outside the current past year. The program designed to extract the data from the csv file and write it to `asic_bulk_extract`, `process_asic_csv.R`, is designed to keep the data from the table that does not appear in the most recent update. Hence, given this table was first formed on from an update from mid-August 2019, `asic.asic_bulk_extract` contains data on all companies that are registered, and deregistered from around mid-August 2018 up until the date of the last updated csv file supplied by ASIC. 

Also, the rows in the original csv file have a many to one relationship to the original `ACN` field, which is usually an Australian Company Number, can be an Australian Registered Business Number (ARBN), if this is more applicable (this is particularly the case with foreign companies). For each `ACN`, there is a single `Company Name`, of these names, precisely one corresponds to the current business name. Contrarily, instead of writing the rows into the table in the same way, `process_asic_csv.R` extracts the portion of the dataset for which the rows do not correspond to the current name, groups them by the `ACN`, and then binds the group names into lists which form values of a field called `former_names`, and then this manipulated data is joined to the portion of the dataset corresponding to the current names by `ACN`. The starting dates of the current company names is also extracted this way. Thus, the table `asic.asic_bulk_extract` contains a single record for each `ACN`, with the relevant information from the rows with older business names contained in the columns `former_names` and `current_name_start_date`.


## The table and fields

 The following

 - `acn`: the specific nine digit number, given as a string, assigned to the entity by ASIC, usually an ACN, but can be an ARBN if the entity has a `type` equal to `RACN` (see later). This is formed from the `ACN` column from the original csv files. Note that unlike the corresponding field in the original csv, the rows of the table are in one-to-one correspondence with this field. As such, `acn` acts as a primary key for the table. 
 
 - `company_name`: This is the current name of the entity, formed from the `Company Name` column in the original csv. 

 - `abn`: The Australian Business Number (ABN) of the entity. If the entity has an ABN, this field is given as string containing the eleven digits, otherwise it is `NULL`.
 
 - `former_names`: A list of formerly used company names for the entity. This is formed from the entries in the `Company Name` column from the rows in the original csv for which `Current Name Indicator` is `NULL`, rather than `Y` (see the guide above).
 
 - `modified_since_last_report`: whether the record corresponding to the `acn` has been modified since the previous update. 
 
 - `type`: the type of company the entity is, given as a four-character string. Same as `Type` in the original csv. Thus, from the guide, the possible values for this field are:
 
    * `APTY`: Australian proprietary company
    * `APUB`: Australian public company
    * `ASSN`: Association
    * `FNOS`: Foreign company (a company incorporated outside Australia but registered as a foreign company in Australia)
    * `NONC`: Non-organisation (a body not registered under _Corporations Act 2001_ but mentioned in the database)
 
 - `class`                           text   
 
 - `subclass`                        text   
 
 - `status`                          text   
 
 - `registration_date`               date   
 
 - `current_name_start_date`         date    
 
 - `previous_state_of_registration`  text    
 
 - `previous_state_number`           text   









