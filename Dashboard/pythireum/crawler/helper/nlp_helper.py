from __future__ import unicode_literals, print_function
from ..models import Value

import spacy
import textacy
import textacy.keyterms
from spacy.matcher import PhraseMatcher
from spacy import displacy
from datetime import datetime


# https://spacy.io/usage/examples#custom-components-api
class NLP_helper():
    def __init__(self,):
        # Number of nlp computed values from texts
        self.total_found_value = 0
        # Number of texts received which is also equal to number of request
        self.total_request_analyzed = 0

    def extract_entity_french(self, text, parent_search_name, source_name):
        model = 'fr_core_news_md'

        nlp = spacy.load(model)

        print("Using model '%s'" % model)
        print("Processing %d words" % len(text))
        self.total_request_analyzed += 1
        #text = "Le CAC40 se maintient au dessus des 5400 points ce matin, cédant quelques points seulement (-0,15% à 5405 points)"
        #      det nusbj expl ROOT    case fixed det nummod obl det nmod punct acl det     obj     advmod  punct punct obl case nummod nmod punct
        # when starting from ROOT
        #print(word.text, word.dep_, word.head.text, word.head.pos_,[child for child in word.children])
        # outputs: maintient ROOT maintient VERB [CAC40, se, points, ,, cédant, -0,15, %, )]

        # Display depedancy graph on localhost:5000

        doc = nlp(text)

        #displacy.serve(doc, style="dep")

        # print number and their dep => result are not too useful
        #for word in doc:
        #    if word.pos_ in ("NUM"):
        #        for w in word.subtree:
        #            print(word, w, "".join(c.text_with_ws for c in w.subtree))

        # output Casino 4567 4572 ORG
        # in french only ORG,PERS,MISC,LOC are available
        # https://spacy.io/api/annotation
        # output also dependancy of the entity => useful some times
        #for ent in doc.ents:
        #    print(ent.text, ent.start_char, ent.end_char, ent.label_)
        #    print("".join(c.text_with_ws for c in ent.subtree))


        # output example:
        # input:  conclue par un grand chelem de cinq hausses et un gain cumulé de 3,3% pour le CAC40
        # output: de cinq hausses hausses nmod chelem
        # output: de 3,3% nmod cumulé
        # output: pour le CAC40 CAC40 nmod chelem
        #for chunk in doc.noun_chunks:
        #   print(chunk.text, chunk.root.text, chunk.root.dep_,
        #          chunk.root.head.text)


        #pattern2 = '<DET>? <NUM>* (<ADJ> <PUNCT>? <CONJ>?)* (<NOUN>|<PROPN> <PART>?)+'
        #pattern3 = '<NOUN>+ <NUM>+'
        #pattern3 = '<DET>? <NOUN>+ (<VERB>+ <ADV>? <CONJ>?)* (<ADJ> <PUNCT>? <CONJ>?)* <NUM>+'
        #doc = textacy.Doc(doc, lang='fr_core_news_md')
        #lists = textacy.extract.pos_regex_matches(doc, pattern3)
        #for list in lists:
        #    print(list.text)

        # Keywords rank of the text
        #print(textacy.keyterms.textrank(doc, normalize='lemma', n_keyterms=10))

        publication_first_sentence = next(doc.sents)
        article_date = ""
        for token in publication_first_sentence:
            if token.text == "publié":
                # Selecting the third token after publié: publié (1) le (2) dd/mm/yyy (3)
                print("article date : ", publication_first_sentence[token.i + 2:token.i + 3])
                article_date = str(publication_first_sentence[token.i + 2:token.i + 3])

        datetime_object = None
        if article_date =="":
            datetime_object = datetime.now()
        else:
            datetime_object = datetime.strptime(article_date, '%d/%m/%Y')



        # print SUJET CAC40 valeur 5400
        # This method shall be improved
        for word in doc:
            current_subject = None
            current_value = None
            if word.dep_ in ("ROOT"):
                #print(word.text, word.dep_, word.head.text, word.head.pos_,
                #      [child for child in word.children])
                for child in word.children:
                    if (child.dep_ in ("nsubj")):
                        # Keep only entities
                        for ent in doc.ents:
                            if(child.text==ent.text):
                                current_subject = child
                    if child.dep_ in ("obl"):
                        for ch in child.children:
                            if ch.dep_ in ("nummod"):
                                current_value = ch
            if current_subject and current_value:
                print(current_subject, " : ", current_value)
                Value.objects.create(parent_search=parent_search_name, origin_source=source_name, key=current_subject,
                                         value=current_value, date=datetime_object)
                self.total_found_value += 1


    def extract_entity_english(self, text, parent_search_name, source_name, tweet_date):
        model = 'en_core_web_md'

        nlp = spacy.load(model)
        print("Using model '%s'" % model)
        print("Processing %d words" % len(text))
        self.total_request_analyzed += 1

        doc = nlp(text)

        datetime_object = datetime.strptime(tweet_date, '%a %b %d %H:%M:%S +0000 %Y')
        print(datetime_object)

        relations = self.extract_currency_relations_en(doc)
        for r1, r2 in relations:
           print('{:<10} : {} \t {}'.format(r1.text, r2.ent_type_, r2.text))
           v = Value.objects.create(parent_search=parent_search_name , origin_source=source_name , key=r1.text , value=r2.text, date=datetime_object)
           self.total_found_value += 1



    def extract_currency_relations_en(self, doc):
        # merge entities and noun chunks into one token
        spans = list(doc.ents) + list(doc.noun_chunks)
        for span in spans:
            span.merge()

        relations = []
        for money in filter(lambda w: w.ent_type_ == 'MONEY' or w.ent_type_ == 'PERCENT' or w.ent_type_ == 'CARDINAL', doc):
            if money.dep_ in ('attr', 'dobj'):
                subject = [w for w in money.head.lefts if w.dep_ == 'nsubj']
                if subject:
                    subject = subject[0]
                    relations.append((subject, money))
            elif money.dep_ == 'pobj' and money.head.dep_ == 'prep':
                relations.append((money.head.head, money))
        return relations

