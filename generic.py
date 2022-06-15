from io import StringIO
from itertools import combinations
import spacy
import streamlit as st
import json


def init_session(spans_rel=None):
    if 'spans_rel' not in st.session_state:
        st.session_state['spans_rel'] = []

    if spans_rel and spans_rel != st.session_state.spans_rel:
        st.session_state.spans_rel = spans_rel

    if 'page' not in st.session_state:
        st.session_state['page'] = 0

    if 'annotation' not in st.session_state:
        st.session_state['annotation'] = {'filename':None, 'data':None}


def update_session(session_key,key,value):
    if session_key in st.session_state:
        # Spans relations
        if session_key == 'spans_rel':
            st.session_state.spans_rel[key] = value
        # Intermediate JSON
        elif session_key == 'annotation':
            st.session_state.annotation[key] = value
        # Category selectbox
        elif session_key == 'category':
            st.session_state.category = None


def pre_nlp(lines,nlp=None):
    if not nlp:
        nlp = spacy.load('en_core_web_md')

    annotations = []

    for line in lines:
        spans = []
        tokens = []
        relations = []

        doc = nlp(line)

        for ent in doc.ents:
            if ent.label_ not in ('DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'):
                spans.append({"text":ent.text,"start":ent.start_char,"token_start":ent.start,"token_end":ent.end,"end":ent.end_char,"type":"span","label":ent.label_})
    
        for span in combinations(spans,2):
            relations.append({"head": span[0]["token_start"], "child": span[1]["token_start"], 
            "head_span": {"start": span[0]["start"], "end": span[0]["end"], "token_start": span[0]["token_start"], "token_end": span[0]["token_end"], "label": span[0]["label"]},
            "child_span": {"start": span[1]["start"], "end": span[1]["end"], "token_start": span[1]["token_start"], "token_end": span[1]["token_end"], "label": span[0]["label"]},
            "label": "No-rel"})

        token_range_2d = list(map(lambda x:[idx for idx in range(x['token_start'],x['token_end'])],spans))
        token_range = []

        list(map(lambda x:token_range.extend(x),token_range_2d))

        for token in doc:
            if token.i in token_range:
                tokens.append({"text":token.text,"start":token.idx,"end":token.idx+len(token.text),"id":token.i,"ws":token.whitespace_ == ' ',"disabled":False})
            else:
                tokens.append({"text":token.text,"start":token.idx,"end":token.idx+len(token.text),"id":token.i,"ws":token.whitespace_ == ' ',"disabled":True})

        annotations.append(json.dumps({"text":line,"spans":spans,"tokens":tokens,"_view_id":"relations","relations":relations,"answer":"accept"}))

    return annotations, nlp


# @st.cache(allow_output_mutation=True)
def read_text(path=None):
    if not path:
        filename = 'assets/sample.jsonl'
    else:
        filename = path.name

    # Check if the same data exists (already loaded)
    if st.session_state.annotation['filename'] == filename:
        return st.session_state.annotation['data']

    # No file uploaded
    if not path:
        with open(filename, "r", encoding="utf-8") as file:
            json_lines = [line.rstrip('\n') for line in file.readlines()]

    else:
        stringio = StringIO(path.getvalue().decode('utf-8'))
        lines = [line.rstrip('\n') for line in stringio.readlines()]

        # .txt file
        if filename.find('txt') != -1:
            lines = list(map(lambda x:x[:x.find(' |')] if x.find('| ') != -1 else x,lines))
            json_lines, nlp = pre_nlp(lines)
        else:
            json_lines = lines

    update_session('annotation','filename',filename)
    update_session('annotation','data',json_lines)

    # st.session_state.annotation['filename'] = filename
    # st.session_state.annotation['data'] = json_lines

    return json_lines


def update_text(iter_obj,text,text_idx,spans_rel):
    text['relations'] = spans_rel
    iter_obj[text_idx] = json.dumps(text)
    # iter_obj[text_idx] = text


def get_list_value(target_list,value):
    return target_list.get(value)


def check_iterator(iter_obj,page_num):
    try:
        # text_idx, line = next(iter_obj)
        text_idx, line = page_num, list(iter_obj)[page_num]
        return text_idx, line
    except:
        return None, ''


def process_text(text_idx, line):
    text = json.loads(line)
    spans_rel = [dict((key,rel[key]) for key in ('head','child','label')) for rel in text['relations']]
    spans_rel = text['relations']
    if not st.session_state.spans_rel:
        init_session(spans_rel)

    spans_pos = dict((span['text'],span['token_start']) for span in text['spans'])

    return text, spans_rel, spans_pos


def process_displayc(text):
    doc = [{'text':text['text'],'ents':text['spans']}]
    labels = [ents['label'] for ents in doc[0]['ents']]

    return doc, labels


def process_btn(json_lines,pages,page_num=0):
    if pages[0]:    # prev_page
        if st.session_state.page > 0:
            st.session_state.page -= 1
            st.session_state.spans_rel = []
    if pages[1]:    # next_page
        if st.session_state.page < len(json_lines)-1:
            st.session_state.page += 1
            st.session_state.spans_rel = []

    page_num = st.session_state.page
    prev_page, next_page = False, False

    return prev_page, next_page, page_num


# def reset_select(key='category'):
#     if key in st.session_state:
#         st.session_state.category = None
#     return