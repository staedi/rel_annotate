import generic
import streamlit as st
import spacy_streamlit
from itertools import combinations
import pandas as pd
import json
import sys

def show_pages(type='page',data=None,layout=[.1,.6]):
    cols = st.columns(layout)
    returns = []

    if type == 'page':
        data = ['Prev Page','Next Page']

    for col_idx, col in enumerate(cols):
        with col:
            if type == 'page':
                returns.append(st.button(data[col_idx],key=data[col_idx].lower().replace(' ','_')))

    return returns


def save_data(update_status,iter_obj,path=None):
    if update_status or path:
        if not path:
            filename = 'sample2.jsonl'
        else:
            filename = f"{path.name[:path.name.rfind('.')]}_out.jsonl"

        if sys.platform != 'linux':
            filename = f'assets/{filename}'
        
        if sys.platform == 'linux':
            json_str = '\n'.join(iter_obj)
            jsonl = list(map(lambda x:json.loads(x),iter_obj))
            save = st.download_button('Download',key='save',data=json_str,file_name=path)

        else:
            save = st.button('Save',key='save')
            if save:
                with open(filename, "w", encoding="utf-8") as jsonfile:
                    for entry in iter_obj:
                        # json.dump(entry,jsonfile)
                        jsonfile.write(entry)
                        jsonfile.write('\n')        

def process_spans(rel_dict,spans,spans_pos,spans_rel,prev_rel):
    st.subheader('Select span elements!')
    sel_spans = st.multiselect('Entities',key='multi_spans',options=[span['text'] for span in spans],on_change=generic.update_session,kwargs={'session_key':'radio_spans','key':None,'value':None})

    if len(sel_spans)>=2:
        _, _, texts_list, rel_idx, rel_str = display_sidebar(rel_dict=rel_dict,spans=sel_spans,spans_pos=spans_pos)
        if rel_idx != None:
            show_summary(texts_list,rel_str,prev_rel[rel_idx])

        if len(rel_str) > 0:
            # show_summary(texts_list,rel_str,spans_rel[rel_idx])
            generic.update_session('spans_rel',rel_idx,rel_str)

            return True

    return None


def show_summary(texts_list,new_rel,prev_rel):
    st.subheader('Entity Relations Set')
    st.markdown(f'Related elements: `{texts_list[1]}` - `{texts_list[2]}`')
    st.markdown(f"Previous Relations: `{prev_rel['label']}`")

    if new_rel != prev_rel:
        st.markdown(f"New Relations: `{new_rel['label']}`")


def show_table(spans_pos):
    df_header = f"Entities | Relations \n---|---\n"
    df_data = [f"***{generic.get_obj_value(spans_pos,spans['head'],access='value')}*** - ***{generic.get_obj_value(spans_pos,spans['child'],access='value')}*** | `{spans['label']}`" for spans in st.session_state.spans_rel]
    
    df = df_header + '\n'.join(df_data)

    st.subheader('Total Entity Relations Set')
    st.markdown(df)
    st.markdown('\n')


def display_sidebar(rel_dict,spans=None,spans_pos=None):
    with st.sidebar:
        if not spans and not spans_pos:
            st.subheader('Select a file to upload')
            upload = st.file_uploader('Upload',type=['txt','jsonl'],key='upload')
            json_lines = generic.read_text(upload)

            return upload, json_lines, None, None, {}

        elif not spans:
            st.subheader('Select entities to analyze')

        else:
            spans_list = list(combinations(spans,2))
            texts = st.selectbox(label='Index - Span', options=[None]+[f'{span_idx}: {span_el[0]} - {span_el[1]}' for span_idx, span_el in enumerate(spans_list)], key='index_span', on_change=generic.update_session, kwargs={'session_key':'category','key':None,'value':None})
            if texts:
                texts_list = texts.replace(':',' -').split(' - ')
                span_dict = [span for span in st.session_state.spans_rel if span['head']==generic.get_obj_value(spans_pos,texts_list[1]) and span['child']==generic.get_obj_value(spans_pos,texts_list[2])][0]
                rel_idx = st.session_state.spans_rel.index(span_dict)

                category = st.selectbox(label='Category', options=[None]+list(rel_dict.keys()), key='category')

                if category != None:
                    if category != 'No-rel':
                        action = st.selectbox(label='Action', options=[None]+list(rel_dict[category].keys()), key='action')
                        if action:
                            polarity = st.selectbox(label='Polarity', options=[None]+rel_dict[category][action], key='polarity')
                            if polarity:
                                span_dict['label'] = f'{polarity}-{action}'
                                # return texts_list, rel_idx, span_dict
                    else:
                        span_dict['label'] = 'No-rel'
                return None, None, texts_list, rel_idx, span_dict
    return None, None, None, None, {}


def process_iterator(iter_obj,page_num,rel_dict):
    text_idx, line = generic.check_iterator(iter_obj,page_num)
    if len(line) > 0:
        text, spans_rel, spans_pos = generic.process_text(text_idx, line)
        st.markdown(f'Current Page: `{page_num+1}` of `{len(iter_obj)}`')
        st.subheader('Text to Annotate!')

        ## NEW - Modify spans
        tokens_sets = [{'text':tokens['text'],'start':tokens['start'],'token_start':tokens['id']} for tokens in text['tokens']]
        spans_sets = []
        # relations = []

        edit_spans = st.sidebar.radio('Modify spans',key='radio_spans',options=[None,'Reset','Individual'])

        if edit_spans:
            iter_idx = 0
            if edit_spans == 'Reset':   # Resetting previous spans and relations
                while tokens_sets and iter_idx >= 0:
                    span_multisels = st.multiselect(f'Span-{iter_idx}',key=f'span_{iter_idx}',options=map(lambda x:f"{x['token_start']}: {x['text']}",tokens_sets))
                    text, spans_sets, tokens_sets, iter_idx = generic.process_multisel_span(span_multisels=span_multisels,text=text,spans_sets=spans_sets,tokens_sets=tokens_sets,type=edit_spans,iter_idx=iter_idx)
                    relations = generic.make_relations(spans=spans_sets,text=text,type=edit_spans)

            elif edit_spans == 'Individual':    # Only changing selected span
                span_sel = st.selectbox('Span',key='select_span',options=[None]+list(map(lambda x:f"{text['spans'].index(x)}: {x['text']}",text['spans'])))
                if span_sel:
                    spans_sets, tokens_sets = generic.process_sel_span(span_sel=span_sel,text=text,tokens_sets=tokens_sets)
                    span_multisel = st.multiselect(f'Span',options=map(lambda x:f"{x['token_start']}: {x['text']}",tokens_sets))
                    iter_idx=int(span_sel[:span_sel.find(':')])
                    text, spans_sets, tokens_sets, spans_idx = generic.process_multisel_span(span_multisels=span_multisel,text=text,spans_sets=spans_sets,tokens_sets=tokens_sets,type=edit_spans,iter_idx=iter_idx)
                    relations = generic.make_relations(spans=spans_sets[iter_idx],text=text,iter_idx=spans_idx,type=edit_spans)

            # relations = generic.make_relations(spans_sets,text,iter_idx)

        doc, labels = generic.process_displayc(text)
        spacy_streamlit.visualize_ner(doc,show_table=False,manual=True,labels=labels,title='')
        # st.info(text['text'])
        show_pages(type='spans',layout=[.2,.3])

        sel_rel = st.sidebar.checkbox('Show Relations')
        if sel_rel:
            show_table(spans_pos)
            
        update_status = process_spans(rel_dict=rel_dict,spans=text['spans'],spans_pos=spans_pos,spans_rel=st.session_state.spans_rel,prev_rel=text['relations'])
        generic.update_text(iter_obj,text,text_idx,st.session_state.spans_rel)


        return update_status

    return False


def display_texts(json_lines,pages,rel_dict,page_num=0):
    prev_page, next_page, page_num = generic.process_btn(json_lines,pages,page_num)
    update_status = process_iterator(json_lines,page_num,rel_dict)

    return prev_page, next_page, update_status