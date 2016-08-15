#!/usr/bin/env python



infile = "preprocess_genotype_data/rnai_datasets/coltv2_zgarp_cancergd.txt";
outfile = "preprocess_genotype_data/rnai_datasets/coltv2_zgarp_cancergd_reformatted_by_python.txt";
outfile2 = "preprocess_genotype_data/sjb_colt_tissues_again.txt"
#        1       2       9       10      12      13      14      15      16      18      19      20      21      22      23      24
# symbol  A1BG    A2M     NAT1    NAT2    SERPINA3        AADAC   AAMP    AANAT   AARS    ABAT    ABCA1   ABCA2   ABCA3   ABCB7   ABCF1
# gene_name       alpha-1-B glycoprotein  alpha-2-macroglobulin   N-acetyltransferase 1 (arylamine N-acetyltransferase)   N-acetyltransf
# 184A1_BREAST    -0.795  -2.73   0.677   1.159   -2.292  0.649   0.58    0.257   1.0490000000000002      -1.635  0.149   0.08    -0.467
# 184B5_BREAST    0.337   0.47700000000000004     1.19    -0.56   0.478   -1.7830000000000001     -0.873  -0.129  1.245   -0.951  1.11


# To:

# WAS: 198_boxplots_for_Colm/data_sets/colt_study_breast/zGARP_scores_transposed_with_Intercell_names_from_James_with_entrez_ids_added.txt


# cell.line       A1BG_1  A2M_2   NAT1_9  NAT2_10 SERPINA3_12     AADAC_13        AAMP_14 AANAT_15        AARS_16 ABAT_18 ABCA1_19
# 184A1_BREAST    -0.795  -2.73   0.677   1.159   -2.292  0.649   0.58    0.257   1.049   -1.635  0.149   0.08    -0.468  -3.973  -1.162
# 184B5_BREAST    0.337   0.477   1.19    -0.56   0.478   -1.783  -0.873  -0.129  1.245   -0.951  1.11    0.275   -0.311  -0.557  -0.025
# 600MPE_BREAST   -0.812  -0.704  -0.064  -2.11   -2.131  -0.574  -0.795  0.158   0.514   -0.93   0.158   0.072   -1.171  -1.121  -1.507
# AU565_BREAST    -0.915  -0.168  -0.561  -0.966  -0.105  0.119   -2.151  -1.742  -0.239  -2.77   0.001   0.352   -1.298  0.351   0.381
# BT20_BREAST     -0.059  -1.73   -0.059  -0.966  -0.749  0.436   -1.498  -0.575  0.451   -0.734  0.603   0.163   -0.809  -2.228  -0.2

print("Reformatting "+infile)
with open(infile) as fin:
  with open(outfile, "w") as fout:
    entrezids = fin.readline().rstrip("\r\n").split("\t") # Read and split header entrez ids line
    symbols = fin.readline().rstrip("\r\n").split("\t") # Read remove any DOS line endings, and split header symbol line
    #print(symbols)    
    if symbols[0] != "symbol":
      print("Expected 'symbol' for first name in symbols line, but got '%s'" %(symbols[0]))
      exit()
      
    if len(entrezids) != len(symbols):
      print("Num Entrez != Num Symbol")
      exit()
      
    descriptions = fin.readline() # Ignore this line of descriptions

    print("Num symbols: %d\n" %(len(symbols)-1)) # -1 as first is 'symbol'
      
    fout.write("cell.line") # Write the 'cell.line' first col heading
            
    for i in range(1,len(symbols)):      
#        entrez = symbol_to_enterez_dict.get(col[i], 'NoEntrezId') # was 'EntrezNotFound' but too long for the 10 character entrez_id field.
#        if entrez == 'NoEntrezId':
#          print("ERROR: Couldn't find entrez id for "+col[i])
      if entrezids[i] == "":
         print("*** No Entrez id for "+symbols[i])
      new_name = symbols[i]+'_'+entrezids[i]
      # print(new_name)
      fout.write("\t"+new_name)
    fout.write("\n")

    with open(outfile2, "w") as fout2:
      fout2.write("cell.line\tBREAST\tBONE\n")      
      for line in fin:
        cols = line.rstrip("\r\n").split("\t") # Read remove any DOS line endings, and split header symbol line.
        fout.write(cols[0])
        for i in range(1,len(cols)):
          fout.write( ("\t%0.3f" %(float(cols[i]))).rstrip('0').rstrip('.') ) # Three decimal places and trim trailing zeros
        fout.write("\n")
        fout2.write(cols[0]+"\t1\t0\n") # The '1' is for BREAST column


print("Finished");
