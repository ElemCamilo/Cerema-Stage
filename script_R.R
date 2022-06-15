#Route à changer en fonction de l'ordinateur de l'utilisateur#

data <- read.csv("C:/Users/camal/Documents/Stage_Cerema/Donnees/fichier_donnes.csv", sep = ",")
for (i in 2:length(data)) { 
  data[,i] = as.factor(data[,i])
}
quant = data[,1]
quali = data[,2:length(data)]
mod.data=lm(quant ~ quali)
#anova_mod = anova(mod.data)
summary_anova = summary(mod.data)

sink("C:/Users/camal/Documents/Stage_Cerema/Donnees/data_ex_export.txt")

summary(mod.data)

sink()
