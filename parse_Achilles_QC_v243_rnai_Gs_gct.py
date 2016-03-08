#!/usr/bin/env python

# The Windows 'py' launcher should also recognise the above shebang line.
# Script for reformatting the Achilles data, which is in gene pattern file format

# Achilles data from the Broad institute:
#     https://www.broadinstitute.org/achilles/datasets/5/download
#     Downloaded this file: Achilles_QC_v2.4.3.rnai.Gs.gct

"""
# The paper from: http://www.nature.com/articles/sdata201435

File 5. ‘Achilles_QC_v2.4.3.rnai.Gs.gct’  - "The final gene-level file obtained after analysis of the shRNA level file with the ATARiS algorithm. This is a.gct formatted file, with cell lines in columns and ATARiS gene solutions in rows. ATARiS gene solutions are in the 1st column (labeled ‘Name’) and gene names are in the 2nd column (labeled ‘Description’)."

.gct = a gene pattern file
Add two header rows at the top of the file:
In the first row, first cell, is format ?version: #1.2
In the second row, first cell, is the number of data rows: 1553
In the second row, second cell, is the number of data columns: 44

#1.2
5711    216
Name    Description     22RV1_PROSTATE  697_HAEMATOPOIETIC_AND_LYMPHOID_TISSUE  786O_KIDNEY     A1207_CENTRAL_NERVOUS_SYSTEM    A172_CENTRAL_NERVOUS_SYSTEM     A204_SOFT_TISSUE
A2ML1_1_01110   A2ML1   0.394594398957629       0.730797648888988       -1.20098807484231       -0.36632733293908       -0.315740208758283      0.485359368104152       0.747857928
AADAC_1_11001   AADAC   -0.130884097950207      -0.621311438047424      -1.28082224322258       1.15587629057016        0.846034797165431       0.339625591051888       0.635004230
AADAT_1_11010   AADAT   -1.23371723221934       1.63082466624542        -0.609780953932604      0.220788092664123       0.520918905779165       1.62510322574951        0.744893487
AADAT_2_00101   AADAT   0.540022249007015   

"""

import os, csv

analysis_dir = "Achilles_data"

achilles_file = os.path.join(analysis_dir, "Achilles_QC_v2.4.3.rnai.Gs.gct")
gene_mapping_file = os.path.join(analysis_dir, "shRNA_to_gene_mapping_CP0004_20131120_19mer_trans_v1.chip")

output_file1 = os.path.join(analysis_dir, "Achilles_rnai_transposed_for_R.txt")
output_file2 = os.path.join(analysis_dir, "Achilles_tissue_types.txt")

"""
mapping is: 
Achilles_QC_v2.4.3.rnai.Gs.gct
  AAK1_1_01111011111
  AAK1_2_10000100000
  
  shRNAs_used_in_ATARiS_gene_solutions_Achilles_QC_v2.4.3.shRNA.table.txt
  shRNA   gene.symbol     isUsed  sol.number 
  (can ignore the isUsed FALSE)
  
  ACAAACCAACAAGCAGTCGAT_AAK1      AAK1    TRUE    2       AAK1_2_10000100000      10000100000     2.14    0.00719 0.0352
  CACACCTGTAATCCCAGCATT_AAK1      AAK1    TRUE    1       AAK1_1_01111011111      01111011111     5.15    7.1e-06 0.00011
  CACCTGTAATCCCAGCACTTT_AAK1      AAK1    TRUE    1       AAK1_1_01111011111      01111011111     1.06    0.0879  0.207
  CCAGGCTTTCAATCAACCCAA_AAK1      AAK1    TRUE    1       AAK1_1_01111011111      01111011111     0.963   0.109   0.246
  CCAGGTGTGCAAGAGAGAAAT_AAK1      AAK1    TRUE    1       AAK1_1_01111011111      01111011111     1.26    0.0545  0.141
  CCCAGTAAGACAACAGCCAAA_AAK1      AAK1    TRUE    2       AAK1_2_10000100000  

  to:
  ACAAACCAACAAGCAGTCGAT   AAK1    NM_014911.3     22848
  (sequence is used for many gene_names, so need sequence+gene_name)
"""
  
genemap = dict() # To read mapping of the Achilles gene names to Entrez ids and Transcripts
def load_gene_mapping():
  global genemap, jgene_symbol, jentrez_id
  print("\nLoading Achilles gene mapping data")
  dataReader = csv.reader(open(gene_mapping_file), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      cols = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
      jbarcode     = cols.get('Barcode Sequence') # AAAAATGGCATCAACCACCAT (for the shRNA)
      jgene_symbol = cols.get('Gene Symbol')      # eg: RPS6KA1
      jtranscript  = cols.get('Transcript')       # eg: NM_001006665.1
      jentrez_id   = cols.get('Gene ID')          # eg: 6195
    else:
      #gene_name = row[jgene_symbol]
      key = row[jbarcode] + '_' + row[jgene_symbol]
      # gene_name = row[jbarcode]
      if key in genemap:
        if genemap[key][jentrez_id] != row[jentrez_id]:
          print("*** ERROR: Duplicated  Entrez_ids %s %s  Transcripts: %s %s  Key %s: " %(genemap[key][jentrez_id], row[jentrez_id], genemap[key][jtranscript], row[jtranscript], key))
        """
There are three genes with duplictaes:

*** ERROR: Duplicated  Entrez_ids 100289635 90462  Transcripts: NM_183238.3 XR_110947.2  Key CAATAGAGAAACCCTACAGTT_ZNF605 (NOT USED)

*** ERROR: Duplicated  Entrez_ids 115653 100133046  Transcripts: NM_153443.3 XM_003119105.2  Key CACAGTTGAATCACTGCGTTT_KIR3DL3 (IS USED)

*** ERROR: Duplicated  Entrez_ids 22947 100288687  Transcripts: NM_033178.2 NR_038191.1  Key AGATCTGGTTTCAGAATCGAA_DUX4 (NOT USED)
        """          
        #if genemap[key][jtranscript] != row[jtranscript]:
        #  print("*** ERROR: Duplicated key %s:  Transcripts: %s %s" %(key, genemap[key][jtranscript], row[jtranscript]))

        
        #if genemap[gene_name][jentrez_id] != row[jentrez_id]:
          #print("*** ERROR: Duplicated gene_name %s with different Entrez_ids %s and %s in genemap file" %(gene_name, genemap[gene_name][jentrez_id], row[jentrez_id]))
        #if genemap[gene_name][jgene_symbol] != row[jgene_symbol]:
         # print("*** ERROR: Duplicated gene_name %s with different Gene_symbol %s and %s in genemap file" %(gene_name, genemap[gene_name][jgene_symbol], row[jgene_symbol]))  
        #if genemap[gene_name][jtranscript] != row[jtranscript]:
        #  print("*** ERROR: Duplicated gene_name %s with different Transcripts %s and %s in genemap file" %(gene_name, genemap[gene_name][jtranscript], row[jtranscript]))
      genemap[key] = row
      #genemap[gene_name] = row
   

hgnc = dict() # To read the HGNC ids into a dictionary
synonyms_to_hgnc = dict()
#ihgnc = dict() # The column name to number for the above HGNC dict. 
def load_hgnc_dictionary():
  global hgnc, synonyms_to_hgnc, isymbol, isynonyms, iprev_names, iensembl_id, ientrez_id, ihgnc_id
  print("\nLoading HGNC data")
  # Alternatively use the webservice: http://www.genenames.org/help/rest-web-service-help
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      ihgnc = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): ihgnc[row[i]] = i       # Store column numbers for each header item
      isymbol     = ihgnc.get('symbol') # eg: 
      isynonyms   = ihgnc.get('alias_symbol')    # eg: NEU|HER-2|CD340|HER2
      iprev_names = ihgnc.get('prev_symbol')     # eg: NGL
      ientrez_id  = ihgnc.get('entrez_id')       # eg: 2064      
      iensembl_id = ihgnc.get('ensembl_gene_id') # eg: ENSG00000141736
      ihgnc_id    = ihgnc.get('hgnc_id')         # eg: 
    else:
      gene_name = row[isymbol]    # The "ihgnc['symbol']" will be 1 - ie the second column, as 0 is first column which is HGNC number
      if gene_name in hgnc:
        print("*** ERROR: Duplicated gene_name in HGNC file: ",gene_name)
      hgnc[gene_name] = row # Store the whole row for simplicity. 
      # print("%s : prev_names=%s, synonyms=%s" %(gene_name,row[iprev_names],row[isynonyms]))
      synonym_list = row[isynonyms].split('|')
      synonym_list.extend( row[iprev_names].split('|') )
      for key in synonym_list:
        if key == '': continue
        # print("  key:",key)
        if key in synonyms_to_hgnc:
          print("**** ERROR: For gene %s Synonym %s already exists in gene %s:" %(gene_name,key,synonyms_to_hgnc[key]))
          synonyms_to_hgnc[key] += ';'+gene_name
        else:
          synonyms_to_hgnc[key] = gene_name
      
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])

load_gene_mapping()
print("GENE:",genemap["ERBB2"])
exit()


load_hgnc_dictionary()
print("Reading Achilles file")
list_of_lists = []
with open(achilles_file, "r") as f:
    version = f.readline().rstrip() # remove trailing whitespace (newline) character, but will remove tabs at end - ie. any empty fields at end of line
    if version != '#1.2': print("*** ERROR: expected #1.2 at start of input file: ", version)  # will be '#1.2'
    num_rows,num_cols = f.readline().rstrip().split("\t")
    num_rows = int(num_rows)
    num_cols = int(num_cols)
    print("Version: %s Rows: %d Cols: %d" %(version,num_rows,num_cols))
    header = f.readline().rstrip().split("\t")
    if header[0] != 'Name' or header[1] != 'Description': print("*** ERROR: expected Name and Description, but read: '%s' '%s'" %(header[0], header[1]))
    list_of_lists.append(header)
    for line in f:
        inner_list = [elt.rstrip() for elt in line.split("\t")]
        # in alternative, if you need to use the file content as numbers
        # inner_list = [int(elt.strip()) for elt in line.split("\t")]
        list_of_lists.append(inner_list)


# Using this zip would be faster:
# list_of_lists = zip(*list_of_lists) # transpose rows and columns.

if len(list_of_lists) != num_rows+1: print("**ERROR: len(list_of_lists)=%s != num_rows=%d" %(len(list_of_lists),num_rows+1))
if len(list_of_lists[0]) != num_cols+2:  print("**ERROR: len(list_of_lists)=%s != num_cols+2=%d" %(len(list_of_lists[0]),num_cols+2))


def format_tissue(tissue):
    t=tissue.split("_") # eg: A1207_CENTRAL_NERVOUS_SYSTEM
    return "_".join(t[1:])

def get_ensembl_name(gene_name):
    if gene_name not in hgnc:
        if gene_name in synonyms_to_hgnc:
            # print("Found gene_name %s in synonyms for %s" %(gene_name,synonyms_to_hgnc[gene_name]))
            new_name = synonyms_to_hgnc[gene_name]
            if ';' in new_name:
                print("** WARNING: %s BUT Synonym is ambigious %s" %(gene_name,new_name))
                return gene_name+"_Unsure_"+new_name
            gene_name = new_name    
            # so search the: isynonyms, iprev_names   eg: reformat hgnc as: '|'+(iprev_names+'|' + isynonyms)+'|'
            # then look for   '|'+gene_name+'|'
        else:
           print("** WARNING: Gene NOT found in hgnc", gene_name)
           return gene_name+"_NotFound"
    return gene_name+'_'+hgnc[gene_name][iensembl_id]

    
print("Writing transformed files")    
cell_lines = []
tissue_types = dict()   # Tissue types eg: "HAEMATOPOIETIC AND LYMPHOID TISSUE" from "697_HAEMATOPOIETIC_AND_LYMPHOID_TISSUE"
# Write transposed file:
with open(output_file1, "w") as fout:
    fout.write("cell.line")
    # Take leftmost column (col=0):
    for row in range(1,num_rows):
        n = (list_of_lists[row][0]).split("_")
        fout.write("\t%s" %(get_ensembl_name(n[0])))  # Not using a variant suffix number at present.
        # fout.write("\t%s_%s" %(n[0],get_ensembl_name(n[0])))  # Not using a variant suffix number at present.
        #fout.write("\t%s%s_%s" %(n[0],n[1],get_ensembl_name(n[0]))) # ie. the original left-most column of names, 'ABL1_1_1110001111' becomes 'ABL11'
    fout.write("\n")

    # Skip column 2 (col=1)

    for col in range(2,num_cols):  # ie. skip the original left-most two columns
        cell_line = list_of_lists[0][col]
        cell_lines.append(cell_line)
        tissue = format_tissue(cell_line) # eg: A1207_CENTRAL_NERVOUS_SYSTEM
        tissue_types[tissue] = tissue_types.get(tissue, 0) + 1
        
        fout.write(list_of_lists[0][col])
        for row in range(1,num_rows):
            fout.write("\t%s" %(list_of_lists[row][col])) # ie. the original left-most column of names
        fout.write("\n")

print("\n\nNumbers of each tissue type:")
for key in sorted(tissue_types):
    print("%s: %d" %(key,tissue_types[key]))

with open(output_file2, "w") as fout:
    fout.write("cell.line")
    i = 0
    for key in sorted(tissue_types):
        fout.write("\t"+key)
        tissue_types[key]=i
        i+=1
    fout.write("\n")
    # print(tissue_types)

    for c in sorted(cell_lines):
        fout.write(c)
        tissue=format_tissue(c) # eg: A1207_CENTRAL_NERVOUS_SYSTEM    
        #print(c,tissue)
        s=''
        for i in range(0,len(tissue_types)):
            if i == tissue_types[tissue]:
                fout.write("\t1")
            #    s=s+'1'
            else:
                fout.write("\t0")
            #    s=s+'0'
        #print(c,tissue,tissue_types[tissue],s)        
        fout.write("\n")

"""    

i = 0
for name in list_of_lists[0]:  # ie. the original left-most column
#    if i == 0: print("")
    print("name, list",name,list_of_lists[1][i])
    n = name.split("_")
    if list_of_lists[1][i] != n[0]: print("ERROR: name '%s' and desc '%s' mismatch" %(list_of_lists[1][i], n[0]))
    print("\t%s%s" %(n[0],n[1]))  # So 'ABL1_1_1110001111' becomes 'ABL11'
    i+=1



for row in range(0,num_row):  # ie. the original left-most column
#    if i == 0: print("")
    print("name, list",name,list_of_lists[1][i])
    n = name.split("_")
    if list_of_lists[1][i] != n[0]: print("ERROR: name '%s' and desc '%s' mismatch" %(list_of_lists[1][i], n[0]))
    print("\t%s%s" %(n[0],n[1]))  # So 'ABL1_1_1110001111' becomes 'ABL11'
    i+=1
"""
    
# skip list_of_lists[0] as this is just the names.

#for name in list_of_lists[0]:  # ie. the original left-most column
#    n = name.split("_")
#    print("\t%s%s" %(n[0],n[1]))  # So 'ABL1_1_1110001111' becomes 'ABL11'

    
#col_names = ('apples sold', 'pears sold', 'apples revenue', 'pears revenue')
#by_names = {}
#for i, col_name in enumerate(col_names):
#    by_names[col_name] = by_cols[i]
    
        
#gtc_version=
#num_rows, num_cols

#headers

#name, desc values .....

#transpose, add ensembl id

#Note: This includes variants of the same gene, eg:
#ABL1_1_1110001111       ABL1    ....
#ABL1_2_0001100000       ABL1    ....

#(Maybe test if unique at the second digit eg. ABL1_1, ABL1_2, then rename to ABL11, ABL12