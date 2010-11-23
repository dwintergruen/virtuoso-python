## RDFLib 3 SPARQL PRocessor

import rdflib
from rdflib.graph import Graph
from rdflib.term import BNode
from rdfextras.sparql.processor import Processor as IHProcessor
from rdfextras.sparql.query import SPARQLQueryResult as IHResult

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'virtuoso.vsparql', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'virtuoso.vsparql', 'Result')

class Processor(IHProcessor):
    def query(self, query, initBindings={}, initNs={}, *av, **kw):
        from virtuoso.vstore import Virtuoso, _bnode_to_nodeid

        if not isinstance(self.graph.store, Virtuoso):
            return super(Processor, self).query(strOrQuery, initBindings, initNs, *av, **kw)
        assert isinstance(query, basestring), "Virtuoso SPARQL processor only supports string queries"

        preamble = u""
        if isinstance(self.graph, rdflib.graph.Graph):
            if isinstance(self.graph.identifier, BNode):
                graph_uri = _bnode_to_nodeid(self.graph.identifier)
            else:
                graph_uri = self.graph.identifier
            preamble = u"DEFINE input:default-graph-uri %s\n" % graph_uri.n3()

        for pfx, ns in initNs.items():
            preamble += u"PREFIX %s: <%s>\n" % (pfx, ns)

        return self.graph.store.sparql_query(preamble + query)

class Result(rdflib.query.Result):
    def __init__(self, qResult):
        self.askAnswer = []
        self.construct = False

        if isinstance(qResult, bool):
            self.askAnswer = [qResult]
        elif isinstance(qResult, Graph):
            self.construct = True
        self.result = qResult
    def __iter__(self):
        return self.result
    def __nonzero__(self):
        if self.askAnswer: return self.askAnswer[0]
        else: return False
        