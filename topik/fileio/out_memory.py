from ._registry import register_input, register_output
from .base_output import OutputInterface

@register_output
class InMemoryOutput(OutputInterface):
    def __init__(self, iterable=None, content_field=None, from_existing_corpus=False,
                 content_filter=None, vectorized_data=None, tokenized_data=None,
                 model_data=None):
        super(InMemoryOutput, self).__init__()
        self.corpus = {}
        self.content_field = content_field
        if from_existing_corpus:
            self.corpus = iterable
        elif iterable and content_field:
            self.import_from_iterable(iterable, content_field)
        #else:
        #    raise ValueError("Output must be instantiated with iterable and ")
        self.content_filter = content_filter
        self.tokenized_data = tokenized_data if tokenized_data else {}
        self.vectorized_data = vectorized_data if vectorized_data else {}
        self.model_data = model_data if model_data else {}

    def get_generator_without_id(self, field=None):
        if not field:
            field = self.content_field
        for doc in self.corpus.values():
            yield doc["_source"][field]

    def append_to_record(self, record_id, field_name, field_value):
        raise NotImplementedError

    def append_from_iterable(self, iterable, field):
        """load an iterable of (id, value) pairs to the specified new or
           new or existing field within existing documents."""
        for doc_id, value in iterable:
            self.corpus[doc_id]['_source'][field] = value

    def import_from_iterable(self, iterable, content_field):
        """
        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        """
        self.content_field = content_field
        for item in iterable:
            if isinstance(item, basestring):
                item = {content_field: item}
            id = hash(item[content_field])
            self.corpus[id] = {"_source": item}

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_date_filtered_data(self, start, end, filter_field="year"):
        return InMemoryOutput(content_field=self.content_field,
                                iterable=self._documents,
                                from_existing_corpus=True,
                                content_filter={"field": filter_field, "expression": "{}<=int({})<={}".format(start, "{}", end)})

    def get_filtered_data(self, field=None, filter=""):
        if not field:
            field = self.content_field
        if not filter:
            for doc_id, doc in self.corpus.items():
                yield doc_id, doc["_source"][field]
        else:
            raise NotImplementedError

    def save(self, filename):
        saved_data = {"iterable": self.corpus,
                      "from_existing_corpus": True,
                      "models": self.models,
                      "vectorized_data": self.vectorized_data,
                      "tokenized_data": self.tokenized_data,
                      "content_filter": self.content_filter}
        return super(InMemoryOutput, self).save(filename, saved_data)
