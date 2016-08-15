#!/usr/bin/env python

# script to add Entrez ids to the transposed zScore data that came from James.

dir = "198_boxplots_for_Colm/data_sets/colt_study_breast/"

entrez_symbol_file = dir + "breast_zgarp.txt"
zScores_file = dir + "zGARP_scores_transposed_with_Intercell_names_from_James.txt"
zScores_file_with_entrez_ids = dir + "zGARP_scores_transposed_with_Intercell_names_from_James_with_entrez_ids_added.txt"
zScores_tissue_file = dir + "zGARP_tissues.txt"


print("Reading entrez_symbol_file ...")
symbol_to_enterez_dict = dict()
with open(entrez_symbol_file) as f:
  line = f.readline() # ignore the header line
  print(line)
  for line in f:
    col = line.split("\t")
    if col[1] in symbol_to_enterez_dict:
      print("ERROR: symbol exists already: "+col[1])
    else:
  	  symbol_to_enterez_dict[col[1]] = col[0]


print("Adding entrez ids to zScore file ...")
with open(zScores_file) as fin:
  with open(zScores_file_with_entrez_ids, "w") as fout:
    with open(zScores_tissue_file, "w") as fout2:
      col = fin.readline().rstrip("\r\n").split("\t") # Read and split header line
      fout.write(col[0]) # Write the 'cell.line' first col heading
      for i in range(1,len(col)):
        entrez = symbol_to_enterez_dict.get(col[i], 'NoEntrezId') # was 'EntrezNotFound' but too long for the 10 character entrez_id field.
        if entrez == 'NoEntrezId':
          print("ERROR: Couldn't find entrez id for "+col[i])

        new_name = col[i]+'_'+entrez
        print(new_name)
        fout.write("\t"+new_name)
      fout.write("\n")

      fout2.write("cell.line\tBREAST\tBONE\n")
      for line in fin:
        fout.write(line)
        col = line.split("\t")
        fout2.write(col[0]+"\t1\t0\n") # The '1' is for BREAST column


# cell.line       BONE    BREAST  CENTRAL_NERVOUS_SYSTEM  CERVICAL        ENDOMETRIUM     ....
# 143B_BONE       1       0       0       0       0       0       0       0       0       0
# 93VU_HEADNECK   0       0  
      

print("Finished")


"""
Adding entrez ids to zScore file ...
ERROR: Couldn't find entrez id for 37864
ERROR: Couldn't find entrez id for 35673
ERROR: Couldn't find entrez id for 36038
ERROR: Couldn't find entrez id for 37134
ERROR: Couldn't find entrez id for 40786
ERROR: Couldn't find entrez id for 37315
ERROR: Couldn't find entrez id for 38595
ERROR: Couldn't find entrez id for 37499
ERROR: Couldn't find entrez id for 35764
ERROR: Couldn't find entrez id for 35854
ERROR: Couldn't find entrez id for 36950
ERROR: Couldn't find entrez id for 35489
ERROR: Couldn't find entrez id for 36403
ERROR: Couldn't find entrez id for 36585
ERROR: Couldn't find entrez id for 35489
ERROR: Couldn't find entrez id for 37680
ERROR: Couldn't find entrez id for 38411
ERROR: Couldn't find entrez id for 36219
ERROR: Couldn't find entrez id for 39691
ERROR: Couldn't find entrez id for 38960
ERROR: Couldn't find entrez id for 38776
ERROR: Couldn't find entrez id for 38046
ERROR: Couldn't find entrez id for 40421
Finished
"""