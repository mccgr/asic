library(readr)
library(lubridate)
library(dplyr)
library(RPostgreSQL, quietly = TRUE)


clean_prob_former_names <- function(x) {
  
  result <- gsub('\\\"', '\\\\\"', x) # handle double quotes in strings
  result <- ifelse(grepl('[,{}]', result), paste0('\"', result, '\"'), result)
  return(result)
}

ASIC_DIR <- Sys.getenv('ASIC_DIR')

csv_file_name <- list.files(paste0(ASIC_DIR, '/', 'bulk_extract_csvs'))[[1]]

csv_path <- paste0(ASIC_DIR, '/', 'bulk_extract_csvs', '/', csv_file_name)

df <- read_tsv(csv_path, col_types = 'cccccccccccccc', locale = locale(encoding = 'ISO-8859-1'))

colnames(df) <- c('company_name_orig', 'acn', 'type', 'class', 'subclass', 'status', 'registration_date',
                'previous_state_of_registration', 'previous_state_number', 'modified_since_last_report',
                'current_name_indicator', 'abn', 'company_name_current', 'current_name_start_date')

df$registration_date <- dmy(df$registration_date)
df$current_name_start_date <- dmy(df$current_name_start_date)

df$abn[df$abn == '0'] <- NA


df$modified_since_last_report <- ifelse(is.na(df$modified_since_last_report), FALSE, TRUE)
df$current_name_indicator <- ifelse(is.na(df$current_name_indicator), FALSE, TRUE)


not_current_name_df <- df %>% filter(!current_name_indicator)
df <- df %>% filter(current_name_indicator)


former_names <- not_current_name_df %>%
                group_by(acn) %>% 
  summarise(former_names = paste0('{', paste(clean_prob_former_names(company_name_orig), collapse=","), '}'))

reg_and_has_former_names_df <- df %>% inner_join(former_names, by = 'acn')


# Some entries in not_current_name_df do not have a corresponding entry by acn in the updated df (filtered by ones 
# for which the name is current), hence the initial use of reg_and_has_former_names_df. This part handles them
cancelled_df <- former_names %>% 
                anti_join(reg_and_has_former_names_df, by = 'acn') %>% 
                inner_join(not_current_name_df, by = 'acn')


cancelled_df <- cancelled_df %>% group_by(acn) %>% summarise(company_name_orig = unique(company_name_current)[[1]], 
                                          type = unique(type)[[1]],
                                          class = unique(class)[[1]],
                                          subclass = unique(subclass)[[1]],
                                          status = unique(status)[[1]],
                                          registration_date = unique(registration_date)[[1]], 
                                          previous_state_of_registration = unique(previous_state_of_registration)[[1]],
                                          previous_state_number = unique(previous_state_number)[[1]],
                                          modified_since_last_report = unique(modified_since_last_report)[[1]], 
                                          current_name_indicator = TRUE,
                                          abn = unique(abn)[[1]],
                                          company_name_current = NA, 
                                          current_name_start_date = unique(current_name_start_date)[[1]]) %>%
                                          inner_join(former_names, by = 'acn')

has_former_names_df <- bind_rows(reg_and_has_former_names_df, cancelled_df)
no_former_names_df <- df %>% anti_join(former_names, by = 'acn')

# Assign NA to former_names for entries with no former names
no_former_names_df$former_names <- NA

# Finally, bind rows of no_former_names_df and has_former_names_df into full_df

full_df <- bind_rows(no_former_names_df, has_former_names_df)

# Also, not all columns are useful now. In particular, current_name_indicator and company_name_current. Drop them

full_df <- full_df %>% select(-c(current_name_indicator, company_name_current))

# Also rename 'company_name_orig' to 'company_name'

full_df <- full_df %>% rename(company_name = company_name_orig)

# Last step, write to the database


order <- c('company_name', 'acn', 'abn', 'former_names', 'modified_since_last_report', 'type', 'class', 'subclass', 
           'status', 'registration_date', 'current_name_start_date', 'previous_state_of_registration', 
           'previous_state_number')

full_df <- full_df[, order]




pg <- dbConnect(PostgreSQL())

table_exists <- dbExistsTable(pg, c("asic", "asic_bulk_extract"))

if(table_exists) {
  
  current_tbl_df <- dbReadTable(pg, c("asic", "asic_bulk_extract"))
  since_deleted_df <- current_tbl_df %>% anti_join(full_df, by = 'acn')
  
  full_df <- full_df %>% bind_rows(since_deleted_df)
  
}



field_types <- c('TEXT', 'TEXT', 'TEXT', 'TEXT[]', 'BOOLEAN', 'TEXT', 
                 'TEXT', 'TEXT', 'TEXT', 'DATE', 'DATE', 'TEXT', 'TEXT')

names(field_types) <- colnames(full_df) 


if(table_exists) {
  
  success <- dbWriteTable(pg, c("asic", "asic_bulk_extract_temp"),
               full_df, row.names = FALSE, field.types = field_types)
  
  if(success) {
    
    dbExecute(pg, 'DROP TABLE asic.asic_bulk_extract')
    dbExecute(pg, 'ALTER TABLE asic.asic_bulk_extract_temp RENAME TO asic_bulk_extract')
    unlink(paste0(ASIC_DIR, '/', 'bulk_extract_csvs'), recursive = TRUE)
    
  }
  
  
} else {
  
  success <- dbWriteTable(pg, c("asic", "asic_bulk_extract"),
               full_df, row.names = FALSE, field.types = field_types)
  
  if(success) {
    
    unlink(paste0(ASIC_DIR, '/', 'bulk_extract_csvs'), recursive = TRUE)
    
  }
  
}


dbDisconnect(pg)






