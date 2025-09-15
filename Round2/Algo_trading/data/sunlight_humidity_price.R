
plot(dayn1$ORCHIDS, dayn1$HUMIDITY,col = "green",ylim = c(80,100),xlim = c(1000, 1240))
points(day0$ORCHIDS, day0$HUMIDITY,col = "red")
points(day1$ORCHIDS, day1$HUMIDITY,col = "blue")

orchids_data <- rbind(dayn1, day0, day1)
orchids_data$SUNLIGHT_group <- cut(orchids_data$SUNLIGHT, breaks = c(0,2500,10000), labels = c("low","high"),right = TRUE)
orchids_data$humid_group <- cut(orchids_data$HUMIDITY, breaks = c(0,60,80,100), labels = c("bad","good","bad"),right = TRUE)

model1 <- lm(ORCHIDS ~ 1+ HUMIDITY+ HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==-1  ,])
model2 <- lm(ORCHIDS ~ 1+ HUMIDITY + HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==0  ,])
model3 <- lm(ORCHIDS ~ 1+ HUMIDITY+HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==1  ,])
model4 <- lm(ORCHIDS ~ 1+ HUMIDITY+HUMIDITY:SUNLIGHT_group,data = orchids_data)

model5 <- lm(ORCHIDS ~ 1+ HUMIDITY:+ HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==-1 & orchids_data$HUMIDITY >80,])
model6 <- lm(ORCHIDS ~ 1+ HUMIDITY+ HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==0 & orchids_data$HUMIDITY >80,])
model7 <- lm(ORCHIDS ~ 1+ HUMIDITY+ HUMIDITY:SUNLIGHT_group,data = orchids_data[orchids_data$DAY ==1 & orchids_data$HUMIDITY >80,])


orchids_data$humid_group <- factor(orchids_data$humid_group, levels = c("bad", "good"))
model8 <- lm(ORCHIDS ~ 1+ humid_group:HUMIDITY:SUNLIGHT_group+ SUNLIGHT_group:SUNLIGHT:humid_group,data = orchids_data[orchids_data$DAY ==-1  ,])
model9 <- lm(ORCHIDS ~ 1+ humid_group:HUMIDITY:SUNLIGHT_group+ SUNLIGHT_group:SUNLIGHT:humid_group,data = orchids_data[orchids_data$DAY ==0  ,])
model10 <- lm(ORCHIDS ~ 1+ humid_group:HUMIDITY:SUNLIGHT_group+ SUNLIGHT_group:SUNLIGHT:humid_group,data = orchids_data[orchids_data$DAY ==1  ,])

model11 <- lm(ORCHIDS ~ 1+ humid_group:HUMIDITY:SUNLIGHT_group+ SUNLIGHT_group:SUNLIGHT:humid_group,data = orchids_data)



humid1 <- lm(ORCHIDS ~ 1+ HUMIDITY + SUNLIGHT,data = dayn1[dayn1$HUMIDITY > 80 & dayn1$SUNLIGHT > 2500,])
humid2 <- lm(ORCHIDS ~ 1+ HUMIDITY +  SUNLIGHT,data = day0[day0$HUMIDITY > 80,])
humid3 <- lm(ORCHIDS ~ 1+ HUMIDITY + SUNLIGHT,data = day1[day1$HUMIDITY > 80,])


