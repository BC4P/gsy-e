import pandas as pd
import os

#df = pd.read_csv(os.path.join(os.getcwd(),"src","gsy_e","resources","fh_data-2022-05-09.csv"), sep=",", header=0)
df = pd.read_csv(os.path.join(os.getcwd(),"fh_data_day.csv"), sep=",", header=0, skiprows=1)

print(df.drop('Time', axis=1).sum(axis=1))
#print(df.sum(axis=1))

data = [df["Time"], df.drop("Time", axis=1).sum(axis=1)]

headers = ["Time", "W"]


df3 = pd.concat(data, axis=1, keys=headers)

print(df3)

df3["Time"] -= df3["Time"][0]


df3 = df3.reset_index()

d = {'Time': 'first', 'W': 'sum'}

df4 = df3.groupby(df3.index // 15).agg(d)

df4["Time"] = pd.to_datetime(df4['Time'], unit='ms').dt.time

print(df4)

df4.to_csv("out.csv",sep=";", index=False) 