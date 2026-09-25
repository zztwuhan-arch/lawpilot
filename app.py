import hashlib
import json
from pathlib import Path
import zipfile
import streamlit as st
from dotenv import load_dotenv
from agent import demo_review, run_agent
load_dotenv()
st.set_page_config(page_title='LawPilot',layout='wide')
st.title('LawPilot · 独立中国法审查 Agent')
st.caption('自主选择工具 → 检索原文 → 校验证据 → 审查草稿 → 人工复核。原型，不自动形成正式法律意见。')
mode=st.sidebar.radio('运行方式',['无密钥演示','OpenAI Agent'])
st.sidebar.info('演示是关键词规则；OpenAI 模式会将材料发送给模型。仅上传你有权处理的材料。')
stance=st.text_input('我方立场与目标','甲方采购方：核查付款、交付和验收安排，输出核心问题。')
with zipfile.ZipFile(Path(__file__).with_name('testset.zip')) as z:
    sample=z.read('china-legal-testset-v1/inputs/C02/contract.md').decode()
text=st.text_area('合同文本（内置为合成示例）',sample,height=260)
files=st.file_uploader('补充合同或附件：UTF-8 TXT / Markdown；本版不解析 PDF / Word',type=['txt','md'],accept_multiple_files=True)
docs={'contract':text} if text.strip() else {}
try:
    for i,f in enumerate(files): docs[f'attachment_{i+1}']=f.getvalue().decode('utf-8-sig')
except UnicodeDecodeError:
    st.error('请上传 UTF-8 文本。'); st.stop()
fingerprint=hashlib.sha256(json.dumps([docs,stance,mode],ensure_ascii=False).encode()).hexdigest()
if st.session_state.get('fingerprint')!=fingerprint:
    st.session_state.pop('report',None); st.session_state.pop('human',None)
if st.button('开始审查',type='primary'):
    try:
        with st.spinner('正在审查；真实 Agent 最多 12 步，通常需要数分钟…'):
            st.session_state['report']=(demo_review if mode=='无密钥演示' else run_agent)(docs,stance)
            st.session_state['fingerprint']=fingerprint
    except (ValueError,RuntimeError) as e: st.error(str(e))
report=st.session_state.get('report')
if report:
    st.subheader('审查草稿 · 等待人工复核')
    st.write(report['summary'])
    for finding in report['findings']:
        with st.expander(f"{finding['severity']} | {finding['title']}",expanded=True):
            st.write(finding['rationale']); st.write('建议：'+finding['suggestion'])
            for e in finding['evidence']: st.code(e['source_id']+'：'+e['quote'])
    st.write('待补充信息',report['missing_information'])
    st.write('待核验法律依据',report['legal_verification_required'])
    if report['unread_ranges']: st.warning('未读范围：'+ '; '.join(report['unread_ranges']))
    with st.expander('Agent 工具执行记录'): st.json(report['trace'])
    with st.form('human_review'):
        decision=st.selectbox('人工处理',['要求补充材料','修改后接受草稿','接受草稿','退回重审'])
        note=st.text_area('复核理由（必填）')
        if st.form_submit_button('记录人工复核'):
            if not note.strip(): st.error('请填写复核理由。')
            else: st.session_state['human']={'decision':decision,'note':note}
    human=st.session_state.get('human')
    if human: st.success('已记录本会话人工复核：'+human['decision'])
    exported={**report,'human_review':human,'status':'human_review_recorded' if human else report['status']}
    st.download_button('下载审查记录 JSON',json.dumps(exported,ensure_ascii=False,indent=2),'lawpilot-review.json','application/json')
    st.caption('材料和结果仅保留在本次会话；需要留档请下载。人工接受草稿不代表已完成法律核验。')
