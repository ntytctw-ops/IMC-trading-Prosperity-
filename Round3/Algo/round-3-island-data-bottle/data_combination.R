day0 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round3/Algo/round-3-island-data-bottle/prices_round_3_day_0_cleaned.csv")
day1 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round3/Algo/round-3-island-data-bottle/prices_round_3_day_1_cleaned.csv")
day2 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round3/Algo/round-3-island-data-bottle/prices_round_3_day_2_cleaned.csv")

day1$timestamp <- day1$timestamp + 1000000

day2$timestamp <- day2$timestamp + 1000000*2

three_days <- rbind(day0, day1, day2)

write.csv(three_days, file = "/Users/smithereen/Desktop/IMC_trading/Round3/Algo/round-3-island-data-bottle/three_days_round3.csv", row.names = FALSE)
