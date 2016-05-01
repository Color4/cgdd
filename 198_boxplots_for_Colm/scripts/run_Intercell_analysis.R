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

setwd("C:/Users/HP/Django_projects/cgdd/198_boxplots_for_Colm/analyses/") # was: setwd("~/Dropbox/198_boxplots_for_Colm/analyses/")

combmuts_func_file <- "../data_sets/func_mut_calls/combined_exome_cnv_func_muts_150225.txt"
combmuts_all_file <- "../data_sets/func_mut_calls/combined_exome_cnv_all_muts_150225.txt"
combmuts_classes_file <- "../data_sets/func_mut_calls/combined_exome_cnv_mut_classes_150225.txt"

# ----------------------------- #
# Analysis specific input files #
# ---------------------- -------#

#isCampbell = TRUE;  isAchilles = FALSE; isColt = FALSE; # Campbell(2016)
#isCampbell = FALSE; isAchilles = TRUE;  isColt = FALSE;  # Achilles (2014)
isCampbell = FALSE; isAchilles = FALSE; isColt = TRUE;  # Colt (2016)

if (isAchilles) { #### Achilles:
  # SJB - for Achilles - input files in C:/Users/HP/Django_projects/cgdd
  pubmed_id <- "25984343" # Cowley(2014) for Achilles
  kinome_file <- "../../Achilles_data/Achilles_rnai_transposed_for_R_kinome_v3_12Mar2016.txt"
  tissues_file <- "../../Achilles_data/Achilles_tissues_v3_12Mar2016.txt"
  }
else if (isColt) { #### For Colt study - are all breast tissue - so only tissue anaylsis:
  # NOTE: There are several ids with just number and '_EntrezNotFound':
  pubmed_id <- "26771497" # Marcotte(2016) for Colt study
  kinome_file <- "../data_sets/colt_study_breast/zGARP_scores_transposed_with_Intercell_names_from_James_with_entrez_ids_added.txt"
  tissues_file <- "../data_sets/colt_study_breast/zGARP_tissues.txt"   # All Colt data are breast tissues.
  }
else if (isCampbell) {  #### For Cambell (2016):
  pubmed_id <- "26947069" # Campbell(2016)
  kinome_file <- "../data_sets/siRNA_Zscores/Intercell_v18_rc4_kinome_zp0_for_publication.txt"
  tissues_file <- "../data_sets/siRNA_Zscores/Intercell_v18_rc4_tissues_zp0_for_publication.txt"
} else {print ......ERROR.... }


# ------------------------ #
# Define the results files
# ------------------------ #

if (isAchilles) {
  # SJB - for Achilles:
  # For 21 drivers being focused on:
  #uv_results_kinome_combmuts_file <- "univariate_results_Achilles_v2_for21drivers_pancan_kinome_combmuts_180312_witheffectsize.txt"
  #uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v2_for21drivers_bytissue_kinome_combmuts_180312_witheffectsize.txt"

  # For the rest of drivers (doesn't include the 21 drivers already processed above):
  uv_results_kinome_combmuts_file <- "univariate_results_Achilles_v2_for_remaining_drivers_pancan_kinome_combmuts_30April2016_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v2_for_remaining_drivers_bytissue_kinome_combmuts_30April2016witheffectsize_and_zdiff.txt"
  
  combined_histotypes_boxplot_dir <- "combined_histotypes_achilles/"
  separate_histotypes_boxplot_dir <- "separate_histotypes_achilles/"
} else if (isColt) {

  # uv_results_kinome_combmuts_file <- "NONE"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Colt_v1_bytissue_kinome_combmuts_29April2016_witheffectsize_and_zdiff.txt"
  
  # combined_histotypes_boxplot_dir <- "NONE/"
  separate_histotypes_boxplot_dir <- "separate_histotypes_colt_allbreast/"
  
} else {
  # For Colm/Cambell (2016)
  # ORIGINAL: uv_results_kinome_combmuts_file <- "univariate_results_v26_pancan_kinome_combmuts_150202.txt"
  uv_results_kinome_combmuts_file <- "univariate_results_v26_pancan_kinome_combmuts_28April2016_witheffectsize_and_zdiff.txt"

  # Just one result to test boxplot printing:
  # uv_results_kinome_combmuts_file <- "one_boxplot_SEMG2_CAMK1_extracted_from_univariate_results_v26_pancan_kinome_combmuts_150202.txt"

  # ORIGINAL: uv_results_kinome_combmuts_bytissue_file <- "univariate_results_v26_bytissue_kinome_combmuts_150202.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_v26_bytissue_kinome_combmuts_28April2016_witheffectsize_and_zdiff.txt"
  combined_histotypes_boxplot_dir <- "combined_histotypes_medium/"
  separate_histotypes_boxplot_dir <- "separate_histotypes_medium/"
}

# ------------------------------ #
# Source the Intercell functions #
# ------------------------------ #

# *** Need to set this 'isAchilles' value before sourcing the Intercell_functions, as isAchilles is used to set the tissue lists and plot colours.

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

# Driver gene mutations in combined histotypes
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
# select associations where wilcox.p ≤ 0.05

source("../scripts/Intercell_analysis_functions.R")
debug(make_mini_box_dot_plots)
make_mini_box_dot_plots(
	results=as.data.frame(
		uv_results_kinome_combmuts[which(
			uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
			uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
			),]
		),
	zscores=kinome_combmuts$rnai,
	mutation.classes=kinome_combmuts$mut_classes,
	mutations=kinome_combmuts$func_muts,
	exclusions=kinome_combmuts$all_muts,
	tissues=kinome_combmuts$tissues,
	prefix_for_filename=combined_histotypes_boxplot_dir,
	suffix_for_filename="PANCAN", # SJB WAS: "allhistotypes",
	pubmed_id_for_filename=pubmed_id, # Added by SJB 
	tissue_pretty_names=legend_pretty_tissues,
	tissue_actual_names=legend_actual_tissues,
	tissue_cols=legend_col
	)


source("../scripts/Intercell_analysis_functions.R")
debug(write_box_dot_plot_data)
write_box_dot_plot_data(
	results=as.data.frame(
		uv_results_kinome_combmuts[which(
			uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
			uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
			),]
		),
	zscores=kinome_combmuts$rnai,
	mutation.classes=kinome_combmuts$mut_classes,
	mutations=kinome_combmuts$func_muts,
	exclusions=kinome_combmuts$all_muts,
	tissues=kinome_combmuts$tissues,
	suffix_for_filename="PANCAN", # SJB WAS: "allhistotypes",
	tissue_actual_names=legend_actual_tissues
	)
	
	
# Plot combmuts results for separate histotypes
# select associations where wilcox.p ≤ 0.05
tissues <- levels(as.factor(uv_results_kinome_combmuts_bytissue$tissue))
for(this_tissue in tissues){
	rows_to_plot <- which(
		kinome_combmuts$tissues[,this_tissue] == 1
		)
	make_mini_box_dot_plots(
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
		prefix_for_filename=separate_histotypes_boxplot_dir,
		suffix_for_filename=this_tissue,
		pubmed_id_for_filename=pubmed_id, # Added by SJB
		tissue_pretty_names=legend_pretty_tissues,
		tissue_actual_names=legend_actual_tissues,
		tissue_cols=legend_col
		)
}


make_legends()

