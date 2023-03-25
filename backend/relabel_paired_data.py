import string
from spacy.tokens import DocBin, Span
import spacy
from components import *
import calendar

presidio_nlp = spacy.load("en_core_web_sm")
presidio_nlp.add_pipe("presidio", name="presidio", last=True)
presidio_nlp.add_pipe("presidio_post", name="presidio_post", last=True)
for name in ['tok2vec', 'attribute_ruler', 'lemmatizer', 'tagger', 'parser', 'ner']:
    presidio_nlp.remove_pipe(name)

total_ids = 0
total_contexts = 0

def should_scrub(label):
    return label.text.isspace() or all(x in string.punctuation for x in label.text) or label.text in ["'s", "’s"]

def is_date(span):
    no_punc = span.text.translate(str.maketrans('', '', string.punctuation)).lower().split(" ")
    if no_punc[0] in [month.lower() for month in calendar.month_name]:
        if len(no_punc) == 1:
            return True
        elif len(no_punc) == 2 and no_punc[1].isnumeric() and int(no_punc[1]) in range(1, 32):
            return True
    return False

hardcoded_ids = ["N’Tolla", "Solange", "Mumbu", "Easter", "Junior", "Jovais", "Vilgrain", "Vanegas", "Velásquez", "Sánchez", "Moreno", "Sanchez", "Ibrahim", "Oluwamuyiwa", "Akpala", "Anjembe", "Manjinder", "Aruwa", "Juanita", "Yveline", "Isnardin", "Jianning", "Liling", "Oluwanifemi", "K.S.", "Luis", "Felipe", "Garces", "Caceres", "Josée", "Al Khatib", "Ali’s", "Desiny", "A.B."]
hardcoded_contexts = ["Los", "Rastrojos", "Les", "Cayes", "Charrier", "Rig", "Luena", "Vanni"]

def find_hardcoded_id(span):
    for id in hardcoded_ids:
        if re.search(id, span.text, re.IGNORECASE):
            return True
    return False

def find_hardcoded_context(span):
    for context in hardcoded_contexts:
        if re.search(context, span.text, re.IGNORECASE):
            return True
    return False

def relabel(doc):
    global total_ids, total_contexts
    id_labels = list()
    context_labels = list()
    for span in doc.spans["sc"]:
        if find_hardcoded_id(span):
            id_labels.append(Span(doc, span.start, span.end, label="ID"))
            continue
        elif find_hardcoded_context(span):
            context_labels.append(Span(doc, span.start, span.end, label="CONTEXT"))
            continue
        elif all(x.isalpha() or x.isspace() for x in span.text) and span.text.isupper() and len(span) / len(doc) > 0.25:
            id_labels.append(Span(doc, span.start, span.end, label="ID"))
            continue
        elif is_date(span):
            id_labels.append(Span(doc, span.start, span.end, label="ID"))
            continue

        id_positions = list()
        temp_id_labels = list()
        temp_context_labels = list()

        start_context_offset = min(40, span.start_char)
        end_context_offset = min(40, len(doc.text)-span.end_char)
        analyzed_span = doc.char_span(span.start_char-start_context_offset, span.end_char+end_context_offset, alignment_mode="contract")
        
        for i, token in enumerate(analyzed_span):
            if token.i == span[0].i:
                start_token_idx = i
            if token.i == span[-1].i:
                end_token_idx = i

        annotated_span = presidio_nlp(analyzed_span.text)
        for key in ["UPI", "PERSON", "ADDRESS", "BANKING", "MEDICAL", "PPI", "POSTCODE", "DATE_TIME"]:
            for id in annotated_span.spans[key]:
                if (id[-1].i >= start_token_idx and id[-1].i <= end_token_idx) or (id[0].i <= end_token_idx and id[0].i >= start_token_idx):
                    id_start_idx_in_span = max(id[0].i, start_token_idx)
                    id_end_idx_in_span = min(id[-1].i, end_token_idx)
                    temp_id_labels.append(Span(doc, analyzed_span.start+id_start_idx_in_span, analyzed_span.start+id_end_idx_in_span+1, label="ID"))
                    id_positions.append((analyzed_span.start+id_start_idx_in_span, analyzed_span.start+id_end_idx_in_span+1))
        if len(id_positions) == 0:
            temp_context_labels.append(Span(doc, span.start, span.end, label="CONTEXT"))
        elif len(id_positions) == 1:
            id = id_positions[0]
            if len(id) < len(span):
                if id[1] < span.end:
                    temp_context_labels.append(Span(doc, id[1], span.end, label="CONTEXT"))
                if id[0] > 0:
                    temp_context_labels.append(Span(doc, span.start, id[0], label="CONTEXT"))

        id_labels.extend(temp_id_labels)
        context_labels.extend(temp_context_labels)

    # scrub out all spans that are purely whitespace or punctuation
    id_labels = [id for id in id_labels if not should_scrub(id)]
    context_labels = [context for context in context_labels if not should_scrub(context)]

    # for alpha strings in context, check if they are substrings of any elements in id_labels. If so, remove from context and add to id_labels.
    to_remove_context = list()
    for i, context in enumerate(context_labels):
        for id in id_labels:
            if context.text.isalpha() and re.search(context.text, id.text, re.IGNORECASE):
                context.label_="ID"
                id_labels.append(context)
                to_remove_context.append(i)
                break
    for idx in reversed(to_remove_context):
        del context_labels[idx]

    doc.spans["sc"].extend(id_labels)
    doc.spans["sc"].extend(context_labels)
    if len(id_labels) > 0 or len(context_labels) > 0:
        print(f"id_labels: {id_labels} context_labels: {context_labels}")
    # to_print = set()
    # for label in context_labels:
    #     if label.text[0].isupper():
    #         to_print.add(label.text)
    # for s in to_print:
    #     print(s)
    total_ids += len(id_labels)
    total_contexts += len(context_labels)
    return doc

def relabelled_doc():
    path = "./paired_data.spacy"
    relabeled_doc_bin = DocBin(attrs=[])
    doc_bin = DocBin().from_disk(path)
    for doc in doc_bin.get_docs(presidio_nlp.vocab):
        relabeled_doc_bin.add(relabel(doc))
    relabeled_doc_bin.to_disk("relabelled_paired_data.spacy")

    print(f"total ids: {total_ids}")
    print(f"total contexts: {total_contexts}")