import lightrdf
import gzip

RDF_FILENAME = 'knotdata/Knots11.rdf.gz'

f = gzip.open(RDF_FILENAME, 'rb')
doc = lightrdf.RDFDocument(f, parser=lightrdf.xml.PatternParser)
#for (s, p, o) in doc.search_triples(None, None, None):
#            print(s, p, o)
