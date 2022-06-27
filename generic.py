from io import StringIO
from itertools import combinations
from requests import session
import spacy
import streamlit as st
import json


def init_session(session_key=None): # No updates
    if not session_key:
        if 'page' not in st.session_state:
            st.session_state['page'] = 0
        if 'text' not in st.session_state:
            st.session_state['text'] = None
        if 'spans' not in st.session_state:
            st.session_state['spans'] = []
        if 'relations' not in st.session_state:
            st.session_state['relations'] = []
        if 'annotation' not in st.session_state:
            st.session_state['annotation'] = {'filename':None, 'data':None}
        if 'span_iter_idx' not in st.session_state:
            st.session_state['span_iter_idx'] = 0
        if 'tokens_sets' not in st.session_state:
            st.session_state['tokens_sets'] = []


    elif session_key == 'page':
        st.session_state.page = 0
    elif session_key == 'text':
        st.session_state.text = None
    elif session_key == 'spans':
        st.session_state.spans = []
    elif session_key == 'relations':
        st.session_state.relations = []
    elif session_key == 'annotation':
        st.session_state.annotation = {'filename':None, 'data':None}
    elif session_key == 'span_iter_idx':
        st.session_state.span_iter_idx = 0
    elif session_key == 'tokens_sets':
        st.session_state.tokens_sets = []



def update_session(session_key,value,key=None):
    if session_key in st.session_state:
        # Category selectbox
        if session_key == 'category':
            st.session_state.category = None
        # Edit Radio button
        elif session_key == 'radio_spans':
            st.session_state.radio_spans = None

        # Page
        elif session_key == 'page':
            st.session_state.page = value
        # Text
        elif session_key == 'text':
            st.session_state.text = value
        # Spans
        elif session_key == 'spans':
            if key != None:
                st.session_state.spans[key] = value
            else:
                st.session_state.spans = value
        # Spans relations
        elif session_key == 'relations':
            if key != None:
                st.session_state.relations[key] = value
            else:
                st.session_state.relations = value
        # Intermediate JSON
        elif session_key == 'annotation':
            st.session_state.annotation[key] = value
        # Span Edit Index
        elif session_key == 'span_iter_idx':
            st.session_state.span_iter_idx = value
        # Tokens Sets
        elif session_key == 'tokens_sets':
            st.session_state.tokens_sets = value



def make_spans(span_list,spans=None,mode='generic'):
    if not isinstance(spans,list):
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


def make_relations(spans,type,relations=None,iter_idx=None):
    if not relations:
        relations = []

    if spans:
        if type == 'Reset':
            relations = []
            for span in combinations(spans,2):
                relations.append({"head": span[0]["token_start"], "child": span[1]["token_start"], 
                "head_span": {"start": span[0]["start"], "end": span[0]["end"], "token_start": span[0]["token_start"], "token_end": span[0]["token_end"], "label": span[0]["label"]},
                "child_span": {"start": span[1]["start"], "end": span[1]["end"], "token_start": span[1]["token_start"], "token_end": span[1]["token_end"], "label": span[0]["label"]},
                "label": "No-rel"})            
            # text['relations'] = relations
            if relations:
                update_session(session_key='relations',value=relations)
            # else:
            #     init_session('relations')

        elif type == 'Individual':
            if isinstance(iter_idx,list):
                for iter_dict in iter_idx:
                    relations = {}
                    for idx, key in iter_dict.items():
                        relations = st.session_state.relations[int(idx)]
                        if key == 'head_span':
                            relations['head'] = spans['token_start']
                            relations['head_span'] = {key:val for key,val in spans.items() if key in ('start','end','token_start','token_end','label')}
                        elif key == 'child_span':
                            relations['child'] = spans['token_start']
                            relations['child_span'] = {key:val for key,val in spans.items() if key in ('start','end','token_start','token_end','label')}
                        relations['label'] = 'No-rel'

                        if relations:
                            update_session(session_key='relations',key=int(idx),value=relations)

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

        spans = make_spans(span_list=doc.ents,spans=spans,mode='spacy')
        relations = make_relations(spans=spans,type='Reset',relations=relations)

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

    init_session('page')
    init_session('text')
    init_session('spans')
    init_session('relations')
    init_session('annotation')
    init_session('span_iter_idx')
    init_session('tokens_sets')

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

    update_session(session_key='annotation',key='filename',value=filename)
    update_session(session_key='annotation',key='data',value=json_lines)

    return json_lines


def update_text(iter_obj,text,text_idx,relations):
    text['relations'] = relations
    iter_obj[text_idx] = json.dumps(text)
    # iter_obj[text_idx] = text


def get_obj_value(iter_obj,target_value,access='key'):
    if access == 'key':    # access by key
        target_list = target_value.replace('(','').replace(')','-').split('-')
        if len(target_list)==1:
            target_list.append(0)
        else:
            target_list[1] = int(target_list[1])-1

        return iter_obj.get(target_list[0])[target_list[1]]
        # return iter_obj.get(target_value)
        # return max([iter[1] for iter in iter_obj if iter[0]==target_value])
    else:   # access by value
        # return max([f'{value.index(target_value)+1}: {idx}' if len(value)>1 else idx for idx,value in iter_obj.items() if target_value in value])
        return max([f'{idx} ({value.index(target_value)+1})' if len(value)>1 else idx for idx,value in iter_obj.items() if target_value in value])


def check_iterator(iter_obj,page_num):
    try:
        # text_idx, line = next(iter_obj)
        text_idx, line = page_num, list(iter_obj)[page_num]
        return text_idx, line
    except:
        return None, ''


def process_text(text_idx, line):
    text = json.loads(line)
    relations = [dict((key,rel[key]) for key in ('head','child','label')) for rel in text['relations']]
    relations = text['relations']
    spans = text['spans']

    if not st.session_state.page or st.session_state.annotation['data'][st.session_state.page] != line:
        update_session(session_key='page',value=text_idx)
    if not st.session_state.text or st.session_state.annotation['data'][st.session_state.page] != line:
        update_session(session_key='text',value=text['text'])
    if not st.session_state.spans or st.session_state.annotation['data'][st.session_state.page] != line:
        update_session(session_key='spans',value=spans)
    if not st.session_state.relations or st.session_state.annotation['data'][st.session_state.page] != line:
        update_session(session_key='relations',value=relations)

    # spans_pos = dict((span['text'],span['token_start']) for span in text['spans'])

    return text, relations#, spans_pos


def process_displayc(text):
    doc = [{'text':text['text'],'ents':text['spans']}]
    labels = [ents['label'] for ents in doc[0]['ents']]

    return doc, labels


def process_btn(json_lines,pages,page_num=0):
    if pages[0]:    # prev_page
        if st.session_state.page > 0:
            update_session(session_key='page',value=st.session_state.page-1)
            # update_session(session_key='radio_span',value=None)
            # update_session(session_key='category',value=None)

            init_session('text')
            init_session('spans')
            init_session('relations')
            init_session('span_iter_idx')
            init_session('tokens_sets')

            # st.session_state.page -= 1
            # st.session_state.text = None
            # st.session_state.spans = []
            # st.session_state.relations = []
            # # st.session_state.spans_rel = []
    if pages[1]:    # next_page
        if st.session_state.page < len(json_lines)-1:
            update_session(session_key='page',value=st.session_state.page+1)
            init_session('text')
            init_session('spans')
            init_session('relations')
            init_session('span_iter_idx')
            init_session('tokens_sets')

            # st.session_state.page += 1
            # st.session_state.text = None
            # st.session_state.spans = []
            # st.session_state.relations = []
            # # st.session_state.spans_rel = []

    page_num = st.session_state.page
    prev_page, next_page = False, False

    return prev_page, next_page, page_num


def process_sel_span(span_sel,text,tokens_sets):
    spans_sets = text['spans']
    token_ends_dict = {'token_end':text['tokens'][-1]['id']+len(text['tokens'][-1]['text']),'end':text['tokens'][-1]['end']}
    spans_start, spans_end = get_tokens_range(span_sel,text['spans'],token_ends_dict)
    tokens_sets = [tokens for tokens in tokens_sets if tokens['token_start']>=spans_start and tokens['token_start']<=spans_end]

    return spans_sets, tokens_sets
    # return tokens_sets


def process_multisel_span(text,spans_sets,tokens_sets,type,span_multisel=None,iter_idx=None):
    # span_multisel = [st.session_state.span_start, st.session_state.span_end]

    if type == 'Individual':
        # span_multisel = st.session_state.multi_span
        span_multisel = [st.session_state.span_start, st.session_state.span_end]
    # elif not span_multisel:
    #     span_multisel = st.session_state[f'span_{iter_idx}']
    # # else:
    # #     span_multisel = [st.session_state[f'span_start_{iter_idx}'], st.session_state[f'span_end_{iter_idx}']]

    if span_multisel and len(span_multisel) > 0:
        span_start, span_end = min(map(lambda x:int(x[:x.find(':')]),span_multisel)), max(map(lambda x:int(x[:x.find(':')]),span_multisel))
        # st.write(make_spans([tokens for tokens in tokens_sets if tokens['token_start']>=span_start and tokens['token_start']<=span_end]))

        if type == 'Reset':
            iters = iter_idx + 1
            if len(span_multisel)>1:
                spans_sets.append(make_spans([token for token in tokens_sets if token['token_start']>=span_start and token['token_start']<=span_end]))
                tokens_sets = [token for token in tokens_sets if (span_start>0 and token['token_start']<span_start) or (span_end<len(text['tokens']) and token['token_start']>span_end)]
                # update_session(session_key='spans',value=spans_sets)
                # make_relations(spans=spans_sets,type=type)

        elif type == 'Individual':
            prev_span = {key:val for key,val in spans_sets[iter_idx].items() if key in ('start','end','token_start','token_end','label')}
            iters = [{idx:'head_span'} if x['head_span']==prev_span else {idx:'child_span'} for idx,x in enumerate(text['relations']) if x['head_span']==prev_span or x['child_span']==prev_span]
            # st.write(make_spans([token for token in tokens_sets if token['token_start']>=span_start and token['token_start']<=span_end]))
            spans_sets[iter_idx] = make_spans([token for token in tokens_sets if token['token_start']>=span_start and token['token_start']<=span_end])
            # update_session(session_key='spans',key=iter_idx,value=spans_sets[iter_idx])
            # make_relations(spans=spans_sets[iter_idx],iter_idx=iters,type=type)

        # # text['spans'] = spans_sets
        # text['spans'], text['relations'] = st.session_state.spans, st.session_state.relations

    # elif type == 'Reset':
    #     # iter_idx = -1
    #     iters = -1

    else:
        iters = -1

    return text, spans_sets, tokens_sets, iters