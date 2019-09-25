# asic_bulk_extract

This README gives a detailed description of the table `asic.asic_bulk_extract`. This table is formed from the data contained in the weekly updated `Company Dataset` supplied by ASIC on `data.gov.au`, a guide to which can be found [here](company-dataset-help-file.pdf). 

The csv file for ASIC's Company Dataset for any given update contains information on all companies currently registered with ASIC, as well as information on all deregistered companies for the last year. Hence, this file does not give a full dataset of the companies and entities that appear on the ASIC Connect website when searching under `Organizations and Business Names`. Furthermore, as the file is updated weekly, some data is deleted, since some deregistered companies then fall outside the current past year. The program designed to extract the data from the csv file and write it to `asic_bulk_extract`, `process_asic_csv.R`, is designed to keep the data from the table that does not appear in the most recent update. Hence, given this table was first formed on from an update from mid-August 2019, `asic.asic_bulk_extract` contains data on all companies that are registered, and deregistered from around mid-August 2018 up until the date of the last updated csv file supplied by ASIC. 

Also, the rows in the original csv file have a many to one relationship to the original `ACN` field, which is usually an Australian Company Number, can be an Australian Registered Business Number (ARBN), if this is more applicable (this is particularly the case with foreign companies). For each `ACN`, there is a single `Company Name`, of these names, precisely one corresponds to the current business name. Contrarily, instead of writing the rows into the table in the same way, `process_asic_csv.R` extracts the portion of the dataset for which the rows do not correspond to the current name, groups them by the `ACN`, and then binds the group names into lists which form values of a field called `former_names`, and then this manipulated data is joined to the portion of the dataset corresponding to the current names by `ACN`. The starting dates of the current company names is also extracted this way. Thus, the table `asic.asic_bulk_extract` contains a single record for each `ACN`, with the relevant information from the rows with older business names contained in the columns `former_names` and `current_name_start_date`.


## The fields

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
    * `NRET`: Non-registered entity (an entity not registered under the _Corporations Act 2001_ but mentioned in the database)
    * `OBJN`: Objection to registration of name (name possibly not available due to requirements of Corporations Law or Regulations)
    * `RACN`: Registered Australian Corporation (an organisation incorporated in Australia under a law other than the Corporations Law but required to be registered under the Corporations Law)
    * `TRST`: Trust (note that trusts don't appear to be a part of the dataset, thought this field is mentioned in the guide)
 
 - `class`: this field signifies the class of the entity, given as a four-character string. Same as the `Class` column of the original csv. Thus, from the guide, the possible values of this field are:
 
    * `LMSH`: Limited by Shares. The liability of the members is limited to the amount unpaid on their shares. Shareholders are not required to contribute any further monies (in the case of a winding up) if the shares they have taken up are fully paid.
    * `LMGT`: Limited by Guarantee. The members' liability is limited to a certain amount that they undertake to contribute in case of a winding up. The amount is specified in a clause in the Memorandum of Association of the company. A member of a company limited by guarantee is not required to in any capital while the company is a going concern.
    * `LMSG`: Limited by Both Shares and Guarantees. The member has the liability as a shareholder (to the extent of the amount unpaid on his shares) and as a guarantor (to the amount nominated in the Memorandum) in the event of a winding up.
    * `NLIA`: No Liability Company. Mining companies only. No legal obligations on the shareholder to pay calls on their shares, e.g. Sterling Silver NL.
    * `UNLM`: Unlimited Company. Is formed on the principle that there is no limit on the liability of the members. Simply, an incorporated partnership, e.g. Mercantile Services Pty, Solicitors.
 
 - `subclass`: this field signifies the subclass of the entity, given as a four-character string. Same as the `Sub Class` column of the original csv. Thus, from the guide, the possible values of this field are:
 
    * `EXPT`: Exempt Proprietary Company
    * `HUNT`: Proprietary home unit company. A company that operates for the sole purpose of administering the day-to-day running of a residential property (refer to paragraph (c) of the definitions of 'special purpose company' in the Corporations (Fees) Regulations for full details)
    * `LISN`: Company licensed under Section 383 of the Corporations Act 2001 to omit 'Limited' from its name
    * `LISS`: Company licensed under Section 383 to omit 'Limited' from its name - superannuation trustee company<sup>[1](#myfootnote1)</sup>
    * `LIST`: Listed public company
    * `NEXT`: Non-Exempt Proprietary Company
    * `NLTD`: Non-profit public company registered without ‘Limited’ in its name under Section 150
    * `NONE`: Unknown
    * `PNPC`: Proprietary non-profit company
    * `PROP`: Proprietary other
    * `PSTC`: Proprietary superannuation trustee company
    * `PUBF`: Foreign company required to lodge a balance sheet
    * `RACA`: Registrable Australian corporation – association
    * `RACO`: Registrable Australian corporation - non association
    * `STFI`: Public company – small transferring financial institution
    * `ULSN`: Unlisted public - non-profit company
    * `ULSS`: Unlisted public - superannuation trustee company
    * `ULST`: Unlisted public company
 
 - `status`: this is the registration status of the entity under ASIC, given as a code represented by a four-character string. Thus, from the guide, the possible values of this field are:
 
    * `DRGD`: De-registered
    * `EXAD`: External administration (in receivership/liquidation)
    * `NOAC`: Not active
    * `NRGD`: Not registered
    * `PROV`: Provisional (mentioned only under charges and refers to those which have not been fully registered)
    * `REGD`: Registered
    * `SOFF`: Strike-off action in progress
    * `DISS`: Dissolved by Special Act of Parliament
    * `DIV3`: Organisation Transferred Registration via DIV3
    * `PEND`: Pending - Schemes
 
 - `registration_date`: the date the entity registered with ASIC.
 
 - `current_name_start_date`: the name start date of the currently registered `company_name`. This column is formed from the values of the `Current Name Start Date` column from the rows in original csv file corresponding to the former names of the entity. 
 
 - `previous_state_of_registration`: the state the company was originally registered in. Same as the analogous field in `asic.asx`.
 
 - `previous_state_number`: the registration number assigned when originally registered by the `previous_state_of_registration`. Same as the analogous field in `asic.asx`.



### Footnotes
<a name="myfootnote1">1</a>: Superannuation Trustee Companies - Operates for the sole purpose of acting as a trustee of a regulated superannuation fund. This class of company may only be used on Annual Returns for 1994 or later.
