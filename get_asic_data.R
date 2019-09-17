library(readr)
library(lubridate)
library(dplyr)

df <- read_tsv('/home/bdcallen/Downloads/company_201908/COMPANY_201908.csv', col_types = 'cccccccccccccc')

colnames(df) <- c('company_name_orig', 'acn', 'type', 'class', 'subclass', 'status', 'registration_date',
                'previous_state_of_registration', 'previous_state_number', 'modified_since_last_report',
                'current_name_indicator', 'abn', 'company_name_current', 'current_name_start_date')

df$registration_date <- dmy(df$registration_date)
df$current_name_start_date <- dmy(df$current_name_start_date)

df$abn[df$abn == '0'] <- NA


df$modified_since_last_report <- ifelse(is.na(df$modified_since_last_report), FALSE, TRUE)
df$current_name_indicator <- ifelse(is.na(df$current_name_indicator), FALSE, TRUE)
