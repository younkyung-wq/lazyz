import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="LAZYZ Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stSidebar"] > div:first-child {
    background-color: #111111 !important;
}
[data-testid="stSidebarContent"] {
    background-color: #111111 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] {
    min-width: 240px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 0px; }
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 10px 16px; border-radius: 8px; cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(255,255,255,0.05);
}
[data-testid="stSidebar"] .stRadio label p { color: #aaaaaa !important; font-size: 14px !important; }
[data-testid="stSidebar"] [aria-checked="true"] p { color: #ffffff !important; }
[data-testid="stSidebar"] input {
    background: #222 !important; color: #fff !important;
    border: 1px solid #333 !important; border-radius: 8px !important;
}
[data-testid="stSidebar"] hr { border-color: #333 !important; }
.block-container {
    padding-top: 0.5rem !important; padding-left: 1.5rem !important;
    padding-right: 1.5rem !important; max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# ── Story Editor HTML (defined before use) ────────────────────
STORY_EDITOR_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
* { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; }
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
  background: #f8f8f8;
  height: 820px;
  overflow: hidden;
}

/* ── GRID VIEW ── */
.grid-view { padding: 20px 24px; height: 820px; overflow-y: auto; }
.page-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px; }
.page-title { font-size: 18px; font-weight: 800; color: #111; }
.page-sub { font-size: 12px; color: #aaa; }
.template-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

.template-card {
  background: white; border-radius: 12px; overflow: hidden;
  cursor: pointer; border: 2px solid transparent;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.template-card:hover {
  border-color: #ff4b4b; transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255,75,75,0.15);
}
.card-preview {
  width: 100%; aspect-ratio: 9/16;
  background: #f0f0f0; position: relative;
  overflow: hidden; display: flex;
  align-items: center; justify-content: center;
}
.card-preview img { width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; }
.card-drop-hint {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  color: #bbb; font-size: 11px; text-align: center; padding: 12px;
  pointer-events: none; z-index: 1;
}
.card-preview.drag-over { background: #fff5f5; border: 2px dashed #ff4b4b; }
.card-preview.drag-over .card-drop-hint { color: #ff4b4b; }
.card-footer {
  padding: 10px 12px; display: flex;
  align-items: center; justify-content: space-between;
}
.card-name { font-size: 13px; font-weight: 700; color: #222; }
.card-edit-btn {
  font-size: 11px; color: #ff4b4b; font-weight: 600;
  background: #fff5f5; border: none; padding: 4px 10px;
  border-radius: 20px; cursor: pointer;
}
.card-edit-btn:hover { background: #ffe0e0; }

/* ── EDITOR VIEW ── */
.editor-view { display: flex; height: 820px; background: white; }

.editor-canvas-area {
  flex: 0 0 auto; background: #1a1a1a;
  padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.back-btn {
  background: none; border: none; color: #888; cursor: pointer;
  font-size: 12px; padding: 0; display: flex; align-items: center; gap: 5px;
  transition: color 0.15s;
}
.back-btn:hover { color: #fff; }

.story-outer {
  position: relative; width: 344px; height: 612px;
  border-radius: 10px; overflow: hidden;
  background: #2a2a2a; flex-shrink: 0;
}
.story-bg-img {
  position: absolute; top:0; left:0; width:100%; height:100%;
  object-fit: cover; pointer-events: none; user-select: none;
}
.story-drop-overlay {
  position: absolute; top:0; left:0; right:0; bottom:0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 10px; color: #555; font-size: 13px; text-align: center;
  cursor: default; transition: all 0.2s; z-index: 1;
}
.story-drop-overlay.drag-over {
  background: rgba(255,75,75,0.15);
  border: 2px dashed #ff4b4b; color: #ff4b4b;
}
.story-drop-overlay.hidden { display: none; }
.size-badge {
  position: absolute; bottom: 8px; right: 8px;
  background: rgba(0,0,0,0.5); color: rgba(255,255,255,0.7);
  font-size: 10px; padding: 3px 8px; border-radius: 4px;
  pointer-events: none; z-index: 100;
}

/* Text layers */
.text-layer {
  position: absolute; cursor: move; user-select: none;
  padding: 2px 4px; border-radius: 2px;
  white-space: normal; z-index: 10; transition: outline 0.1s;
}
.text-layer.selected { outline: none; }
.text-layer[contenteditable="true"] {
  cursor: text; outline: none !important;
  background: rgba(0,0,0,0.15); white-space: pre; min-width: 40px;
}

/* Controls */
.editor-controls {
  flex: 1; padding: 20px 22px; overflow-y: auto;
  border-left: 1px solid #f0f0f0;
}
.ctrl-section { margin-bottom: 22px; }
.ctrl-label {
  font-size: 11px; font-weight: 700; color: #bbb;
  letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px;
}

.upload-zone {
  border: 2px dashed #e5e5e5; border-radius: 10px;
  padding: 16px; text-align: center; cursor: pointer;
  transition: all 0.2s; background: #fafafa;
}
.upload-zone:hover, .upload-zone.drag-over { border-color: #ff4b4b; background: #fff8f8; }
.upload-zone p { font-size: 12px; color: #bbb; margin-top: 6px; }

.text-item {
  display: flex; align-items: center; gap: 8px; padding: 9px 12px;
  border-radius: 8px; border: 1.5px solid #eee; margin-bottom: 7px;
  cursor: pointer; transition: all 0.15s;
}
.text-item:hover, .text-item.active { border-color: #ff4b4b; background: #fff8f8; }
.text-item-text {
  flex: 1; font-size: 12px; color: #444;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.text-item-del {
  color: #ddd; cursor: pointer; font-size: 18px;
  line-height: 1; padding: 0 4px; font-weight: 300;
}
.text-item-del:hover { color: #ff4b4b; }

.add-text-btn {
  width: 100%; padding: 9px;
  border: 1.5px dashed #ddd; border-radius: 8px;
  background: none; font-size: 13px; color: #aaa;
  cursor: pointer; transition: all 0.15s; font-weight: 600;
}
.add-text-btn:hover { border-color: #ff4b4b; color: #ff4b4b; background: #fff8f8; }

.style-grid { display: flex; flex-direction: column; gap: 10px; }
.style-row { display: flex; align-items: center; gap: 10px; }
.style-row-label { font-size: 11px; color: #aaa; min-width: 44px; }

input[type="range"] { flex:1; accent-color: #ff4b4b; height: 4px; cursor:pointer; }
input.num-input {
  flex:1; padding:6px 10px; border:1.5px solid #eee; border-radius:7px;
  font-size:12px; color:#333; background:white; outline:none;
  text-align:left; -moz-appearance:textfield;
}
input.num-input:focus { border-color:#ff4b4b; }
input.num-input::-webkit-inner-spin-button,
input.num-input::-webkit-outer-spin-button { opacity:1; height:22px; }
input[type="color"] {
  width: 32px; height: 32px; border: none; border-radius: 6px;
  padding: 1px; cursor: pointer; background: none;
}
select {
  flex:1; padding: 6px 8px; border: 1.5px solid #eee; border-radius: 7px;
  font-size: 12px; color: #333; background: white; cursor: pointer;
}
select:focus { outline: none; border-color: #ff4b4b; }

.style-btns { display: flex; gap: 4px; }
.style-btn {
  width: 30px; height: 30px; border: 1.5px solid #eee; border-radius: 6px;
  background: white; cursor: pointer; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.style-btn:hover, .style-btn.on { border-color: #ff4b4b; background: #fff0f0; color: #ff4b4b; }

.dl-btn {
  width: 100%; padding: 13px; background: #111; color: white;
  border: none; border-radius: 10px; font-size: 13px; font-weight: 700;
  cursor: pointer; letter-spacing: 1px; transition: background 0.2s; margin-top: 4px;
}
.dl-btn:hover { background: #333; }
.hidden { display: none !important; }
.no-select-hint {
  padding: 16px 12px; background: #f9f9f9; border-radius: 8px;
  text-align: center; color: #ccc; font-size: 12px;
}
</style>
</head>
<body>

<!-- GRID VIEW -->
<div id="gridView" class="grid-view">
  <div class="page-header">
    <span class="page-title">스토리 모듈</span>
    <span class="page-sub">1080 × 1920px &nbsp;·&nbsp; 4개 템플릿</span>
  </div>
  <div class="template-grid" id="templateGrid"></div>
</div>

<!-- EDITOR VIEW -->
<div id="editorView" class="editor-view hidden">
  <div class="editor-canvas-area">
    <button class="back-btn" onclick="showGrid()">← 목록으로</button>
    <div id="storyOuter" class="story-outer"
         ondragover="onBgDragOver(event)"
         ondragleave="onBgDragLeave(event)"
         ondrop="onBgDrop(event)"
         onclick="onCanvasClick(event)">
      <div id="storyDropOverlay" class="story-drop-overlay">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
          <rect x="3" y="3" width="18" height="18" rx="2.5"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
        <div>이미지를 여기에 드롭하세요</div>
        <div style="font-size:11px;opacity:0.6;">또는 우측 패널에서 업로드</div>
      </div>
      <img id="storyBgImg" class="story-bg-img hidden" src="" alt="">
      <div id="guideV" style="display:none;position:absolute;top:0;bottom:0;left:50%;width:0;border-left:1.5px dashed rgba(255,75,75,0.85);pointer-events:none;z-index:50;"></div>
      <div id="guideH" style="display:none;position:absolute;left:0;right:0;top:50%;height:0;border-top:1.5px dashed rgba(255,75,75,0.85);pointer-events:none;z-index:50;"></div>
      <div class="size-badge">1080 × 1920</div>
    </div>
  </div>

  <div class="editor-controls">
    <div id="editorTemplName" style="font-size:16px;font-weight:800;color:#111;margin-bottom:20px;"></div>

    <div class="ctrl-section">
      <div class="ctrl-label">배경 이미지</div>
      <div class="upload-zone" id="uploadZone"
           onclick="document.getElementById('fileInput').click()"
           ondragover="onUploadDragOver(event)"
           ondragleave="onUploadDragLeave(event)"
           ondrop="onUploadDrop(event)">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2">
          <polyline points="16 16 12 12 8 16"/>
          <line x1="12" y1="12" x2="12" y2="21"/>
          <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
        </svg>
        <p>드래그하거나 클릭하여 업로드</p>
        <p style="font-size:10px;">JPG · PNG · WEBP</p>
      </div>
      <input type="file" id="fileInput" accept="image/*" class="hidden" onchange="onFileInput(event)">
    </div>

    <div class="ctrl-section">
      <div class="ctrl-label">텍스트 레이어</div>
      <div id="textList"></div>
      <button class="add-text-btn" onclick="addText()">+ 텍스트 추가</button>
    </div>

    <div class="ctrl-section">
      <div class="ctrl-label">선택된 텍스트 스타일</div>
      <div id="stylePanel" class="no-select-hint">텍스트를 클릭하여 선택하세요</div>
    </div>

    <div style="display:flex;gap:8px;">
      <button class="dl-btn" style="flex:1;" onclick="downloadPNG('png')">↓ PNG</button>
      <button class="dl-btn" style="flex:1;" onclick="downloadPNG('jpg')">↓ JPG</button>
    </div>
  </div>
</div>

<script>
const W=344, H=612, RW=1080, RH=1920, SX=344/1080, SY=612/1920;

const REPO_RAW = 'https://raw.githubusercontent.com/younkyung-wq/lazyz/main/';

let templates=[
  {id:1,name:'템플릿 1',bgData:REPO_RAW+'1b.jpg',bgThumb:REPO_RAW+'1.jpg',texts:[
    {id:1,text:'5/6(WED) - 5/16(SAT)',x:540,y:1195,fs:45,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.04em'},
    {id:2,text:'24H HOUR\\n26SS ~45%',x:540,y:1290,fs:120,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.04em',lh:1.083},
  ]},
  {id:2,name:'템플릿 2',bgData:REPO_RAW+'2b.jpg',bgThumb:REPO_RAW+'2.jpg',texts:[
    {id:1,text:'BRAND WEEK',x:72,y:100,fs:126,color:'#ffffff',fw:800,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.03em'},
    {id:2,text:'UP TO 45%',x:72,y:260,fs:126,color:'#ffffff',fw:800,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.03em'},
    {id:3,text:'5/4-5/10',x:72,y:420,fs:50,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
  ]},
  {id:3,name:'템플릿 3',bgData:REPO_RAW+'3b.jpg',bgThumb:REPO_RAW+'3.jpg',texts:[
    {id:1,text:'Kurly',x:80,y:870,fs:130,color:'#ffffff',fw:700,italic:true,ff:'Georgia, serif',shadow:false,ls:'-0.01em'},
    {id:2,text:'컬리 반짝특가',x:750,y:930,fs:48,color:'#ffffff',fw:700,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.01em'},
    {id:3,text:'정가 109,000원 → 46,300원',x:72,y:1650,fs:44,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
  ]},
  {id:4,name:'템플릿 4',bgData:REPO_RAW+'4b.jpg',bgThumb:REPO_RAW+'4.jpg',texts:[
    {id:1,text:'단독 브랜드 위크',x:72,y:400,fs:60,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
    {id:2,text:'~52% OFF',x:72,y:500,fs:126,color:'#ffffff',fw:800,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.03em'},
    {id:3,text:'5.18(MON) - 5.24(SUN)',x:72,y:700,fs:46,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
  ]},
];

let activeTplId=null, selTextId=null, dragInfo=null, nextId=200;
let undoStack=[], redoStack=[];
const getTpl=()=>templates.find(t=>t.id===activeTplId);
const getTexts=()=>getTpl()?.texts??[];
const getTxt=id=>getTexts().find(t=>t.id===id);

function saveUndo(){
  undoStack.push(JSON.stringify(getTpl()?.texts));
  if(undoStack.length>30)undoStack.shift();
  redoStack=[];
}
function undo(){
  if(!undoStack.length)return;
  redoStack.push(JSON.stringify(getTpl()?.texts));
  const tpl=getTpl(); if(!tpl)return;
  tpl.texts=JSON.parse(undoStack.pop());
  refreshLayers(); refreshTextList(); refreshStylePanel();
}
function redo(){
  if(!redoStack.length)return;
  undoStack.push(JSON.stringify(getTpl()?.texts));
  const tpl=getTpl(); if(!tpl)return;
  tpl.texts=JSON.parse(redoStack.pop());
  refreshLayers(); refreshTextList(); refreshStylePanel();
}
document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key==='z'&&!e.shiftKey){e.preventDefault();undo();}
  if((e.metaKey||e.ctrlKey)&&(e.key==='y'||(e.key==='z'&&e.shiftKey))){e.preventDefault();redo();}
});

// ── GRID ──
function renderGrid(){
  const g=document.getElementById('templateGrid');
  g.innerHTML='';
  templates.forEach(tpl=>{
    const card=document.createElement('div');
    card.className='template-card';
    card.innerHTML=`
      <div class="card-preview" id="cp${tpl.id}">
        ${(tpl.bgThumb||tpl.bgData)
          ?`<img src="${tpl.bgThumb||tpl.bgData}">`
          :`<div class="card-drop-hint">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2.5"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>이미지 드롭
            </div>`
        }
      </div>
      <div class="card-footer">
        <div class="card-name">${tpl.name}</div>
        <button class="card-edit-btn">편집 →</button>
      </div>`;
    const prev=card.querySelector('.card-preview');
    prev.addEventListener('dragover',e=>{e.preventDefault();prev.classList.add('drag-over');});
    prev.addEventListener('dragleave',()=>prev.classList.remove('drag-over'));
    prev.addEventListener('drop',e=>{
      e.preventDefault(); prev.classList.remove('drag-over');
      const f=e.dataTransfer.files[0];
      if(f&&f.type.startsWith('image/'))loadBg(tpl.id,f,renderGrid);
    });
    card.querySelector('.card-edit-btn').addEventListener('click',e=>{e.stopPropagation();openEditor(tpl.id);});
    prev.addEventListener('click',()=>openEditor(tpl.id));
    g.appendChild(card);
  });
}

// ── EDITOR ──
function openEditor(id){
  activeTplId=id; selTextId=null;
  document.getElementById('gridView').classList.add('hidden');
  document.getElementById('editorView').classList.remove('hidden');
  document.getElementById('editorTemplName').textContent=getTpl().name;
  refreshBg(); refreshLayers(); refreshTextList(); refreshStylePanel();
}
function showGrid(){
  document.getElementById('editorView').classList.add('hidden');
  document.getElementById('gridView').classList.remove('hidden');
  renderGrid();
}
function refreshBg(){
  const tpl=getTpl();
  const img=document.getElementById('storyBgImg');
  const ov=document.getElementById('storyDropOverlay');
  if(tpl.bgData){img.src=tpl.bgData;img.classList.remove('hidden');ov.classList.add('hidden');}
  else{img.classList.add('hidden');ov.classList.remove('hidden');}
}

// ── TEXT LAYERS ──
function refreshLayers(){
  const outer=document.getElementById('storyOuter');
  outer.querySelectorAll('.text-layer').forEach(el=>el.remove());
  getTexts().forEach(t=>outer.appendChild(makeEl(t)));
}
function makeEl(t){
  const el=document.createElement('div');
  el.className='text-layer';
  el.dataset.tid=t.id;
  applyStyle(el,t); placeEl(el,t);
  renderChars(el,t);
  el.addEventListener('mousedown',e=>onTextMouseDown(e,t.id));
  return el;
}

function hideGuides(){
  document.getElementById('guideV').style.display='none';
  document.getElementById('guideH').style.display='none';
}

function renderChars(el,t){
  el.innerHTML='';
  let i=0;
  for(const ch of t.text){
    if(ch==='\\n'){
      el.appendChild(document.createElement('br'));
    } else {
      const sp=document.createElement('span');
      sp.textContent=ch===' '?' ':ch;
      const baseLs=Math.round(parseFloat(t.ls||'0')*1000);
      const kern=(t.kerns&&t.kerns[i])||0;
      sp.style.letterSpacing=((baseLs+kern)/1000)+'em';
      el.appendChild(sp);
    }
    i++;
  }
}

function applyStyle(el,t){
  el.style.fontSize=(t.fs*SY)+'px';
  el.style.color=t.color;
  el.style.fontWeight=t.fw||400;
  el.style.fontStyle=t.italic?'italic':'normal';
  el.style.fontFamily=t.ff;
  el.style.lineHeight=t.lh||'1.1';
  el.style.letterSpacing='0em'; // handled per-char
  el.style.textShadow='none';
}
function placeEl(el,t){
  el.style.width='auto';
  el.style.textAlign=t.ta||'left';
  // 행간이 폰트크기보다 클 때 첫 줄 위쪽 leading만큼 위로 보정 → 첫 줄 top 고정 (canvas와 일치)
  const lh=parseFloat(t.lh||'1.1');
  const halfLeading=Math.max(0,(lh-1))*(t.fs*SY)/2;
  const tY='translateY('+(-halfLeading)+'px)';
  el.style.transform=(t.ta==='center'?'translateX(-50%) ':'')+tY;
  el.style.left=(t.x*SX)+'px';
  el.style.top=(t.y*SY)+'px';
}
function selectText(id){
  selTextId=id;
  document.querySelectorAll('.text-layer').forEach(el=>{
    el.classList.toggle('selected',+el.dataset.tid===id);
    el.removeAttribute('contenteditable');
  });
  refreshTextList(); refreshStylePanel();
}
function startEdit(id, clickEvent){
  saveUndo();
  selTextId=id;
  refreshTextList(); refreshStylePanel();
  const el=document.querySelector(`.text-layer[data-tid="${id}"]`);
  if(!el)return;
  const t=getTxt(id); if(!t)return;

  el.setAttribute('contenteditable','true');
  el.focus({preventScroll:true});

  // 클릭한 좌표로 커서 위치 직접 지정
  if(clickEvent){
    const range=document.caretRangeFromPoint
      ? document.caretRangeFromPoint(clickEvent.clientX, clickEvent.clientY)
      : null;
    if(range){
      const sel=window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
  }

  el.addEventListener('blur',()=>{
    el.removeAttribute('contenteditable');
    // innerText로 줄바꿈 보존
    t.text=el.innerText.replace(/\\r\\n/g,'\\n').replace(/\\r/g,'\\n').replace(/\\n$/,'');
    renderChars(el,t);
    refreshTextList();
  },{once:true});

  el.addEventListener('keydown',e=>{
    // Enter = 줄바꿈 (기본동작), Cmd+Enter = 편집완료
    if(e.key==='Enter'&&(e.metaKey||e.ctrlKey)){e.preventDefault();el.blur();}
    if(e.key==='Escape'){el.blur();return;}
    // Cmd+Z/Y는 document 핸들러로 넘김
    if((e.metaKey||e.ctrlKey)&&(e.key==='z'||e.key==='y'))return;

    // Cmd+↑/↓ : 행간 조절
    if((e.metaKey||e.ctrlKey)&&(e.key==='ArrowUp'||e.key==='ArrowDown')){
      e.preventDefault();
      const curLh=parseFloat(t.lh||'1.1');
      const delta=2/t.fs;
      t.lh=e.key==='ArrowUp'?Math.max(0.5,curLh-delta):curLh+delta;
      el.style.lineHeight=t.lh;
      placeEl(el,t);
      refreshStylePanel();
      return;
    }

    // Cmd+← / Cmd+→ : 커서 위치 글자 kern 조정
    if((e.metaKey||e.ctrlKey)&&(e.key==='ArrowLeft'||e.key==='ArrowRight')){
      e.preventDefault();
      const sel=window.getSelection();
      if(!sel.rangeCount)return;

      // 커서가 어느 span(=글자) 안에 있는지 찾기
      const anchor=sel.getRangeAt(0).startContainer;
      const spans=[...el.querySelectorAll('span')];
      let spanIdx=-1;
      if(anchor.nodeType===Node.TEXT_NODE&&anchor.parentElement.tagName==='SPAN'){
        spanIdx=spans.indexOf(anchor.parentElement);
      } else if(anchor===el){
        spanIdx=sel.getRangeAt(0).startOffset;
      }
      if(spanIdx<0)return;

      // ← : 커서 왼쪽(spanIdx-1) 글자 kern 조정 / → : 현재 위치(spanIdx) 글자
      const adjustIdx=e.key==='ArrowLeft'?Math.max(0,spanIdx-1):spanIdx;
      if(!t.kerns)t.kerns={};
      t.kerns[adjustIdx]=(t.kerns[adjustIdx]||0)+(e.key==='ArrowRight'?2:-2);

      // 해당 span만 실시간 업데이트
      if(spans[adjustIdx]){
        const baseLs=Math.round(parseFloat(t.ls||'0')*1000);
        spans[adjustIdx].style.letterSpacing=((baseLs+(t.kerns[adjustIdx]||0))/1000)+'em';
      }
      refreshStylePanel();
      return;
    }
    e.stopPropagation();
  });
}
function onTextMouseDown(e,id){
  const el=document.querySelector(`.text-layer[data-tid="${id}"]`);
  // 이미 편집모드면 네이티브 커서 위치 지정에 맡김
  if(el&&el.getAttribute('contenteditable')==='true')return;
  e.preventDefault();
  e.stopPropagation();
  const t=getTxt(id);
  const startX=e.clientX, startY=e.clientY;
  const startTx=t.x, startTy=t.y;
  let moved=false, undoSaved=false;
  selectText(id);
  const SNAP=8;
  const onMove=ev=>{
    if(!moved && (Math.abs(ev.clientX-startX)>3||Math.abs(ev.clientY-startY)>3)){
      moved=true;
      if(!undoSaved){saveUndo();undoSaved=true;}
    }
    if(!moved)return;
    t.x=Math.round(startTx+(ev.clientX-startX)/SX);
    t.y=Math.round(startTy+(ev.clientY-startY)/SY);
    if(!el){hideGuides();return;}

    // 수직 중앙 스냅
    const elH=el.offsetHeight;
    const elCy=(t.y*SY)+elH/2;
    if(Math.abs(elCy-H/2)<SNAP){
      t.y=Math.round((H/2-elH/2)/SY);
      document.getElementById('guideH').style.display='block';
    } else { document.getElementById('guideH').style.display='none'; }

    // 수평 중앙 스냅
    const elW=el.offsetWidth;
    const elCx=t.ta==='center'?t.x*SX:(t.x*SX)+elW/2;
    if(Math.abs(elCx-W/2)<SNAP){
      t.x=Math.round(W/2/SX);
      document.getElementById('guideV').style.display='block';
    } else { document.getElementById('guideV').style.display='none'; }

    placeEl(el,t);
  };
  const onUp=ev=>{
    hideGuides();
    document.removeEventListener('mousemove',onMove);
    document.removeEventListener('mouseup',onUp);
    if(!moved){
      // 클릭 → 편집모드 진입 (클릭 좌표에 커서)
      startEdit(id, ev);
    }
  };
  document.addEventListener('mousemove',onMove);
  document.addEventListener('mouseup',onUp);
}
function onCanvasClick(e){
  // 텍스트 레이어(또는 그 안의 span) 클릭이면 무시
  if(e.target.closest&&e.target.closest('.text-layer'))return;
  selTextId=null;
  document.querySelectorAll('.text-layer').forEach(el=>{el.classList.remove('selected');el.removeAttribute('contenteditable');});
  refreshTextList(); refreshStylePanel();
}
function addText(){
  const tpl=getTpl(); if(!tpl)return;
  const t={id:nextId++,text:'텍스트',x:540,y:960,fs:70,color:'#ffffff',fw:700,italic:false,ff:'Pretendard, sans-serif',shadow:false};
  tpl.texts.push(t);
  document.getElementById('storyOuter').appendChild(makeEl(t));
  refreshTextList(); selectText(t.id);
  setTimeout(()=>startEdit(t.id),40);
}
function deleteText(id){
  const tpl=getTpl(); if(!tpl)return;
  tpl.texts=tpl.texts.filter(t=>t.id!==id);
  if(selTextId===id){selTextId=null;refreshStylePanel();}
  refreshLayers(); refreshTextList();
}

// ── TEXT LIST ──
function refreshTextList(){
  const list=document.getElementById('textList'); list.innerHTML='';
  getTexts().forEach(t=>{
    const item=document.createElement('div');
    item.className='text-item'+(selTextId===t.id?' active':'');
    item.innerHTML=`
      <input class="text-item-input" value="${t.text.replace(/"/g,'&quot;')}"
        style="flex:1;border:none;background:transparent;font-size:12px;color:#444;outline:none;min-width:0;">
      <span class="text-item-del" onclick="event.stopPropagation();deleteText(${t.id})">×</span>`;
    const input=item.querySelector('input');
    input.addEventListener('focus',()=>{selTextId=t.id;refreshStylePanel();document.querySelectorAll('.text-item').forEach(el=>el.classList.remove('active'));item.classList.add('active');});
    input.addEventListener('input',()=>{
      saveUndo();
      t.text=input.value;
      const el=document.querySelector(`.text-layer[data-tid="${t.id}"]`);
      if(el)renderChars(el,t);
    });
    item.addEventListener('click',e=>{if(e.target!==input){selectText(t.id);refreshLayers();}});
    list.appendChild(item);
  });
}

// ── STYLE PANEL ──
function refreshStylePanel(){
  const panel=document.getElementById('stylePanel');
  if(!selTextId){panel.innerHTML='<div class="no-select-hint">텍스트를 클릭하여 선택하세요</div>';return;}
  const t=getTxt(selTextId); if(!t)return;
  panel.innerHTML=`
    <div class="style-grid">
      <div class="style-row">
        <span class="style-row-label">폰트</span>
        <select onchange="setS('ff',this.value)">
          <option value="Pretendard, sans-serif" ${t.ff==='Pretendard, sans-serif'?'selected':''}>Pretendard</option>
          <option value="sans-serif" ${t.ff==='sans-serif'?'selected':''}>Sans-serif</option>
          <option value="Georgia, serif" ${t.ff==='Georgia, serif'?'selected':''}>Georgia</option>
          <option value="'Helvetica Neue',sans-serif" ${t.ff==="'Helvetica Neue',sans-serif"?'selected':''}>Helvetica</option>
          <option value="'Courier New',monospace" ${t.ff==="'Courier New',monospace"?'selected':''}>Courier</option>
        </select>
      </div>
      <div class="style-row">
        <span class="style-row-label">크기</span>
        <input class="num-input" type="number" min="1" max="500" step="1" value="${t.fs}"
          oninput="setS('fs',+this.value)">
        <span style="font-size:11px;color:#bbb;">px</span>
      </div>
      <div class="style-row">
        <span class="style-row-label">굵기</span>
        <select onchange="setS('fw',+this.value)">
          <option value="100" ${t.fw===100?'selected':''}>100 Thin</option>
          <option value="200" ${t.fw===200?'selected':''}>200 ExtraLight</option>
          <option value="300" ${t.fw===300?'selected':''}>300 Light</option>
          <option value="400" ${t.fw===400?'selected':''}>400 Regular</option>
          <option value="500" ${t.fw===500?'selected':''}>500 Medium</option>
          <option value="600" ${t.fw===600?'selected':''}>600 SemiBold</option>
          <option value="700" ${t.fw===700?'selected':''}>700 Bold</option>
          <option value="800" ${t.fw===800?'selected':''}>800 ExtraBold</option>
          <option value="900" ${t.fw===900?'selected':''}>900 Black</option>
        </select>
      </div>
      <div class="style-row">
        <span class="style-row-label">색상</span>
        <input type="color" value="${t.color}" oninput="setS('color',this.value)">
        <div class="style-btns">
          <button class="style-btn ${t.italic?'on':''}" onclick="toggleItalic()"><i>I</i></button>
        </div>
      </div>
      <div class="style-row">
        <span class="style-row-label">자간</span>
        <input class="num-input" type="number" step="1" value="${Math.round(parseFloat(t.ls||'0')*1000)}"
          oninput="setS('ls',(this.value/1000)+'em')">
        <span style="font-size:11px;color:#bbb;">‱</span>
      </div>
      <div class="style-row">
        <span class="style-row-label">행간</span>
        <input class="num-input" type="number" step="1" value="${Math.round((parseFloat(t.lh||'1.1'))*t.fs)}"
          oninput="setLh(+this.value)">
        <span style="font-size:11px;color:#bbb;">px</span>
      </div>
    </div>`;
}
function setS(prop,val){
  const t=getTxt(selTextId); if(!t)return;
  t[prop]=val;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`);
  if(el){applyStyle(el,t);placeEl(el,t);renderChars(el,t);}
}
function setLh(px){
  const t=getTxt(selTextId); if(!t)return;
  t.lh=px/t.fs;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`);
  if(el){el.style.lineHeight=t.lh;placeEl(el,t);}
}
function toggleItalic(){
  const t=getTxt(selTextId); if(!t)return; t.italic=!t.italic;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`); if(el)applyStyle(el,t);
  refreshStylePanel();
}

// ── IMAGE UPLOAD ──
function loadBg(id,file,cb){
  const reader=new FileReader();
  reader.onload=e=>{
    templates.find(t=>t.id===id).bgData=e.target.result;
    if(cb)cb(); if(activeTplId===id)refreshBg();
  };
  reader.readAsDataURL(file);
}
function onBgDragOver(e){e.preventDefault();const ov=document.getElementById('storyDropOverlay');ov.classList.remove('hidden');ov.classList.add('drag-over');}
function onBgDragLeave(){const ov=document.getElementById('storyDropOverlay');ov.classList.remove('drag-over');if(getTpl()?.bgData)ov.classList.add('hidden');}
function onBgDrop(e){e.preventDefault();const ov=document.getElementById('storyDropOverlay');ov.classList.remove('drag-over');const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))loadBg(activeTplId,f);}
function onUploadDragOver(e){e.preventDefault();document.getElementById('uploadZone').classList.add('drag-over');}
function onUploadDragLeave(){document.getElementById('uploadZone').classList.remove('drag-over');}
function onUploadDrop(e){e.preventDefault();document.getElementById('uploadZone').classList.remove('drag-over');const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))loadBg(activeTplId,f);}
function onFileInput(e){const f=e.target.files[0];if(f)loadBg(activeTplId,f);}

// ── DOWNLOAD ──
function downloadPNG(fmt){
  fmt=fmt||'png';
  const tpl=getTpl();
  if(!tpl.bgData){alert('배경 이미지를 먼저 업로드해주세요.');return;}
  const canvas=document.createElement('canvas');
  canvas.width=RW; canvas.height=RH;
  const ctx=canvas.getContext('2d');
  const img=new Image();
  img.onload=()=>{
    const ia=img.width/img.height, ca=RW/RH;
    let sx,sy,sw,sh;
    if(ia>ca){sh=img.height;sw=sh*ca;sx=(img.width-sw)/2;sy=0;}
    else{sw=img.width;sh=sw/ca;sx=0;sy=(img.height-sh)/2;}
    ctx.drawImage(img,sx,sy,sw,sh,0,0,RW,RH);
    tpl.texts.forEach(t=>{
      ctx.save();
      ctx.font=`${t.italic?'italic':'normal'} ${t.fw||400} ${t.fs}px ${t.ff}`;
      ctx.fillStyle=t.color; ctx.textBaseline='top';
      if(t.shadow){ctx.shadowColor='rgba(0,0,0,0.85)';ctx.shadowOffsetX=2;ctx.shadowOffsetY=2;ctx.shadowBlur=18;}
      const baseLs=parseFloat(t.ls||'0')*t.fs;
      const lineH=(parseFloat(t.lh||'1.1'))*t.fs;
      const lines=t.text.split('\\n');
      let charOffset=0;
      lines.forEach((line,li)=>{
        const chars=[...line];
        // 전체 너비 계산 (center용)
        let totalW=0;
        chars.forEach((ch,i)=>{
          const kern=((t.kerns&&t.kerns[charOffset+i])||0)/1000*t.fs;
          totalW+=ctx.measureText(ch).width+baseLs+kern;
        });
        let x=t.ta==='center'?t.x-totalW/2:t.x;
        const y=t.y+li*lineH;
        chars.forEach((ch,i)=>{
          ctx.fillText(ch,x,y);
          const kern=((t.kerns&&t.kerns[charOffset+i])||0)/1000*t.fs;
          x+=ctx.measureText(ch).width+baseLs+kern;
        });
        charOffset+=chars.length+1; // +1 for the newline
      });
      ctx.restore();
    });
    const a=document.createElement('a');
    const isJpg=fmt==='jpg';
    const mime=isJpg?'image/jpeg':'image/png';
    a.download=`lazyz_story_${tpl.id}_${Date.now()}.${isJpg?'jpg':'png'}`;
    a.href=canvas.toDataURL(mime,isJpg?0.95:undefined); a.click();
  };
  img.src=tpl.bgData;
}

renderGrid();
</script>
</body>
</html>
"""

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 32px 20px 24px; border-bottom: 1px solid #222;">
        <div style="color:#fff; font-size:22px; font-weight:800; letter-spacing:5px;">LAZYZ</div>
        <div style="color:#555; font-size:10px; letter-spacing:3px; margin-top:5px;">INSTAGRAM DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["🔴  피드 기획", "⬜  광고소재 생성기", "📱  스토리 모듈"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="padding: 0 16px;">
        <div style="color:#555; font-size:11px; letter-spacing:1px; margin-bottom:8px; font-weight:600;">API KEY</div>
    </div>""", unsafe_allow_html=True)
    st.text_input("", type="password", placeholder="••••••••••••••••••••••••••",
                  label_visibility="collapsed", key="api_key")

    st.markdown("""
    <div style="padding: 24px 20px 0; color:#444; font-size:11px; line-height:2;">
        사용법<br>
        ① 템플릿 선택<br>
        ② 이미지 드롭 → 배경 교체<br>
        ③ 텍스트 드래그 → 이동<br>
        ④ 텍스트 더블클릭 → 편집<br>
        ⑤ PNG 다운로드
    </div>
    """, unsafe_allow_html=True)

# ── Main content ─────────────────────────────────────────────
if "스토리 모듈" in menu:
    components.html(STORY_EDITOR_HTML, height=820, scrolling=False)

elif "피드 기획" in menu:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:60vh;flex-direction:column;gap:12px;color:#999;">
        <div style="font-size:40px;">🖼️</div>
        <div style="font-size:16px;font-weight:600;">피드 기획</div>
        <div style="font-size:13px;">기존 사이트에서 이용해주세요</div>
    </div>
    """, unsafe_allow_html=True)

elif "광고소재 생성기" in menu:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:60vh;flex-direction:column;gap:12px;color:#999;">
        <div style="font-size:40px;">🎯</div>
        <div style="font-size:16px;font-weight:600;">광고소재 생성기</div>
        <div style="font-size:13px;">기존 사이트에서 이용해주세요</div>
    </div>
    """, unsafe_allow_html=True)
