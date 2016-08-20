#!/bin/bash

DIR="198_boxplots_for_Colm/analyses"

# Colt:
# OLD1="$DIR/univariate_results_Colt_v1_bytissue_kinome_combmuts_7May2016_witheffectsize_and_zdiff"
# OLD1="$DIR/univariate_results_Colt_v1_with_fixed_colt_mut_genenames__bytissue_kinome_combmuts_12Aug2016_witheffectsize_and_zdiff"
# NEW1="$DIR/univariate_results_Colt_v2_bytissue_kinome_combmuts_12Aug2016_witheffectsize_and_zdiff"
NEW1="$DIR/univariate_results_Colt_v2_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff"

OLD2=""
NEW2=""

# Campbell:
# OLD1="$DIR/univariate_results_v26_pancan_kinome_combmuts_28April2016_witheffectsize_and_zdiff"
# OLD2="$DIR/univariate_results_v26_bytissue_kinome_combmuts_28April2016_witheffectsize_and_zdiff"
# NEW1="$DIR/univariate_results_Campbell_v26_for23drivers_pancan_kinome_combmuts_12Aug2016_witheffectsize_and_zdiff"
# NEW2="$DIR/univariate_results_Campbell_v26_for23drivers_bytissue_kinome_combmuts_12Aug2016_witheffectsize_and_zdiff"
NEW1="$DIR/univariate_results_Campbell_v26_for23drivers_pancan_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff"
NEW2="$DIR/univariate_results_Campbell_v26_for23drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff"


for EXTN in ".txt" "_and_boxplotdata_mutantstate.txt"
do
  TYPE="(filtered by wilcox.p <= 0.05 & CLES >= 0.65)"  
  if [ "$EXTN" == ".txt" ]; then
    TYPE="(unfiltered)"
  fi
  
  echo "Old pancan $TYPE:"
  wc -l ${OLD1}${EXTN}
  echo "New pancan $TYPE:"
  wc -l ${NEW1}${EXTN}
  echo ""
  
  if [ "$NEW2" != "" ]
  then
    echo "Old bytissue $TYPE:"
    wc -l ${OLD2}${EXTN}
    echo "New bytissue $TYPE:"
    wc -l ${NEW2}${EXTN}	
  fi  
  echo ""  
done

echo ""
for CUT in 1 2
do
  TYPE="(drivers)"  
  if [ "$CUT" -eq "2" ]; then TYPE="(targets)"; fi
  echo "Diff cut$CUT $TYPE old new (unfiltered):"
  cut -f $CUT $OLD1.txt | sort | uniq > junk_results_old_sort_uniq_cut$CUT.txt
  cut -f $CUT $NEW1.txt | sort | uniq > junk_results_new_sort_uniq_cut$CUT.txt
  diff junk_results_old_sort_uniq_cut$CUT.txt junk_results_new_sort_uniq_cut$CUT.txt
  echo ""
  
#  echo "Diff cut$CUT $TYPE old new (unfiltered):"  
#  if [ "$NEW2" != "" ]
#  then
#    cut -f $CUT $OLD2.txt | sort | uniq > junk_results_old_sort_uniq_cut$CUT.txt
#    cut -f $CUT $NEW2.txt | sort | uniq > junk_results_new_sort_uniq_cut$CUT.txt
#    diff junk_results_old_sort_uniq_cut$CUT.txt junk_results_new_sort_uniq_cut$CUT.txt  
#  fi
#  echo ""
done
