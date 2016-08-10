import pandas as pd
intercell = pd.read_csv("./rnai_datasets/Intercell_v18_rc4_kinome_zp0_for_publication.txt",sep="\t")
name_dict = {}
with open("./rnai_datasets/intercell_to_cancergd.txt","rU") as f :
    for i in f :
        parts = i.strip().split()
        name_dict[parts[0]] = parts[1]
for i in intercell.index :
    if intercell.loc[i,'cell.line'] in name_dict :
        intercell.loc[i,'cell.line'] = name_dict[intercell.loc[i,'cell.line']]
intercell.to_csv("./rnai_datasets/Intercell_v18_rc4_kinome_cancergd.txt",sep="\t",index=False)


