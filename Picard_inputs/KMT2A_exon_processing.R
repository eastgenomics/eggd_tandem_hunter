setwd("~/new_projects/tandemhunter_coverage")

#import csv to make exons BED for KMT2A
KMT2A_coord <- read_csv("ExonsSpreadsheet-Homo_sapiens_Transcript_Exons_ENST00000534358.csv")
#change colname 
colnames(KMT2A_coord)[2] <- "Exon_Intron"
KMT2A_exons <- drop_na(KMT2A_coord)
#Make a new dataframe with chr, start and end coordinate
KMT2A_bed <- select(KMT2A_exons, c(3,4))
KMT2A_bed <- cbind(chr= "chr11", KMT2A_bed)
#Write dataframe into bed file 
write.table(KMT2A_bed, file = "KMT2A_exons.bed", sep = "\t",
            row.names = FALSE, col.names = FALSE)