import pandas as pd

# Define human breast cancer cell types and marker genes
cell_data = [
    # Epithelial cell types
    ("Luminal epithelial cells", ["KRT7", "KRT8", "KRT18", "EPCAM", "ITGA6 (low)", "ESR1", "PGR", "ERBB2", "AR", "BCL2", "BIRC5", "MKI67"]),
    ("Basal-like (myoepithelial) cells", ["KRT5", "KRT14", "VIM", "ACTA2", "KRT7 (absent)", "KRT8 (absent)", "KRT18 (absent)", "ESR1 (absent)", "ERBB2 (absent)"]),
    ("EMT-like tumor cells", ["EPCAM", "CDH1", "VIM"]),
    # T cell subtypes
    ("Regulatory T cells (T-regs)", ["CD4", "FOXP3", "CD25", "CTLA4"]),
    ("Exhausted CD8+ T cells", ["PDCD1", "HAVCR2", "CTLA4", "HLA-DRA", "CD38"]),
    ("Exhausted CD4+ T cells", ["PDCD1", "CTLA4", "CD38", "ICOS"]),
    ("Less exhausted T cells", ["PDCD1 (int)", "CTLA4 (neg)", "CD38 (neg)", "HLA-DRA (neg)"]),
    # TAMs and other myeloid cells
    ("TAMs (M01)", ["CD38", "MSR1", "MRC1", "CD163", "CD169"]),
    ("TAMs (M02)", ["MSR1", "CD169", "CD163", "CD38"]),
    ("TAMs (M17)", ["CD169", "CD38"]),
    ("MDSCs", ["HLA-DRA (low)"]),
    ("Classical monocytes", ["CD14", "FCGR3A (neg)"]),
    ("Tissue-resident macrophages", ["MRC1", "HLA-DRA"])
]

# Create DataFrame
df_human = pd.DataFrame(cell_data, columns=["Cell Type", "Human Marker Genes"])

# Mapping from human to mouse gene symbols (based on known orthologs)
human_to_mouse = {
    "KRT7": "Krt7", "KRT8": "Krt8", "KRT18": "Krt18", "EPCAM": "Epcam", "ITGA6": "Itga6",
    "ESR1": "Esr1", "PGR": "Pgr", "ERBB2": "Erbb2", "AR": "Ar", "BCL2": "Bcl2", "BIRC5": "Birc5", "MKI67": "Mki67",
    "KRT5": "Krt5", "KRT14": "Krt14", "VIM": "Vim", "ACTA2": "Acta2", "CDH1": "Cdh1",
    "CD4": "Cd4", "FOXP3": "Foxp3", "CD25": "Il2ra", "CTLA4": "Ctla4", "PDCD1": "Pdcd1", 
    "HAVCR2": "Havcr2", "HLA-DRA": "H2-Aa", "CD38": "Cd38", "ICOS": "Icos",
    "MSR1": "Msr1", "MRC1": "Mrc1", "CD163": "Cd163", "CD169": "Siglec1",
    "CD14": "Cd14", "FCGR3A": "Fcgr3"
}

# Convert human markers to mouse markers
def convert_to_mouse_markers(human_genes):
    mouse_genes = []
    for gene in human_genes:
        base_gene = gene.split(" ")[0]  # Remove annotation like (low), (absent), etc.
        mouse_gene = human_to_mouse.get(base_gene, base_gene)
        mouse_genes.append(mouse_gene)
    return mouse_genes

# Apply conversion
df_human["Mouse Marker Genes"] = df_human["Human Marker Genes"].apply(convert_to_mouse_markers)
df_human["Mouse Marker Genes"] = df_human["Mouse Marker Genes"].apply(lambda x: ",".join(x))
df_selected = df_human[["Cell Type", "Mouse Marker Genes"]]
df_selected.to_csv("./mouse_breast_cancer_marker.csv")

