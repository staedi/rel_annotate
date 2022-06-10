import generic
import streamlit as st
from itertools import combinations

def show_pages(layout=[.1,.6]):
    col1, col2 = st.columns(layout)

    with col1:
        prev_page = st.button('Prev Page',key='prev_page')
    with col2:
        next_page = st.button('Next Page',key='next_page')

    return prev_page, next_page

def show_status(update_status):
    if update_status:
        save = st.button('Save',key='save')

        return save

    return False

        

def process_spans(rel_dict,spans,spans_pos,spans_rel):
    st.subheader('Select span elements!')
    sel_spans = st.multiselect('Entities',key='multi_spans',options=[span['text'] for span in spans])

    if len(sel_spans)>=2:
        texts_list, rel_idx, rel_str = display_sidebar(rel_dict=rel_dict,spans=sel_spans,spans_pos=spans_pos)
        if rel_idx != None:
            show_summary(texts_list,rel_str,spans_rel[rel_idx])

        if len(rel_str) > 0:
            # show_summary(texts_list,rel_str,spans_rel[rel_idx])
            generic.update_session(spans_rel,rel_idx,rel_str)

            return True

    return None

def show_summary(texts_list,new_rel,prev_rel):
    st.subheader('Entity Relations Set')
    st.markdown(f'Related elements: `{texts_list[1]}` - `{texts_list[2]}`')
    st.markdown(f"Previous Relations: `{prev_rel['label']}`")

    if new_rel != prev_rel:
        st.markdown(f"New Relations: `{new_rel['label']}`")


def display_sidebar(rel_dict,spans=None,spans_pos=None):
    with st.sidebar:
        if not spans:
            st.subheader('Select relationship!')
        else:
            spans_list = list(combinations(spans,2))
            texts = st.selectbox(label='Index - Span', options=[None]+[f'{span_idx}: {span_el[0]} - {span_el[1]}' for span_idx, span_el in enumerate(spans_list)])
            if texts:
                texts_list = texts.replace(':',' -').split(' - ')
                span_dict = [span for span in st.session_state.spans_rel if span['head']==generic.get_list_value(spans_pos,texts_list[1]) and span['child']==generic.get_list_value(spans_pos,texts_list[2])][0]
                rel_idx = st.session_state.spans_rel.index(span_dict)
                category = st.selectbox(label='Category', index=len(rel_dict)-1, options=rel_dict.keys(), key='category')
                if category != 'No-rel':
                    action = st.selectbox(label='Action', options=[None]+list(rel_dict[category].keys()), key='action')
                    if action:
                        polarity = st.selectbox(label='Polarity', options=[None]+rel_dict[category][action], key='polarity')
                        if polarity:
                            span_dict['label'] = f'{polarity}-{action}'
                            # return texts_list, rel_idx, span_dict
                else:
                    span_dict['label'] = 'No-rel'
                return texts_list, rel_idx, span_dict
    return None, None, {}

def process_iterator(iter_obj,page_num,rel_dict):
    text_idx, line = generic.check_iterator(iter_obj,page_num)
    if len(line) > 0:
        text, spans_rel, spans_pos = generic.process_text(text_idx, line)
        st.subheader('Text to Annotate!')
        st.info(text['text'])

        update_status = process_spans(rel_dict=rel_dict,spans=text['spans'],spans_pos=spans_pos,spans_rel=st.session_state.spans_rel)
        generic.update_text(iter_obj,text,text_idx,st.session_state.spans_rel)

        return update_status

    return False


def display_texts(json_lines,pages,rel_dict,page_num=0):
    prev_page, next_page, page_num = generic.process_btn(json_lines,pages,page_num)
    update_status = process_iterator(json_lines,page_num,rel_dict)

    return prev_page, next_page, update_status