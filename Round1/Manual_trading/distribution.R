scuba <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round1/Manual_trading/output.csv")
library(dplyr)
n = 500
scuba <- scuba %>%
  mutate(low_CI = qnorm(0.1, mean = mean, sd = sqrt(variance/n)))
scuba <- scuba %>%
  mutate(high_CI = qnorm(0.9, mean = mean, sd = sqrt(variance/n)))

scuba[scuba['mean'] == max(scuba['mean']),]
scuba[scuba['high_CI'] == max(scuba['high_CI']),]
scuba[scuba['low_CI'] == max(scuba['low_CI']),]

max(scuba['high_CI'])




qnorm(c(0.1, 0.9), mean = max(scuba['mean']), sd = sqrt(380.46197572581957/n))

qnorm(c(0.05, 0.95), mean = 14.453310036886041, sd = sqrt(656.2889771042265/n))
