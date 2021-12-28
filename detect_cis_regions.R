library(cicero)

CHROMOSOME = Sys.getenv('chromosome')
PREFIX = Sys.getenv('prefix')
OUTPUT = Sys.getenv('output')
GENOME_PATH = Sys.getenv('genome_path')

input_cds = make_atac_cds(paste(PREFIX,  CHROMOSOME, '.tsv', sep=''))

set.seed(2017)

input_cds <- detectGenes(input_cds)
input_cds <- estimateSizeFactors(input_cds)
input_cds <- reduceDimension(input_cds, max_components = 2, num_dim=6,
                      reduction_method = 'tSNE', norm_method = "none", verbose = T, check_duplicates = FALSE)


tsne_coords <- t(reducedDimA(input_cds))
row.names(tsne_coords) <- row.names(pData(input_cds))
cicero_cds <- make_cicero_cds(input_cds, reduced_coordinates = tsne_coords)


genome <- read.table(GENOME_PATH)
sample_genome <- subset(genome, V1 == CHROMOSOME)
conns <- run_cicero(cicero_cds, sample_genome)


filtered_data <- subset(conns, conns$coaccess > 0.05)

write.csv(filtered_data, paste(OUTPUT, CHROMOSOME, '.csv', sep=''), row.names = FALSE)
