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


def make_spans(span_list,spans=None,mode='generic'):
    if not spans:
        if mode == 'spacy':
            if span_list.label_ not in ('DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'):
                start = span_list.start_char
                token_start = span_list.start
                token_end = span_list.end
                end = span_list.end_char
                text = span_list.text
                type = 'span'
                label = span_list.label_
            else:
                return {'text':None,'start':None,'token_start':None,'token_end':None,'end':None,'type':None,'label':None}

        else:   # custom spans ('generic')
            start = min(map(lambda x:x['start'],span_list))
            token_start = min(map(lambda x:x['token_start'],span_list))
            token_end = max(map(lambda x:x['token_start']+1,span_list))
            end = max(map(lambda x:x['start']+len(x['text']),span_list))
            text = ' '.join(map(lambda x:x['text'],span_list))
            type = 'span'
            label = 'ORG'
        return {'text':text,'start':start,'token_start':token_start,'token_end':token_end,'end':end,'type':type,'label':label}

    else:
        if mode == 'spacy':
            for ent in span_list:
                if ent.label_ not in ('DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'):
                    spans.append({"text":ent.text,"start":ent.start_char,"token_start":ent.start,"token_end":ent.end,"end":ent.end_char,"type":"span","label":ent.label_})
            return spans


def make_relations(spans,text):
    relations = []
    if spans:
        for span in combinations(spans,2):
            relations.append({"head": span[0]["token_start"], "child": span[1]["token_start"], 
            "head_span": {"start": span[0]["start"], "end": span[0]["end"], "token_start": span[0]["token_start"], "token_end": span[0]["token_end"], "label": span[0]["label"]},
            "child_span": {"start": span[1]["start"], "end": span[1]["end"], "token_start": span[1]["token_start"], "token_end": span[1]["token_end"], "label": span[0]["label"]},
            "label": "No-rel"})
        text['relations'] = relations
        init_session(spans_rel=relations)

    return relations


def get_tokens_range(span_sel,spans,token_ends_dict):
    idx = int(span_sel[:span_sel.find(':')])

    # First span
    if idx-1<0:
        start, token_start = 0, 0
    else:
        start, token_start = spans[idx-1]['end'], spans[idx-1]['token_end']

    # Last span
    if idx+1>=len(spans):
        token_end, end = token_ends_dict['token_end'], token_ends_dict['end']
    else:
        token_end, end = spans[idx+1]['token_start']-1, spans[idx+1]['start']-len(spans[idx+1]['text'])

    return token_start, token_end


def pre_nlp(lines,nlp=None):
    if not nlp:
        nlp = spacy.load('en_core_web_md')

    annotations = []

    for line in lines:
        spans = []
        tokens = []
        relations = []

        doc = nlp(line)

        # Original
        # for ent in doc.ents:
        #     if ent.label_ not in ('DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'):
        #         spans.append({"text":ent.text,"start":ent.start_char,"token_start":ent.start,"token_end":ent.end,"end":ent.end_char,"type":"span","label":ent.label_})

        # Individual
        # for ent in doc.ents:  
        #     spans.append(make_spans(ent))

        spans = make_spans(doc.ents,spans,'spacy')
        relations = make_relations(spans,relations)

        # for span in combinations(spans,2):
        #     relations.append({"head": span[0]["token_start"], "child": span[1]["token_start"], 
        #     "head_span": {"start": span[0]["start"], "end": span[0]["end"], "token_start": span[0]["token_start"], "token_end": span[0]["token_end"], "label": span[0]["label"]},
        #     "child_span": {"start": span[1]["start"], "end": span[1]["end"], "token_start": span[1]["token_start"], "token_end": span[1]["token_end"], "label": span[0]["label"]},
        #     "label": "No-rel"})

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


def get_obj_value(iter_obj,target_value,access='key'):
    if access == 'key':    # access by key
        return iter_obj.get(target_value)
    else:   # access by value
        return max([idx for idx,value in iter_obj.items() if value==target_value])


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
    if not st.session_state.spans_rel or spans_rel != st.session_state.spans_rel:
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


def process_sel_span(span_sel,text,tokens_sets):
    spans_sets = text['spans']
    token_ends_dict = {'token_end':text['tokens'][-1]['id']+len(text['tokens'][-1]['text']),'end':text['tokens'][-1]['end']}
    spans_start, spans_end = get_tokens_range(span_sel,text['spans'],token_ends_dict)
    tokens_sets = [tokens for tokens in tokens_sets if tokens['token_start']>=spans_start and tokens['token_start']<=spans_end]

    return spans_sets, tokens_sets


def process_multisel_span(span_multisels,text,spans_sets,tokens_sets,type,iter_idx=0):
    if len(span_multisels) > 0:
        span_start, span_end = min(map(lambda x:int(x[:x.find(':')]),span_multisels)), max(map(lambda x:int(x[:x.find(':')]),span_multisels))
        st.write(make_spans([tokens for tokens in tokens_sets if tokens['token_start']>=span_start and tokens['token_start']<=span_end]))

        if type == 'Reset':
            spans_sets.append(make_spans([token for token in tokens_sets if token['token_start']>=span_start and token['token_start']<=span_end]))
            tokens_sets = [token for token in tokens_sets if (span_start>0 and token['token_start']<span_start) or (span_end<len(text['tokens']) and token['token_start']>span_end)]
            iter_idx += 1
            
        elif type == 'Individual':
            spans_sets[iter_idx] = make_spans([token for token in tokens_sets if token['token_start']>=span_start and token['token_start']<=span_end])

        text['spans'] = spans_sets

    elif type == 'Reset':
        iter_idx = -1

    return text, spans_sets, tokens_sets, iter_idx