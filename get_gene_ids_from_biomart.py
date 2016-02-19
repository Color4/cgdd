from biomart import BiomartServer

server = BiomartServer( "http://www.biomart.org/biomart" )  # if not behind a proxy, otherwise see: https://pypi.python.org/pypi/biomart/0.8.0

server.verbose = True  # set verbose to True to get some messages

# run a search with custom filters and attributes (no header)
response = uniprot.search({
    'filters': {
        'accession': ['Q9FMA1', 'Q8LFJ9']
        },
    'attributes': [
        'accession', 'protein_name'
    ]
})
