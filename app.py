import streamlit as st
import streamlit.components.v1 as components
import os, io, zipfile
from PIL import Image, ImageOps

st.set_page_config(
    page_title="LAZYZ Dashboard",
    page_icon="💤",
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
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 10px 16px; border-radius: 8px; cursor: pointer; margin: 0 8px;
}
/* 라디오 동그라미 숨김 */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] [aria-checked="true"] { background: rgba(255,255,255,0.06); }
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
    padding-right: 1.5rem !important; padding-bottom: 0 !important; max-width: 100% !important;
}
iframe { display: block; }
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
.editor-view { display: flex; height: 820px; background: white; justify-content: flex-start; }

.editor-canvas-area {
  flex: 1 1 auto; max-width: 760px; background: #ffffff;
  padding: 16px; position: relative; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.back-btn {
  background: none; border: none; color: #999; cursor: pointer;
  font-size: 12px; padding: 0; display: flex; align-items: center; gap: 5px;
  transition: color 0.15s; position: absolute; top: 16px; left: 16px; z-index: 5;
}
.back-btn:hover { color: #111; }

.story-outer {
  position: relative; width: 405px; height: 720px;
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
.mz-tag {
  position: absolute; background: rgba(0,0,0,0.78); color: #00e5ff;
  font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px;
  transform: translate(-50%,-50%); white-space: nowrap; pointer-events: none;
}
.xf-handle {
  position: absolute; width: 10px; height: 10px;
  background: #fff; border: 1.5px solid #2b8cff; border-radius: 2px;
}
.img-layer {
  position: absolute; cursor: move; z-index: 9;
}
.img-layer img { display: block; width: 100%; height: 100%; pointer-events: none; }
.img-layer.selected { outline: 1.5px solid #54fffd; }
.img-handle {
  position: absolute; width: 14px; height: 14px;
  background: #fff; border: 2px solid #54fffd; border-radius: 3px; z-index: 20;
}

/* Text layers */
.text-layer {
  position: absolute; cursor: move; user-select: none;
  padding: 0; border-radius: 2px;
  white-space: nowrap; z-index: 10; transition: outline 0.1s;
}
.text-layer.selected { outline: 1.5px solid #54fffd; outline-offset: 3px; }
.text-layer[contenteditable="true"] {
  cursor: text; outline: none !important;
  background: rgba(0,0,0,0.15); white-space: pre; min-width: 40px;
}

/* Controls */
.editor-controls {
  flex: 0 0 360px; width: 360px; padding: 20px 22px; overflow-y: auto;
  border-left: 1px solid #f0f0f0;
}
.editor-style {
  flex: 0 0 340px; width: 340px; padding: 20px 22px; overflow-y: auto;
  border-left: 1px solid #f0f0f0; background: #fcfcfc;
}
.ctrl-section { margin-bottom: 22px; }
.ctrl-label {
  font-size: 11px; font-weight: 700; color: #bbb;
  letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px;
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; user-select: none;
}
.ctrl-label .caret { transition: transform 0.15s; font-size: 10px; }
.ctrl-section.collapsed .caret { transform: rotate(-90deg); }
.ctrl-section.collapsed .sec-body { display: none; }

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
/* compact field groups */
.fld-row { display: flex; gap: 8px; }
.fld { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.fld-label { font-size: 10px; color: #bbb; font-weight: 600; letter-spacing: 0.3px; }
.fld-input-wrap { display: flex; align-items: center; gap: 6px; }
.fld select, .fld input.num-input {
  width: 100%; padding: 6px 8px; border: 1.5px solid #eee; border-radius: 7px;
  font-size: 12px; color: #333; background: white; outline: none; min-width: 0;
}
.fld select:focus, .fld input.num-input:focus { border-color: #ff4b4b; }
.fld .unit { font-size: 10px; color: #bbb; flex-shrink: 0; }

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
      <!-- 측정 오버레이 (선택된 텍스트 박스 ↔ 가장자리 간격) -->
      <div id="measure" style="display:none;position:absolute;inset:0;pointer-events:none;z-index:90;">
        <div id="mzBox" style="position:absolute;border:1px solid #00e5ff;box-sizing:border-box;"></div>
        <div id="mzLineL" style="position:absolute;height:0;border-top:1px dashed #00e5ff;"></div>
        <div id="mzLineR" style="position:absolute;height:0;border-top:1px dashed #00e5ff;"></div>
        <div id="mzLineT" style="position:absolute;width:0;border-left:1px dashed #00e5ff;"></div>
        <div id="mzLineB" style="position:absolute;width:0;border-left:1px dashed #00e5ff;"></div>
        <div id="mzL" class="mz-tag"></div>
        <div id="mzR" class="mz-tag"></div>
        <div id="mzT" class="mz-tag"></div>
        <div id="mzB" class="mz-tag"></div>
      </div>
      <div class="size-badge">1080 × 1920</div>
    </div>
    <!-- 이미지 변형 핸들 (프레임 밖에서도 보이도록 캔버스 영역에 배치) -->
    <div id="imgXf" style="display:none;position:absolute;inset:0;z-index:80;pointer-events:none;">
      <div id="imgXfBox" style="position:absolute;border:1.5px solid #2b8cff;cursor:move;pointer-events:auto;">
        <div class="xf-handle" data-h="nw" style="top:-5px;left:-5px;cursor:nwse-resize;"></div>
        <div class="xf-handle" data-h="ne" style="top:-5px;right:-5px;cursor:nesw-resize;"></div>
        <div class="xf-handle" data-h="sw" style="bottom:-5px;left:-5px;cursor:nesw-resize;"></div>
        <div class="xf-handle" data-h="se" style="bottom:-5px;right:-5px;cursor:nwse-resize;"></div>
        <div id="xfScaleTag" style="position:absolute;top:-26px;left:50%;transform:translateX(-50%);background:#2b8cff;color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;white-space:nowrap;"></div>
      </div>
    </div>
  </div>

  <div class="editor-controls">
    <div id="editorTemplName" style="font-size:16px;font-weight:800;color:#111;margin-bottom:20px;"></div>

    <div class="ctrl-section" id="secBg">
      <div class="ctrl-label" onclick="toggleSection('secBg')">배경 이미지 <span class="caret">▾</span></div>
      <div class="sec-body">
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
      <input type="file" id="fileInput" accept="image/*" multiple class="hidden" onchange="onFileInput(event)">
      <div id="bgThumbs" style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;"></div>
      <div style="display:flex;gap:8px;margin-top:8px;align-items:center;">
        <button id="imgModeBtn" onclick="toggleImgMode()" style="flex:1;padding:8px;border:1.5px solid #eee;border-radius:8px;background:#fafafa;font-size:12px;color:#666;cursor:pointer;font-weight:600;">🖼 이미지 크기/위치 조절</button>
        <button onclick="resetBgTransform()" style="padding:8px 12px;border:1.5px solid #eee;border-radius:8px;background:#fff;font-size:12px;color:#999;cursor:pointer;">초기화</button>
      </div>
      </div>
    </div>

    <div class="ctrl-section" id="secText">
      <div class="ctrl-label" onclick="toggleSection('secText')">텍스트 레이어 <span class="caret">▾</span></div>
      <div class="sec-body">
        <div id="textList"></div>
        <button class="add-text-btn" onclick="addText()">+ 텍스트 추가</button>
        <input type="file" id="imgLayerInput" accept="image/*" class="hidden" onchange="onAddImgLayer(event)">
        <input type="file" id="imgReplaceInput" accept="image/*" class="hidden" onchange="onReplaceImg(event)">
      </div>
    </div>

    <button id="pickDirBtn" onclick="pickSaveDir()" style="width:100%;padding:9px;border:1.5px solid #eee;border-radius:8px;background:#fafafa;font-size:12px;color:#666;cursor:pointer;margin-bottom:8px;font-weight:600;">📁 저장 폴더 지정 (선택)</button>
    <div id="dirStatus" style="font-size:11px;color:#aaa;margin-bottom:10px;text-align:center;"></div>
    <div style="display:flex;gap:8px;">
      <button class="dl-btn" style="flex:1;" onclick="downloadPNG('png')">↓ PNG</button>
      <button class="dl-btn" style="flex:1;" onclick="downloadPNG('jpg')">↓ JPG</button>
    </div>
  </div>

  <div class="editor-style">
    <div style="font-size:16px;font-weight:800;margin-bottom:20px;visibility:hidden;">.</div>
    <div class="ctrl-label" style="cursor:default;">선택된 텍스트 스타일</div>
    <div id="stylePanel" class="no-select-hint">텍스트를 클릭하여 선택하세요</div>
  </div>
</div>

<script>
const W=405, H=720, RW=1080, RH=1920, SX=405/1080, SY=720/1920;

const REPO_RAW = 'https://raw.githubusercontent.com/younkyung-wq/lazyz/main/';
// 유통채널 로고 (가로 폭 유지, 비율로 높이 계산)
const LOGOS=[
  {key:'wconcept',label:'W컨셉',src:REPO_RAW+'logo_wconcept.png',ar:478/60,w:400},
  {key:'musinsa',label:'무신사',src:REPO_RAW+'logo_musinsa.png',ar:668/126,w:350},
  {key:'29cm',label:'29CM',src:REPO_RAW+'logo_29cm.png',ar:1000/250,w:300},
  {key:'kurly',label:'컬리',src:REPO_RAW+'logo_kurly.png',ar:501/247,w:340},
  {key:'kream',label:'크림',src:REPO_RAW+'logo_kream.png?v=2',ar:1200/191,w:370},
  {key:'eql',label:'EQL',src:REPO_RAW+'logo_eql.png',ar:994/342,w:300},
  {key:'lotteon',label:'롯데온',src:REPO_RAW+'logo_lotteon.png',ar:336/68,w:370},
  {key:'ohou',label:'오늘의집',src:REPO_RAW+'logo_ohou.png',ar:662/193,w:300},
];

let templates=[
  {id:1,name:'템플릿 1',bgData:REPO_RAW+'1b.jpg',bgThumb:REPO_RAW+'thumb1.jpg',texts:[
    {id:1,text:'5/6(WED) - 5/16(SAT)',x:540,y:1085,fs:35,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.04em'},
    {id:2,text:'24H HOUR\\n26SS ~45%',x:540,y:1152,fs:120,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.04em',lh:1.083},
    {id:3,text:'레이지지 26ss 최대 45% 할인',x:540,y:1478,fs:45,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.04em'},
  ]},
  {id:2,name:'템플릿 2',bgData:REPO_RAW+'2b.jpg',bgThumb:REPO_RAW+'thumb2.jpg',texts:[
    {id:1,text:'BRAND WEEK\\nUP TO 45%',x:72,y:170,fs:120,color:'#ffffff',fw:600,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.02em',lh:1.083},
    {id:3,text:'레이지지 최대 45% 할인\\n5.04 - 5.08',x:82,y:473,fs:45,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.03em',lh:1.333,sw:0.3},
  ]},
  {id:3,name:'템플릿 3',bgData:REPO_RAW+'t3bg.jpg',bgThumb:REPO_RAW+'thumb3.jpg',
   imgs:[{id:50,src:REPO_RAW+'wweek.png',anchor:'bc',by:1310,w:720,h:156}],texts:[
    {id:3,text:'단 2주간, 최대 50% 할인',x:540,y:1350,fs:42,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'center',ls:'-0.03em',lh:1.4286},
    {id:1,text:'5.31(SUN) -\\n6.15(MON)',x:1000,y:150,fs:35,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'right',ls:'-0.03em',lh:1.4286},
  ]},
  {id:4,name:'템플릿 4',bgData:REPO_RAW+'3b.jpg',bgThumb:REPO_RAW+'thumb4.jpg',ver:0,
   versions:[
    {name:'가격',
     imgs:[{id:60,src:REPO_RAW+'logo_kurly.png',logo:'kurly',picker:true,anchor:'lc',x:60,cy:905,w:340,h:168},
           {id:61,src:REPO_RAW+'arrow.png',hideList:true,x:55,y:1514,w:340,h:16}],
     texts:[
       {id:2,text:'컬리 반짝특가',x:1020,y:880,fs:50,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'right',ls:'-0.03em',lh:1.4},
       {id:3,text:'정가 109,000원',x:72,y:1496,fs:44,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
       {id:4,text:'46,300원',x:415,y:1496,fs:44,color:'#ffffff',fw:400,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em'},
     ]},
    {name:'이벤트',
     imgs:[{id:70,src:REPO_RAW+'logo_kurly.png',logo:'kurly',picker:true,anchor:'lc',x:60,cy:905,w:340,h:168}],
     texts:[
       {id:5,text:'컬리 반짝특가',x:1020,y:880,fs:50,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ta:'right',ls:'-0.03em',lh:1.4},
       {id:6,text:'Loose Fit Classic Solid Shirt\\n45% Sale',x:80,y:1440,fs:45,color:'#ffffff',fw:300,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'0em',lh:1.6},
     ]},
   ]},
];

let activeTplId=null, selTextId=null, dragInfo=null, nextId=200;
let undoStack=[], redoStack=[];
const getTpl=()=>templates.find(t=>t.id===activeTplId);
const getTexts=()=>getTpl()?.texts??[];
const getTxt=id=>getTexts().find(t=>t.id===id);

function snapTpl(){const t=getTpl();return JSON.stringify({texts:t?.texts||[],imgs:t?.imgs||[],bgX:t?.bgX||0,bgY:t?.bgY||0,bgScale:t?.bgScale||1});}
function restoreTpl(s){const tpl=getTpl();if(!tpl)return;const d=JSON.parse(s);tpl.texts=d.texts;tpl.imgs=d.imgs;tpl.bgX=d.bgX;tpl.bgY=d.bgY;tpl.bgScale=d.bgScale;if(tpl.versions){tpl.versions[tpl.ver||0].texts=d.texts;tpl.versions[tpl.ver||0].imgs=d.imgs;}applyBgTransform();}
function saveUndo(){
  undoStack.push(snapTpl());
  if(undoStack.length>30)undoStack.shift();
  redoStack=[];
}
function undo(){
  if(!undoStack.length)return;
  redoStack.push(snapTpl());
  restoreTpl(undoStack.pop());
  refreshLayers(); refreshTextList(); refreshStylePanel();
}
function redo(){
  if(!redoStack.length)return;
  undoStack.push(snapTpl());
  restoreTpl(redoStack.pop());
  refreshLayers(); refreshTextList(); refreshStylePanel();
}
document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key==='z'&&!e.shiftKey){e.preventDefault();undo();}
  if((e.metaKey||e.ctrlKey)&&(e.key==='y'||(e.key==='z'&&e.shiftKey))){e.preventDefault();redo();}
});
// 복사/붙여넣기/복제 (Cmd+C / Cmd+V / Cmd+D)
let clip=null;
document.addEventListener('keydown',e=>{
  if(!(e.metaKey||e.ctrlKey))return;
  const ae=document.activeElement;
  if(ae&&(ae.isContentEditable||ae.tagName==='INPUT'||ae.tagName==='TEXTAREA'||ae.tagName==='SELECT'))return; // 편집 중엔 일반 복붙
  const k=e.key.toLowerCase();
  if(k==='c'){
    if(selTextId){clip={kind:'text',data:JSON.parse(JSON.stringify(getTxt(selTextId)))};e.preventDefault();}
    else if(selImgId){clip={kind:'img',data:JSON.parse(JSON.stringify(getImg(selImgId)))};e.preventDefault();}
  } else if(k==='v'&&clip){
    e.preventDefault(); saveUndo();
    if(clip.kind==='text'){
      const t={...JSON.parse(JSON.stringify(clip.data)),id:nextId++,x:(clip.data.x||0)+30,y:(clip.data.y||0)+30};
      getTexts().push(t); refreshLayers(); selectText(t.id);
    } else {
      const m={...JSON.parse(JSON.stringify(clip.data)),id:nextId++};
      if(m.anchor==='bc')m.by=(m.by||0)+30; else if(m.anchor==='lc'){m.x=(m.x||0)+30;m.cy=(m.cy||0)+30;} else {m.x=(m.x||0)+30;m.y=(m.y||0)+30;}
      getImgs().push(m); refreshLayers(); selectImg(m.id);
    }
  } else if(k==='d'){ // 즉시 복제
    if(selTextId){e.preventDefault();saveUndo();const o=getTxt(selTextId);const t={...JSON.parse(JSON.stringify(o)),id:nextId++,x:(o.x||0)+30,y:(o.y||0)+30};getTexts().push(t);refreshLayers();selectText(t.id);}
    else if(selImgId){e.preventDefault();saveUndo();const o=getImg(selImgId);const m={...JSON.parse(JSON.stringify(o)),id:nextId++};if(m.anchor==='bc')m.by=(m.by||0)+30;else if(m.anchor==='lc'){m.x=(m.x||0)+30;m.cy=(m.cy||0)+30;}else{m.x=(m.x||0)+30;m.y=(m.y||0)+30;}getImgs().push(m);refreshLayers();selectImg(m.id);}
  }
});
// 화살표키 미세조정 (선택된 텍스트/이미지, Shift=10px)
document.addEventListener('keydown',e=>{
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  const ae=document.activeElement;
  if(ae&&(ae.isContentEditable||ae.tagName==='INPUT'||ae.tagName==='TEXTAREA'||ae.tagName==='SELECT'))return;
  // T = 배경 이미지 크기/위치 조절 토글
  if(e.key==='t'||e.key==='T'){
    const ev=document.getElementById('editorView');
    if(ev&&!ev.classList.contains('hidden')){ e.preventDefault(); toggleImgMode(); }
    return;
  }
  // Delete/Backspace = 선택 레이어 삭제
  if(e.key==='Delete'||e.key==='Backspace'){
    if(selTextId){ e.preventDefault(); deleteText(selTextId); selTextId=null; refreshStylePanel(); document.getElementById('measure').style.display='none'; return; }
    if(selImgId){ e.preventDefault(); deleteImg(selImgId); return; }
    return;
  }
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;
  e.preventDefault(); // 페이지 스크롤 방지
  const step=e.shiftKey?10:1;
  const dx=(e.key==='ArrowLeft'?-step:e.key==='ArrowRight'?step:0);
  const dy=(e.key==='ArrowUp'?-step:e.key==='ArrowDown'?step:0);
  if(imgMode){ // 배경 이미지 조절 모드
    const tpl=getTpl(); if(!tpl)return;
    saveUndo();
    tpl.bgX=(tpl.bgX||0)+dx; tpl.bgY=(tpl.bgY||0)+dy;
    applyBgTransform();
  } else if(selTextId){
    const t=getTxt(selTextId); if(!t)return;
    saveUndo();
    t.x+=dx; t.y+=dy;
    const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`); if(el)placeEl(el,t);
    showMeasure();
  } else if(selImgId){
    const m=getImg(selImgId); if(!m)return;
    saveUndo();
    if(m.anchor==='bc'){ m.by+=dy; }
    else if(m.anchor==='lc'){ m.x+=dx; m.cy+=dy; }
    else { m.x+=dx; m.y+=dy; }
    refreshLayers();
  }
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
  activeTplId=id; selTextId=null; selImgId=null;
  if(imgMode)toggleImgMode();
  const tpl=getTpl();
  // 버전 템플릿이면 현재 버전 내용 연결
  if(tpl.versions){ const v=tpl.versions[tpl.ver||0]; tpl.texts=v.texts; tpl.imgs=v.imgs; }
  document.getElementById('gridView').classList.add('hidden');
  document.getElementById('editorView').classList.remove('hidden');
  document.getElementById('editorTemplName').textContent=tpl.name;
  refreshBg(); refreshLayers(); refreshTextList(); refreshStylePanel(); renderBgList();
}
function switchVersion(idx){
  const tpl=getTpl(); if(!tpl||!tpl.versions)return;
  selTextId=null; selImgId=null;
  tpl.ver=idx;
  const v=tpl.versions[idx];
  tpl.texts=v.texts; tpl.imgs=v.imgs;
  refreshLayers(); refreshTextList(); refreshStylePanel();
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
  applyBgTransform();
}
function clampBg(tpl){
  // 항상 프레임을 덮도록 제한 (회색 안 보이게)
  let s=tpl.bgScale||1; if(s<1)s=1;
  const maxX=RW*(s-1)/2, maxY=RH*(s-1)/2;
  let ox=tpl.bgX||0, oy=tpl.bgY||0;
  ox=Math.max(-maxX,Math.min(maxX,ox));
  oy=Math.max(-maxY,Math.min(maxY,oy));
  tpl.bgScale=s; tpl.bgX=ox; tpl.bgY=oy;
}
function applyBgTransform(){
  const tpl=getTpl(); if(!tpl)return;
  clampBg(tpl);
  // 활성 배경 항목에 변형 저장 (배경별 개별 유지)
  if(tpl.bgList&&tpl.bgList[tpl.bgIdx]){ const it=tpl.bgList[tpl.bgIdx]; it.sc=tpl.bgScale; it.x=tpl.bgX; it.y=tpl.bgY; }
  const img=document.getElementById('storyBgImg');
  const s=tpl.bgScale||1, ox=tpl.bgX||0, oy=tpl.bgY||0;
  img.style.transformOrigin='center';
  img.style.transform=`translate(${ox*SX}px,${oy*SY}px) scale(${s})`;
  if(imgMode)updateXfBox();
}
function updateXfBox(){
  const tpl=getTpl(); if(!tpl)return;
  const s=tpl.bgScale||1, ox=tpl.bgX||0, oy=tpl.bgY||0;
  const outer=document.getElementById('storyOuter');
  const baseL=outer.offsetLeft, baseT=outer.offsetTop;
  const boxW=W*s, boxH=H*s;
  const box=document.getElementById('imgXfBox');
  box.style.width=boxW+'px'; box.style.height=boxH+'px';
  box.style.left=(baseL+(W-boxW)/2+ox*SX)+'px';
  box.style.top=(baseT+(H-boxH)/2+oy*SY)+'px';
  document.getElementById('xfScaleTag').textContent=Math.round(s*100)+'%';
}

// ── TEXT LAYERS ──
function refreshLayers(){
  const outer=document.getElementById('storyOuter');
  outer.querySelectorAll('.text-layer').forEach(el=>el.remove());
  outer.querySelectorAll('.img-layer').forEach(el=>el.remove());
  getImgs().forEach(im=>outer.appendChild(makeImgEl(im))); // 이미지 먼저(아래)
  getTexts().forEach(t=>outer.appendChild(makeEl(t)));
}
// ── 이미지 레이어 ──
let selImgId=null;
const getImgs=()=>{const t=getTpl();if(!t)return [];if(!t.imgs)t.imgs=[];return t.imgs;};
const getImg=id=>getImgs().find(m=>m.id===id);
// 실제 위치/크기 (bottom-center 앵커면 계산)
function imgRect(m){
  if(m.anchor==='bc') return {x:Math.round((RW-m.w)/2), y:Math.round(m.by-m.h), w:m.w, h:m.h};
  if(m.anchor==='lc') return {x:m.x, y:Math.round(m.cy-m.h/2), w:m.w, h:m.h};
  return {x:m.x, y:m.y, w:m.w, h:m.h};
}
function makeImgEl(im){
  const r=imgRect(im);
  const el=document.createElement('div');
  el.className='img-layer'+(selImgId===im.id?' selected':'');
  el.dataset.iid=im.id;
  el.style.left=(r.x*SX)+'px'; el.style.top=(r.y*SY)+'px';
  el.style.width=(r.w*SX)+'px'; el.style.height=(r.h*SY)+'px';
  if(im.onTop)el.style.zIndex=15;
  const img=document.createElement('img'); img.src=im.src; el.appendChild(img);
  if(selImgId===im.id){
    ['nw','ne','sw','se'].forEach(pos=>{
      const h=document.createElement('div'); h.className='img-handle'; h.dataset.pos=pos;
      const s='-8px';
      if(pos==='nw'){h.style.top=s;h.style.left=s;h.style.cursor='nwse-resize';}
      if(pos==='ne'){h.style.top=s;h.style.right=s;h.style.cursor='nesw-resize';}
      if(pos==='sw'){h.style.bottom=s;h.style.left=s;h.style.cursor='nesw-resize';}
      if(pos==='se'){h.style.bottom=s;h.style.right=s;h.style.cursor='nwse-resize';}
      h.addEventListener('mousedown',e=>startImgResize(e,im.id,pos));
      el.appendChild(h);
    });
  }
  el.addEventListener('mousedown',e=>onImgMouseDown(e,im.id));
  return el;
}
function selectImg(id){
  selImgId=id; selTextId=null;
  document.querySelectorAll('.text-layer').forEach(el=>el.classList.remove('selected'));
  refreshLayers(); refreshTextList();
}
function onAddImgLayer(e){
  const f=e.target.files[0]; if(!f)return;
  const reader=new FileReader();
  reader.onload=ev=>{
    const img=new Image();
    img.onload=()=>{
      const tpl=getTpl(); if(!tpl)return;
      saveUndo();
      const w=720, h=Math.round(720*img.height/img.width);
      const m={id:nextId++,src:ev.target.result,x:Math.round((RW-w)/2),y:Math.round((RH-h)/2),w,h};
      getImgs().push(m);
      selectImg(m.id);
    };
    img.src=ev.target.result;
  };
  reader.readAsDataURL(f);
  e.target.value='';
}
function onImgMouseDown(e,id){
  if(e.target.classList.contains('img-handle'))return;
  e.preventDefault(); e.stopPropagation();
  const m=getImg(id); if(!m)return;
  selectImg(id);
  if(m.anchor==='bc'||m.anchor==='lc')return; // 고정 앵커: 클릭=선택만, 크기는 핸들로
  const sx=e.clientX, sy=e.clientY, x0=m.x, y0=m.y;
  let moved=false, saved=false;
  const mv=ev=>{
    if(!moved&&(Math.abs(ev.clientX-sx)>3||Math.abs(ev.clientY-sy)>3)){moved=true;}
    if(!moved)return;
    if(!saved){saveUndo();saved=true;}
    let ddx=ev.clientX-sx, ddy=ev.clientY-sy;
    if(ev.shiftKey){ if(Math.abs(ddx)>Math.abs(ddy)) ddy=0; else ddx=0; }
    m.x=Math.round(x0+ddx/SX); m.y=Math.round(y0+ddy/SY);
    const el=document.querySelector(`.img-layer[data-iid="${id}"]`);
    if(el){el.style.left=(m.x*SX)+'px';el.style.top=(m.y*SY)+'px';}
  };
  const up=()=>{document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);};
  document.addEventListener('mousemove',mv); document.addEventListener('mouseup',up);
}
function startImgResize(e,id,pos){
  e.preventDefault(); e.stopPropagation();
  const m=getImg(id); if(!m)return;
  saveUndo();
  const sx=e.clientX, w0=m.w, h0=m.h, x0=m.x, y0=m.y, ar=m.w/m.h;
  const mv=ev=>{
    const dx=(ev.clientX-sx)/SX;
    if(m.anchor==='bc'){
      // 중앙 정렬 + 하단 고정: 좌우 대칭으로 너비 변경, 위로만 자람
      const sign=(pos==='ne'||pos==='se')?1:-1;
      let nw=Math.max(60,w0+sign*dx*2);
      m.w=Math.round(nw); m.h=Math.round(nw/ar);
      refreshLayers(); return;
    }
    if(m.anchor==='lc'){
      // 왼쪽 고정 + 세로중앙 고정: 우측 핸들로 너비 변경
      const sign=(pos==='ne'||pos==='se')?1:-1;
      let nw=Math.max(60,w0+sign*dx);
      m.w=Math.round(nw); m.h=Math.round(nw/ar);
      refreshLayers(); return;
    }
    let nw=(pos==='ne'||pos==='se')?w0+dx:w0-dx;
    nw=Math.max(40,nw);
    const nh=Math.round(nw/ar);
    m.w=Math.round(nw); m.h=nh;
    if(pos==='nw'||pos==='sw') m.x=Math.round(x0+(w0-nw));
    if(pos==='nw'||pos==='ne') m.y=Math.round(y0+(h0-nh));
    refreshLayers();
  };
  const up=()=>{document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);};
  document.addEventListener('mousemove',mv); document.addEventListener('mouseup',up);
}
function deleteImg(id){
  const tpl=getTpl(); if(!tpl)return;
  saveUndo();
  tpl.imgs=getImgs().filter(m=>m.id!==id);
  if(selImgId===id)selImgId=null;
  refreshLayers(); refreshTextList();
}
function setLogo(id,key){
  const m=getImg(id); if(!m)return;
  const L=LOGOS.find(x=>x.key===key); if(!L)return;
  saveUndo();
  m.src=L.src; m.logo=key;
  m.w=L.w; // 로고별 기본 가로폭
  m.h=Math.round(L.w/L.ar);
  refreshLayers(); refreshTextList();
}
function makeEl(t){
  const el=document.createElement('div');
  el.className='text-layer';
  el.dataset.tid=t.id;
  applyStyle(el,t); placeEl(el,t);
  renderChars(el,t);
  el.addEventListener('mousedown',e=>onTextMouseDown(e,t.id));
  el.addEventListener('dblclick',e=>{e.stopPropagation();startEdit(t.id,e);});
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
      const baseLs=Math.round(parseFloat(t.ls||'0')*1000);
      const kern=(t.kerns&&t.kerns[i])||0;
      if(ch===' '){ sp.style.display='inline-block'; sp.style.width=(t.sw||0.15)+'em'; } else { sp.textContent=ch; }
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
  el.style.textDecoration=t.strike?'line-through':'none';
  el.style.textDecorationThickness=t.strike?Math.max(1,t.fs*SY*0.045)+'px':'';
}
function placeEl(el,t){
  el.style.width='auto';
  el.style.textAlign=t.ta||'left';
  // 행간이 폰트크기보다 클 때 첫 줄 위쪽 leading만큼 위로 보정 → 첫 줄 top 고정 (canvas와 일치)
  const lh=parseFloat(t.lh||'1.1');
  const halfLeading=Math.max(0,(lh-1))*(t.fs*SY)/2;
  const tY='translateY('+(-halfLeading)+'px)';
  const tX=(t.ta==='center'?'translateX(-50%) ':t.ta==='right'?'translateX(-100%) ':'');
  el.style.transform=tX+tY;
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
  showMeasure();
}
function startEdit(id, clickEvent){
  saveUndo();
  selTextId=id;
  refreshTextList(); refreshStylePanel();
  const el=document.querySelector(`.text-layer[data-tid="${id}"]`);
  if(!el)return;
  const t=getTxt(id); if(!t)return;

  el.setAttribute('contenteditable','true');
  el.textContent=t.text; // 편집 중엔 일반 텍스트(공백 보존)
  el.style.letterSpacing=(t.ls||'0em'); // 편집 중 기본 자간 유지
  el.focus({preventScroll:true});
  showMeasure();

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
    el.style.letterSpacing='0em'; // per-char로 복원
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
    let ddx=ev.clientX-startX, ddy=ev.clientY-startY;
    if(ev.shiftKey){ if(Math.abs(ddx)>Math.abs(ddy)) ddy=0; else ddx=0; } // 직선 이동
    t.x=Math.round(startTx+ddx/SX);
    t.y=Math.round(startTy+ddy/SY);
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
    showMeasure();
  };
  const onUp=ev=>{
    hideGuides();
    document.removeEventListener('mousemove',onMove);
    document.removeEventListener('mouseup',onUp);
    // 단일 클릭은 선택만 (이미 selectText됨). 편집은 더블클릭.
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
  document.getElementById('measure').style.display='none';
}
function addText(){
  const tpl=getTpl(); if(!tpl)return;
  const t={id:nextId++,text:'텍스트',x:540,y:960,fs:45,color:'#ffffff',fw:500,italic:false,ff:'Pretendard, sans-serif',shadow:false,ls:'-0.03em',lh:1.333};
  (getTexts()).push(t);
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
  // 버전 선택 (versions 있을 때)
  const tpl=getTpl();
  if(tpl&&tpl.versions){
    const tabs=tpl.versions.map((v,i)=>`
      <button onclick="switchVersion(${i})" style="flex:1;padding:9px;border:none;border-radius:7px;cursor:pointer;font-size:12px;font-weight:700;
        background:${(tpl.ver||0)===i?'#111':'#f0f0f0'};color:${(tpl.ver||0)===i?'#fff':'#888'};">${v.name}</button>`).join('');
    const box=document.createElement('div');
    box.style.cssText='margin-bottom:14px;';
    box.innerHTML=`<div style="font-size:11px;font-weight:700;color:#bbb;letter-spacing:0.5px;margin-bottom:6px;">버전</div>
      <div style="display:flex;gap:6px;background:#fafafa;padding:5px;border-radius:9px;">${tabs}</div>`;
    list.appendChild(box);
  }
  // 이미지 레이어 = 맨 위
  getImgs().forEach((m)=>{
    if(m.hideList)return;
    const item=document.createElement('div');
    item.style.cssText='margin-bottom:9px;';
    if(m.picker){
      // 로고 선택 드롭다운
      const opts=LOGOS.map(L=>`<option value="${L.key}" ${m.logo===L.key?'selected':''}>${L.label}</option>`).join('');
      item.innerHTML=`
        <div style="font-size:11px;font-weight:700;color:#bbb;letter-spacing:0.5px;margin-bottom:6px;">로고 선택</div>
        <select onchange="setLogo(${m.id},this.value)" style="width:100%;padding:9px 32px 9px 12px;border:1.5px solid #eee;border-radius:8px;font-size:13px;color:#333;cursor:pointer;-webkit-appearance:none;appearance:none;background:white url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2212%22 height=%2212%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%23999%22 stroke-width=%222%22><polyline points=%226 9 12 15 18 9%22/></svg>') no-repeat right 12px center;">${opts}</select>`;
    } else {
      item.style.cssText='display:flex;gap:8px;align-items:center;margin-bottom:7px;';
      item.innerHTML=`<button onclick="event.stopPropagation();replaceImg(${m.id})" style="flex:1;padding:10px;border:none;border-radius:8px;background:#111;color:#fff;font-size:12px;font-weight:700;cursor:pointer;">타이틀 이미지 교체</button>`;
    }
    list.appendChild(item);
  });
  // 텍스트 레이어
  getTexts().forEach(t=>{
    const item=document.createElement('div');
    item.className='text-item'+(selTextId===t.id?' active':'');
    const rows=(t.text.match(/\\n/g)||[]).length+1;
    item.innerHTML=`
      <textarea class="text-item-input" rows="${rows}"
        style="flex:1;border:none;background:transparent;font-size:12px;color:#444;outline:none;min-width:0;resize:none;font-family:inherit;line-height:1.4;overflow:hidden;">${t.text.replace(/</g,'&lt;')}</textarea>
      <span class="text-item-del" onclick="event.stopPropagation();deleteText(${t.id})">×</span>`;
    const input=item.querySelector('textarea');
    const autosize=()=>{input.style.height='auto';input.style.height=input.scrollHeight+'px';};
    setTimeout(autosize,0);
    input.addEventListener('focus',()=>{selTextId=t.id;refreshStylePanel();document.querySelectorAll('.text-item').forEach(el=>el.classList.remove('active'));item.classList.add('active');showMeasure();});
    input.addEventListener('input',()=>{
      saveUndo();
      t.text=input.value;
      autosize();
      const el=document.querySelector(`.text-layer[data-tid="${t.id}"]`);
      if(el)renderChars(el,t);
    });
    item.addEventListener('click',e=>{if(e.target!==input){selectText(t.id);refreshLayers();}});
    list.appendChild(item);
  });
}
let replaceTargetId=null;
function replaceImg(id){
  replaceTargetId=id;
  document.getElementById('imgReplaceInput').click();
}
function onReplaceImg(e){
  const f=e.target.files[0]; if(!f||replaceTargetId==null)return;
  const m=getImg(replaceTargetId); if(!m){e.target.value='';return;}
  const reader=new FileReader();
  reader.onload=ev=>{
    const img=new Image();
    img.onload=()=>{
      saveUndo();
      // 가로 폭 유지, 새 비율로 높이만 재계산
      m.src=ev.target.result;
      m.h=Math.round(m.w*img.height/img.width);
      refreshLayers();
    };
    img.src=ev.target.result;
  };
  reader.readAsDataURL(f);
  e.target.value='';
}

// ── STYLE PANEL ──
function refreshStylePanel(){
  const panel=document.getElementById('stylePanel');
  if(!selTextId){panel.innerHTML='<div class="no-select-hint">텍스트를 클릭하여 선택하세요</div>';return;}
  const t=getTxt(selTextId); if(!t)return;
  panel.innerHTML=`
    <div class="style-grid">
      <div class="fld">
        <span class="fld-label">폰트</span>
        <select onchange="setS('ff',this.value)">
          <option value="Pretendard, sans-serif" ${t.ff==='Pretendard, sans-serif'?'selected':''}>Pretendard</option>
          <option value="sans-serif" ${t.ff==='sans-serif'?'selected':''}>Sans-serif</option>
          <option value="Georgia, serif" ${t.ff==='Georgia, serif'?'selected':''}>Georgia</option>
          <option value="'Helvetica Neue',sans-serif" ${t.ff==="'Helvetica Neue',sans-serif"?'selected':''}>Helvetica</option>
          <option value="'Courier New',monospace" ${t.ff==="'Courier New',monospace"?'selected':''}>Courier</option>
        </select>
      </div>
      <div class="fld-row">
        <div class="fld">
          <span class="fld-label">크기 (px)</span>
          <input class="num-input" type="number" min="1" max="500" step="1" value="${t.fs}" oninput="setS('fs',+this.value)">
        </div>
        <div class="fld">
          <span class="fld-label">굵기</span>
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
      </div>
      <div class="fld-row">
        <div class="fld">
          <span class="fld-label">자간 (‱)</span>
          <input class="num-input" type="number" step="1" value="${Math.round(parseFloat(t.ls||'0')*1000)}" oninput="setS('ls',(this.value/1000)+'em')">
        </div>
        <div class="fld">
          <span class="fld-label">행간 (px)</span>
          <input class="num-input" type="number" step="1" value="${Math.round((parseFloat(t.lh||'1.1'))*t.fs)}" oninput="setLh(+this.value)">
        </div>
      </div>
      <div class="fld-row" style="align-items:flex-end;">
        <div class="fld" style="flex:0 0 auto;">
          <span class="fld-label">색상</span>
          <input type="color" value="${t.color}" oninput="setS('color',this.value)" style="width:38px;height:34px;border:1.5px solid #eee;border-radius:7px;padding:1px;cursor:pointer;background:none;">
        </div>
        <div class="fld" style="flex:0 0 auto;">
          <span class="fld-label">기울임</span>
          <button class="style-btn ${t.italic?'on':''}" onclick="toggleItalic()" style="height:34px;width:38px;"><i>I</i></button>
        </div>
        <div class="fld" style="flex:0 0 auto;">
          <span class="fld-label">취소선</span>
          <button class="style-btn ${t.strike?'on':''}" onclick="toggleStrike()" style="height:34px;width:38px;text-decoration:line-through;">S</button>
        </div>
      </div>
    </div>`;
}
function toggleStrike(){
  const t=getTxt(selTextId); if(!t)return; t.strike=!t.strike;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`); if(el)applyStyle(el,t);
  refreshStylePanel();
}
function setS(prop,val){
  const t=getTxt(selTextId); if(!t)return;
  t[prop]=val;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`);
  if(el){applyStyle(el,t);placeEl(el,t);renderChars(el,t);}
  showMeasure();
}
function setLh(px){
  const t=getTxt(selTextId); if(!t)return;
  t.lh=px/t.fs;
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`);
  if(el){el.style.lineHeight=t.lh;placeEl(el,t);}
  showMeasure();
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
    const tpl=templates.find(t=>t.id===id);
    if(!tpl.bgList)tpl.bgList=[];
    tpl.bgList.push({src:e.target.result,sc:1,x:0,y:0}); // 배경별 변형 저장
    setActiveBg(tpl,tpl.bgList.length-1);
    if(cb)cb(); if(activeTplId===id){refreshBg();renderBgList();}
  };
  reader.readAsDataURL(file);
}
function setActiveBg(tpl,i){
  const it=tpl.bgList&&tpl.bgList[i]; if(!it)return;
  tpl.bgData=it.src; tpl.bgScale=it.sc||1; tpl.bgX=it.x||0; tpl.bgY=it.y||0; tpl.bgIdx=i;
}
function loadBgs(id,files){
  [...files].filter(f=>f.type.startsWith('image/')).forEach(f=>loadBg(id,f));
}
function renderBgList(){
  const box=document.getElementById('bgThumbs'); if(!box)return;
  const tpl=getTpl(); box.innerHTML='';
  const list=(tpl&&tpl.bgList)||[];
  list.forEach((it,i)=>{
    const d=document.createElement('div');
    d.style.cssText='position:relative;width:54px;height:54px;border-radius:6px;overflow:hidden;cursor:pointer;border:2px solid '+(tpl.bgIdx===i?'#ff4b4b':'#eee')+';';
    d.innerHTML=`<img src="${it.src}" style="width:100%;height:100%;object-fit:cover;">
      <span style="position:absolute;top:1px;right:2px;background:rgba(0,0,0,0.55);color:#fff;font-size:11px;line-height:1;padding:2px 4px;border-radius:3px;">×</span>`;
    d.querySelector('img').addEventListener('click',()=>{setActiveBg(tpl,i);refreshBg();renderBgList();});
    d.querySelector('span').addEventListener('click',e=>{e.stopPropagation();tpl.bgList.splice(i,1);if(tpl.bgList.length){setActiveBg(tpl,Math.min(i,tpl.bgList.length-1));}else{tpl.bgData=null;tpl.bgIdx=-1;}refreshBg();renderBgList();});
    box.appendChild(d);
  });
}
function onBgDragOver(e){e.preventDefault();const ov=document.getElementById('storyDropOverlay');ov.classList.remove('hidden');ov.classList.add('drag-over');}
function onBgDragLeave(){const ov=document.getElementById('storyDropOverlay');ov.classList.remove('drag-over');if(getTpl()?.bgData)ov.classList.add('hidden');}
function onBgDrop(e){e.preventDefault();const ov=document.getElementById('storyDropOverlay');ov.classList.remove('drag-over');loadBgs(activeTplId,e.dataTransfer.files);}
function onUploadDragOver(e){e.preventDefault();document.getElementById('uploadZone').classList.add('drag-over');}
function onUploadDragLeave(){document.getElementById('uploadZone').classList.remove('drag-over');}
function onUploadDrop(e){e.preventDefault();document.getElementById('uploadZone').classList.remove('drag-over');loadBgs(activeTplId,e.dataTransfer.files);}
function onFileInput(e){loadBgs(activeTplId,e.target.files);e.target.value='';}

// ── DOWNLOAD ──
function downloadPNG(fmt){
  fmt=fmt||'png';
  const tpl=getTpl();
  if(!tpl.bgData){alert('배경 이미지를 먼저 업로드해주세요.');return;}
  const canvas=document.createElement('canvas');
  canvas.width=RW; canvas.height=RH;
  const ctx=canvas.getContext('2d');
  const img=new Image();
  img.crossOrigin='anonymous';
  img.onerror=()=>{alert('이미지를 불러오지 못했어요. 다시 시도해주세요.');};
  img.onload=()=>{
    const ia=img.width/img.height, ca=RW/RH;
    let sx,sy,sw,sh;
    if(ia>ca){sh=img.height;sw=sh*ca;sx=(img.width-sw)/2;sy=0;}
    else{sw=img.width;sh=sw/ca;sx=0;sy=(img.height-sh)/2;}
    // 배경 변형 적용 (중심 기준 scale + offset)
    const bs=tpl.bgScale||1, bx=tpl.bgX||0, by=tpl.bgY||0;
    ctx.save();
    ctx.translate(RW/2+bx,RH/2+by);
    ctx.scale(bs,bs);
    ctx.translate(-RW/2,-RH/2);
    ctx.drawImage(img,sx,sy,sw,sh,0,0,RW,RH);
    ctx.restore();
    // 모든 이미지 로드 → 하위이미지 그리기 → 텍스트 → 상위(onTop)이미지 → 내보내기
    const imgs=(tpl.imgs||[]);
    Promise.all(imgs.map(m=>new Promise(res=>{
      const im=new Image(); im.crossOrigin='anonymous'; im.onload=()=>res({m,im}); im.onerror=()=>res(null); im.src=m.src;
    }))).then(loaded=>{
      loaded.filter(Boolean).filter(o=>!o.m.onTop).forEach(o=>{const r=imgRect(o.m);ctx.drawImage(o.im,r.x,r.y,r.w,r.h);});
      window.__topImgs=loaded.filter(Boolean).filter(o=>o.m.onTop);
      drawTextsAndExport();
    });

    function drawTextsAndExport(){
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
        const swEm=(t.sw||0.15)*t.fs; // 공백 폭
        const chW=ch=>(ch===' '?swEm:ctx.measureText(ch).width);
        // 전체 너비 계산 (center용)
        let totalW=0;
        chars.forEach((ch,i)=>{
          const kern=((t.kerns&&t.kerns[charOffset+i])||0)/1000*t.fs;
          totalW+=chW(ch)+baseLs+kern;
        });
        let x=t.ta==='center'?t.x-totalW/2:t.ta==='right'?t.x-totalW:t.x;
        const startX=x;
        const y=t.y+li*lineH;
        chars.forEach((ch,i)=>{
          if(ch!==' ')ctx.fillText(ch,x,y);
          const kern=((t.kerns&&t.kerns[charOffset+i])||0)/1000*t.fs;
          x+=chW(ch)+baseLs+kern;
        });
        if(t.strike){
          const ly=y+t.fs*0.42;
          ctx.save();
          ctx.strokeStyle=t.color; ctx.lineWidth=Math.max(1,t.fs*0.045);
          ctx.beginPath(); ctx.moveTo(startX,ly); ctx.lineTo(x-baseLs,ly); ctx.stroke();
          ctx.restore();
        }
        charOffset+=chars.length+1; // +1 for the newline
      });
      ctx.restore();
    });
    // 상위(onTop) 이미지 = 텍스트 위에 그리기
    (window.__topImgs||[]).forEach(o=>{const r=imgRect(o.m);ctx.drawImage(o.im,r.x,r.y,r.w,r.h);});
    const isJpg=fmt==='jpg';
    const mime=isJpg?'image/jpeg':'image/png';
    const fname=`lazyz_story_${tpl.id}_${Date.now()}.${isJpg?'jpg':'png'}`;
    canvas.toBlob(async(blob)=>{
      if(!blob){alert('이미지 생성 실패');return;}
      // 폴더가 지정돼 있으면 그 폴더에 바로 저장
      if(saveDir){
        try{
          const fh=await saveDir.getFileHandle(fname,{create:true});
          const w=await fh.createWritable();
          await w.write(blob);
          await w.close();
          flashStatus('저장됨 → '+fname);
          return;
        }catch(err){
          alert('폴더 저장 실패: '+err.message+'\\n기본 다운로드로 전환합니다.');
        }
      }
      // 기본 다운로드
      const a=document.createElement('a');
      a.download=fname;
      a.href=URL.createObjectURL(blob);
      a.click();
      setTimeout(()=>URL.revokeObjectURL(a.href),1000);
    }, mime, isJpg?0.95:undefined);
    } // drawTextsAndExport end
  };
  img.src=tpl.bgData;
}

// ── 섹션 접기/펴기 ──
function toggleSection(id){
  document.getElementById(id).classList.toggle('collapsed');
}

// ── 배경 이미지 변형 ──
let imgMode=false;
function toggleImgMode(){
  imgMode=!imgMode;
  const btn=document.getElementById('imgModeBtn');
  const xf=document.getElementById('imgXf');
  if(imgMode){
    // 텍스트 선택 해제
    selTextId=null;
    document.querySelectorAll('.text-layer').forEach(el=>{el.classList.remove('selected');el.removeAttribute('contenteditable');el.style.pointerEvents='none';});
    document.getElementById('measure').style.display='none';
    refreshTextList(); refreshStylePanel();
    xf.style.display='block'; updateXfBox();
    btn.textContent='✓ 이미지 조절 중 (클릭하여 종료)';
    btn.style.background='#fff0f0'; btn.style.borderColor='#ff4b4b'; btn.style.color='#ff4b4b';
  } else {
    document.querySelectorAll('.text-layer').forEach(el=>{el.style.pointerEvents='';});
    xf.style.display='none';
    btn.textContent='🖼 이미지 크기/위치 조절';
    btn.style.background='#fafafa'; btn.style.borderColor='#eee'; btn.style.color='#666';
  }
}
function resetBgTransform(){
  const tpl=getTpl(); if(!tpl)return;
  tpl.bgScale=1; tpl.bgX=0; tpl.bgY=0;
  applyBgTransform();
}
(function initImgXf(){
  const box=document.getElementById('imgXfBox');
  // 빈 공간(박스 밖) 클릭 시 조절 모드 종료 (박스/핸들 드래그는 stopPropagation으로 제외됨)
  document.querySelector('.editor-canvas-area').addEventListener('mousedown',e=>{
    if(imgMode){ if(!e.target.closest('#imgXfBox')) toggleImgMode(); return; }
    // 빈 여백(텍스트/이미지 아님) 클릭 시 선택 해제
    if(!e.target.closest('.text-layer') && !e.target.closest('.img-layer')){
      if(selTextId!==null){
        selTextId=null;
        document.querySelectorAll('.text-layer').forEach(el=>{el.classList.remove('selected');el.removeAttribute('contenteditable');});
        refreshStylePanel();
        document.getElementById('measure').style.display='none';
      }
      if(selImgId!==null){ selImgId=null; refreshLayers(); }
      refreshTextList();
    }
  });
  // 박스 내부 드래그 = 이동
  box.addEventListener('mousedown',e=>{
    if(e.target.classList.contains('xf-handle'))return;
    e.preventDefault(); e.stopPropagation();
    const tpl=getTpl(); if(!tpl)return;
    const sx=e.clientX, sy=e.clientY, ox0=tpl.bgX||0, oy0=tpl.bgY||0;
    const mv=ev=>{ tpl.bgX=ox0+(ev.clientX-sx)/SX; tpl.bgY=oy0+(ev.clientY-sy)/SY; applyBgTransform(); };
    const up=()=>{document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);};
    document.addEventListener('mousemove',mv); document.addEventListener('mouseup',up);
  });
  // 코너 핸들 = 중심 기준 균등 확대/축소
  box.querySelectorAll('.xf-handle').forEach(h=>{
    h.addEventListener('mousedown',e=>{
      e.preventDefault(); e.stopPropagation();
      const tpl=getTpl(); if(!tpl)return;
      const outer=document.getElementById('storyOuter').getBoundingClientRect();
      const cx=outer.left+W/2+(tpl.bgX||0)*SX, cy=outer.top+H/2+(tpl.bgY||0)*SY;
      const startDist=Math.hypot(e.clientX-cx,e.clientY-cy);
      const s0=tpl.bgScale||1;
      const mv=ev=>{
        const d=Math.hypot(ev.clientX-cx,ev.clientY-cy);
        tpl.bgScale=Math.max(0.2,Math.min(5,s0*(d/startDist)));
        applyBgTransform();
      };
      const up=()=>{document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);};
      document.addEventListener('mousemove',mv); document.addEventListener('mouseup',up);
    });
  });
})();

// ── 저장 폴더 지정 (File System Access API) ──
let saveDir=null;
async function pickSaveDir(){
  if(!window.showDirectoryPicker){
    alert('이 브라우저는 폴더 지정을 지원하지 않아요.\\nChrome/Edge 최신 버전을 사용하거나, Chrome 설정 > 다운로드 > "다운로드 전에 위치 확인"을 켜주세요.');
    return;
  }
  try{
    saveDir=await window.showDirectoryPicker({mode:'readwrite'});
    document.getElementById('dirStatus').textContent='✓ 폴더 지정됨 — 이제 PNG/JPG가 자동 저장돼요';
    document.getElementById('dirStatus').style.color='#2e9e44';
    document.getElementById('pickDirBtn').textContent='📁 저장 폴더 변경';
  }catch(err){
    if(err.name==='SecurityError'){
      alert('이 화면(iframe)에서는 폴더 지정이 차단돼요.\\n대신 Chrome 설정 > 다운로드 > "다운로드 전에 각 파일의 저장 위치 확인"을 켜면 매번 폴더를 고를 수 있어요.');
    } else if(err.name!=='AbortError'){
      alert('폴더 지정 실패: '+err.message);
    }
  }
}
function flashStatus(msg){
  const el=document.getElementById('dirStatus');
  const prev=el.textContent, prevC=el.style.color;
  el.textContent=msg; el.style.color='#2e9e44';
  setTimeout(()=>{el.textContent=prev;el.style.color=prevC;},2500);
}

// ── 측정 모드: Cmd 누를 때만, 선택 박스 ↔ 가장자리 + 다른 박스 간격 ──
let cmdHeld=false;
function setCmd(on){ if(cmdHeld===on)return; cmdHeld=on; showMeasure(); }
document.addEventListener('keydown',e=>{ if(e.key==='Meta'||e.key==='Control')setCmd(true); });
document.addEventListener('keyup',e=>{ if(e.key==='Meta'||e.key==='Control')setCmd(false); });
window.addEventListener('blur',()=>setCmd(false));
// iframe에서 keydown이 안 잡힐 때 대비: 마우스 이벤트의 metaKey로 동기화
document.addEventListener('mousemove',e=>{ setCmd(e.metaKey||e.ctrlKey); },true);

function showMeasure(){
  const m=document.getElementById('measure');
  // 기존 동적 형제-간격 요소 제거
  m.querySelectorAll('.mz-sib').forEach(el=>el.remove());
  if(!cmdHeld||!selTextId){m.style.display='none';return;}
  const outer=document.getElementById('storyOuter');
  const el=document.querySelector(`.text-layer[data-tid="${selTextId}"]`);
  if(!el){m.style.display='none';return;}
  const o=outer.getBoundingClientRect(), b=el.getBoundingClientRect();
  const bx=b.left-o.left, by=b.top-o.top, bw=b.width, bh=b.height;
  const cx=bx+bw/2, cy=by+bh/2;
  const toReal=(px,dim)=>Math.round(px/(dim==='x'?o.width:o.height)*(dim==='x'?RW:RH));
  m.style.display='block';
  // 박스
  const box=document.getElementById('mzBox');
  box.style.left=bx+'px'; box.style.top=by+'px'; box.style.width=bw+'px'; box.style.height=bh+'px';
  // 가장자리 연결선
  const L=document.getElementById('mzLineL'); L.style.left='0px'; L.style.top=cy+'px'; L.style.width=bx+'px';
  const R=document.getElementById('mzLineR'); R.style.left=(bx+bw)+'px'; R.style.top=cy+'px'; R.style.width=(o.width-bx-bw)+'px';
  const T=document.getElementById('mzLineT'); T.style.left=cx+'px'; T.style.top='0px'; T.style.height=by+'px';
  const B=document.getElementById('mzLineB'); B.style.left=cx+'px'; B.style.top=(by+bh)+'px'; B.style.height=(o.height-by-bh)+'px';
  const set=(id,x,y,txt)=>{const e=document.getElementById(id);e.style.left=x+'px';e.style.top=y+'px';e.textContent=txt;};
  set('mzL',bx/2,cy,toReal(bx,'x')+'');
  set('mzR',bx+bw+(o.width-bx-bw)/2,cy,toReal(o.width-bx-bw,'x')+'');
  set('mzT',cx,by/2,toReal(by,'y')+'');
  set('mzB',cx,by+bh+(o.height-by-bh)/2,toReal(o.height-by-bh,'y')+'');

  // 다른 텍스트 박스와의 간격
  document.querySelectorAll('.text-layer').forEach(other=>{
    if(+other.dataset.tid===selTextId)return;
    const r=other.getBoundingClientRect();
    const ox2=r.left-o.left, oy2=r.top-o.top, ow=r.width, oh=r.height;
    const xOverlap=Math.min(bx+bw,ox2+ow)-Math.max(bx,ox2);
    const yOverlap=Math.min(by+bh,oy2+oh)-Math.max(by,oy2);
    const addLine=(x,y,w,h)=>{const d=document.createElement('div');d.className='mz-sib';d.style.cssText=`position:absolute;left:${x}px;top:${y}px;${w?('width:'+w+'px;border-top:1px solid #ff3df0;'):('height:'+h+'px;border-left:1px solid #ff3df0;')}`;m.appendChild(d);};
    const addTag=(x,y,txt)=>{const d=document.createElement('div');d.className='mz-tag mz-sib';d.style.color='#ff3df0';d.style.left=x+'px';d.style.top=y+'px';d.textContent=txt;m.appendChild(d);};
    if(xOverlap>0){ // 세로 간격
      const ix=Math.max(bx,ox2)+xOverlap/2;
      if(oy2+oh<=by){ const g=by-(oy2+oh); addLine(ix,oy2+oh,0,g); addTag(ix,oy2+oh+g/2,toReal(g,'y')+''); }
      else if(oy2>=by+bh){ const g=oy2-(by+bh); addLine(ix,by+bh,0,g); addTag(ix,by+bh+g/2,toReal(g,'y')+''); }
    }
    if(yOverlap>0){ // 가로 간격
      const iy=Math.max(by,oy2)+yOverlap/2;
      if(ox2+ow<=bx){ const g=bx-(ox2+ow); addLine(ox2+ow,iy,g,0); addTag(ox2+ow+g/2,iy,toReal(g,'x')+''); }
      else if(ox2>=bx+bw){ const g=ox2-(bx+bw); addLine(bx+bw,iy,g,0); addTag(bx+bw+g/2,iy,toReal(g,'x')+''); }
    }
  });
}
renderGrid();
</script>
</body>
</html>
"""

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 32px 20px 40px; border-bottom: 1px solid #222;">
        <img src="https://raw.githubusercontent.com/younkyung-wq/lazyz/main/logo.png" style="width:100px;display:block;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    menu = st.radio(
        "",
        ["📱  스토리 모듈", "🖼  썸네일 모듈"],
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:52vh'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="padding: 0 16px;">
        <div style="color:#555; font-size:11px; letter-spacing:1px; margin-bottom:8px; font-weight:600;">API KEY</div>
    </div>""", unsafe_allow_html=True)
    st.text_input("", type="password", placeholder="••••••••••••••••••••••••••",
                  label_visibility="collapsed", key="api_key")

# ── 썸네일 크로퍼 (HTML/JS 캔버스) ────────────────────────────
THUMB_HTML = r"""
<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Pretendard',-apple-system,sans-serif;}
body{background:#f8f8f8;height:870px;overflow:hidden;color:#222;}
.wrap{display:flex;flex-direction:column;height:870px;padding:16px 20px;gap:12px;}
.top{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.btn{padding:9px 16px;border:none;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;}
.btn-dark{background:#111;color:#fff;}
.btn-line{background:#fff;border:1.5px solid #ddd;color:#555;}
.btn-red{background:#ff4b4b;color:#fff;}
.hint{font-size:12px;color:#999;}
.mid{display:flex;gap:14px;flex:1;min-height:0;}
.left{width:150px;overflow-y:auto;display:flex;flex-direction:column;gap:7px;flex-shrink:0;}
.thumb{border:2px solid #eee;border-radius:7px;overflow:hidden;cursor:pointer;position:relative;flex-shrink:0;}
.thumb.on{border-color:#ff4b4b;}
.thumb img{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;}
.thdel{position:absolute;top:3px;right:3px;background:rgba(0,0,0,0.6);color:#fff;width:19px;height:19px;border-radius:50%;font-size:13px;line-height:19px;text-align:center;cursor:pointer;z-index:2;}
.thdel:hover{background:#ff4b4b;}
.thnum{position:absolute;top:3px;left:3px;background:#111;color:#fff;min-width:19px;height:19px;padding:0 5px;border-radius:10px;font-size:11px;font-weight:700;line-height:19px;text-align:center;z-index:2;}
.thumb{cursor:grab;}
.center{flex:1;display:flex;flex-direction:column;gap:10px;min-width:0;align-items:center;}
.tabs{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;}
.tab{padding:7px 13px;border-radius:20px;font-size:12px;font-weight:700;cursor:pointer;background:#eee;color:#888;border:none;}
.tab.on{background:#111;color:#fff;}
.stage{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;background:#fff;border-radius:12px;width:100%;}
canvas{border-radius:6px;box-shadow:0 2px 14px rgba(0,0,0,0.12);cursor:grab;}
canvas:active{cursor:grabbing;}
.info{font-size:12px;color:#888;text-align:center;}
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#bbb;height:100%;}
select{padding:8px 10px;border:1.5px solid #ddd;border-radius:8px;font-size:13px;}
#prog{font-size:12px;color:#2e9e44;font-weight:700;}
</style></head><body>
<div class="wrap">
  <div class="top">
    <button class="btn btn-dark" onclick="document.getElementById('fd').click()">📂 폴더 선택</button>
    <input id="fd" type="file" accept="image/*" webkitdirectory multiple style="display:none">
    <button class="btn btn-line" onclick="document.getElementById('fi').click()">📁 파일 선택</button>
    <input id="fi" type="file" accept="image/*" multiple style="display:none">
    <input id="pname" placeholder="상품명 (폴더명)" style="padding:8px 10px;border:1.5px solid #ddd;border-radius:8px;font-size:13px;width:170px;">
    <select id="fmt"><option value="jpg">JPG (최상화질)</option><option value="png">PNG</option></select>
    <button class="btn btn-line" onclick="saveOne()">↓ 이 채널만 저장</button>
    <button class="btn btn-red" onclick="saveAll()">📦 전체 저장 (ZIP)</button>
    <span id="prog"></span>
    <span class="hint">이미지 드래그=이동 · 마우스 휠=확대/축소 · 채널마다 따로 조절</span>
  </div>
  <div class="mid">
    <div class="left" id="strip"></div>
    <div class="center">
      <div class="tabs" id="tabs"></div>
      <div class="stage" id="stage">
        <div class="empty"><div style="font-size:40px">🖼️</div><div>이미지를 선택하세요</div></div>
      </div>
      <div class="info" id="info"></div>
    </div>
  </div>
</div>
<script>
const CH=[
 {k:'EQL',w:1500,h:2000,bg:'#ffffff',grp:'g_eqlmusinsa'},
 {k:'무신사',w:1500,h:1800,bg:'#ffffff',grp:'g_eqlmusinsa'},
 {k:'W컨셉',w:960,h:1280,bg:'#ffffff',grp:'g_wconcept'},
 {k:'29CM',w:1000,h:1000,bg:'#EBEBEB',grp:'g_29cm'},
 {k:'공홈',w:1000,h:1400,bg:'#ffffff',grp:'g_home',one:true},
 {k:'컬리',w:550,h:708,bg:'#F9F9F9',grp:'g_kurly',one:true},
 {k:'크림',w:1120,h:1120,bg:'#ffffff',grp:'g_kream',png:true,pngonly:true},
 {k:'조조타운',w:600,h:600,bg:'#ffffff',grp:'g_kream',pngonly:true},
];
// 그룹(채널)별 독립 이미지 목록 — 삭제/순서/크롭 모두 그룹별로 따로
const GROUPS={}; CH.forEach(c=>{ if(!GROUPS[c.grp])GROUPS[c.grp]={png:false}; if(c.pngonly)GROUPS[c.grp].png=true; });
let gImgs={}; let gAi={}; let ac=0;
function curGrp(){return CH[ac].grp;}
function curList(){return gImgs[curGrp()]||[];}
function curAi(){return gAi[curGrp()]||0;}
function setAi(v){gAi[curGrp()]=v;}
function anyImgs(){return Object.values(gImgs).some(l=>l&&l.length);}
const cvs=document.createElement('canvas');

function fitDisplay(cw,chh){
  const maxW=560,maxH=430;
  let dh=maxH, dw=dh*cw/chh;
  if(dw>maxW){dw=maxW; dh=dw*chh/cw;}
  return {dw:Math.round(dw),dh:Math.round(dh)};
}
function clampTf(img,cw,chh,t){
  // 이미지가 프레임을 항상 덮도록 cx,cy 제한
  const cover=Math.max(cw/img.width,chh/img.height);
  const ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  // 이미지가 프레임을 덮도록 cx,cy 범위 제한
  const half=cw/(2*iw);
  t.cx=Math.min(1-half,Math.max(half,t.cx));
  const halfY=chh/(2*ih);
  t.cy=Math.min(1-halfY,Math.max(halfY,t.cy));
}
function emptyStage(msg){
  document.getElementById('stage').innerHTML='<div class="empty"><div style="font-size:40px">🖼️</div><div>'+(msg||'이미지를 선택하세요')+'</div></div>';
  document.getElementById('info').textContent='';
}
function draw(){
  const st=document.getElementById('stage');
  const list=curList();
  if(!list.length){ emptyStage(GROUPS[curGrp()].png?'이 채널은 PNG(누끼) 이미지만 사용해요':'이미지를 선택하세요'); return; }
  let idx=curAi(); if(idx>=list.length){idx=list.length-1;setAi(idx);}
  const c=CH[ac], img=list[idx].img, t=list[idx].tf;
  const {dw,dh}=fitDisplay(c.w,c.h);
  const ratio=Math.max(2,window.devicePixelRatio||1); // 고해상도 렌더
  cvs.width=Math.round(dw*ratio); cvs.height=Math.round(dh*ratio);
  cvs.style.width=dw+'px'; cvs.style.height=dh+'px';
  if(cvs.parentElement!==st){st.innerHTML='';st.appendChild(cvs);}
  clampTf(img,dw,dh,t);
  const g=cvs.getContext('2d');
  g.setTransform(ratio,0,0,ratio,0,0);
  g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
  g.fillStyle=c.bg; g.fillRect(0,0,dw,dh);
  const cover=Math.max(dw/img.width,dh/img.height), ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  const dx=dw/2 - t.cx*iw, dy=dh/2 - t.cy*ih;
  g.drawImage(img,dx,dy,iw,ih);
  document.getElementById('info').textContent=c.k+'  '+c.w+'×'+c.h+' px  ·  확대 '+Math.round(t.z*100)+'%';
}
function renderTabs(){
  const t=document.getElementById('tabs'); t.innerHTML='';
  CH.forEach((c,i)=>{const b=document.createElement('button');b.className='tab'+(i===ac?' on':'');b.textContent=c.k+(c.one?' · 1장':'');b.onclick=()=>{ac=i;renderTabs();renderStrip();draw();};t.appendChild(b);});
}
let dragObj=null;
function delImg(o){
  const list=curList(); const idx=list.indexOf(o); if(idx<0)return;
  list.splice(idx,1);
  let a=curAi(); if(a>=list.length)a=Math.max(0,list.length-1); setAi(a);
  renderStrip(); draw();
}
function makeThumb(o){
  const d=document.createElement('div'); d.className='thumb'; d.draggable=true;
  d.innerHTML='<span class="thnum"></span><img draggable="false"><span class="thdel">×</span>';
  d.querySelector('img').src=o.url;
  d.querySelector('img').onclick=()=>{setAi(curList().indexOf(o));renderStrip();draw();};
  d.querySelector('.thdel').onclick=(e)=>{e.stopPropagation();delImg(o);};
  d.addEventListener('dragstart',()=>{dragObj=o;setTimeout(()=>d.style.opacity='0.35',0);});
  d.addEventListener('dragend',()=>{dragObj=null;d.style.opacity='1';});
  o.el=d; return d;
}
function renderStrip(){
  const s=document.getElementById('strip'); const list=curList(); const a=curAi();
  list.forEach((o,i)=>{
    if(!o.el)makeThumb(o);
    o.el.querySelector('.thnum').textContent=(i+1);
    o.el.classList.toggle('on',i===a);
    s.appendChild(o.el);
  });
  [...s.children].forEach(ch=>{ if(!list.some(o=>o.el===ch)) s.removeChild(ch); });
}
function getAfterEl(y){
  const els=[...document.getElementById('strip').children].filter(el=>el!==dragObj.el);
  let closest={offset:-Infinity,element:null};
  for(const el of els){ const b=el.getBoundingClientRect(); const off=y-(b.top+b.height/2);
    if(off<0 && off>closest.offset){ closest={offset:off,element:el}; } }
  return closest.element;
}
function flipAnimate(first){
  curList().forEach(o=>{ const f=first.get(o.el); if(!f||!o.el)return;
    const l=o.el.getBoundingClientRect(); const dy=f.top-l.top;
    if(dy){ o.el.style.transition='none'; o.el.style.transform='translateY('+dy+'px)';
      requestAnimationFrame(()=>{ o.el.style.transition='transform .18s cubic-bezier(.2,.8,.3,1)'; o.el.style.transform=''; }); }
  });
}
function flipMoveBefore(beforeObj){
  const list=curList();
  const arr=list.filter(o=>o!==dragObj);
  let idx=beforeObj?arr.indexOf(beforeObj):arr.length; if(idx<0)idx=arr.length;
  arr.splice(idx,0,dragObj);
  if(arr.every((o,i)=>o===list[i]))return;
  const act=list[curAi()];
  const first=new Map(); list.forEach(o=>{ if(o.el)first.set(o.el,o.el.getBoundingClientRect()); });
  gImgs[curGrp()]=arr; setAi(arr.indexOf(act));
  renderStrip(); flipAnimate(first);
}
function moveSel(delta){
  const list=curList(); const a=curAi(); const to=a+delta;
  if(to<0||to>=list.length)return;
  const act=list[a];
  const first=new Map(); list.forEach(o=>{ if(o.el)first.set(o.el,o.el.getBoundingClientRect()); });
  list.splice(a,1); list.splice(to,0,act); setAi(to);
  renderStrip(); flipAnimate(first);
}
function loadFiles(fileList,fromFolder){
  const files=[...fileList].filter(f=>f.type.startsWith('image/'));
  if(!files.length)return;
  if(fromFolder){
    const rel=files[0].webkitRelativePath||'';
    const folder=rel.split('/')[0];
    if(folder)document.getElementById('pname').value=folder;
  }
  files.sort((a,b)=>a.name.localeCompare(b.name));
  const pool=new Array(files.length); let loaded=0;
  files.forEach((f,idx)=>{
    const url=URL.createObjectURL(f);
    const im=new Image();
    im.onload=()=>{ pool[idx]={name:f.name,img:im,url:url}; loaded++; if(loaded===files.length)distribute(pool.filter(Boolean)); };
    im.src=url;
  });
}
function distribute(pool){
  gImgs={}; gAi={};
  Object.keys(GROUPS).forEach(grp=>{
    const src=GROUPS[grp].png ? pool.filter(p=>/\.png$/i.test(p.name)) : pool.slice();  // 누끼채널=PNG만, 나머지=전부
    gImgs[grp]=src.map(p=>({name:p.name,img:p.img,url:p.url,tf:{z:1,cx:0.5,cy:0.5},el:null}));
    gAi[grp]=0;
  });
  ac=0; renderTabs(); renderStrip(); draw();
}
document.getElementById('fi').addEventListener('change',e=>{loadFiles(e.target.files,false);e.target.value='';});
document.getElementById('fd').addEventListener('change',e=>{loadFiles(e.target.files,true);e.target.value='';});
// 드래그 이동
let drag=null;
cvs.addEventListener('mousedown',e=>{drag={x:e.clientX,y:e.clientY};});
window.addEventListener('mousemove',e=>{
  if(!drag||!curList().length)return;
  const c=CH[ac],slot=curList()[curAi()],img=slot.img,t=slot.tf;
  const {dw,dh}=fitDisplay(c.w,c.h);
  const cover=Math.max(dw/img.width,dh/img.height),ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  t.cx-=(e.clientX-drag.x)/iw; t.cy-=(e.clientY-drag.y)/ih;
  drag={x:e.clientX,y:e.clientY};
  draw();
});
window.addEventListener('mouseup',()=>drag=null);
// 휠 확대
cvs.addEventListener('wheel',e=>{
  if(!curList().length)return; e.preventDefault();
  const t=curList()[curAi()].tf;
  t.z*=(e.deltaY<0?1.06:0.94);
  t.z=Math.max(1,Math.min(5,t.z));
  draw();
},{passive:false});

function saveAll(){ makeZip(CH); }
function saveOne(){ makeZip([CH[ac]]); }
async function makeZip(chanList){
  if(!anyImgs()){alert('이미지를 먼저 선택하세요.');return;}
  if(!window.JSZip){alert('압축 라이브러리 로딩 중입니다. 잠시 후 다시 시도하세요.');return;}
  const fmt=document.getElementById('fmt').value;
  const zip=new JSZip();
  const pname=(document.getElementById('pname').value||'').trim();
  const root=pname?zip.folder(pname):zip; // 상품명 폴더가 최상위
  const pr=document.getElementById('prog');
  const listFor=c=>{ let l=(gImgs[c.grp]||[]); if(c.one)l=l.slice(0,1); return l; };
  let total=0; chanList.forEach(c=>total+=listFor(c).length);
  let done=0;
  for(const c of chanList){
    const list=listFor(c);
    if(!list.length)continue;
    const folder=root.folder(c.k);
    let n=0;
    for(const o of list){
      n++;
      const img=o.img, t=o.tf;
      const oc=document.createElement('canvas'); oc.width=c.w; oc.height=c.h;
      const g=oc.getContext('2d');
      g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
      g.fillStyle=c.bg; g.fillRect(0,0,c.w,c.h);
      const cover=Math.max(c.w/img.width,c.h/img.height), ds=cover*t.z;
      const iw=img.width*ds, ih=img.height*ds;
      const dx=c.w/2 - t.cx*iw, dy=c.h/2 - t.cy*ih;
      g.drawImage(img,dx,dy,iw,ih);
      const cf=c.png?'png':fmt;  // 크림은 항상 PNG
      const cm=cf==='png'?'image/png':'image/jpeg';
      const blob=await new Promise(res=>oc.toBlob(res,cm,cf==='png'?undefined:1.0));
      const fname=(pname||'thumb')+'_'+n+'.'+cf;
      folder.file(fname,blob);
      done++; pr.textContent='제작 중… '+done+'/'+total;
    }
  }
  pr.textContent='압축 중…';
  const out=await zip.generateAsync({type:'blob'});
  const a=document.createElement('a');
  const suffix=(chanList.length===1)?('_'+chanList[0].k):'';
  a.href=URL.createObjectURL(out); a.download=(pname||'썸네일')+suffix+'.zip'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  pr.textContent='완료! ('+total+'개)';
}
(function(){
  const strip=document.getElementById('strip');
  let raf=null;
  strip.addEventListener('dragover',e=>{
    e.preventDefault(); if(!dragObj)return;
    if(raf)return; // 프레임당 1회만 처리
    const y=e.clientY;
    raf=requestAnimationFrame(()=>{ raf=null;
      const after=getAfterEl(y);
      const beforeObj=after?curList().find(o=>o.el===after):null;
      flipMoveBefore(beforeObj);
    });
  });
  strip.addEventListener('drop',e=>e.preventDefault());
})();
// 방향키로 선택 이미지 순서 이동
document.addEventListener('keydown',e=>{
  if(!curList().length)return;
  const ae=document.activeElement;
  if(ae&&(ae.tagName==='INPUT'||ae.tagName==='SELECT'||ae.tagName==='TEXTAREA'))return;
  if(e.key==='ArrowUp'){e.preventDefault();moveSel(-1);}
  else if(e.key==='ArrowDown'){e.preventDefault();moveSel(1);}
});
renderTabs();
</script></body></html>
"""

# ── Main content ─────────────────────────────────────────────
if "스토리 모듈" in menu:
    components.html(STORY_EDITOR_HTML, height=820, scrolling=False)

elif "썸네일 모듈" in menu:
    components.html(THUMB_HTML, height=880, scrolling=False)

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
