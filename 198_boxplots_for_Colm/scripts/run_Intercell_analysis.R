# ================================== #
# Analysis code as described in
# "Large scale profiling of kinase
# dependencies in cancer cell lines"
# jamesc@icr.ac.uk, 3rd March 2016
# ================================== #

# Need to have preprocessCore,
# gplots and mixtools installed.

# ------------------------------ #
# Common inputs for all datasets #
# ------------------------------ #

# On Windows:
#setwd("C:/Users/HP/Django_projects/cgdd/198_boxplots_for_Colm/analyses/") # was: setwd("~/Dropbox/198_boxplots_for_Colm/analyses/")
# On Mac:
setwd("/Users/sbridgett/Documents/UCD/cgdd/198_boxplots_for_Colm/analyses/")

# Original genotype files (pre-August 2016):
#combmuts_func_file <- "../data_sets/func_mut_calls/combined_exome_cnv_func_muts_150225.txt"
#combmuts_all_file <- "../data_sets/func_mut_calls/combined_exome_cnv_all_muts_150225.txt"
#combmuts_classes_file <- "../data_sets/func_mut_calls/combined_exome_cnv_mut_classes_150225.txt" # contains the mutation types (1 to 5)

# From Colms email - 11 Aug 2016 - The new genotype files:
combmuts_func_file <- "../../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_func_muts_v1.txt" # (indicates if there is a functional mutation)
combmuts_all_file <- "../../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_all_muts_v1.txt"  # (indicates if there is any mutation)
combmuts_classes_file <- "../../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_func_mut_types_v1.txt" # (indicates mutation types: 1 or 2)


# ----------------------------------------------------- #
# Specify the Analysis specific input and results files #
# ------------------------------------------------------#

data_set <- "Campbell"  # Campbell(2016)
data_set <- "Achilles"  # Achilles (2014)
data_set <- "Colt"  # Colt (2016)

if (data_set == "Campbell") {  #### For Cambell (2016):
  pubmed_id <- "26947069" # Campbell(2016)
  tissues_file <- "../data_sets/siRNA_Zscores/Intercell_v18_rc4_tissues_zp0_for_publication.txt"

  # kinome_file <- "../data_sets/siRNA_Zscores/Intercell_v18_rc4_kinome_zp0_for_publication.txt" # pre-August-2016
  # From Colms email - 11 Aug 2016 - the renamed RNAi files are in this directory:

  kinome_file <- "../../preprocess_genotype_data/rnai_datasets/Intercell_v18_rc4_kinome_cancergd.txt"

  uv_results_kinome_combmuts_file <- "univariate_results_Campbell_v26_for23drivers_pancan_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Campbell_v26_for23drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff.txt"  

  # For Colm/Cambell (2016)
  # ORIGINAL: uv_results_kinome_combmuts_file <- "univariate_results_v26_pancan_kinome_combmuts_150202.txt"
  # uv_results_kinome_combmuts_file <- "univariate_results_v26_pancan_kinome_combmuts_28April2016_witheffectsize_and_zdiff.txt"
  # ORIGINAL: uv_results_kinome_combmuts_bytissue_file <- "univariate_results_v26_bytissue_kinome_combmuts_150202.txt"
  # uv_results_kinome_combmuts_bytissue_file <- "univariate_results_v26_bytissue_kinome_combmuts_5May2016_witheffectsize_and_zdiff.txt"
  
  # Just one result to test boxplot printing:
  # uv_results_kinome_combmuts_file <- "one_boxplot_SEMG2_CAMK1_extracted_from_univariate_results_v26_pancan_kinome_combmuts_150202.txt"
  
  # Just for plotting the boxplot .png files:
  # combined_histotypes_boxplot_dir <- "combined_histotypes_medium/"
  # separate_histotypes_boxplot_dir <- "separate_histotypes_medium/"

} else if (data_set == "Achilles") { #### Achilles:
  # SJB - for Achilles - input files in C:/Users/HP/Django_projects/cgdd
  pubmed_id <- "25984343" # Cowley(2014) for Achilles
  tissues_file <- "../../Achilles_data/Achilles_tissues_v4_17Aug2016.txt"  


#*************************************************************
#******** REMEMBER TO CHANGE TO COLMS NEW MUTS FILES *********
#*************************************************************

  # kinome_file <- "../../Achilles_data/Achilles_rnai_transposed_for_R_kinome_v3_12Mar2016.txt"  # pre-August-2016

  kinome_file <- "../../Achilles_data/Achilles_rnai_transposed_for_R_kinome_v4_17Aug2016.txt"  # 17-August-2016

  # From Colms email - 11 Aug 2016 - the renamed RNAi files are in this directory:
  # kinome_file <- "../../preprocess_genotype_data/rnai_datasets/Achilles_QC_v2.4.3_cancergd.txt"
  # ********** STILL TO TRY WITH COLMS FILE ABOVE ****************

  uv_results_kinome_combmuts_file <- "univariate_results_Achilles_v4_for36drivers_pancan_kinome_combmuts_17Aug2016_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v4_for36drivers_bytissue_kinome_combmuts_17Aug2016witheffectsize_and_zdiff.txt"
  
  # SJB - for Achilles:
  # For 23 drivers being focused on:
  # uv_results_kinome_combmuts_file <- "univariate_results_Achilles_v2_for23drivers_pancan_kinome_combmuts_5May2016_witheffectsize_and_zdiff.txt"  
  # uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v2_for23drivers_bytissue_kinome_combmuts_5May2016witheffectsize_and_zdiff.txt"

  # For the rest of drivers (doesn't include the 23 drivers already processed above):
  # uv_results_kinome_combmuts_file <- "univariate_results_Achilles_v2_for_remaining_drivers_pancan_kinome_combmuts_5May2016_witheffectsize_and_zdiff.txt"
  # uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v2_for_remaining_drivers_bytissue_kinome_combmuts_5May2016witheffectsize_and_zdiff.txt"

  # Just for plotting the boxplot .png files:
  # combined_histotypes_boxplot_dir <- "combined_histotypes_achilles/"
  # separate_histotypes_boxplot_dir <- "separate_histotypes_achilles/"

} else if (data_set == "Colt") { #### For Colt study - are all breast tissue - so only tissue anaylsis:
  # NOTE: There are several ids with just number and '_EntrezNotFound':
  pubmed_id <- "26771497" # Marcotte(2016) for Colt study
  tissues_file <- "../data_sets/colt_study_breast/zGARP_tissues.txt"   # All Colt data are breast tissues.
  # kinome_file <- "../data_sets/colt_study_breast/zGARP_scores_transposed_with_Intercell_names_from_James_with_entrez_ids_added.txt"  # pre-August-2016
  # From Colms email - 11 Aug 2016 - the renamed RNAi files are in this directory:
  kinome_file <- "../../preprocess_genotype_data/rnai_datasets/coltv2_zgarp_cancergd_reformatted.txt"


# === testing:
  # rerunning with the corrected gene names (ie. coltv2_zgarp_cancergd_reformatted.txt, as my file: zGARP_scores_transposed_with_Intercell_names_from_James_with_entrez_ids_added.txt contained numbers for genenames DEC, SEP, MARCH, etc)
  # but using the OLD muts (combined_exome_cnv_func_muts_150225.txt, rather than Colms new muts: 
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Colt_v1_with_fixed_colt_mut_genenames__bytissue_kinome_combmuts_12Aug2016_witheffectsize_and_zdiff.txt"
# =============

  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Colt_v2_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff.txt"


  uv_results_kinome_combmuts_file <- "NONE"
  # uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Colt_v1_bytissue_kinome_combmuts_7May2016_witheffectsize_and_zdiff.txt"

  # Just for plotting the boxplot .png files:  
  # combined_histotypes_boxplot_dir <- "NONE/"
  # separate_histotypes_boxplot_dir <- "separate_histotypes_colt_allbreast/"
  
  }
} else {
  stop(paste("ERROR: Invalid data_set: '",data_set,"' but should be 'Campbell', 'Achilles' or 'Colt'"))
  }

# ------------------------------ #
# Source the Intercell functions #
# ------------------------------ #

# ******* Always need to set this 'data_set' value before sourcing the Intercell_functions, as it is used to set the tissue lists and plot colours.

source_script <- "../scripts/Intercell_analysis_functions.R"; source_file_info <- file.info(source_script); source(source_script); # returns: size, isdir, mode, mtime, ctime, atime = integer of class "POSIXct": modification, ‘last status change’ and last access times. So compare 'mtime' with previous mtime. Better to get info before reading the file, as might change between.

#source("../scripts/Intercell_analysis_functions_plotted_legend_graphs_ok.R")

# ---------------- #
# Read in the data
# ---------------- #

kinome_combmuts <- read_rnai_mutations(
	rnai_file=kinome_file,
	func_muts_file=combmuts_func_file,
	all_muts_file=combmuts_all_file,
	mut_classes_file=combmuts_classes_file,
	tissues_file=tissues_file
	)

# -------------------------------- #
# Run the set of hypothesis tests
# on the kinome z-score data sets
# -------------------------------- #

# dependencies associated with histotype
#uv_results_kinome_tissue <- run_univariate_tests(
#	zscores=kinome_tissue$rnai,
#	mutations=kinome_tissue$func_muts,
#	all_variants=kinome_tissue$all_muts,
#	sensitivity_thresholds=kinome_tissue$rnai_iqr_thresholds
#	)
#write.table(
#	uv_results_kinome_tissue,
#	file=uv_results_kinome_tissue_file,
#	sep="\t",
#	quote=FALSE,
#	row.names=FALSE
#	)

# Driver gene mutations in combined histotypes -- *** NOT COLT *** 
uv_results_kinome_combmuts <- run_univariate_tests(
	zscores=kinome_combmuts$rnai,
	mutations=kinome_combmuts$func_muts,
	all_variants=kinome_combmuts$all_muts,
	sensitivity_thresholds=kinome_combmuts$rnai_iqr_thresholds
	)
write.table(
	uv_results_kinome_combmuts,
	file=uv_results_kinome_combmuts_file,
	sep="\t",
	quote=FALSE,
	row.names=FALSE
	)

# Driver gene mutations in separate histotypes
uv_results_kinome_combmuts_bytissue <- run_univariate_test_bytissue(kinome_combmuts)
write.table(
	uv_results_kinome_combmuts_bytissue,
	file=uv_results_kinome_combmuts_bytissue_file,
	sep="\t",
	quote=FALSE,
	row.names=FALSE
)


# ------------------------------ #
# (Re-)load in the results files
# ------------------------------ #


uv_results_kinome_combmuts <- read.table(
	file=uv_results_kinome_combmuts_file,
	header=TRUE,
	sep="\t",
	stringsAsFactors=FALSE
	)

uv_results_kinome_combmuts_bytissue <- read.table(
	file=uv_results_kinome_combmuts_bytissue_file,
	header=TRUE,
	sep="\t",
	stringsAsFactors=FALSE
	)

# ------------------- #
# boxplot the results
# ------------------- #

# Plot all combmuts results coloured by tissue
# select associations where wilcox.p <= 0.05 and CLES > =0.65
source("../scripts/Intercell_analysis_functions.R")
fileConn<-file(open="w", paste0( sub("\\.txt$","",uv_results_kinome_combmuts_file), "_and_boxplotdata_mutantstate.txt") ) # Need "\\." to correctly escape the dot in regexp in R
#debug(write_box_dot_plot_data)
write_box_dot_plot_data(
	results=as.data.frame(
		uv_results_kinome_combmuts[which(
			uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
			uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
			),]
		),
	zscores=kinome_combmuts$rnai,
	mutation.classes=kinome_combmuts$mut_classes, # SJB - I think this is the mutation types.
	mutations=kinome_combmuts$func_muts,
	exclusions=kinome_combmuts$all_muts,
	tissues=kinome_combmuts$tissues,
	fileConn = fileConn,
	writeheader=TRUE,
	tissue_actual_names=legend_actual_tissues
	)
close(fileConn) # caller should close the fileConn	

	
# Plot combmuts results for separate histotypes
# select associations where wilcox.p <= 0.05 and CLES > =0.65
source("../scripts/Intercell_analysis_functions.R")
fileConn<-file(open="w", 
paste0( sub("\\.txt$","",uv_results_kinome_combmuts_bytissue_file), "_and_boxplotdata_mutantstate.txt") ) # Output file. Needs "w" otherwise cat(...) overwrites previous cat()'s rather than appending. To open and append to existing file use "a"
tissues <- levels(as.factor(uv_results_kinome_combmuts_bytissue$tissue))
write_header <- TRUE
for(this_tissue in tissues){
	rows_to_plot <- which(
		kinome_combmuts$tissues[,this_tissue] == 1
		)
	write_box_dot_plot_data(
		results=as.data.frame(
			uv_results_kinome_combmuts_bytissue[which(
				uv_results_kinome_combmuts_bytissue[,"wilcox.p"] <= 0.05 &
				uv_results_kinome_combmuts_bytissue[,"CLES"] >= 0.65 & # SJB Added this effect_size test
				uv_results_kinome_combmuts_bytissue[,"tissue"] == this_tissue
				),]
			),
		zscores=kinome_combmuts$rnai[rows_to_plot,],
		mutation.classes=kinome_combmuts$mut_classes[rows_to_plot,],
		mutations=kinome_combmuts$func_muts[rows_to_plot,],
		exclusions=kinome_combmuts$all_muts[rows_to_plot,],
		tissues=kinome_combmuts$tissues[rows_to_plot,],
		fileConn=fileConn,
		writeheader=write_header,
		tissue_actual_names=legend_actual_tissues,
		)
	write_header <- FALSE # As only write the header line for first call of the above write_boxplot_data
}
close(fileConn) # caller should close the fileConn


# Plot all combmuts results coloured by tissue
# select associations where wilcox.p <= 0.05 and CLES > =0.65
#source("../scripts/Intercell_analysis_functions.R")
#debug(make_mini_box_dot_plots)
#make_mini_box_dot_plots(
#	results=as.data.frame(
#		uv_results_kinome_combmuts[which(
#			uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
#			uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
#			),]
#		),
#	zscores=kinome_combmuts$rnai,
#	mutation.classes=kinome_combmuts$mut_classes,
#	mutations=kinome_combmuts$func_muts,
#	exclusions=kinome_combmuts$all_muts,
#	tissues=kinome_combmuts$tissues,
#	prefix_for_filename=combined_histotypes_boxplot_dir,
#	suffix_for_filename="PANCAN", # SJB WAS: "allhistotypes",
#	pubmed_id_for_filename=pubmed_id, # Added by SJB 
#	tissue_pretty_names=legend_pretty_tissues,
#	tissue_actual_names=legend_actual_tissues,
#	tissue_cols=legend_col
#	)

	
# Plot combmuts results for separate histotypes
# select associations where wilcox.p <= 0.05
#tissues <- levels(as.factor(uv_results_kinome_combmuts_bytissue$tissue))
#for(this_tissue in tissues){
#	rows_to_plot <- which(
#		kinome_combmuts$tissues[,this_tissue] == 1
#		)
#	make_mini_box_dot_plots(
#		results=as.data.frame(
#			uv_results_kinome_combmuts_bytissue[which(
#				uv_results_kinome_combmuts_bytissue[,"wilcox.p"] <= 0.05 &
#				uv_results_kinome_combmuts_bytissue[,"CLES"] >= 0.65 & # SJB Added this effect_size test
#				uv_results_kinome_combmuts_bytissue[,"tissue"] == this_tissue
#				),]
#			),
#		zscores=kinome_combmuts$rnai[rows_to_plot,],
#		mutation.classes=kinome_combmuts$mut_classes[rows_to_plot,],
#		mutations=kinome_combmuts$func_muts[rows_to_plot,],
#		exclusions=kinome_combmuts$all_muts[rows_to_plot,],
#		tissues=kinome_combmuts$tissues[rows_to_plot,],
#		prefix_for_filename=separate_histotypes_boxplot_dir,
#		suffix_for_filename=this_tissue,
#		pubmed_id_for_filename=pubmed_id, # Added by SJB
#		tissue_pretty_names=legend_pretty_tissues,
#		tissue_actual_names=legend_actual_tissues,
#		tissue_cols=legend_col
#		)
#}


# make_legends()

