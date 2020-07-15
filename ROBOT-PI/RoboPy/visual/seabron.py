import seaborn as sns
import matplotlib
import pandas

sns.set()
teste = pandas.read_csv("teste_27-02-2020.csv")

## modelo:
#sns.relplot(x="", y="", col="", hue="", style="", size="", data=tips)

sns.relplot(x="teste", y="desvio", hue="direcao", size="desvio", data=teste);
#sns.lmplot(x="teste", y="desvio", data=teste);

matplotlib.pyplot.show()
