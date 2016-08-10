import pandas as pd
achilles = pd.read_csv("./rnai_datasets/Achilles_QC_v2.4.3.rnai.Gs.gct",skiprows=(0,1),sep="\t",index_col=0)
name_dict = {}
with open("./rnai_datasets/achilles_to_cancergd.txt","rU") as f :
    for i in f :
        parts = i.strip().split()
        name_dict[parts[0]] = parts[1]
achilles.rename(columns=name_dict,inplace=True)
achilles = achilles.T
achilles.to_csv("./rnai_datasets/Achilles_QC_v2.4.3_cancergd.txt",sep="\t")

