dayn1_imex <- cbind(dayn1, export_price = dayn1$ORCHIDS - dayn1$EXPORT_TARIFF - dayn1$TRANSPORT_FEES, import_price = dayn1$ORCHIDS + dayn1$IMPORT_TARIFF + dayn1$TRANSPORT_FEES)

day0_imex <- cbind(day0, export_price = day0$ORCHIDS - day0$EXPORT_TARIFF - day0$TRANSPORT_FEES, import_price = day0$ORCHIDS + day0$IMPORT_TARIFF + day0$TRANSPORT_FEES)

day1_imex <- cbind(day1, export_price = day1$ORCHIDS - day1$EXPORT_TARIFF - day1$TRANSPORT_FEES, import_price = day1$ORCHIDS + day1$IMPORT_TARIFF + day1$TRANSPORT_FEES)

par(mfrow=c(1,1))
plot(dayn1_imex$timestamp, dayn1_imex$export_price,type = "l",col = "blue", ylim = c(min(dayn1_imex$export_price),max(dayn1_imex$import_price)))
lines(dayn1_imex$timestamp, dayn1_imex$import_price,type = "l",col = "orange")
plot(day0_imex$timestamp, day0_imex$export_price,type = "l",col = "blue",ylim = c(min(day0_imex$export_price),max(day0_imex$import_price)))
lines(day0_imex$timestamp, day0_imex$import_price,type = "l",col = "orange")


plot(day1_imex[day1_imex$timestamp<10000,]$timestamp, day1_imex[day1_imex$timestamp<10000,]$export_price,type = "l",col = "blue",ylim = c(1060,1110))
lines(day1_imex[day1_imex$timestamp<10000,]$timestamp, day1_imex[day1_imex$timestamp<10000,]$import_price,type = "l",col = "orange")
lines(orchids_sim$timestamp, orchids_sim$ask_price_1,type = "l",col = "green")
lines(orchids_sim$timestamp, orchids_sim$bid_price_1,type = "l",col = "red")
legend("topright",legend = c("export","import", "ask", "bid"), col = c("blue", "orange", "green", "red"), lty = 1, pch=1,bty="n", cex = 0.6)



dayn1_imex$spread <- dayn1_imex$import_price - dayn1_imex$export_price 

hist(dayn1_imex$spread)
summary(dayn1_imex$spread)


