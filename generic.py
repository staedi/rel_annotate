import streamlit as st
import json


def init_session(spans_rel=None):
    if 'spans_rel' not in st.session_state:
        st.session_state['spans_rel'] = []

    if spans_rel and spans_rel != st.session_state.spans_rel:
        st.session_state.spans_rel = spans_rel

    if 'page' not in st.session_state:
        st.session_state['page'] = 0


def update_session(spans_rel,idx,value):
    if 'spans_rel' in st.session_state:
        st.session_state.spans_rel[idx] = value


def read_text(path=None):
    if not path:
        path = 'assets/sample.jsonl'

    with open(path, "r", encoding="utf-8") as jsonfile:
        json_lines = [json_line.rstrip('\n') for json_line in jsonfile.readlines()]
        return json_lines


def update_text(iter_obj,text,text_idx,spans_rel):
    text['relations'] = spans_rel
    iter_obj[text_idx] = json.dumps(text)
    # iter_obj[text_idx] = text
    

# def write_text(iter_obj,save,path=None):
#     if save:
#         st.write(iter_obj)
#         # if not path:
#         #     path = 'assets/sample.jsonl'

#         # with open(path, "w", encoding="utf-8") as jsonfile:
#         #     for entry in iter_obj:
#         #         # json.dump(entry,jsonfile)
#         #         jsonfile.write(entry)
#         #         jsonfile.write('\n')


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