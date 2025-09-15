dayn1 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round2/Algo_trading/data/round-2-island-data-bottle/prices_round_2_day_-1_cleaned.csv")
day0 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round2/Algo_trading/data/round-2-island-data-bottle/prices_round_2_day_0_cleaned.csv")
day1 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round2/Algo_trading/data/round-2-island-data-bottle/prices_round_2_day_1_cleaned.csv")

three_days_orchid_data <- rbind(dayn1, day0, day1)

three_days_orchid_data$timestamp[three_days_orchid_data$DAY == 0] <- three_days_orchid_data$timestamp[three_days_orchid_data$DAY == 0] + 1000100

three_days_orchid_data$timestamp[three_days_orchid_data$DAY == 1] <- three_days_orchid_data$timestamp[three_days_orchid_data$DAY == 1] + 1000100*2

write.csv(three_days_orchid_data, file = "/Users/smithereen/Desktop/IMC_trading/Round2/Algo_trading/data/three_days_orchid_data.csv", row.names = FALSE)

par(mfrow=c(1,2))
plot(three_days_orchid_data$timestamp,three_days_orchid_data$SUNLIGHT)
plot(three_days_orchid_data$timestamp,three_days_orchid_data$HUMIDITY)
abline(three_days_orchid_data$timestamp,three_days_orchid_data$ORCHIDS)

simulation <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round2/Algo_trading/data/simulation.csv")
orchids_sim <- simulation[simulation$product == "ORCHIDS",]

par(mfrow=c(1,1))
plot(day1[day1$timestamp<100000,]$timestamp,day1[day1$timestamp<100000,]$ORCHIDS,type = "l",col = "orange")
lines(orchids_sim$timestamp, orchids_sim$mid_price,ylim = c(1000,1130),type = "l",col = "green")

# Draw multiple variables against the same variable
par(mfrow=c(1,1))
matplot(x = three_days_orchid_data$timestamp, y = three_days_orchid_data[, c(2,6,7)], type = "l", lty = 1:3, col = 1:3)


model1 <- lm(ORCHIDS ~ 1 + SUNLIGHT*HUMIDITY, data = day1)
model2 <- lm(ORCHIDS ~ 1 + SUNLIGHT*HUMIDITY, data = day0)
model3 <- lm(ORCHIDS ~ 1 + SUNLIGHT*HUMIDITY, data = dayn1)
model4 <- lm(ORCHIDS ~ 1 + SUNLIGHT + I(SUNLIGHT^2) + I(SUNLIGHT^3), data = day1)



