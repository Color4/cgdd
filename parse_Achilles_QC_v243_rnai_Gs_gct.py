#!/usr/bin/env python

# This script to to generate the data for input to R.


# 22 March 2016:
Partly added the ensembl_protein_id - but NOT finished - (simpler to annotate database after data is loaded into database) - so use the earlier script if need to rebuild the Achilles R input data.

# To load the Achilles data after R, use load_data.py


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
import mygene

analysis_dir = "Achilles_data"

achilles_file = os.path.join(analysis_dir, "Achilles_QC_v2.4.3.rnai.Gs.gct")
shRNA_mapping_file = os.path.join(analysis_dir, "shRNA_to_gene_mapping_CP0004_20131120_19mer_trans_v1.chip")
ATAR_mapping_file =  os.path.join(analysis_dir, "shRNAs_used_in_ATARiS_gene_solutions_Achilles_QC_v2.4.3.shRNA.table.txt")

read_R_cnv_muts_file = "198_boxplots_for_Colm/data_sets/func_mut_calls/combined_exome_cnv_all_muts_150225.txt"
read_R_kinome_file = "198_boxplots_for_Colm/data_sets/siRNA_Zscores/Intercell_v18_rc4_kinome_zp0_for_publication.txt"


analysis_dir = "Achilles_data"
output_file1 = os.path.join(analysis_dir, "Achilles_rnai_transposed_for_R_kinome_v3_12Mar2016.txt")
output_file2 = os.path.join(analysis_dir, "Achilles_tissues_v3_12Mar2016.txt")
output_file3 = os.path.join(analysis_dir, "Achilles_solname_to_entrez_map.txt")
output_file4_newnames = os.path.join(analysis_dir, "Achilles_solname_to_entrez_map_with_names_used_for_R_v3_12Mar2016.txt")


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

entrez_ids_renamed = {  # better to initialise here using {...} rather than dict(...)
  '244'      : '728113',   # confirmed on entrez ANXA8L2 -> ANXA8L1
  '9503'     : '653067',   # confirmed on entrez XAGE1D -> XAGE1E
  '90462'    : '100289635',# confirmed on entrez LOC90462 is withdrawn as redundant in assembly (renaming 100289635 as ZNF605).
  '164022'   : '653505',   # confirmed on entrez PPIAL4A -> PPIAL4A
  '399753'   : '414224',   # confirmed on entrez LOC399753 -> AGAP12P
  '554045'   : '100288711',# confirmed on entrez DUX4L9 -> DUX4L9  
  '653048'   : '653067',   # confirmed on entrez XAGE1C -> XAGE1E
  '653219'   : '653220',   # confirmed on entrez XAGE1A -> XAGE1B
  '653501'   : '401509',   # confirmed on entrez LOC653501 -> ZNF658B
  '727787'   : '3812',     # confirmed on entrez LOC727787 -> KIR3DL2
  '728127'   : '653234',   # confirmed on entrez AGAP10 -> AGAP10P
  '100036519': '349334',   # confirmed on entrez FOXD4L2 -> FOXD4L4  
  '100131392': '729384',   # confirmed on entrez LOC100131392 -> TRIM49D2
  '100131530': '5435',     # confirmed on entrez LOC100131530 -> POLR2F
  '100133046': '115653',   # confirmed on entrez KIR3DL3 -> KIR3DL3 (ie. same symbol)
  '100170939': '11039',    # confirmed on entrez LOC100170939 -> SMA4
  '100287534': '3805',     # confirmed on entrez LOC100287534 -> KIR2DL4
#  '100288687': '22947',    # *not* same on entrez nor on NGNC. DUX4 (HGNC:50800; also known as DUX4L) different record from DUX4L1 (HGNC:3082; also known previously as DUX4; DUX10)
  '100505503': '6218',     # confirmed on entrez RPS17L -> RPS17
  '100505793': '10772',    # confirmed on entrez LOC100505793 -> SRSF10
  '100506499': '196913',   # confirmed on entrez LOC100506499 -> LINC01599
  '100506859': '341676',   # confirmed on entrez LOC100506859 -> 
  '100507018': '101927612',# confirmed on entrez RNF139-AS1 -> RNF139-AS1
  '100507699': '728806',   # confirmed on entrez LOC100507699 -> NSFP1
  '100509575': '280657',   # confirmed on entrez LOC100509575 -> SSX6
  '100509582': '3126',     # confirmed on entrez LOC100509582 -> HLA-DRB4
  '100653070': '11026',    # confirmed on entrez LOC100653070 -> LILRA3
  '100653112': '266722'    # confirmed on entrez LOC100653112 -> HS6ST3
}

  
shRNAmap = dict() # Map of the Achilles shRNA names (sequence_name, eg: AAAAATGGCATCAACCACCAT_RPS6KA1) to Entrez ids (and Transcripts).
def load_shRNAmap():
  global shRNAmap, jgene_symbol, jentrez_id
  print("\nLoading Achilles shRNA mapping data")
  dataReader = csv.reader(open(shRNA_mapping_file), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  # Format for file: "shRNA_to_gene_mapping_CP0004_20131120_19mer_trans_v1.chip"
  # Barcode Sequence        Gene Symbol     Transcript      Gene ID
  # AAAAATGGCATCAACCACCAT   RPS6KA1         NM_001006665.1  6195
  # AAAAATGGCATCAACCACCAT   RPS6KA1         NM_002953.3     6195
  # AAAAGGATAACCCAGGTGTTT   TSC1            NM_000368.4     7248

  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      cols = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
      jbarcode     = cols.get('Barcode Sequence') # AAAAATGGCATCAACCACCAT (for the shRNA)
      jgene_symbol = cols.get('Gene Symbol')      # eg: RPS6KA1
      jtranscript  = cols.get('Transcript')       # eg: NM_001006665.1
      jentrez_id   = cols.get('Gene ID')          # eg: 6195
    else:
      key = row[jbarcode] + '_' + row[jgene_symbol]
      this_entrez_id = row[jentrez_id]
      if this_entrez_id in ('-40', '-43'): # "if this_entrez_id in ('-40')" also matches for this_entrez_id is '40'
              # BECAUSE python treats a single item in brackets as one string, not as a list, so need to use ("-40",) to force python to recognise this as a list
        print("*** WARNING: Entrez_id '%s' is negative for:" %(this_entrez_id),row)
        # sys.exit
        # -43 is 'Luciferase', which isn't a human gene.
        # -40 is 'BFP', which is probably: Blue Fluorescent Protein (BFP), a Blue variant of Aequoria victoria GFP. so non-human.
      #print(type(this_entrez_id))
      if this_entrez_id in entrez_ids_renamed:
        this_entrez_id = entrez_ids_renamed[this_entrez_id]
        row[jentrez_id] = this_entrez_id

      if key in shRNAmap:
        if shRNAmap[key][jentrez_id] != this_entrez_id:
          print("*** WARNING: Duplicated  Entrez_ids %s %s  Transcripts: %s %s  Key %s: " %(shRNAmap[key][jentrez_id], this_entrez_id, shRNAmap[key][jtranscript], row[jtranscript], key))
          shRNAmap[key][jentrez_id]  += ';'+this_entrez_id
          print("************* Joining: '%s' '%s'" %(shRNAmap[key][jentrez_id], this_entrez_id))
        if shRNAmap[key][jtranscript] != row[jtranscript]:
          shRNAmap[key][jtranscript] += ';'+row[jtranscript]
        """
There are three genes with duplictaes:
*** Duplicated  Entrez_ids 100289635 90462  Transcripts: NM_183238.3 XR_110947.2  Key CAATAGAGAAACCCTACAGTT_ZNF605 (NOT USED)

*** Duplicated  Entrez_ids 115653 100133046  Transcripts: NM_153443.3 XM_003119105.2  Key CACAGTTGAATCACTGCGTTT_KIR3DL3 (IS USED in the shRHA studies)
   this KIR3DL3 is ok as from: http://www.ncbi.nlm.nih.gov/gene/100133046  says "This record was replaced with Gene ID: 115653"

*** Duplicated  Entrez_ids 22947 100288687  Transcripts: NM_033178.2 NR_038191.1  Key AGATCTGGTTTCAGAATCGAA_DUX4 

        """
      else:   
        shRNAmap[key] = row

ATARmap = dict() # Map of the Achilles ATARiS gene solution names (eg: A2ML1_1_01110) to shRNA names (sequence_name, eg: AAAAATGGCATCAACCACCAT_RPS6KA1).
def load_ATARmap():
  global ATARmap, jshRNA, jisUsed, jsol_name, jsol_entrez
  print("\nLoading Achilles ATARiS gene solution mapping")
  dataReader = csv.reader(open(ATAR_mapping_file), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), 
  # Format for file: "shRNAs_used_in_ATARiS_gene_solutions_Achilles_QC_v2.4.3.shRNA.table.txt"
  # shRNA                      gene.symbol isUsed  sol.number   sol.name     sol.id   cscore   pval    qval
  # CAGTGACAGAAGCAGCCATAT_A1BG      A1BG    FALSE     NA          NA           NA      0.453   0.352   0.715
  # CCGCCTGTGCTGATGCACCAT_A1BG      A1BG    FALSE     NA          NA           NA      0.191   0.644   0.87
  # ...
  # CCTGGTGAAGAAGGTTGAATT_A2ML1     A2ML1   FALSE     NA          NA           NA      0.218   0.605   0.851
  # CTCACTATTCACACCAGTTAT_A2ML1     A2ML1   TRUE      1        A2ML1_1_01110   01110   0.273   0.533   0.813
  # GCAACAATTCAGTATTCTGAT_A2ML1     A2ML1   TRUE      1        A2ML1_1_01110   01110   0.478   0.333   0.68

  print("********** CHECK THESE MyGene same id responses below *******") 
  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      cols = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
      jshRNA     = cols.get('shRNA')     # eg: CTCACTATTCACACCAGTTAT_A2ML1 (for the shRNA)
      jisUsed    = cols.get('isUsed')    # FALSE or TRUE
      jsol_name  = cols.get('sol.name')  # eg: A2ML1_1_01110
      jsol_entrez = len(cols)  # As below appends the entrez_id col onto the row
    elif row[jisUsed] == 'TRUE':
      key = row[jsol_name]
      # print(key)
      this_entrez_id = shRNAmap[row[jshRNA]][jentrez_id]
      if this_entrez_id in ('-40', '-43'):
        print("*********** WARNING: Entrez_id '%s' is negative for %s" %(this_entrez_id,shRNAmap[row[jshRNA]]))
        
      if ';' in this_entrez_id:
        print('WARNING: %s isUsed and has two or more entrez_ids: %s' %(key,this_entrez_id))
      if key in ATARmap:
        shmap_entrez_id = shRNAmap[ATARmap[key][jshRNA]][jentrez_id]
        if shmap_entrez_id != this_entrez_id and this_entrez_id not in shmap_entrez_id.split(';'):  # split as maybe already has 2 entrez ids:
          print("*** ERROR: Different Entrez_ids %s %s for sol.name %s: " %(shmap_entrez_id, this_entrez_id,key)) # Transcripts: %s %s  
          ATARmap[key][jsol_entrez] += ';'+this_entrez_id
          print("************* ATARmap: Joining: '%s' '%s'" %(ATARmap[key][jsol_entrez], this_entrez_id))
      else:
        ATARmap[key] = row
        if len(ATARmap[key]) != jsol_entrez: print("*** ERROR len(ATARmap[key]) != jsol_entrez") # Just chcek is correct column to append to.
        ATARmap[key].append(this_entrez_id) # Add the entrez_id 
    elif row[jsol_name] != 'NA': # As row[jisUsed] != 'TRUE' (ie. must be FALSE)
      print("*** ERROR: sol.name %s != NA, for ATARiS shRNA %s" %(row[jsol_name], row[jshRNA]))

      
      
def write_solname_to_entrez_map_file(outfile,new_names_dict=None):
  print("\nWriting the solname to Entrez_id mapping file")
  with open(outfile, "w") as fout:
#    fout.write("sol.name\tentrez\tmg_ensembl_gene\tmg_symbol\tmg_entrez\n")
#    for key in sorted(ATARmap):  # .keys() .items()) # , key=itemgetter(jsol_name)):
#      fout.write("%s\t%s" %(key, ATARmap[key][jsol_entrez]))
#      if len(ATARmap[key]) > jsol_entrez+1:
#        fout.write("\t%s\t%s\t%s" %(ATARmap[key][img_ensembl_gene_id], ATARmap[key][img_symbol], ATARmap[key][img_entrezgene])) # The mg_ensembl_gene, mg_symbol, mg_entrezid
#      fout.write("\n")  
    fout.write("sol.name\tmg_symbol\tentrez\tmg_entrez\tmg_hgnc\thgnc_ensembl\tmg_ensembl_gene\tmg_ensembl_protein") # if change these titles, then update the 'read_ATARmap_from_file()' function too
    if new_names_dict is not None:
        fout.write("\tname_used_for_R")
    fout.write("\n")
    for key in sorted(ATARmap):  # .keys() .items()) # , key=itemgetter(jsol_name)):
      n = key.split('_')  # eg: A2ML1_1_01110
      if ATARmap[key][img_symbol] == '': print("*** mg_symbol missing for %s" %(key))
      elif n[0] != ATARmap[key][img_symbol]: print("*** %s differ %s" %(key,ATARmap[key][img_symbol]))
      fout.write("%s\t%s\t%s\t%s\t%s\t%s\t%s" %(key, ATARmap[key][img_symbol], ATARmap[key][jsol_entrez], ATARmap[key][img_entrezgene], ATARmap[key][img_hgnc], ATARmap[key][ihgnc_ensembl_id], ATARmap[key][img_ensembl_gene_id], ATARmap[key][img_ensembl_protein_id]))
      if new_names_dict is not None and key in new_names_dict:
        fout.write("\t%s" %(new_names_dict[key]) )
      fout.write("\n")


hgnc = dict() # To read the HGNC ids into a dictionary
synonyms_to_hgnc = dict()
#ihgnc = dict() # The column name to number for the above HGNC dict. 
def load_hgnc_dictionary():
  global hgnc, synonyms_to_hgnc, isymbol, isynonyms, iprev_names, iensembl_id, ientrez_id, ihgnc_id
  print("\nLoading HGNC data")
  # Alternatively use the webservice: http://www.genenames.org/help/rest-web-service-help
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  num_synonmys_already_exist = 0
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
          num_synonmys_already_exist += 1
          # print("**** ERROR: For gene %s Synonym %s already exists in gene %s:" %(gene_name,key,synonyms_to_hgnc[key]))
          synonyms_to_hgnc[key] += ';'+gene_name
        else:
          synonyms_to_hgnc[key] = gene_name
  if num_synonmys_already_exist > 0: print("**** ERROR: %d synonmys already exist in other genes" %(num_synonmys_already_exist))
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])


def compare_ATARmap_with_hgnc_add_ensemblid():
  print("Comparing ATARmap with HGNC")
  for key in sorted(ATARmap):   # .keys() .items()) # , key=itemgetter(jsol_name)):
    ATrow = ATARmap[key]
    mg_name = ATrow[img_symbol]
    AT_name, num, barcode = key.split('_')   # eg: A2ML1_1_01110
    #print("\nATARmap KEY: '%s' names: AT='%s' mg='%s'\n" %(key,AT_name,mg_name))
    print("")
    if mg_name !=  AT_name: name_list = (mg_name,AT_name)
    else: name_list = (mg_name,)
    HGNC_ensembl_id = ''
    for name in name_list:
      if name in hgnc:
        Hrow = hgnc[name]
        if Hrow[ientrez_id] != ATrow[img_entrezgene]: print("** Entrez: hgnc='%s' BUT ATAR='%s' (jsol='%s') for key '%s', '%s'" %(Hrow[ientrez_id],  ATrow[jsol_entrez], ATrow[img_entrezgene], key, name))  # also: jsol_entrez
        
        if Hrow[iensembl_id]!= ATrow[img_ensembl_gene_id] and Hrow[iensembl_id] not in ATrow[img_ensembl_gene_id].split(';'):        
          print("** Ensembl: hgnc='%s' BUT ATAR='%s' for key '%s', '%s'" %(Hrow[iensembl_id],ATrow[img_ensembl_gene_id], key, name))
        if (HGNC_ensembl_id != '') and (HGNC_ensembl_id !=Hrow[iensembl_id]):
          HGNC_ensembl_id += ';'+Hrow[iensembl_id]
        else:
          HGNC_ensembl_id = Hrow[iensembl_id]
        
        if Hrow[ihgnc_id]   != 'HGNC:'+ATrow[img_hgnc]:  print("** HGNC: hgnc='%s'  BUT ATAR='%s' for key '%s', '%s'" %(Hrow[ihgnc_id],ATrow[img_hgnc], key, name))
      else:
        if name == mg_name: print("***** MG_name %s not in hgnc for key %s (AT='%s' mg='%s')" %(name,key,AT_name,mg_name))
        else: print("*AT_name %s not in hgnc for key %s (AT='%s' mg='%s')" %(name,key,AT_name,mg_name))
    ATARmap[key].append(HGNC_ensembl_id) # Always add this column even if empty, as is needed for the write ATARmap file

    
def get_ensembl_and_symbol_from_mygene(entrez_id):
  # For one entrez_id
  mg = mygene.MyGeneInfo()
  fields = mg.get_fields()
  for k in fields: print("\n",k,fields[k])
  
  print("Mygene: %s\r" %(entrez_id))
  # To see the available fields, see eg: http://mygene.info/v2/gene/1017
  result = mg.getgene(entrez_id, fields="ensembl.gene, symbol, ensembl.gene", email="sbridgett@gmail.com")  # use entrez gene id (string or integer) OR ensembl gene id.
  #result = mg.getgene(entrez_id, fields="all", email="sbridgett@gmail.com")  # use entrez gene id (string or integer) OR ensembl gene id.
  # print(result)
  # for k in result: print("\n",k,result[k])

  if result is None: # or 'notfound' in result: # I think the "'notfound' in result" only applies to the getgenes() below for list of results
    print("*** Ensembl_id NOT in MyGene for Entrez_id: '%s'" %(entrez_id))
    return '',''
  # entrez_ids = ["1017","7248"]
  #results = mg.getgenes(entrez_ids, fields='ensembl.gene', email="sbridgett@gmail.com") # entrezgene
  else:
    if result['_id'] != entrez_id:
      print("*** ERROR: returned id %s doesn't match query %s" %(result['_id'],entrez_id))
      
    # successful result either:
    # {'ensembl.gene': 'ENSG00000149313', '_id': '60496', 'symbol': 'AASDHPPT'}
    # {'ensembl': [{'gene': 'ENSG00000275700'}, {'gene': 'ENSG00000276072'}], '_id': '26574', 'symbol': 'AATF'}
    if 'ensembl.gene' in result:
      ensembl_id = result['ensembl.gene']
    elif 'ensembl' in result:
      ensembl_list = result['ensembl']
      ensembl_id = ''
      for gene in ensembl_list:
        ensembl_id += gene['gene']
    else: 
      ensembl_id = ''
      print("*** Ensembl_id NOT in MyGene for Entrez_id: '%s'" %(entrez_id), result)

    symbol = result['symbol']
      
    return ensembl_id, symbol

  
def get_ensembl_and_symbol_list_from_mygene(entrez_id_list):
  # A list of entrez_ids
  mg = mygene.MyGeneInfo()
  # fields = mg.get_fields()
  # for k in fields: print("\n",k,fields[k])

  # gene = mg.getgene("1017", fields="ensembl.gene", email="sbridgett@gmail.com")  # use entrez gene id (string or integer) OR ensembl gene id.
  # for k in gene: print("\n",k,gene[k])

  # entrez_ids = ["1017","7248"]
  #print(entrez_id_list)
  results = mg.getgenes(entrez_id_list, fields='ensembl.gene, symbol, entrezgene, HGNC', email="sbridgett@gmail.com") # entrezgene
  #print(results)
  # for k in ensembl_ids: print("\n",k['query'],k['ensembl.gene']) # ,ensembl_ids[k])
  entrez_to_ensembl = dict()
  for result in results:
    entrez_id = result['query']
    if 'notfound' in result:
      print("*** Ensembl_id NOT found for Entrez_id: %s" %(entrez_id), result)
      entrez_to_ensembl[entrez_id] = ('','','','')
      continue

    entrezgene = str(result['entrezgene'])  # result['entrezgene'] is returned as an integer, not a string, whereas 'query' and '_id' are strings, eg: {'_id': '729384', 'query': '100131392', 'ensembl.gene': 'ENSG00000233802', 'symbol': 'TRIM49D2', 'entrezgene': 729384}
    if entrezgene != entrez_id:
      print("*** ERROR: returned entrezgene '%s' doesn't match entrez query '%s'" %(entrezgene,entrez_id), type(entrezgene),type(entrez_id), result)
    if result['_id'] != entrez_id:
      print("*** ERROR: returned _id '%s' doesn't match entrez query '%s'" %(result['_id'],entrez_id), type(result['_id']),type(entrez_id), result)
    if entrezgene != result['_id']:
      print("******* ERROR: returned entrezgene '%s' doesn't match returned _id '%s'" %(entrezgene,result['_id']), type(entrezgene), type(result['_id']), result)

    if 'ensembl.gene' in result:
      ensembl_id = result['ensembl.gene']
    elif 'ensembl' in result:
      ensembl_list = result['ensembl']
      ensembl_id = ''
      for gene in ensembl_list:
        if ensembl_id != '': ensembl_id += ';' # separate list using semi-colons
        ensembl_id += gene['gene']
    else:
      ensembl_id = ''
      print("*** Ensembl_id NOT in MyGene for Entrez_id: %s" %(entrez_id), result)

    if 'symbol' in result:
      symbol = result['symbol']
    else:
      symbol = ''
      print("*** Symbol NOT in MyGene for Entrez_id: %s" %(entrez_id), result)

    if 'HGNC' in result:
      hgnc = result['HGNC']
    else:
      hgnc = ''
      print("*** HGNC NOT in MyGene for Entrez_id: %s" %(entrez_id), result)
      
    if entrez_id in entrez_to_ensembl:
      print("*** ERROR Entrez_query in result list more than once: ", entrez_id)
    entrez_to_ensembl[entrez_id] = (entrezgene, symbol, hgnc, ensembl_id)
  
  
  
  if len(entrez_to_ensembl.keys()) != len(entrez_id_list):
    print("*** ERROR len(entrez_to_ensembl.keys()) %d != len(entrez_id_list) %d" %(len(entrez_to_ensembl.keys()), len(entrez_id_list)))
  return entrez_to_ensembl

  
def format_tissue(tissue):
    t=tissue.split("_") # eg: A1207_CENTRAL_NERVOUS_SYSTEM
    tissue = "_".join(t[1:])
    # We're combining LARGE_INTESTINE: (20 tissues) and SMALL_INTESTINE: (1 tissue)
    # and combining LUNG: (21 tissues) and PLEURA: (2 tissues)
    if tissue in ("LARGE_INTESTINE", "SMALL_INTESTINE"):  tissue = "INTESTINE"
    if tissue == "PLEURA": tissue = "LUNG"
    return tissue
    
    
def get_ensembl_name_from_solname(solname):
    n = (solname).split("_")
    gene_name = n[0]
    gene_in_hgnc = True
    ensembl_id = 'NotFound'
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
                #fout.write("\t%s_%s" %(n[0],get_ensembl_name(n[0])))  # Not using a variant suffix number at present.
    #fout.write("\t%s%s_%s" %(n[0],n[1],get_ensembl_name(n[0]))) # ie. the original left-most column of names, 'ABL1_1_1110001111' becomes 'ABL11'  
        else:
           print("** WARNING: Gene NOT found in hgnc", gene_name)
           gene_in_hgnc = False
#           return gene_name+"_NotFound"
        # Does this match the entrez_id from the ATARmap:
        
    if gene_in_hgnc:
      hgnc_entrez_id  = hgnc[gene_name][ientrez_id]
      hgnc_ensembl_id = hgnc[gene_name][iensembl_id]
      ensembl_id = hgnc_ensembl_id
      
    if solname not in ATARmap:
      print("********* ERROR: solname '%s' NOT in ATARmap ******" %(solname))
    else:  
      AT_entrez_id = ATARmap[solname][jsol_entrez]
      if AT_entrez_id is None or AT_entrez_id == '':
          print("***** ERROR: AT_entrez_id is None or Empty for solname '%s' hgnc_entrez_id '%s'" %(AT_entrez_id, hgnc_entrez_id))
      if gene_in_hgnc and AT_entrez_id != hgnc_entrez_id:
        print("***** ERROR: AT_entrez_id %s != hgnc_entrez_id '%s'" %(AT_entrez_id, hgnc_entrez_id))
      mg_ensembl_gene_id, mg_symbol = get_ensembl_and_symbol_from_mygene(AT_entrez_id)
      if mg_ensembl_gene_id == '':
        print("*** ERROR: ensembl_id NOT in MyGene for AT_entrez_id %s" %(AT_entrez_id))
      elif mg_symbol == '':
        print("*** ERROR: symbol NOT in MyGene for AT_entrez_id %s" %(AT_entrez_id))
      else:
        if gene_in_hgnc and mg_ensembl_gene_id != hgnc_ensembl_id:
          print("***** ERROR: mg_ensembl_gene_id '%s' != hgnc_ensembl_id '%s'" %(mg_ensembl_gene_id, hgnc_ensembl_id))
        if mg_symbol != gene_name:
          print("***** ERROR: mg_symbol '%s' != gene_name '%s' in solname %s" %(mg_symbol, gene_name, solname))
        if len(ATARmap[solname]) <= jsol_entrez:
          ATARmap[solname].append(mg_ensembl_gene_id)
          ATARmap[solname].append(mg_symbol)
        return mg_symbol+'_'+mg_ensembl_gene_id  
          
    return gene_name+'_'+ensembl_id
  
  
def add_mygene_to_ATARmap():
  global img_entrezgene, img_symbol, img_hgnc, img_ensembl_gene_id, ihgnc_ensembl_id
  entrez_dict = dict() # Using a dict first to eliminate duplicates to reduce downloads from mygene
  for key in ATARmap:
    entrez_id = ATARmap[key][jsol_entrez]    
    # print("entrez_id=%s ,ATARmap[key]=%s,jsol_entrez=%s" %(entrez_id,ATARmap[key],jsol_entrez))
    if ';' in entrez_id:  # The only case is: '22947;100288687'
      for entrez_id in entrez_id.split(';'):
        entrez_dict[entrez_id] = True
    else:    
      entrez_dict[entrez_id] = True
  entrez_id_list = sorted(entrez_dict.keys(), key=int) # 'key=int' to sort numerically.
  print("Will submit %d queries to MyGene" %(len(entrez_id_list)))
  #for id in entrez_id_list: print(id)
  mg_dict = get_ensembl_and_symbol_list_from_mygene(entrez_id_list)
  # Append to the map:
  for key in ATARmap:
    if len(ATARmap[key]) != jsol_entrez+1:
      print("**** ERROR: len(ATARmap[key]) != jsol_entrez for key %s" %(len(ATARmap[key]),jsol_entrez, key))
    entrez_id = ATARmap[key][jsol_entrez]
    if ';' in entrez_id:
       t_entrezgene =''; t_symbol = '';  t_hgnc = ''; t_ensembl_id = ''
       for entrez_id in entrez_id.split(';'):
          mg = mg_dict[entrez_id]
          t_entrezgene += ('' if (t_entrezgene=='' or mg[0]=='') else ';') + mg[0]
          t_symbol += ('' if (t_symbol=='' or mg[1]=='') else ';') + mg[1]
          t_hgnc += ('' if (t_hgnc=='' or mg[2]=='') else ';') + mg[2]
          t_ensembl_id += ('' if (t_ensembl_id=='' or mg[3]=='') else ';') + mg[3]
       ATARmap[key].extend( [t_entrezgene, t_symbol, t_hgnc, t_ensembl_id] )  # So will have three extra columns for each entrez_id         
    else:
       ATARmap[key].extend(mg_dict[entrez_id])   # mg_dict contains (entrezgene, symbol, img_hgnc, ensembl_id)

    img_entrezgene = jsol_entrez+1
    img_symbol = jsol_entrez+2
    img_hgnc = jsol_entrez+3
    img_ensembl_gene_id = jsol_entrez+4
    ihgnc_ensembl_id = jsol_entrez+5  # Is added by the compare_ATARmap_with_hgnc_add_ensemblid()
    
# if __name__ == "__main__":
#ids = get_ensembl_list_from_mygene(["1017","7248","J8888"])
#for k in ids:
#  print(k,ids[k])
  
#id,sy = get_ensembl_and_symbol_from_mygene("1017")
#print(id)
#print(sy)
#sys.exit

def get_ensembl_name_from_ATARmap(solname,gene_ensembl_names_dict):
    # gene_ensembl_names_dict contains existing names, to check to ensure new name is unique by incrementing num
    # This function assumes the caller adds the new names to this dict
    
    if solname not in ATARmap:
      print("**ERROR: solname '%s' not found in ATARmap" %(solname))
    row = ATARmap[solname]

    solname_symbol, solname_num, solname_barcode = solname.split('_')
    
    gene_symbol = row[img_symbol]
    if gene_symbol == '': # As wasn't found in HGNC
        gene_symbol = solname_symbol
    if ';' in gene_symbol:
      #print("**WARNING solname '%s' has two gene_symbols %s, so just using first symbol" %(solname,gene_symbol),row)
      #gene_symbol = gene_symbol.split(';')[0]
      print("**WARNING solname '%s' has two gene_symbols %s, so will use the solname symbol" %(solname,gene_symbol),row)
      gene_symbol = solname_symbol
      if gene_symbol not in gene_symbol.split(';'):
        print("**BUT the solname symbol %s isn't in the gene_symbols" %(solname),gene_symbol)
       
    ensembl_id = row[ihgnc_ensembl_id]
    if ensembl_id == '':
      ensembl_id = row[img_ensembl_gene_id]
    elif row[img_ensembl_gene_id] !='' and ensembl_id != row[img_ensembl_gene_id] and ensembl_id not in row[img_ensembl_gene_id].split(';'):
      print("**Solname %s HGNC ensembl id %s, is not in MG %s" %(solname,ensembl_id,row[img_ensembl_gene_id]) )
    
    if ';' in ensembl_id:
      print("**Solname %s has more than one ensembl id, so just using the first one: " %(solname),ensembl_id)
      ensembl_id = ensembl_id.split(';')[0]  # Just take the first ensmbl_id
    if ensembl_id == '':
      ensembl_id = 'NoEnsemblIdFound'
       
    solname_num = int(solname_num)
    while True:
       new_name = gene_symbol+str(solname_num)+'_'+ensembl_id
       if new_name not in gene_ensembl_names_dict: break
       solname_num += 1
       
    return new_name # Using the solname_num to try to keep names unique.



#### Script to convert the 
def build_ATARmap():
  load_shRNAmap()
  load_ATARmap()
  add_mygene_to_ATARmap()
  load_hgnc_dictionary()
  compare_ATARmap_with_hgnc_add_ensemblid()
  for key in ATARmap:
    if len(ATARmap[key]) != ihgnc_ensembl_id+1:
      print(len(ATARmap[key]), ihgnc_ensembl_id+1, ATARmap[key],"\n")
    else: print("OK")
  write_solname_to_entrez_map_file(output_file3)
  

  
def read_ATARmap_from_file():
  global ATARmap, jsol_name, jsol_entrez, img_entrezgene, img_symbol, img_hgnc, ihgnc_ensembl_id, img_ensembl_gene_id, img_ensembl_protein_id
  
  print("\nLoading ATARmap from file:", output_file3)
  dataReader = csv.reader(open(output_file3), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), 
  # Format for file: "......"

  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      cols = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
      jsol_name  = cols.get('sol.name')  # eg: A2ML1_1_01110      
      jsol_entrez = cols.get('entrez')
      img_entrezgene = cols.get('mg_entrez')
      img_symbol = cols.get('mg_symbol')
      img_hgnc = cols.get('mg_hgnc')
      ihgnc_ensembl_id = cols.get('hgnc_ensembl')
      img_ensembl_gene_id = cols.get('mg_ensembl_gene')
      img_ensembl_protein_id = cols.get('mg_ensembl_protein')
    else:
      key = row[jsol_name]
      if key in ATARmap:
        print("*** ERROR: Duplicate sol.name %s in file: " %(key),row)
      ATARmap[key] = row


      

    

def read_cellines_from_R_analysis_file(infile,colname):
  R_cellines = dict() # Return this dict, rather than making it global.
  print("\nLoading known cellines from R_existing_analysis file:", infile)
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), 
  # Format for file: "......"

  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      cols = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
      if colname not in cols: print("***** ERROR: colname '%s' NOT found in cols" %(colname),cols)
      k_celline = cols.get(colname)  # eg: CAL72_BONE 
    else:
      key = row[k_celline]
      if key in R_cellines:
        print("*** ERROR: Duplicate cell_line %s in file: " %(key),row)
      R_cellines[key] = True
  return R_cellines
    
    
# build_ATARmap(); sys.exit  # To build and write the ATARmap file.
read_ATARmap_from_file()  # To read the previously built ATARmap file.
# sys.exit

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
    
    # Using "for i ...", rather than eg. "for cellline in header:", as want to change the value, removing the "NCI" (National Cancer Institute) so that will match with some known cell line names in Campbell et al data:
    for i in range(2,len(header)):
        if header[i][:3] == "NCI":  # ie. characters 0,1,2
            header[i] = header[i][3:]  # eg: "NCIH1299_LUNG" => "H1299_LUNG"
    # The Achilles cell lines with NCI prefix are: NCIH1299_LUNG, NCIH1437_LUNG, NCIH1650_LUNG, NCIH1792_LUNG, NCIH196_LUNG, NCIH1975_LUNG, NCIH2052_PLEURA, NCIH2122_LUNG, NCIH2171_LUNG, NCIH23_LUNG, NCIH2452_PLEURA, NCIH441_LUNG, NCIH508_LARGE_INTESTINE, NCIH660_PROSTATE, NCIH661_LUNG, NCIH716_LARGE_INTESTINE, NCIH838_LUNG, NCIN87_STOMACH

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


# List of drivers from run_......R
# Define the set of 21 genes with
# good represention (≥ 7 mutants).
# This list can be used to filter
# the complete set of tests
cgc_vogel_genes = (
	"CCND1_595_ENSG00000110092",
	"CDKN2A_1029_ENSG00000147889",
	"EGFR_1956_ENSG00000146648",
	"ERBB2_2064_ENSG00000141736",
	"GNAS_2778_ENSG00000087460",
	"KRAS_3845_ENSG00000133703",
	"SMAD4_4089_ENSG00000141646",
	"MDM2_4193_ENSG00000135679",
	"MYC_4609_ENSG00000136997",
	"NF1_4763_ENSG00000196712",
	"NOTCH2_4853_ENSG00000134250",
	"NRAS_4893_ENSG00000213281",
	"PIK3CA_5290_ENSG00000121879",
	"PTEN_5728_ENSG00000171862",
	"RB1_5925_ENSG00000139687",
	"MAP2K4_6416_ENSG00000065559",
	"SMARCA4_6597_ENSG00000127616",
	"STK11_6794_ENSG00000118046",
	"TP53_7157_ENSG00000141510",
	"ARID1A_8289_ENSG00000117713",
	"FBXW7_55294_ENSG00000109670"
	)
    
print("Writing transformed files")    
gene_ensembl_names = dict()
new_names_dict = dict()
cell_lines = []
tissue_types = dict()   # Tissue types eg: "HAEMATOPOIETIC AND LYMPHOID TISSUE" from "697_HAEMATOPOIETIC_AND_LYMPHOID_TISSUE"
# Write transposed file:
with open(output_file1, "w") as fout:
    fout.write("cell.line")
    # Take leftmost column (col=0):
    for row in range(1,num_rows):
        # fout.write("\t%s" %(get_ensembl_name_from_solname(list_of_lists[row][0])))  # Not using a variant suffix number at present.
        gene_ensembl_name = get_ensembl_name_from_ATARmap(list_of_lists[row][0], gene_ensembl_names)
        if list_of_lists[row][0] in new_names_dict:
          if new_names_dict[list_of_lists[row][0]] != gene_ensembl_name: print("ERROR Name '%s' for %s already in new_names dict, and is different")
        else:   
          new_names_dict[list_of_lists[row][0]] = gene_ensembl_name # To write names to file.
          
        if gene_ensembl_name in gene_ensembl_names: print("******* Duplicate gene_ensembl_name '%s' already exists" %(gene_ensembl_name))
        else: gene_ensembl_names[gene_ensembl_name] = True
        fout.write("\t%s" %(gene_ensembl_name))  # Not using a variant suffix number at present.        
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


# Write the new names to file for use later:
write_solname_to_entrez_map_file(output_file4_newnames,new_names_dict)


def diff_dictionaries(dict1,dict2,name1,name2):
  inboth=[]
  in1only=[]
  in2only=[]
  for key in sorted(dict1):
    if key in dict2:
        inboth.append(key)
    else:
        # print("%s cell line '%s' not found in %s" %(name1,key,name2))
        in1only.append(key)
  for key in sorted(dict2):
    if key not in dict1:
        # print("%s ce)ll line '%s' not found in %s" %(name1,key,name2))
        in2only.append(key)    
  print("InBoth: %d   In %s only: %d  In %s only: %d\n" %(len(inboth),name1,len(in1only),name2,len(in2only)))
  # for inboth, "\n1only", in1only, "\n2only", in2only)
  print("inboth:")
  for key in inboth: print("  ",key)
  print("\nonly in",name1)
  for key in in1only: print("  ",key) 
  print("\nonly in",name2)
  for key in in2only: print("  ",key)
  return inboth # in1only, in2only


def get_only_codes_dict(dictfull):
  dict_codes = dict()
  for key in dictfull:
    dict_codes[key.split('_')[0]]=True
  return dict_codes  

  
def cell_lines_in_common():  
  cell_line_dict = dict()
  for key in cell_lines: 
    if key in cell_line_dict: print("Duplicate celline '%s' in Achilles data" %(key))
    cell_line_dict[key] = True
#  
# Just compare the codes now, eg: HT55 for HT55_LARGE_INTESTINE
#  cell_line_codes_dict = get_only_codes_dict(cell_line_dict)

# Now check if cellines match with existing cnv/mutation files:
  R_cellines = read_cellines_from_R_analysis_file(read_R_cnv_muts_file, "cell_line")
  #R_cellline_codes = get_only_codes_dict(R_cellines)
  inboth = diff_dictionaries(cell_line_dict,R_cellines,"Achilles","existing R_cnv_muts_celllines")
  #inboth_codes = diff_dictionaries(cell_line_codes_dict,R_cellline_codes,"Achilles codes","existing R_cnv_muts_celllines codes")

  #for key_code in inboth_codes:
  #  found=False
  #  for key in inboth:
  #    key = key.split('_')[0]
  #    if key_code == key:
  #      found=True
  #      break
  #  if found==False: print("Not Found",key_code)
#print("BUT the 'TT' codes found in both is very different: 'TT_THYROID' 'TT_OESOPHAGUS'")
#
  R_cellines = read_cellines_from_R_analysis_file(read_R_kinome_file, "cell.line")
  # R_cellline_codes = get_only_codes_dict(R_cellines)
  diff_dictionaries(cell_line_dict,R_cellines,"Achilles","existing R_kinome_celllines")
  # diff_dictionaries(cell_line_codes_dict,R_cellline_codes,"Achilles codes","existing R_cnv_muts_celllines codes")

"NCI"

  

cell_lines_in_common()
  
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