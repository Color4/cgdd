#!/usr/bin/bash

# Script to create sub-directories A to Z, and move the boxplot .png files
# into those sub-directories based on the first letter of the image filename.
# This might let the server find the image slightly faster as fewer files in
# each director's inodes to search.

alpha=( A B C D E F G H I J K L M N O P Q R S T U V W X Y Z )

for DIR in ${alpha[@]}
do
  echo "Processing $DIR"

  # Make directory:
  if [ ! -e "$DIR" ]; then mkdir "$DIR"; fi

  # Find and move file (using this 'xargs' can cope with any special characters in file names):
  find . -mindepth 1 -maxdepth 1 -iname "$DIR*.png" -type f -print0 | xargs -0 -I '{}' /bin/mv "{}" "$DIR/"

  # Count number of .png files in the subdirectory:
  # Using 'find' would be better than this 'ls':
  C=$(ls -U ${DIR}/*.png | wc -l); echo $DIR $C
done
