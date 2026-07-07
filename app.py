import streamlit as st
import streamlit.components.v1 as components
import os, io, zipfile
from PIL import Image, ImageOps

st.set_page_config(
    page_title="LAZYZ Dashboard",
    page_icon="⭐️",
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
[data-testid="stSidebar"] label[data-testid="stRadioOption"],
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 10px 16px; border-radius: 8px; cursor: pointer; margin: 0 8px;
}
/* 라디오 동그라미 숨김 (최신 stRadioOption 구조 + 구버전 baseweb 둘 다) */
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > span,
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div > div:first-child,
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] .stRadio label input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] [aria-checked="true"] { background: rgba(255,255,255,0.06); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover,
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
        ["📱  스토리 모듈", "🖼  썸네일 생성기", "📄  상세 생성기"],
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
body{background:#f8f8f8;height:812px;overflow:hidden;color:#222;}
.wrap{display:flex;flex-direction:column;height:812px;padding:16px 20px;gap:12px;}
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
.thumb canvas{width:100%;height:auto;display:block;}
.addtile{display:flex;align-items:center;justify-content:center;height:72px;border:2px dashed #ccc;border-radius:7px;background:#fafafa;cursor:pointer;flex-shrink:0;}
.addtile div{font-size:26px;color:#bbb;line-height:1;}
.addtile:hover{border-color:#ff4b4b;background:#fff8f8;}
.addtile:hover div{color:#ff4b4b;}
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
    <button class="btn btn-dark" onclick="document.getElementById('fd').click()">📂 폴더 선택 (자동명)</button>
    <input id="fd" type="file" accept="image/*" webkitdirectory multiple style="display:none">
    <button class="btn btn-line" onclick="document.getElementById('fi').click()">📁 파일 선택</button>
    <input id="fi" type="file" accept="image/*" multiple style="display:none">
    <button class="btn btn-line" onclick="clearAll()">🗑 비우기</button>
    <input id="pname" placeholder="상품명 (폴더명)" style="padding:8px 10px;border:1.5px solid #ddd;border-radius:8px;font-size:13px;width:170px;">
    <button class="btn btn-line" onclick="saveOne()">↓ 이 채널만</button>
    <button class="btn btn-red" onclick="saveAll()">📥 전체 저장</button>
    <span id="dirlabel" style="font-size:12px;color:#888;cursor:pointer;" onclick="pickDir()"></span>
    <span id="prog"></span>
  </div>
  <div style="font-size:11px;color:#aaa;margin-top:-4px;">이미지 드래그=이동 · 휠=확대/축소 · 화살표=미세조정 · Delete=삭제</div>
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
 {k:'EQL',w:1500,h:2000,bg:'#ffffff',grp:'g_eqlw'},
 {k:'무신사',w:1500,h:1800,bg:'#ffffff',grp:'g_musinsa'},
 {k:'W컨셉',w:960,h:1280,bg:'#ffffff',grp:'g_eqlw'},
 {k:'29CM',w:1000,h:1000,bg:'#EBEBEB',grp:'g_29cm'},
 {k:'공홈',w:1000,h:1400,bg:'#ffffff',grp:'g_home',one:true},
 {k:'컬리',w:550,h:708,bg:'#F9F9F9',grp:'g_kurly',one:true},
 {k:'크림',w:1120,h:1120,bg:'#ffffff',grp:'g_kream',png:true,pngonly:true},
 {k:'조조타운',w:600,h:600,bg:'#ffffff',grp:'g_zozo',pngonly:true},
];
// 그룹(채널)별 독립 이미지 목록 — 삭제/순서/크롭 모두 그룹별로 따로
const GROUPS={}; CH.forEach(c=>{ if(!GROUPS[c.grp])GROUPS[c.grp]={png:false}; if(c.pngonly)GROUPS[c.grp].png=true; });
// 탭 = 그룹 단위 (같은 그룹 채널은 탭 하나로 합침, 저장은 각각)
const TABS=[]; CH.forEach(c=>{ let t=TABS.find(x=>x.grp===c.grp); if(!t){t={grp:c.grp,chans:[]};TABS.push(t);} t.chans.push(c); });
TABS.forEach(t=>{ t.label=t.chans.map(c=>c.k).join('/')+(t.chans.some(c=>c.one)?' · 1장':''); t.rep=t.chans[0]; });
let gImgs={}; let gAi={}; let ac=0;
function curGrp(){return TABS[ac].grp;}
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
// 고품질 축소: 소스 크롭영역을 단계적으로 절반씩 줄여 계단현상 방지
function hqDraw(g,img,sx,sy,sw,sh,dw,dh){
  let cw=Math.max(1,Math.round(sw)), ch=Math.max(1,Math.round(sh));
  let tmp=document.createElement('canvas'); tmp.width=cw; tmp.height=ch;
  let tg=tmp.getContext('2d'); tg.imageSmoothingEnabled=true; tg.imageSmoothingQuality='high';
  tg.drawImage(img,sx,sy,sw,sh,0,0,cw,ch);
  while(cw>dw*2 && ch>dh*2){
    const ncw=Math.max(Math.round(dw),Math.round(cw/2)), nch=Math.max(Math.round(dh),Math.round(ch/2));
    const t2=document.createElement('canvas'); t2.width=ncw; t2.height=nch;
    const g2=t2.getContext('2d'); g2.imageSmoothingEnabled=true; g2.imageSmoothingQuality='high';
    g2.drawImage(tmp,0,0,cw,ch,0,0,ncw,nch);
    tmp=t2; cw=ncw; ch=nch;
  }
  g.drawImage(tmp,0,0,cw,ch,0,0,dw,dh);
}
// 전체 이미지를 dw×dh로 고품질 축소한 캔버스 반환 (누끼 자유배치용)
function hqScaleImg(img,dw,dh){
  dw=Math.max(1,Math.round(dw)); dh=Math.max(1,Math.round(dh));
  let cw=img.width, ch=img.height;
  let tmp=document.createElement('canvas'); tmp.width=cw; tmp.height=ch;
  tmp.getContext('2d').drawImage(img,0,0);
  while(cw>dw*2 && ch>dh*2){
    const ncw=Math.max(dw,Math.round(cw/2)), nch=Math.max(dh,Math.round(ch/2));
    const t2=document.createElement('canvas'); t2.width=ncw; t2.height=nch;
    const g2=t2.getContext('2d'); g2.imageSmoothingEnabled=true; g2.imageSmoothingQuality='high';
    g2.drawImage(tmp,0,0,cw,ch,0,0,ncw,nch); tmp=t2; cw=ncw; ch=nch;
  }
  const out=document.createElement('canvas'); out.width=dw; out.height=dh;
  const g=out.getContext('2d'); g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
  g.drawImage(tmp,0,0,cw,ch,0,0,dw,dh);
  return out;
}
function drawChecker(g,w,h){
  const s=9;
  for(let y=0;y<h;y+=s){ for(let x=0;x<w;x+=s){
    g.fillStyle=(((x/s|0)+(y/s|0))%2)?'#e6e6e6':'#fafafa'; g.fillRect(x,y,s,s);
  }}
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
  const c=TABS[ac].rep, img=list[idx].img, t=list[idx].tf;
  const {dw,dh}=fitDisplay(c.w,c.h);
  const ratio=Math.max(2,window.devicePixelRatio||1); // 고해상도 렌더
  cvs.width=Math.round(dw*ratio); cvs.height=Math.round(dh*ratio);
  cvs.style.width=dw+'px'; cvs.style.height=dh+'px';
  if(cvs.parentElement!==st){st.innerHTML='';st.appendChild(cvs);}
  if(t.z>=1) clampTf(img,dw,dh,t);  // 프레임 덮을 때만 여백 없게, 축소(z<1) 시 자유배치
  const g=cvs.getContext('2d');
  g.setTransform(ratio,0,0,ratio,0,0);
  g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
  if(c.png){ drawChecker(g,dw,dh); } else { g.fillStyle=c.bg; g.fillRect(0,0,dw,dh); }
  const cover=Math.max(dw/img.width,dh/img.height), ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  const dx=dw/2 - t.cx*iw, dy=dh/2 - t.cy*ih;
  g.drawImage(img,dx,dy,iw,ih);
  if(guideV){ g.strokeStyle='rgba(255,75,75,0.85)'; g.lineWidth=1; g.setLineDash([5,4]); g.beginPath(); g.moveTo(dw/2,0); g.lineTo(dw/2,dh); g.stroke(); g.setLineDash([]); }
  document.getElementById('info').textContent=c.k+'  '+c.w+'×'+c.h+' px  ·  확대 '+Math.round(t.z*100)+'%';
  drawThumb(list[idx]); // 조절 중 썸네일도 실시간 반영
}
function renderTabs(){
  const t=document.getElementById('tabs'); t.innerHTML='';
  TABS.forEach((tb,i)=>{const b=document.createElement('button');b.className='tab'+(i===ac?' on':'');b.textContent=tb.label;b.onclick=()=>{ac=i;renderTabs();renderStrip();draw();};t.appendChild(b);});
}
let dragObj=null;
function delImg(o){
  const list=curList(); const idx=list.indexOf(o); if(idx<0)return;
  list.splice(idx,1);
  let a=curAi(); if(a>=list.length)a=Math.max(0,list.length-1); setAi(a);
  renderStrip(); draw();
}
function drawThumb(o){
  const cv=o.canvas; if(!cv)return;
  const c=TABS[ac].rep, t=o.tf, img=o.img;
  const bw=140, ratio=2, ah=bw*c.h/c.w;   // 채널 비율 그대로
  cv.width=Math.round(bw*ratio); cv.height=Math.round(ah*ratio);
  const g=cv.getContext('2d'); g.setTransform(ratio,0,0,ratio,0,0);
  if(c.png){ drawChecker(g,bw,ah); } else { g.fillStyle=c.bg||'#fff'; g.fillRect(0,0,bw,ah); }
  g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
  const cover=Math.max(bw/img.width,ah/img.height), ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  g.drawImage(img, bw/2 - t.cx*iw, ah/2 - t.cy*ih, iw, ih);
}
function makeThumb(o){
  const d=document.createElement('div'); d.className='thumb'; d.draggable=true;
  d.innerHTML='<span class="thnum"></span><canvas></canvas><span class="thdel">×</span>';
  o.canvas=d.querySelector('canvas');
  d.querySelector('canvas').onclick=()=>{setAi(curList().indexOf(o));renderStrip();draw();};
  d.querySelector('.thdel').onclick=(e)=>{e.stopPropagation();delImg(o);};
  d.addEventListener('dragstart',()=>{dragObj=o;setTimeout(()=>d.style.opacity='0.35',0);});
  d.addEventListener('dragend',()=>{dragObj=null;d.style.opacity='1';});
  o.el=d; return d;
}
let addTile=null;
function getAddTile(){
  if(addTile)return addTile;
  const d=document.createElement('div'); d.className='addtile'; d.innerHTML='<div>＋</div>';
  d.onclick=()=>document.getElementById('fi').click();
  addTile=d; return d;
}
function renderStrip(){
  const s=document.getElementById('strip'); const list=curList(); const a=curAi();
  list.forEach((o,i)=>{
    if(!o.el)makeThumb(o);
    o.el.querySelector('.thnum').textContent=(i+1);
    o.el.classList.toggle('on',i===a);
    drawThumb(o);  // 현재 채널 크롭 반영
    s.appendChild(o.el);
  });
  s.appendChild(getAddTile()); // 맨 아래 + 추가 칸
  [...s.children].forEach(ch=>{ if(ch!==addTile && !list.some(o=>o.el===ch)) s.removeChild(ch); });
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
  // 기존 목록에 추가(append)
  Object.keys(GROUPS).forEach(grp=>{
    if(!gImgs[grp]) gImgs[grp]=[];
    if(gAi[grp]==null) gAi[grp]=0;
    const src=GROUPS[grp].png ? pool.filter(p=>/\.png$/i.test(p.name)) : pool.slice();  // 누끼=PNG만, 나머지=전부
    src.forEach(p=>gImgs[grp].push({name:p.name,img:p.img,url:p.url,tf:{z:1,cx:0.5,cy:0.5},el:null}));
  });
  renderTabs(); renderStrip(); draw();
}
function clearAll(){
  gImgs={}; gAi={}; ac=0;
  document.getElementById('strip').innerHTML='';
  renderTabs(); emptyStage('이미지를 선택하세요');
  document.getElementById('prog').textContent='';
}
document.getElementById('fi').addEventListener('change',e=>{loadFiles(e.target.files,false);e.target.value='';});
document.getElementById('fd').addEventListener('change',e=>{loadFiles(e.target.files,true);e.target.value='';});
// 드래그 이동
let drag=null; let guideV=false;
cvs.addEventListener('mousedown',e=>{drag={x:e.clientX,y:e.clientY};});
window.addEventListener('mousemove',e=>{
  if(!drag||!curList().length)return;
  const c=TABS[ac].rep,slot=curList()[curAi()],img=slot.img,t=slot.tf;
  const {dw,dh}=fitDisplay(c.w,c.h);
  const cover=Math.max(dw/img.width,dh/img.height),ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  t.cx-=(e.clientX-drag.x)/iw; t.cy-=(e.clientY-drag.y)/ih;
  const snap=1.5; // 가로중심만 스냅(덜 끈적이게)
  if(Math.abs((t.cx-0.5)*iw)<snap){t.cx=0.5;guideV=true;}else guideV=false;
  drag={x:e.clientX,y:e.clientY};
  draw();
});
window.addEventListener('mouseup',()=>{drag=null;if(guideV){guideV=false;draw();}});
// 휠 확대
cvs.addEventListener('wheel',e=>{
  if(!curList().length)return; e.preventDefault();
  const t=curList()[curAi()].tf;
  t.z*=(e.deltaY<0?1.03:0.97);  // 더 세밀하게
  t.z=Math.max(0.15,Math.min(5,t.z));  // 모든 채널 축소 가능
  draw();
},{passive:false});

// 저장 폴더 기억 (한 번 지정하면 이후 바로 저장)
let savedDir=null;
function updateDirLabel(){
  const el=document.getElementById('dirlabel');
  el.textContent=savedDir?('📁 '+savedDir.name+' (변경)'):'📁 저장폴더 지정';
}
async function ensureDir(){
  if(savedDir){
    try{ let p=await savedDir.queryPermission({mode:'readwrite'});
      if(p!=='granted') p=await savedDir.requestPermission({mode:'readwrite'});
      if(p==='granted') return savedDir; }catch(e){}
    savedDir=null;
  }
  const dir=await window.showDirectoryPicker({mode:'readwrite'});
  savedDir=dir; updateDirLabel(); return dir;
}
async function pickDir(){ try{ savedDir=null; await ensureDir(); }catch(e){} }
function saveAll(){ makeZip(CH); }
function saveOne(){ makeZip(TABS[ac].chans); }
async function makeZip(chanList){
  if(!anyImgs()){alert('이미지를 먼저 선택하세요.');return;}
  if(!window.JSZip){alert('압축 라이브러리 로딩 중입니다. 잠시 후 다시 시도하세요.');return;}
  const fmt='jpg';  // 기본 JPG (크림만 PNG 강제)
  const pname=(document.getElementById('pname').value||'').trim();
  const pr=document.getElementById('prog');
  const listFor=c=>{ let l=(gImgs[c.grp]||[]); if(c.one)l=l.slice(0,1); return l; };
  let total=0; chanList.forEach(c=>total+=listFor(c).length);
  let done=0;
  // 1) 렌더 → 결과 모으기
  const entries=[]; // {chan, name, blob}
  for(const c of chanList){
    const list=listFor(c);
    if(!list.length)continue;
    let n=0;
    for(const o of list){
      n++;
      const img=o.img, t=o.tf;
      const oc=document.createElement('canvas'); oc.width=c.w; oc.height=c.h;
      const g=oc.getContext('2d');
      g.imageSmoothingEnabled=true; g.imageSmoothingQuality='high';
      if(!c.png){ g.fillStyle=c.bg; g.fillRect(0,0,c.w,c.h); }
      const cover=Math.max(c.w/img.width,c.h/img.height), ds=cover*t.z;
      if(t.z<1){
        // 축소: 자유 배치(여백 허용) — 전체 이미지를 배치
        const iw=img.width*ds, ih=img.height*ds;
        const scaled=hqScaleImg(img,iw,ih);
        g.drawImage(scaled, c.w/2 - t.cx*iw, c.h/2 - t.cy*ih);
      } else {
        // 확대/기본: 크롭 영역을 고품질 축소
        const srcW=c.w/ds, srcH=c.h/ds;
        let srcX=t.cx*img.width - srcW/2, srcY=t.cy*img.height - srcH/2;
        srcX=Math.max(0,Math.min(img.width-srcW,srcX));
        srcY=Math.max(0,Math.min(img.height-srcH,srcY));
        hqDraw(g,img,srcX,srcY,srcW,srcH,c.w,c.h);
      }
      const cf=c.png?'png':fmt;
      const cm=cf==='png'?'image/png':'image/jpeg';
      const blob=await new Promise(res=>oc.toBlob(res,cm,cf==='png'?undefined:1.0));
      const base=o.name.replace(/\.[^.]+$/,'');  // 원본 파일명(확장자 제외)
      entries.push({chan:c.k, name:base+'_'+n+'.'+cf, blob});
      done++; pr.textContent='제작 중… '+done+'/'+total;
    }
  }
  if(!entries.length){alert('생성된 이미지가 없어요.');return;}
  // 2) 폴더 선택해서 직접 저장 (지원 시)
  if(window.showDirectoryPicker){
    try{
      let dir=await ensureDir();  // 기억된 폴더 재사용, 없으면 선택
      if(!dir){pr.textContent='취소됨';return;}
      const root=await dir.getDirectoryHandle(pname||'썸네일',{create:true}); // 항상 상위폴더 생성
      let i=0;
      for(const e of entries){
        const cd=await root.getDirectoryHandle(e.chan,{create:true});
        const fh=await cd.getFileHandle(e.name,{create:true});
        const w=await fh.createWritable();
        await w.write(await e.blob.arrayBuffer());
        await w.close();
        i++; pr.textContent='저장 중… '+i+'/'+entries.length;
      }
      pr.textContent='저장 완료! ('+entries.length+'개) → '+(pname||dir.name);
      return;
    }catch(err){
      if(err.name==='AbortError'){pr.textContent='취소됨'; return;}
      // 그 외는 아래 ZIP 다운로드로
    }
  }
  // 3) 폴백: ZIP 다운로드
  pr.textContent='압축 중…';
  const zip=new JSZip(); const rootF=zip.folder(pname||'썸네일');
  entries.forEach(e=>rootF.folder(e.chan).file(e.name,e.blob));
  const out=await zip.generateAsync({type:'blob'});
  const suffix=(chanList.length===1)?('_'+chanList[0].k):'';
  const a=document.createElement('a');
  a.href=URL.createObjectURL(out); a.download=(pname||'썸네일')+suffix+'.zip'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  pr.textContent='완료! ('+entries.length+'개)';
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
function nudgeImg(dx,dy){
  const c=TABS[ac].rep, slot=curList()[curAi()]; if(!slot)return;
  const t=slot.tf, img=slot.img;
  const {dw,dh}=fitDisplay(c.w,c.h);
  const cover=Math.max(dw/img.width,dh/img.height), ds=cover*t.z;
  const iw=img.width*ds, ih=img.height*ds;
  t.cx-=dx/iw; t.cy-=dy/ih;  // 드래그와 동일 방향
  draw();
}
document.addEventListener('keydown',e=>{
  if(!curList().length)return;
  const ae=document.activeElement;
  if(ae&&(ae.tagName==='INPUT'||ae.tagName==='SELECT'||ae.tagName==='TEXTAREA'))return;
  const arrows=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];
  if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();const l=curList();if(l.length)delImg(l[curAi()]);return;}
  if(!arrows.includes(e.key))return;
  e.preventDefault();
  if(e.shiftKey){ // Shift+↑/↓ = 순서 변경
    if(e.key==='ArrowUp')moveSel(-1); else if(e.key==='ArrowDown')moveSel(1);
    return;
  }
  // 화살표 = 이미지 미세조정 (Shift로 10px)
  const step=1;
  const dx=(e.key==='ArrowLeft'?-step:e.key==='ArrowRight'?step:0);
  const dy=(e.key==='ArrowUp'?-step:e.key==='ArrowDown'?step:0);
  nudgeImg(dx,dy);
});
renderTabs();
updateDirLabel();
</script></body></html>
"""

# ── 상세페이지 조합기 (HTML/JS) ───────────────────────────────
# ── 상세페이지 조합기 (HTML/JS) ───────────────────────────────
DETAIL_HTML = r"""
<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Pretendard',-apple-system,sans-serif;}
body{background:#eee;height:812px;overflow:hidden;color:#222;}
.wrap{display:flex;flex-direction:row;height:812px;}
.panel{width:300px;flex-shrink:0;background:#fff;border-left:1px solid #e5e5e5;order:2;padding:22px 20px;display:flex;flex-direction:column;gap:14px;overflow:auto;}
.panel h3{font-size:15px;font-weight:800;color:#111;}
.panel .lbl{font-size:12px;font-weight:700;color:#888;margin-bottom:-6px;}
.btn{padding:11px 15px;border:none;border-radius:9px;font-size:13px;font-weight:700;cursor:pointer;width:100%;}
.btn-dark{background:#111;color:#fff;} .btn-line{background:#fff;border:1.5px solid #ddd;color:#555;} .btn-red{background:#ff4b4b;color:#fff;}
.hint{font-size:11.5px;color:#aaa;line-height:1.7;}
.divider{height:1px;background:#eee;margin:4px 0;}
#prog{font-size:12px;color:#2e9e44;font-weight:700;min-height:16px;}
.stage{flex:1;order:1;overflow:auto;display:flex;justify-content:flex-start;flex-direction:column;align-items:center;padding:24px;}
#page{width:1000px;background:#fff;flex-shrink:0;height:max-content;transform-origin:top center;}
.imgrow{position:relative;display:block;font-size:0;margin-bottom:10px;}
.imgrow canvas{width:100%;display:block;cursor:default;}
.imgrow.cropping{outline:2px solid #ff4b4b;outline-offset:-2px;}
.imgrow.cropping canvas{cursor:grab;}
.imgrow .badge{position:absolute;top:8px;left:8px;background:rgba(0,0,0,0.65);color:#fff;font-size:13px;padding:5px 11px;border-radius:12px;z-index:2;transform-origin:top left;transform:scale(var(--iz,1));font-weight:700;}
.imgrow .del{position:absolute;top:8px;right:8px;background:rgba(0,0,0,0.65);color:#fff;width:30px;height:30px;border-radius:50%;font-size:18px;line-height:30px;text-align:center;cursor:pointer;z-index:2;transform-origin:top right;transform:scale(var(--iz,1));}
.imgrow .del:hover{background:#ff4b4b;}
.imgrow .cropbar{position:absolute;bottom:8px;left:50%;transform:translateX(-50%) scale(var(--iz,1));transform-origin:bottom center;background:#111;color:#fff;font-size:13px;padding:6px 14px;border-radius:20px;z-index:3;display:none;gap:12px;}
.imgrow.cropping .cropbar{display:flex;}
.imgrow .cropbar span{cursor:pointer;}
.sec{padding:56px 70px;}
.sec h2{font-size:22px;font-weight:800;letter-spacing:-0.5px;margin-bottom:22px;}
.sec .k{font-size:15px;line-height:2;color:#333;white-space:pre-wrap;outline:none;}
.sec.center{text-align:center;}
table.size{width:100%;border-collapse:collapse;font-size:14px;}
table.size th,table.size td{border:1px solid #e2e2e2;padding:11px;text-align:center;}
table.size th{background:#f7f7f7;font-weight:700;}
.colorbar{display:flex;justify-content:center;gap:26px;padding:34px 0;}
.colorbar .c{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:13px;color:#555;}
.colorbar .sw{width:34px;height:34px;border-radius:50%;border:1px solid #ddd;}
[contenteditable]:focus{background:#fffef2;}
</style></head><body>
<div class="wrap">
  <div class="stage"><div id="page"></div></div>
  <div class="panel">
    <h3>상세 생성기</h3>
    <div class="lbl">이미지 폴더 나스 경로</div>
    <div style="display:flex;gap:6px;">
      <input id="folderpath" type="text" placeholder="폴더 선택 →" readonly style="flex:1;min-width:0;padding:9px 11px;border:1.5px solid #e2e2e2;border-radius:9px;font-size:11px;color:#555;background:#fafafa;">
      <button class="btn btn-line" style="width:auto;padding:9px 13px;white-space:nowrap;flex-shrink:0;" onclick="document.getElementById('fdir').click()">불러오기</button>
    </div>
    <input id="fdir" type="file" accept="image/*" webkitdirectory multiple style="display:none">
    <div class="lbl">또는 개별 이미지 선택</div>
    <button class="btn btn-dark" onclick="document.getElementById('fi').click()">📁 이미지 선택</button>
    <input id="fi" type="file" accept="image/*" multiple style="display:none">
    <button class="btn btn-line" onclick="clearImgs()">🗑 이미지 비우기</button>
    <div class="divider"></div>
    <div class="lbl">전체 미리보기 확대/축소</div>
    <div style="display:flex;gap:6px;">
      <button class="btn btn-line" style="padding:8px;" onclick="zoomOut()">－</button>
      <button class="btn btn-line" style="padding:8px;" onclick="zoomReset()"><span id="zlabel">100%</span></button>
      <button class="btn btn-line" style="padding:8px;" onclick="zoomIn()">＋</button>
    </div>
    <div class="divider"></div>
    <div class="lbl">상세페이지 생성하기</div>
    <button class="btn btn-red" onclick="save('jpg')">📥 저장하기</button>
    <span id="prog"></span>
  </div>
</div>
<script>
// 시트에서 가져온 제품 정보(수정 가능)
const P={
 name_ko:'슬로우 멜트 케이블 니트', name_en:'Slow Melt Cable Knit',
 desc:'· 넥라인 여유를 활용한 오프숄더 투웨이 연출 가능\n· 도톰하게 짜인 케이블 니트 조직으로 보온성 확보\n· 오버핏 실루엣과 여유로운 소매 기장으로 여리여리한 무드 연출\n· 까슬거림 없는 부드러운 터치감으로 피부 자극 최소화\n· 밑단 자연스러운 롤링 디테일로 내추럴하고 편안한 스타일링 가능\n· 홈웨어는 물론 원마일웨어로도 활용 가능한 디자인',
 sizeItems:['총장','어깨너비','가슴단면','밑단단면','소매길이','암홀','목너비'],
 sizeVals:{'F':['70','50','40','50','40','10','20']},
 model:'MODEL 173cm · FREE 착용',
 care:'· 첫 세탁은 단독 손세탁을 권장합니다.\n· 30℃ 이하 미온수에 중성세제로 가볍게 손세탁하세요.\n· 비틀어 짜지 말고 뉘어서 그늘에 건조하세요.\n· 표백제, 건조기, 드라이클리닝 사용을 피해주세요.\n· 케이블 조직 특성상 날카로운 물체에 올 빠짐이 발생할 수 있어 주의를 권장합니다.',
 refund:'· 상품 수령 후 7일 이내 교환/반품 신청 가능합니다.\n· 단순 변심에 의한 반품 시 왕복 배송비는 고객 부담입니다.\n· 착용 흔적, 오염, 택 제거, 세탁한 상품은 교환/반품이 불가합니다.\n· 색상/사이즈 교환은 재고 상황에 따라 제한될 수 있습니다.',
 maker:'제조사: (주)레이지지  |  제조국: 중국\n혼용률: Acrylic 50% Polyester 35% Rayon 10% Span 5%\n품질보증기준: 관련법 및 소비자분쟁해결규정에 따름'
};
let imgs=[]; let cropRow=null;
const INIT_IMAGES = __INIT_IMAGES__;  // 서버(경로 불러오기)에서 주입
function loadInit(){
  if(!INIT_IMAGES||!INIT_IMAGES.length){ renderPage(); return; }
  let n=INIT_IMAGES.length;
  INIT_IMAGES.forEach(it=>{ const im=new Image();
    im.onload=()=>{ imgs.push({name:it.name,img:im,url:it.src,crop:{z:1,cx:0.5,cy:0.5}}); if(--n===0){sortImgs();renderPage();} };
    im.src=it.src; });
}
function colorRank(n){n=n.toUpperCase(); if(n.includes('WH')||n.includes('화이트'))return 0; if(n.includes('BR')||n.includes('브라운'))return 1; if(n.includes('BK')||n.includes('블랙'))return 2; return 9;}
function grp(n){ if(n.includes('누끼'))return 1; if(/-F-/i.test(n))return 0; return 2; }
function numOf(n){const m=n.match(/(\d+)(?=\.\w+$)/); return m?parseInt(m[1]):0;}
function sortImgs(){ imgs.sort((a,b)=> grp(a.name)-grp(b.name) || colorRank(a.name)-colorRank(b.name) || numOf(a.name)-numOf(b.name) || a.name.localeCompare(b.name)); }
function drawRow(o){
  const cv=o.canvas, img=o.img, t=o.crop;
  const W=1000, H=Math.round(W*img.height/img.width);
  const r=2; cv.width=W*r; cv.height=H*r; cv.style.width='100%';
  const g=cv.getContext('2d'); g.setTransform(r,0,0,r,0,0); g.imageSmoothingQuality='high';
  g.fillStyle='#fff'; g.fillRect(0,0,W,H);
  const ds=t.z; const iw=W*ds, ih=H*ds;
  let dx=W/2-((t.cx)*iw), dy=H/2-((t.cy)*ih);
  // clamp so image covers
  dx=Math.min(0,Math.max(W-iw,dx)); dy=Math.min(0,Math.max(H-ih,dy));
  t.cx=(W/2-dx)/iw; t.cy=(H/2-dy)/ih;
  g.drawImage(img,dx,dy,iw,ih);
}
function renderPage(){
  const pg=document.getElementById('page'); pg.innerHTML='';
  // 컬러 순서 라벨
  // 이미지들
  imgs.forEach((o,i)=>{
    const row=document.createElement('div'); row.className='imgrow';
    const cv=document.createElement('canvas'); o.canvas=cv;
    row.innerHTML='<span class="badge">'+(i+1)+'</span><span class="del">×</span><div class="cropbar"><span onclick="endCrop()">✓ 완료</span><span onclick="resetCrop()">초기화</span></div>';
    row.insertBefore(cv,row.firstChild);
    row.querySelector('.del').onclick=(ev)=>{ev.stopPropagation();const k=imgs.indexOf(o);if(k>=0)imgs.splice(k,1);renderPage();};
    cv.addEventListener('mousedown',e=>{ e.preventDefault(); const md=(cropRow===row?'pan':'pending'); if(md==='pending') startCrop(row,o); pointer={o:o,row:row,sx:e.clientX,sy:e.clientY,lx:e.clientX,ly:e.clientY,moved:false,mode:md}; });
    cv.addEventListener('wheel',e=>{ if(cropRow!==row)return; e.preventDefault(); o.crop.z*=(e.deltaY<0?1.04:0.96); o.crop.z=Math.max(1,Math.min(4,o.crop.z)); drawRow(o); },{passive:false});
    pg.appendChild(row); o.el=row; drawRow(o);
  });
  // 텍스트 섹션들
  pg.insertAdjacentHTML('beforeend', sectionsHTML());
  bindEditable();
  applyZoom();
}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function sizeTable(){
  let th='<th>구분</th>'+P.sizeItems.map(x=>'<th>'+x+'</th>').join('');
  let rows=Object.keys(P.sizeVals).map(sz=>'<tr><td>'+sz+'</td>'+P.sizeVals[sz].map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('');
  return '<table class="size"><tr>'+th+'</tr>'+rows+'</table>';
}
function sectionsHTML(){
  return ''
  +'<div class="sec center"><h2>'+esc(P.name_en)+'</h2><div class="k" data-k="name_ko" contenteditable>'+esc(P.name_ko)+'</div></div>'
  +'<div class="sec"><h2>PRODUCT</h2><div class="k" data-k="desc" contenteditable>'+esc(P.desc)+'</div></div>'
  +'<div class="sec"><h2>SIZE (cm)</h2>'+sizeTable()+'<div class="k" style="font-size:12px;color:#999;margin-top:10px">* 측정 방법에 따라 1~3cm 오차가 있을 수 있습니다.</div></div>'
  +'<div class="sec center"><h2>MODEL</h2><div class="k" data-k="model" contenteditable>'+esc(P.model)+'</div></div>'
  +'<div class="sec"><h2>CARE</h2><div class="k" data-k="care" contenteditable>'+esc(P.care)+'</div></div>'
  +'<div class="sec"><h2>EXCHANGE / REFUND</h2><div class="k" data-k="refund" contenteditable>'+esc(P.refund)+'</div></div>'
  +'<div class="sec"><h2>MADE</h2><div class="k" data-k="maker" contenteditable>'+esc(P.maker)+'</div></div>';
}
function bindEditable(){
  document.querySelectorAll('[data-k]').forEach(el=>{ el.addEventListener('blur',()=>{ P[el.dataset.k]=el.innerText; }); });
}
function startCrop(row,o){ if(cropRow&&cropRow!==row)cropRow.classList.remove('cropping'); cropRow=row; row.classList.add('cropping'); }
function endCrop(){ if(cropRow){cropRow.classList.remove('cropping');cropRow=null;} }
function resetCrop(){ if(!cropRow)return; const o=imgs.find(x=>x.el===cropRow); if(o){o.crop={z:1,cx:0.5,cy:0.5};drawRow(o);} }
// 방향키 = 선택 이미지 미세조정
window.addEventListener('keydown',e=>{
  if(!cropRow) return;
  if(document.activeElement&&document.activeElement.isContentEditable) return;
  const o=imgs.find(x=>x.el===cropRow); if(!o) return;
  const iw=1000*o.crop.z, ih=(1000*o.img.height/o.img.width)*o.crop.z;
  const step=(e.shiftKey?10:2);
  if(e.key==='ArrowLeft'){o.crop.cx-= step/iw;}
  else if(e.key==='ArrowRight'){o.crop.cx+= step/iw;}
  else if(e.key==='ArrowUp'){o.crop.cy-= step/ih;}
  else if(e.key==='ArrowDown'){o.crop.cy+= step/ih;}
  else return;
  e.preventDefault(); drawRow(o);
});
// 전체 미리보기 확대/축소
let pageZoom=0.5;
function applyZoom(){ const pg=document.getElementById('page'); pg.style.transform='scale('+pageZoom+')'; document.documentElement.style.setProperty('--iz',(1/pageZoom).toFixed(3)); const zl=document.getElementById('zlabel'); if(zl) zl.textContent=Math.round(pageZoom*100)+'%'; }
function zoomIn(){ pageZoom=Math.min(2,+(pageZoom+0.1).toFixed(2)); applyZoom(); }
function zoomOut(){ pageZoom=Math.max(0.3,+(pageZoom-0.1).toFixed(2)); applyZoom(); }
function zoomReset(){ pageZoom=1; applyZoom(); }
// 통합 포인터: 클릭=선택 / 미선택 드래그=순서변경(FLIP) / 선택 드래그=위치이동
let pointer=null;
function flipReorder(fromO, toRow){
  const t=imgs.findIndex(o=>o.el===toRow); const f=imgs.indexOf(fromO);
  if(t<0||f<0||t===f) return;
  const first=new Map(); imgs.forEach(o=>{ if(o.el) first.set(o,o.el.getBoundingClientRect().top); });
  const [m]=imgs.splice(f,1); imgs.splice(t,0,m); renderPage();
  imgs.forEach(o=>{ if(!o.el||!first.has(o))return; const dy=(first.get(o)-o.el.getBoundingClientRect().top)/pageZoom;
    if(Math.abs(dy)>0.5){ o.el.style.transition='none'; o.el.style.transform='translateY('+dy+'px)';
      requestAnimationFrame(()=>{ o.el.style.transition='transform .22s cubic-bezier(.2,.7,.3,1)'; o.el.style.transform=''; }); } });
}
window.addEventListener('mousemove',e=>{
  if(!pointer) return;
  const o=pointer.o;
  if(Math.abs(e.clientX-pointer.sx)+Math.abs(e.clientY-pointer.sy)>4) pointer.moved=true;
  if(pointer.mode==='pan'){
    const rect=o.canvas.getBoundingClientRect(), sc=1000/rect.width;
    const iw=1000*o.crop.z, ih=(1000*o.img.height/o.img.width)*o.crop.z;
    o.crop.cx-=((e.clientX-pointer.lx)*sc)/iw; o.crop.cy-=((e.clientY-pointer.ly)*sc)/ih;
    pointer.lx=e.clientX; pointer.ly=e.clientY; drawRow(o); return;
  }
  if(pointer.mode==='pending' && pointer.moved){ pointer.mode='reorder'; endCrop(); pointer.row.style.opacity='0.4'; document.body.style.userSelect='none'; }
  if(pointer.mode==='reorder'){
    const el=document.elementFromPoint(e.clientX,e.clientY); const r=el&&el.closest&&el.closest('.imgrow');
    if(r && r!==pointer.o.el){ flipReorder(pointer.o, r); }
  }
});
window.addEventListener('mouseup',()=>{
  if(!pointer) return;
  // 선택은 이미 mousedown에서 즉시 반영됨. 안 움직이고 '이미 선택된' 이미지를 다시 클릭하면 해제.
  if(!pointer.moved && pointer.mode==='pan'){ endCrop(); }
  if(pointer.o.el) pointer.o.el.style.opacity='';
  document.body.style.userSelect='';
  pointer=null;
});
function addFiles(fileList){
  const files=[...fileList].filter(f=>f.type.startsWith('image/'));
  let n=files.length; if(!n)return;
  files.forEach(f=>{ const url=URL.createObjectURL(f); const im=new Image();
    im.onload=()=>{ imgs.push({name:f.name,img:im,url,crop:{z:1,cx:0.5,cy:0.5}}); if(--n===0){sortImgs();renderPage();} }; im.src=url; });
}
document.getElementById('fi').addEventListener('change',e=>{ addFiles(e.target.files); e.target.value=''; });
document.getElementById('fdir').addEventListener('change',e=>{
  const first=e.target.files[0];
  if(first){ const rel=first.webkitRelativePath||''; const folder=rel.split('/')[0]||''; if(folder) document.getElementById('folderpath').value=folder; }
  addFiles(e.target.files); e.target.value='';
});
function clearImgs(){ imgs=[]; renderPage(); }
// 이미지 바깥 여백 클릭 = 선택 해제(적용)
document.querySelector('.stage').addEventListener('mousedown',e=>{ if(!e.target.closest('.imgrow')) endCrop(); });
// ⌘/Ctrl + 휠 = 전체 확대/축소
document.querySelector('.stage').addEventListener('wheel',e=>{
  if(e.ctrlKey||e.metaKey){ e.preventDefault(); pageZoom=Math.max(0.3,Math.min(2,+(pageZoom+(e.deltaY<0?0.06:-0.06)).toFixed(2))); applyZoom(); }
},{passive:false});
async function save(fmt){
  endCrop();
  const pg=document.getElementById('page');
  const oz=pg.style.transform; pg.style.transform='none';   // 저장 시 실제 크기로
  document.getElementById('prog').textContent='저장 중…';
  const canvas=await html2canvas(pg,{scale:2,backgroundColor:'#ffffff',useCORS:true});
  pg.style.transform=oz;
  const mime=fmt==='png'?'image/png':'image/jpeg';
  const blob=await new Promise(res=>canvas.toBlob(res,mime,fmt==='png'?undefined:0.95));
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=(P.name_en||'상세페이지')+'.'+fmt; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),1500);
  document.getElementById('prog').textContent='완료!';
}
loadInit();
</script></body></html>
"""

# ── Main content ─────────────────────────────────────────────
if "스토리 모듈" in menu:
    components.html(STORY_EDITOR_HTML, height=820, scrolling=False)

elif "썸네일 생성기" in menu:
    components.html(THUMB_HTML, height=820, scrolling=False)

elif "상세 생성기" in menu:
    components.html(DETAIL_HTML.replace("__INIT_IMAGES__", "[]"), height=820, scrolling=False)

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
