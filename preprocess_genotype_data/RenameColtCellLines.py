import pandas as pd
colt = pd.read_csv("./rnai_datasets/breast_zgarp.txt",sep="\t",index_col=0)
name_dict = {}
for i in colt.columns.values[2:] :
    name_dict[i] = "%s_BREAST" % i.upper()
colt.rename(columns=name_dict,inplace=True)
colt=colt.T
colt.to_csv("./rnai_datasets/coltv2_zgarp_cancergd.txt",sep="\t")