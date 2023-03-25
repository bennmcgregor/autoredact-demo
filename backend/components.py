import spacy
from spacy.language import Language
from spacy.tokens import Doc, Token, Span
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, PatternRecognizer, Pattern
import types
import re

# takes an annotated doc (with all redacted spans under "sc") and replaces redacted spans with an exclusion attribute
@Language.component("presidio_pre")
def presidio_pre_component(doc):
    if not Token.has_extension("is_excluded_presidio"):
        Token.set_extension("is_excluded_presidio", default=False)
    for span in doc.spans["sc"]:
        for token in span:
            token._.is_excluded_presidio = True
    return doc

def digital_root(n):
    x = sum(int(digit) for digit in str(n))
    if x < 10:
        return x
    else:
        return digital_root(x)

def sin_validation(self, pattern_text: str):
    digits = list(re.sub('[^0-9]','', pattern_text))
    mult = [digital_root(int(a)*b) for a,b in zip(digits,[1,2,1,2,1,2,1,2,1])]
    return sum(mult) % 10 == 0

can_sin_recognizer = PatternRecognizer(supported_entity="CAN_SIN", patterns=[Pattern("regex", r"\b\d{3}(?:\d{6}|([ .\/-])\d{3}\1\d{3})\b", 1.)])
can_sin_recognizer.validate_result = types.MethodType(sin_validation, can_sin_recognizer)

can_passport_recognizer = PatternRecognizer(supported_entity="CAN_PASSPORT", patterns=[Pattern("regex", r"\b[A-Z]{2}([ .\/-])?\d{3}([ .\/-])?\d{3}\b", 1.)])

zip_recognizer = PatternRecognizer(supported_entity="ZIPCODE", patterns=[Pattern("regex", r"\b\d{5}(?:[-\s]\d{4})?\b", 1.)])

can_postal_code_recognizer = PatternRecognizer(supported_entity="CAN_POSTAL_CODE", patterns=[Pattern("regex", r"\b[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d\b", 1.)])

registry = RecognizerRegistry()
registry.load_predefined_recognizers()
registry.add_recognizer(can_sin_recognizer)
registry.add_recognizer(can_passport_recognizer)
registry.add_recognizer(zip_recognizer)
registry.add_recognizer(can_postal_code_recognizer)

analyzer = AnalyzerEngine(registry=registry)

def has_excluded_tokens(span: Span):
    for token in span:
        if token._.is_excluded_presidio:
            return True
    return False

@Language.component("presidio")
def presidio_component(doc):
    if not Token.has_extension("is_excluded_presidio"):
        Token.set_extension("is_excluded_presidio", default=False)
    labels = {entity: list() for entity in analyzer.get_supported_entities()}
    analyzer_results = analyzer.analyze(text=doc.text, language="en")
    for res in analyzer_results:
        char_span = doc.char_span(res.start, res.end, label=res.entity_type, alignment_mode='expand')
        if not has_excluded_tokens(char_span):
            labels[res.entity_type].append(char_span)
    for entity in labels:
        doc.spans[entity] = labels[entity]
    return doc

condensed_categories = {
    "UPI": ["CAN_SIN", "US_SSN", "US_ITIN", "CAN_PASSPORT", "US_PASSPORT", "SG_NRIC_FIN", "AU_TFN"],
    "PERSON": ["PERSON"],
    "ADDRESS": ["EMAIL_ADDRESS", "IP_ADDRESS", "PHONE_NUMBER", "URL"],
    "BANKING": ["CREDIT_CARD", "CRYPTO", "IBAN_CODE", "US_BANK_NUMBER"],
    "MEDICAL": ["MEDICAL_LICENSE", "UK_NHS", "AU_MEDICARE"],
    "PPI": ["US_DRIVER_LICENSE", "AU_ABN", "AU_ACN"],
    "POSTCODE": ["CAN_POSTAL_CODE", "ZIPCODE"],
    "DATE_TIME": ["DATE_TIME"],
    "LOCATION": ["LOCATION"],
    "NRP": ["NRP"]
}

categorized_hierarchy = ["UPI", "PERSON", "ADDRESS", "BANKING", "MEDICAL", "PPI", "POSTCODE", "DATE_TIME", "LOCATION", "NRP"]

@Language.component("presidio_post")
def presidio_post_component(doc):
    all_data = set()
    spans = {entity: set() for entity in categorized_hierarchy}
    for entity in categorized_hierarchy:
        for cat in condensed_categories[entity]:
            for elem in doc.spans[cat]:
                if elem.text not in all_data:
                    spans[entity].add(elem)
                    all_data.add(elem.text)
    for key in list(doc.spans.keys()):
        del doc.spans[key]
    for entity in spans:
        doc.spans[entity] = list(spans[entity])
    return doc

@Language.component("redact")
def redact_component(doc):
    redacted = list()
    for entity in doc.spans:
        for span in doc.spans[entity]:
            span.label_ = "REDACTED"
            redacted.append(span)
    for key in list(doc.spans.keys()):
        del doc.spans[key]
    doc.spans["sc"] = redacted
    return doc

# nlp = spacy.load("en_core_web_sm")
# nlp.add_pipe("presidio", name="presidio", last=True)
# nlp.add_pipe("presidio_post", name="presidio_post", last=True)
# nlp.add_pipe("redact", name="redact", last=True)
# for name in ['tok2vec', 'attribute_ruler', 'lemmatizer', 'tagger', 'parser', 'ner']:
#     nlp.remove_pipe(name)
# doc = nlp("Letter from Christine Delphine Mbappé Léppé dated October 4, 2021, regarding the police search for the appellant.")