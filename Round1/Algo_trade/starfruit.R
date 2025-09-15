day_n2 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round1/Algo_trade/round-1-island-data-bottle/prices_round_1_day_-2_cleaned.csv") 

day_n1 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round1/Algo_trade/round-1-island-data-bottle/prices_round_1_day_-1_cleaned.csv") 

day_0 <- read.csv("/Users/smithereen/Desktop/IMC_trading/Round1/Algo_trade/round-1-island-data-bottle/prices_round_1_day_0_cleaned.csv") 

day_all_3 <- rbind(day_n2, day_n1, day_0)

day_all_3$timestamp[day_all_3$day == -1] <- day_all_3$timestamp[day_all_3$day == -1] + 999900

day_all_3$timestamp[day_all_3$day == 0] <- day_all_3$timestamp[day_all_3$day == 0] + 999900*2

day_all_3[day_all_3$day == 0,]

write.csv(day_all_3, file = "/Users/smithereen/Desktop/IMC_trading/Round1/Algo_trade/mydata.csv", row.names = FALSE)

starfruit <- day_all_3[day_all_3$product == "STARFRUIT",]
amethysts <- day_all_3[day_all_3$product == "AMETHYSTS",]

starfruit$spread <- starfruit$ask_price_1 - starfruit$bid_price_1
hist(starfruit$spread)

starfruit_small_2 <- starfruit[starfruit$timestamp>30000 & starfruit$timestamp<=60000,]
starfruit_small_3 <- starfruit[starfruit$timestamp>60000 & starfruit$timestamp<=90000,]
starfruit_small_4 <- starfruit[starfruit$timestamp>90000 & starfruit$timestamp<=120000,]

library(zoo)
par(mfrow=c(1,1))
starfruit_small_1 <- starfruit[starfruit$timestamp<=100000,]
plot(starfruit_small_1$timestamp, starfruit_small_1$bid_price_1, col="blue",pch=16,ylim = c(min(starfruit_small_1$bid_price_1), max(starfruit_small_1$ask_price_1)))
points(starfruit_small_1$timestamp, starfruit_small_1$ask_price_1, col='red', pch=16)
short_ma_best_bid <- rollmean(starfruit_small_1$bid_price_1, k = 5, fill = NA)
short_ma_best_ask <- rollmean(starfruit_small_1$ask_price_1, k = 5, fill = NA)
long_ma_best_bid <- rollmean(starfruit_small_1$bid_price_1, k = 20, fill = NA)
long_ma_best_ask <- rollmean(starfruit_small_1$ask_price_1, k = 20, fill = NA)
lines(starfruit_small_1$timestamp, short_ma_best_bid, col = "purple",lwd=2)
lines(starfruit_small_1$timestamp, short_ma_best_ask, col = "orange",lwd=2)
lines(starfruit_small_1$timestamp, long_ma_best_bid, col = "pink",lwd=2)
lines(starfruit_small_1$timestamp, long_ma_best_ask, col = "green",lwd=2)

hist(starfruit_small_1$spread)






lines(smooth.spline(starfruit_small_1$timestamp,starfruit_small_1$bid_price_1),col='purple',lwd=2)
lines(smooth.spline(starfruit_small_1$timestamp,starfruit_small_1$ask_price_1),col='orange',lwd=2)



par(mfrow=c(2,2))
plot(starfruit_small_1$timestamp, starfruit_small_1$mid_price,type="b", col="green")
lines(ksmooth(starfruit_small_1$timestamp,starfruit_small_1$bid_price_1,kernel='normal',bandwidth=1),col='blue',lwd=0.5)
lines(ksmooth(starfruit_small_1$timestamp,starfruit_small_1$ask_price_1,kernel='normal',bandwidth=1),col='red',lwd=0.5)
plot(starfruit_small_2$timestamp, starfruit_small_2$mid_price,type="b", col="green")
lines(ksmooth(starfruit_small_2$timestamp,starfruit_small_2$bid_price_1,kernel='normal',bandwidth=1),col='blue',lwd=0.5)
lines(ksmooth(starfruit_small_2$timestamp,starfruit_small_2$ask_price_1,kernel='normal',bandwidth=1),col='red',lwd=0.5)
plot(starfruit_small_3$timestamp, starfruit_small_3$mid_price,type="b", col="green")
lines(ksmooth(starfruit_small_3$timestamp,starfruit_small_3$bid_price_1,kernel='normal',bandwidth=1),col='blue',lwd=0.5)
lines(ksmooth(starfruit_small_3$timestamp,starfruit_small_3$ask_price_1,kernel='normal',bandwidth=1),col='red',lwd=0.5)
plot(starfruit_small_4$timestamp, starfruit_small_4$mid_price,type="b", col="green")
lines(ksmooth(starfruit_small_4$timestamp,starfruit_small_4$bid_price_1,kernel='normal',bandwidth=1),col='blue',lwd=0.5)
lines(ksmooth(starfruit_small_4$timestamp,starfruit_small_4$ask_price_1,kernel='normal',bandwidth=1),col='red',lwd=0.5)










abline(v = 999900, col = "red", lwd = 2, lty = 2)
abline(v = 999900*2, col = "red", lwd = 2, lty = 2)
smoothing <- ksmooth(starfruit$timestamp,starfruit$mid_price,kernel='normal',bandwidth=500000)
lines(smoothing,col='blue',lwd=2)


lines(smooth.spline(starfruit$timestamp, starfruit$mid_price),col=5,lwd=2)

hist(starfruit$ask_volume_1,breaks = 32)
hist(starfruit$bid_volume_1,breaks = 32)


