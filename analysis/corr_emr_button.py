import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

params = ["sharpness", "contrast", "brightness", "gamma", "equalization"]


def calculateCorr(df):
    corr = df["diopter"].corr(df["timeFromDisplay_std"])
    return corr


def main():
    df = pd.read_csv("../data/all_integrated_emr_button.csv")
    df = df.dropna()
    df = df[df["diopter"] != 0]
    df = df[df["timeFromDisplay_std"] != 0]
    # sns.heatmap(df.corr())
    # plt.show()
    for param in params:
        scatter(df, param1=param)
    scatter(df)


def scatter(df, param1="diopter", param2="timeFromDisplay_std"):
    plt.scatter(df[param1], df[param2])
    plt.show()


def saveBestParam(df, dioRange=[0, 10], timeRange=[-3.0, 3.0]):
    df = df[df["diopter"] > dioRange[0]]
    df = df[df["diopter"] < dioRange[1]]
    df = df[df["timeFromDisplay_std"] > timeRange[0]]
    df = df[df["timeFromDisplay_std"] < timeRange[1]]
    df.to_csv("../data/best_param.csv", index=False)


if __name__ == "__main__":
    main()
