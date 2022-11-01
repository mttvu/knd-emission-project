from SPARQLWrapper import SPARQLWrapper

%load_ext ipython_sparql_pandas
%%sparql http://localhost:7200/repositories/emission-project -s provinces
PREFIX brt: <https://brt.basisregistraties.overheid.nl/brt/def/>
PREFIX typeRegistratiefGebied: <https://brt.basisregistraties.overheid.nl/brt/id/typeRegistratiefGebied/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX : <http://www.example.org/>
SELECT ?name ?polyClean {

    SERVICE <https://api.labs.kadaster.nl/datasets/brt/top10nl/services/default/sparql> 	{
        ?s ?p typeRegistratiefGebied:provincie .
        ?s skos:altLabel ?name .
        ?s brt:geometrieVlak ?poly .
        BIND((?poly) as ?polyStr) .
        BIND(replace(?polyStr, 'SRID=28992;', '<http://www.opengis.net/def/crs/EPSG/0/28992> ') as ?polyClean) .
        FILTER (lang(?name) = 'nl')
    }
}

for index, province in provinces.iterrows():
    sparql = SPARQLWrapper("http://localhost:7200/repositories/emission-project/statements")
    sparql.setMethod(POST)
    sparql.setQuery(f"""
        PREFIX : <http://www.example.org/>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        INSERT {{
            :{province['name']} a :Province .
            :{province['name']} :hasName "{province['name']}"@nl .
            :{province['name']} geo:hasGeometry ?poly
        }}
        WHERE {{
            BIND(STRDT("{province['polyClean']}", geo:wktLiteral) as ?poly)
        }}
    """)
    results = sparql.query()
