tile <- data.frame(
  Multiplier = c(24, 70, 41, 21, 60, 47, 82, 87, 80, 35, 73, 89, 100, 90, 17, 77, 83, 85, 79, 55, 12, 27, 52, 15, 30),
  Hunters = c(2, 4, 3, 2, 4, 3, 5, 5, 5, 3, 4, 5, 8, 7, 2, 5, 5, 5, 5, 4, 2, 3, 4, 2, 3)
)

sorted_tile <- tile[order(tile$Hunters, tile$Multiplier), ]
sorted_tile[order(sorted_tile$plain_profit), ]

# Print the sorted data frame
print(sorted_data_frame)

profit_each_tile <- function(multiplier, hunters, percentage){
  return (multiplier / (hunters + percentage*100))
}

sorted_tile$minimum_profit <- profit_each_tile(sorted_tile$Multiplier, sorted_tile$Hunters,1)
sorted_tile$maximum_profit <- profit_each_tile(sorted_tile$Multiplier, sorted_tile$Hunters,0)
sorted_tile[order(sorted_tile$maximum_profit), ]


single_profit_tile <- function(x,number){
  return (profit_each_tile(sorted_tile[number,]$Multiplier, sorted_tile[number,]$Hunters,x))
}


x <- seq(0, 0.5, length.out = 1000)
y5 <- single_profit_tile(x,5)
y10 <- single_profit_tile(x,10)
y15 <- single_profit_tile(x,15)
y23 <- single_profit_tile(x,23)
y24 <- single_profit_tile(x,24)
y25 <- single_profit_tile(x,25)
plot(x, y5, type = "l", col = "green", ylim = c(0,18.5),lwd=2)
lines(x, y10, type = "l",col = "red",lwd=2)
lines(x, y15, type = "l",col = "blue",lwd=2)
lines(x, y23, type = "l",col = "violet",lwd=2)
lines(x, y24, type = "l",col = "orange",lwd=2)
lines(x, y25, type = "l",col = "purple",lwd=2)
abline(h = 10, col = "brown")
abline(h = 3.33333,col = "black")
legend("topright", legend=c("24", "47", "73", "89", "90", "100"), col=c("green", "red","blue", "violet", "orange", "purple"), cex=0.5, lwd = 2)

x <- seq(0,0.5, length.out = 1000)
y1 <- single_profit_tile(x,1)
y2 <- single_profit_tile(x,2)
y3 <- single_profit_tile(x,3)
y4 <- single_profit_tile(x,4)
y5 <- single_profit_tile(x,5)
plot(x, y1, type = "l", col = "green", ylim = c(0,12.1),lwd=2)
lines(x, y2, type = "l",col = "red",lwd=2)
lines(x, y3, type = "l",col = "blue",lwd=2)
lines(x, y4, type = "l",col = "orange",lwd=2)
lines(x, y5, type = "l",col = "purple",lwd=2)
abline(h = 10, col = "brown")
abline(h = 3.33333,col = "black")
legend("topright", legend=c("12", "15", "17", "21", "24"), col=c("green", "red","blue", "orange", "purple"), cex=0.5, lwd = 2)

x <- seq(0,0.5, length.out = 1000)
y6 <- single_profit_tile(x,6)
y7 <- single_profit_tile(x,7)
y8 <- single_profit_tile(x,8)
y9 <- single_profit_tile(x,9)
y10 <- single_profit_tile(x,10)
plot(x, y6, type = "l", col = "green", ylim = c(0,12.1),lwd=2)
lines(x, y7, type = "l",col = "red",lwd=2)
lines(x, y8, type = "l",col = "blue",lwd=2)
lines(x, y9, type = "l",col = "orange",lwd=2)
lines(x, y10, type = "l",col = "purple",lwd=2)
abline(h = 10, col = "brown")
abline(h = 3.33333,col = "black")
legend("topright", legend=c("27", "30", "35", "41", "47"), col=c("green", "red","blue", "orange", "purple"), cex=0.5, lwd = 2)


x <- seq(0,0.5, length.out = 1000)
y11 <- single_profit_tile(x,11)
y12 <- single_profit_tile(x,12)
y13 <- single_profit_tile(x,13)
y14 <- single_profit_tile(x,14)
y15 <- single_profit_tile(x,15)
plot(x, y11, type = "l", col = "green", ylim = c(0,12.1),lwd=2)
lines(x, y12, type = "l",col = "red",lwd=2)
lines(x, y13, type = "l",col = "blue",lwd=2)
lines(x, y14, type = "l",col = "orange",lwd=2)
lines(x, y15, type = "l",col = "purple",lwd=2)
abline(h = 10, col = "brown")
abline(h = 3.33333,col = "black")
legend("topright", legend=c("52", "55", "60", "70", "73"), col=c("green", "red","blue", "orange", "purple"), cex=0.5, lwd = 2)


x <- seq(0.15, 0.5, length.out = 1000)
y16 <- single_profit_tile(x,16)
y17 <- single_profit_tile(x,17)
y18 <- single_profit_tile(x,18)
y19 <- single_profit_tile(x,19)
y20 <- single_profit_tile(x,20)
y21 <- single_profit_tile(x,21)
y22 <- single_profit_tile(x,22)
y23 <- single_profit_tile(x,23)
plot(x, y16, type = "l", col = "green",lwd=2)
lines(x, y17, type = "l",col = "red",lwd=2)
lines(x, y18, type = "l",col = "blue",lwd=2)
lines(x, y19, type = "l",col = "violet",lwd=2)
lines(x, y20, type = "l",col = "orange",lwd=2)
lines(x, y21, type = "l",col = "purple",lwd=2)
lines(x, y22, type = "l",col = "grey",lwd=2)
lines(x, y23, type = "l",col = "maroon",lwd=2)
abline(h = 10, col = "brown")
abline(h = 3.33333,col = "black")
legend("topright", legend=c("77", "79", "80", "82", "83", "85","87","89"), col=c("green", "red","blue", "violet", "orange", "purple","grey", "maroon"), cex=0.5, lwd = 2)






























random_vars <- runif(25)
normalized_vars <- random_vars / sum(random_vars)
sorted_tile$plain_profit <- profit_each_tile(sorted_tile$Multiplier, sorted_tile$Hunters,normalized_vars)
sorted_tile[order(sorted_tile$plain_profit),]






