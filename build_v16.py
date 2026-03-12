#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 v15 的 canvas 替换为 HTML 闯关地图，生成 v16
"""
import re

with open('/home/ubuntu/mathkg/五年级数学知识图谱_v15.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ─────────────────────────────────────────────
# 1. 修改标题
# ─────────────────────────────────────────────
src = src.replace(
    '五年级数学知识图谱 v15 · 竹子学校',
    '五年级数学知识图谱 v16 · 竹子学校'
)

# ─────────────────────────────────────────────
# 2. 替换 canvas-wrap 样式 → map-wrap 样式
# ─────────────────────────────────────────────
old_canvas_css = """/* ───── 画布区域 ───── */
#canvas-wrap{position:fixed;left:280px;top:60px;right:260px;bottom:0;overflow:hidden;background:#1a1d2e;cursor:grab;}
#canvas-wrap:active{cursor:grabbing;}
canvas{display:block;}"""

new_map_css = """/* ───── 地图区域 ───── */
#map-wrap{position:fixed;left:280px;top:60px;right:260px;bottom:0;overflow-y:auto;overflow-x:hidden;background:#87CEEB;}
#map-wrap::-webkit-scrollbar{width:6px;}
#map-wrap::-webkit-scrollbar-thumb{background:rgba(0,0,0,0.2);border-radius:3px;}
#map-canvas{position:relative;width:100%;min-height:100%;}

/* 背景层 */
.map-bg{position:absolute;inset:0;pointer-events:none;}

/* 轨道 SVG */
.track-svg{position:absolute;top:0;left:0;width:100%;pointer-events:none;}

/* 知识点节点 */
.knode{
  position:absolute;
  width:90px;height:90px;
  border-radius:50%;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  cursor:pointer;
  transition:transform .15s, box-shadow .15s;
  user-select:none;
  z-index:10;
  transform:translate(-50%,-50%);
}
.knode:hover{transform:translate(-50%,-50%) scale(1.08);}
.knode.unmastered{
  background:#ffffff;
  border:4px solid #ccc;
  box-shadow:0 4px 12px rgba(0,0,0,0.18);
  color:#333;
}
.knode.mastered{
  background:#27ae60;
  border:4px solid #2ecc71;
  box-shadow:0 4px 18px rgba(46,204,113,0.5);
  color:#fff;
}
.knode-num{
  font-size:0.65rem;font-weight:700;
  position:absolute;top:6px;
  width:22px;height:22px;
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  line-height:1;
}
.knode.unmastered .knode-num{background:#e0e0e0;color:#555;}
.knode.mastered   .knode-num{background:rgba(255,255,255,0.3);color:#fff;}
.knode-name{
  font-size:0.72rem;font-weight:600;
  text-align:center;line-height:1.25;
  padding:0 6px;margin-top:16px;
  word-break:break-all;
}
.knode-id{
  font-size:0.58rem;margin-top:2px;
  opacity:0.6;
}

/* 节点序号徽章（右上角） */
.knode-badge{
  position:absolute;top:-6px;left:-6px;
  width:26px;height:26px;
  border-radius:50%;
  font-size:0.7rem;font-weight:700;
  display:flex;align-items:center;justify-content:center;
  border:2px solid #fff;
  z-index:11;
}

/* tooltip */
#tooltip{position:fixed;background:rgba(12,15,36,0.97);border:1px solid #4a5070;border-radius:8px;padding:9px 12px;font-size:0.76rem;pointer-events:none;display:none;max-width:240px;z-index:600;box-shadow:0 4px 20px rgba(0,0,0,0.7);}"""

src = src.replace(old_canvas_css, new_map_css)

# ─────────────────────────────────────────────
# 3. 替换 HTML 中的 canvas-wrap → map-wrap
# ─────────────────────────────────────────────
src = src.replace(
    '<!-- ═══════════ 画布 ═══════════ -->\n<div id="canvas-wrap"><canvas id="c"></canvas></div>',
    '<!-- ═══════════ 闯关地图 ═══════════ -->\n<div id="map-wrap"><div id="map-canvas"></div></div>'
)

# ─────────────────────────────────────────────
# 4. 删除 canvas 物理引擎相关变量和函数
#    （从 "⑤ 画布 & 物理引擎" 到 "⑥ 命中检测 & 事件" 结束）
# ─────────────────────────────────────────────
# 找到要删除的代码段
canvas_engine_start = """// ================================================================
// ⑤ 画布 & 物理引擎
// ================================================================
let canvas, ctx, W, H;"""

canvas_engine_end = """// ================================================================
// ⑦ Tooltip
// ================================================================"""

# 找到 initEvents 函数结束位置，删除从引擎开始到 initEvents 结束
idx_start = src.find(canvas_engine_start)
idx_end = src.find(canvas_engine_end)

if idx_start >= 0 and idx_end >= 0:
    # 保留 tooltip 部分
    src = src[:idx_start] + src[idx_end:]
    print("✅ 删除了 canvas 物理引擎代码")
else:
    print(f"⚠️ 未找到引擎代码段: start={idx_start}, end={idx_end}")

# ─────────────────────────────────────────────
# 5. 替换 ⑭ 画布初始化 和 ⑮ 启动 中的 canvas 相关代码
# ─────────────────────────────────────────────
old_canvas_init = """// ================================================================
// ⑭ 画布初始化
// ================================================================
function resizeCanvas(){
  const wrap = document.getElementById('canvas-wrap');
  W = wrap.clientWidth;
  H = wrap.clientHeight;
  if(W<=0) W = window.innerWidth-540;
  if(H<=0) H = window.innerHeight-60;
  canvas.width  = W;
  canvas.height = H;
}

function initCamera(){
  const scaleX = W/VIRT_W;
  const scaleY = H/VIRT_H;
  camScale = Math.min(scaleX,scaleY)*0.88;
  const vw = VIRT_W*camScale;
  const vh = VIRT_H*camScale;
  camX = (W-vw)/2/camScale;
  camY = (H-vh)/2/camScale;
}"""

new_canvas_init = """// ================================================================
// ⑭ 地图渲染
// ================================================================
// 上册知识点顺序（按参考图从下到上、蛇形排列）
// 图中上册共29个知识点（K01-K29），蛇形每行4个，从下往上
// 下册共29个知识点（K36-K64），蛇形每行4个，从下往上
// 注意：NODES中上册是K01-K35（35个），下册是K36-K64（29个）
// 参考图中上册显示K1-K29（29个），下册K36-K64（29个）
// 这里按NODES实际数据排列

function getBookNodes(book){
  if(book==='all') return NODES;
  return NODES.filter(n=>{ const u=UNITS.find(u=>u.id===n.unit); return u&&u.book===book; });
}

// 根据节点序号生成蛇形位置
// 每行4个，从下往上，奇数行从左到右，偶数行从右到左
function snakeLayout(nodes, colW, rowH, padX, padY, totalH){
  const COLS = 4;
  const positions = [];
  const n = nodes.length;
  for(let i=0;i<n;i++){
    const row = Math.floor(i/COLS);
    const col = i % COLS;
    const isEvenRow = row % 2 === 0;
    const actualCol = isEvenRow ? col : (COLS-1-col);
    const x = padX + actualCol * colW + colW/2;
    const y = totalH - padY - row * rowH - rowH/2;
    positions.push({x, y, node: nodes[i]});
  }
  return positions;
}

function renderMap(){
  const wrap = document.getElementById('map-wrap');
  const mc = document.getElementById('map-canvas');
  const wrapW = wrap.clientWidth || (window.innerWidth - 540);

  // 确定要显示的节点
  let upperNodes, lowerNodes;
  if(curBookFilter==='上册'){
    upperNodes = getBookNodes('上册');
    lowerNodes = [];
  } else if(curBookFilter==='下册'){
    upperNodes = [];
    lowerNodes = getBookNodes('下册');
  } else {
    upperNodes = getBookNodes('上册');
    lowerNodes = getBookNodes('下册');
  }

  const COLS = 4;
  const COL_W = Math.max(120, (wrapW - 40) / COLS);
  const ROW_H = 130;
  const PAD_X = (wrapW - COL_W * COLS) / 2;
  const PAD_Y = 60;
  const SECTION_GAP = 80; // 上下册之间的间距

  // 计算各册高度
  const upperRows = Math.ceil(upperNodes.length / COLS);
  const lowerRows = Math.ceil(lowerNodes.length / COLS);
  const upperH = upperRows > 0 ? upperRows * ROW_H + PAD_Y * 2 : 0;
  const lowerH = lowerRows > 0 ? lowerRows * ROW_H + PAD_Y * 2 : 0;
  const totalH = upperH + lowerH + (upperH>0&&lowerH>0 ? SECTION_GAP : 0);
  const minH = Math.max(totalH, wrap.clientHeight || window.innerHeight - 60);

  mc.style.height = minH + 'px';
  mc.innerHTML = '';

  // ── 背景 SVG（天空+草地+山脉）──
  const bgSvg = createBackgroundSVG(wrapW, minH, curBookFilter);
  mc.appendChild(bgSvg);

  // ── 下册（在上方显示，因为全册时下册接在上册之上）──
  let lowerOffsetY = 0;
  if(lowerNodes.length > 0){
    const lowerPositions = snakeLayout(lowerNodes, COL_W, ROW_H, PAD_X, PAD_Y, lowerH);
    // 绘制蓝色轨道
    const trackSvg = createTrackSVG(lowerPositions, wrapW, lowerH, '#1565C0', '#42A5F5', 0);
    mc.appendChild(trackSvg);
    // 绘制节点
    lowerPositions.forEach(pos=>{
      const el = createNodeEl(pos.node, pos.x, pos.y + lowerOffsetY);
      mc.appendChild(el);
    });
  }

  // ── 上册（在下方显示）──
  const upperOffsetY = lowerH + (lowerH>0&&upperH>0 ? SECTION_GAP : 0);
  if(upperNodes.length > 0){
    const upperPositions = snakeLayout(upperNodes, COL_W, ROW_H, PAD_X, PAD_Y, upperH);
    // 绘制黄色轨道
    const trackSvg = createTrackSVG(upperPositions, wrapW, upperH, '#F57F17', '#FFD54F', upperOffsetY);
    mc.appendChild(trackSvg);
    // 绘制节点
    upperPositions.forEach(pos=>{
      const el = createNodeEl(pos.node, pos.x, pos.y + upperOffsetY);
      mc.appendChild(el);
    });
  }
}

function createBackgroundSVG(w, h, book){
  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('width', w);
  svg.setAttribute('height', h);
  svg.style.cssText = 'position:absolute;top:0;left:0;pointer-events:none;z-index:0;';

  // 天空渐变
  const defs = document.createElementNS('http://www.w3.org/2000/svg','defs');
  const skyGrad = document.createElementNS('http://www.w3.org/2000/svg','linearGradient');
  skyGrad.id = 'skyGrad';
  skyGrad.setAttribute('x1','0');skyGrad.setAttribute('y1','0');
  skyGrad.setAttribute('x2','0');skyGrad.setAttribute('y2','1');
  const s1 = document.createElementNS('http://www.w3.org/2000/svg','stop');
  s1.setAttribute('offset','0%');s1.setAttribute('stop-color','#87CEEB');
  const s2 = document.createElementNS('http://www.w3.org/2000/svg','stop');
  s2.setAttribute('offset','60%');s2.setAttribute('stop-color','#B0E0FF');
  const s3 = document.createElementNS('http://www.w3.org/2000/svg','stop');
  s3.setAttribute('offset','100%');s3.setAttribute('stop-color','#90EE90');
  skyGrad.appendChild(s1);skyGrad.appendChild(s2);skyGrad.appendChild(s3);
  defs.appendChild(skyGrad);
  svg.appendChild(defs);

  // 背景矩形
  const bg = document.createElementNS('http://www.w3.org/2000/svg','rect');
  bg.setAttribute('width',w);bg.setAttribute('height',h);
  bg.setAttribute('fill','url(#skyGrad)');
  svg.appendChild(bg);

  // 云朵（随机分布）
  const clouds = [
    {x:w*0.1, y:h*0.05, r:30},
    {x:w*0.35, y:h*0.08, r:25},
    {x:w*0.6, y:h*0.04, r:35},
    {x:w*0.82, y:h*0.07, r:28},
    {x:w*0.2, y:h*0.25, r:22},
    {x:w*0.7, y:h*0.22, r:30},
    {x:w*0.5, y:h*0.45, r:25},
    {x:w*0.15, y:h*0.55, r:20},
    {x:w*0.85, y:h*0.5, r:28},
  ];
  clouds.forEach(c=>{
    const g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.setAttribute('opacity','0.8');
    [
      {dx:0,dy:0,r:c.r},
      {dx:-c.r*0.6,dy:c.r*0.2,r:c.r*0.7},
      {dx:c.r*0.6,dy:c.r*0.2,r:c.r*0.7},
      {dx:-c.r*1.1,dy:c.r*0.5,r:c.r*0.5},
      {dx:c.r*1.1,dy:c.r*0.5,r:c.r*0.5},
    ].forEach(({dx,dy,r})=>{
      const circle = document.createElementNS('http://www.w3.org/2000/svg','circle');
      circle.setAttribute('cx', c.x+dx);
      circle.setAttribute('cy', c.y+dy);
      circle.setAttribute('r', r);
      circle.setAttribute('fill','white');
      g.appendChild(circle);
    });
    svg.appendChild(g);
  });

  // 山脉（绿色）
  const mountainY = h * 0.75;
  const mPath = document.createElementNS('http://www.w3.org/2000/svg','path');
  const mPoints = [];
  mPoints.push(`M 0 ${h}`);
  mPoints.push(`L 0 ${mountainY}`);
  // 生成锯齿山脉
  const mCount = Math.ceil(w/120)+1;
  for(let i=0;i<=mCount;i++){
    const mx = i * (w/mCount);
    const my = mountainY - (i%2===0 ? 80 : 30) - Math.sin(i*1.3)*20;
    mPoints.push(`L ${mx} ${my}`);
  }
  mPoints.push(`L ${w} ${h}`);
  mPoints.push('Z');
  mPath.setAttribute('d', mPoints.join(' '));
  mPath.setAttribute('fill','#4CAF50');
  mPath.setAttribute('opacity','0.6');
  svg.appendChild(mPath);

  // 草地
  const grassPath = document.createElementNS('http://www.w3.org/2000/svg','path');
  const gPoints = [];
  gPoints.push(`M 0 ${h}`);
  gPoints.push(`L 0 ${h*0.88}`);
  const gCount = Math.ceil(w/60)+1;
  for(let i=0;i<=gCount;i++){
    const gx = i*(w/gCount);
    const gy = h*0.88 + Math.sin(i*0.8)*8;
    gPoints.push(`L ${gx} ${gy}`);
  }
  gPoints.push(`L ${w} ${h}`);
  gPoints.push('Z');
  grassPath.setAttribute('d', gPoints.join(' '));
  grassPath.setAttribute('fill','#66BB6A');
  svg.appendChild(grassPath);

  // 树木（简单三角形）
  const trees = [
    {x:w*0.05, y:h*0.82},
    {x:w*0.25, y:h*0.80},
    {x:w*0.45, y:h*0.83},
    {x:w*0.65, y:h*0.81},
    {x:w*0.85, y:h*0.82},
    {x:w*0.95, y:h*0.80},
  ];
  trees.forEach(t=>{
    const tg = document.createElementNS('http://www.w3.org/2000/svg','g');
    // 树干
    const trunk = document.createElementNS('http://www.w3.org/2000/svg','rect');
    trunk.setAttribute('x', t.x-4);trunk.setAttribute('y', t.y);
    trunk.setAttribute('width', 8);trunk.setAttribute('height', 20);
    trunk.setAttribute('fill','#795548');
    tg.appendChild(trunk);
    // 树冠（三层）
    [[0,20,30],[0,10,22],[0,0,16]].forEach(([dy,w2,h2])=>{
      const tri = document.createElementNS('http://www.w3.org/2000/svg','polygon');
      const tx = t.x, ty = t.y - dy;
      tri.setAttribute('points', `${tx},${ty-h2} ${tx-w2},${ty} ${tx+w2},${ty}`);
      tri.setAttribute('fill','#2E7D32');
      tg.appendChild(tri);
    });
    svg.appendChild(tg);
  });

  // 彩虹（左上角装饰）
  const rainbowColors = ['#FF0000','#FF7F00','#FFFF00','#00FF00','#0000FF','#8B00FF'];
  rainbowColors.forEach((color, i)=>{
    const arc = document.createElementNS('http://www.w3.org/2000/svg','path');
    const r = 80 + i*15;
    arc.setAttribute('d', `M ${w*0.05} ${h*0.15} A ${r} ${r} 0 0 1 ${w*0.05+r*2} ${h*0.15}`);
    arc.setAttribute('fill','none');
    arc.setAttribute('stroke', color);
    arc.setAttribute('stroke-width','6');
    arc.setAttribute('opacity','0.4');
    svg.appendChild(arc);
  });

  return svg;
}

function createTrackSVG(positions, w, sectionH, trackColor, trackHighlight, offsetY){
  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('width', w);
  svg.setAttribute('height', sectionH);
  svg.style.cssText = `position:absolute;top:${offsetY}px;left:0;pointer-events:none;z-index:1;`;

  if(positions.length < 2) return svg;

  // 绘制轨道（连接相邻节点的路径）
  for(let i=0;i<positions.length-1;i++){
    const a = positions[i], b = positions[i+1];
    const ax=a.x, ay=a.y, bx=b.x, by=b.y;

    // 判断是否是行末转折（同一行最后一个到下一行第一个）
    const COLS = 4;
    const rowA = Math.floor(i/COLS);
    const rowB = Math.floor((i+1)/COLS);
    const isRowEnd = rowA !== rowB;

    // 轨道主体（黄色/蓝色宽条）
    const trackPath = document.createElementNS('http://www.w3.org/2000/svg','path');
    let d;
    if(isRowEnd){
      // 行末：用弯曲路径连接
      const midX = (ax+bx)/2;
      const midY = (ay+by)/2;
      // 弯曲方向：根据行号决定弯向左还是右
      const isEvenRow = rowA % 2 === 0;
      const curveDx = isEvenRow ? -80 : 80;
      d = `M ${ax} ${ay} C ${ax+curveDx} ${ay}, ${bx+curveDx} ${by}, ${bx} ${by}`;
    } else {
      // 同行：直线
      d = `M ${ax} ${ay} L ${bx} ${by}`;
    }

    // 轨道外框（深色）
    const trackBg = document.createElementNS('http://www.w3.org/2000/svg','path');
    trackBg.setAttribute('d', d);
    trackBg.setAttribute('stroke', trackColor);
    trackBg.setAttribute('stroke-width', '36');
    trackBg.setAttribute('fill', 'none');
    trackBg.setAttribute('stroke-linecap', 'round');
    svg.appendChild(trackBg);

    // 轨道内部（亮色）
    const trackInner = document.createElementNS('http://www.w3.org/2000/svg','path');
    trackInner.setAttribute('d', d);
    trackInner.setAttribute('stroke', trackHighlight);
    trackInner.setAttribute('stroke-width', '24');
    trackInner.setAttribute('fill', 'none');
    trackInner.setAttribute('stroke-linecap', 'round');
    svg.appendChild(trackInner);

    // 轨道横纹（铁路枕木效果）
    if(!isRowEnd){
      const dx = bx-ax, dy = by-ay;
      const len = Math.sqrt(dx*dx+dy*dy);
      const steps = Math.max(2, Math.floor(len/30));
      for(let s=1;s<steps;s++){
        const t = s/steps;
        const px = ax + dx*t, py = ay + dy*t;
        const nx = -dy/len*14, ny = dx/len*14;
        const tie = document.createElementNS('http://www.w3.org/2000/svg','line');
        tie.setAttribute('x1', px+nx); tie.setAttribute('y1', py+ny);
        tie.setAttribute('x2', px-nx); tie.setAttribute('y2', py-ny);
        tie.setAttribute('stroke', '#8B4513');
        tie.setAttribute('stroke-width', '5');
        svg.appendChild(tie);
      }
    }
  }

  return svg;
}

function createNodeEl(node, x, y){
  const mastered = isMastered(node.id);
  const u = UNITS.find(u=>u.id===node.unit);
  const nodeNum = parseInt(node.id.replace('K',''));

  const div = document.createElement('div');
  div.className = 'knode ' + (mastered ? 'mastered' : 'unmastered');
  div.style.left = x + 'px';
  div.style.top  = y + 'px';
  div.id = 'knode-' + node.id;
  div.title = node.name + ' — ' + node.desc;

  // 徽章（节点序号）
  const badge = document.createElement('div');
  badge.className = 'knode-badge';
  badge.textContent = nodeNum;
  badge.style.background = mastered ? 'rgba(255,255,255,0.3)' : (u?.color || '#888');
  badge.style.color = mastered ? '#fff' : '#fff';
  div.appendChild(badge);

  // 名称
  const nameEl = document.createElement('div');
  nameEl.className = 'knode-name';
  nameEl.textContent = node.name;
  div.appendChild(nameEl);

  // ID
  const idEl = document.createElement('div');
  idEl.className = 'knode-id';
  idEl.textContent = node.id;
  div.appendChild(idEl);

  // 点击事件
  div.addEventListener('click', ()=>{ toggleMastery(node.id); renderMap(); });
  // hover tooltip
  div.addEventListener('mouseenter', e=>{ showTooltipForNode(e, node); });
  div.addEventListener('mouseleave', ()=>{ hideTooltip(); });

  return div;
}

function showTooltipForNode(e, n){
  const u = UNITS.find(u=>u.id===n.unit);
  document.getElementById('tt-title').textContent = n.name;
  document.getElementById('tt-id').textContent = n.id;
  document.getElementById('tt-unit').textContent = (u ? u.book+' · '+u.name : '');
  document.getElementById('tt-desc').textContent = n.desc;
  const st = document.getElementById('tt-st');
  if(isMastered(n.id)){ st.textContent='✅ 已掌握 — 再次点击取消'; st.className='st-ok'; }
  else { st.textContent='⚪ 点击标记为已掌握'; st.className='st-no'; }
  const tip = document.getElementById('tooltip');
  tip.style.display='block';
  let x=e.clientX+16, y=e.clientY-12;
  if(x+250>window.innerWidth) x=e.clientX-266;
  if(y+140>window.innerHeight) y=e.clientY-154;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}"""

src = src.replace(old_canvas_init, new_canvas_init)

# ─────────────────────────────────────────────
# 6. 替换 ⑮ 启动 中的 canvas 初始化代码
# ─────────────────────────────────────────────
old_startup = """window.addEventListener('DOMContentLoaded', async ()=>{
  // 初始化画布
  canvas = document.getElementById('c');
  ctx = canvas.getContext('2d');
  // 先用缓存快速渲染一次（避免白屏）
  try{
    const rawCls = localStorage.getItem(LS_CLASSES);
    if(rawCls) CLASSES = JSON.parse(rawCls);
    const rawCur = localStorage.getItem(LS_CUR_CLASS);
    if(rawCur && CLASSES.find(c=>c.id===rawCur)) curClassId = rawCur;
    else if(CLASSES.length) curClassId = CLASSES[0].id;
    if(curClassId){
      const rawGrp = localStorage.getItem(lsKeyGrp(curClassId));
      if(rawGrp) GROUPS = JSON.parse(rawGrp);
      const rawData = localStorage.getItem(lsKeyData(curClassId));
      if(rawData){ const p=JSON.parse(rawData); for(const k in p) masteredMap[k]=new Set((p[k]||[]).filter(x=>x!=='__none__')); }
    }
  }catch(e){}
  // 快速渲染页面
  buildStudentPanel();
  resizeCanvas();
  initCamera();
  initNodes();
  initEvents();
  updateStats();
  updateDetail();
  loop();
  const firstStu = GROUPS[0]?.members[0];
  curStudent = firstStu || '';
  if(firstStu) selectStudent(firstStu);
  updateClassSelect();
  updateAllStudentProgress();
  // 异步从 Firebase 加载最新数据
  await initApp();
  // Firebase 数据加载完成后刷新页面
  buildStudentPanel();
  const newFirstStu = GROUPS[0]?.members[0];
  curStudent = newFirstStu || '';
  if(newFirstStu) selectStudent(newFirstStu);
  updateClassSelect();
  updateAllStudentProgress();
  updateStats();
  updateDetail();
  console.log('[App] Firebase 数据加载完成');
});

window.addEventListener('resize',()=>{
  resizeCanvas();
  initCamera();
});"""

new_startup = """window.addEventListener('DOMContentLoaded', async ()=>{
  // 先用缓存快速渲染一次（避免白屏）
  try{
    const rawCls = localStorage.getItem(LS_CLASSES);
    if(rawCls) CLASSES = JSON.parse(rawCls);
    const rawCur = localStorage.getItem(LS_CUR_CLASS);
    if(rawCur && CLASSES.find(c=>c.id===rawCur)) curClassId = rawCur;
    else if(CLASSES.length) curClassId = CLASSES[0].id;
    if(curClassId){
      const rawGrp = localStorage.getItem(lsKeyGrp(curClassId));
      if(rawGrp) GROUPS = JSON.parse(rawGrp);
      const rawData = localStorage.getItem(lsKeyData(curClassId));
      if(rawData){ const p=JSON.parse(rawData); for(const k in p) masteredMap[k]=new Set((p[k]||[]).filter(x=>x!=='__none__')); }
    }
  }catch(e){}
  // 快速渲染页面
  buildStudentPanel();
  initMapEvents();
  renderMap();
  updateStats();
  updateDetail();
  const firstStu = GROUPS[0]?.members[0];
  curStudent = firstStu || '';
  if(firstStu) selectStudent(firstStu);
  updateClassSelect();
  updateAllStudentProgress();
  // 异步从 Firebase 加载最新数据
  await initApp();
  // Firebase 数据加载完成后刷新页面
  buildStudentPanel();
  const newFirstStu = GROUPS[0]?.members[0];
  curStudent = newFirstStu || '';
  if(newFirstStu) selectStudent(newFirstStu);
  updateClassSelect();
  updateAllStudentProgress();
  updateStats();
  updateDetail();
  renderMap();
  console.log('[App] Firebase 数据加载完成');
});

window.addEventListener('resize', ()=>{ renderMap(); });

function initMapEvents(){
  // 书册切换事件
  document.querySelectorAll('.book-tab').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.querySelectorAll('.book-tab').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      curBookFilter = btn.dataset.book;
      updateStats();
      updateDetail();
      updateAllStudentProgress();  // 同步左侧进度百分比
      renderMap();
    });
  });

  document.addEventListener('click', e=>{
    if(!e.target.closest('#move-menu') && !e.target.closest('.move-btn')){
      closeMoveMenu();
    }
  });

  document.addEventListener('keydown', e=>{
    if(e.key==='Escape'){
      closeAddStuModal();
      closeAddGrpModal();
      closeModal();
    }
    if(e.key==='Enter'){
      if(document.getElementById('add-stu-modal').style.display!=='none' &&
         document.activeElement===document.getElementById('new-stu-name')){
        confirmAddStudent();
      }
      if(document.getElementById('add-grp-modal').style.display!=='none' &&
         document.activeElement===document.getElementById('new-grp-name')){
        confirmAddGroup();
      }
    }
  });
}"""

src = src.replace(old_startup, new_startup)

# ─────────────────────────────────────────────
# 7. 修改 getStudentMasteryPct 以支持书册过滤
# ─────────────────────────────────────────────
old_pct = """function getStudentMasteryPct(name){
  const s = masteredMap[name];
  if(!s||!s.size) return 0;
  // 过滤占位符
  const realCount = [...s].filter(x=>x!=='__none__').length;
  return Math.round(realCount/NODES.length*100);
}"""

new_pct = """function getStudentMasteryPct(name){
  const s = masteredMap[name];
  // 根据当前书册过滤器计算进度
  const visNodes = filteredNodes();
  if(!visNodes.length) return 0;
  if(!s||!s.size) return 0;
  const realIds = [...s].filter(x=>x!=='__none__');
  const visIds = new Set(visNodes.map(n=>n.id));
  const masteredCount = realIds.filter(id=>visIds.has(id)).length;
  return Math.round(masteredCount/visNodes.length*100);
}"""

src = src.replace(old_pct, new_pct)

# ─────────────────────────────────────────────
# 8. 修改 toggleMastery 以在修改后重新渲染地图
# ─────────────────────────────────────────────
old_toggle = """  updateStats();
  updateDetail();
  updateStudentRowProgress(curStudent);
  // 同步左侧进度条显示
  const barEl2 = document.getElementById('stu-bar-'+encodeURI(curStudent));
  const pctEl2 = document.getElementById('stu-pct-'+encodeURI(curStudent));
  const pct2 = getStudentMasteryPct(curStudent);
  if(barEl2) barEl2.style.width = pct2+'%';
  if(pctEl2) pctEl2.textContent = pct2+'%';
  if(hoveredNode===id){
    const st = document.getElementById('tt-st');
    if(isMastered(id)){ st.textContent='✅ 已掌握 — 再次点击取消'; st.className='st-ok'; }
    else { st.textContent='⚪ 点击节点标记为已掌握'; st.className='st-no'; }
  }
}"""

new_toggle = """  updateStats();
  updateDetail();
  updateStudentRowProgress(curStudent);
  updateAllStudentProgress();
  // 更新单个节点样式（无需全量重渲染）
  const nodeEl = document.getElementById('knode-' + id);
  if(nodeEl){
    const nowMastered = isMastered(id);
    nodeEl.className = 'knode ' + (nowMastered ? 'mastered' : 'unmastered');
    const badge = nodeEl.querySelector('.knode-badge');
    const u2 = UNITS.find(u=>u.id===(NODES.find(n=>n.id===id)?.unit));
    if(badge) badge.style.background = nowMastered ? 'rgba(255,255,255,0.3)' : (u2?.color||'#888');
    // 更新 tooltip
    const st = document.getElementById('tt-st');
    if(st){
      if(nowMastered){ st.textContent='✅ 已掌握 — 再次点击取消'; st.className='st-ok'; }
      else { st.textContent='⚪ 点击标记为已掌握'; st.className='st-no'; }
    }
  }
}"""

src = src.replace(old_toggle, new_toggle)

# ─────────────────────────────────────────────
# 9. 删除旧的 book-tab 事件绑定（在 initEvents 中）
#    因为已经在 initMapEvents 中重新绑定
# ─────────────────────────────────────────────
old_book_tab = """  document.querySelectorAll('.book-tab').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.querySelectorAll('.book-tab').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      curBookFilter = btn.dataset.book;
      updateStats();
      updateDetail();
    });
  });

  document.addEventListener('click', e=>{
    if(!e.target.closest('#move-menu') && !e.target.closest('.move-btn')){
      closeMoveMenu();
    }
  });

  document.addEventListener('keydown', e=>{
    if(e.key==='Escape'){
      closeAddStuModal();
      closeAddGrpModal();
      closeModal();
    }
    if(e.key==='Enter'){
      if(document.getElementById('add-stu-modal').style.display!=='none' &&
         document.activeElement===document.getElementById('new-stu-name')){
        confirmAddStudent();
      }
      if(document.getElementById('add-grp-modal').style.display!=='none' &&
         document.activeElement===document.getElementById('new-grp-name')){
        confirmAddGroup();
      }
    }
  });
}"""

new_book_tab = """}"""

src = src.replace(old_book_tab, new_book_tab)

# ─────────────────────────────────────────────
# 10. 删除 showTooltip 函数（已被 showTooltipForNode 替代）
# ─────────────────────────────────────────────
old_show_tooltip = """function showTooltip(e,n){
  const u = UNITS.find(u=>u.id===n.unit);
  document.getElementById('tt-title').textContent = n.name;
  document.getElementById('tt-id').textContent = n.id;
  document.getElementById('tt-unit').textContent = (u ? u.book+' · '+u.name : '');
  document.getElementById('tt-desc').textContent = n.desc;
  const st = document.getElementById('tt-st');
  if(isMastered(n.id)){ st.textContent='✅ 已掌握 — 再次点击取消'; st.className='st-ok'; }
  else { st.textContent='⚪ 点击节点标记为已掌握'; st.className='st-no'; }
  const tip = document.getElementById('tooltip');
  tip.style.display='block';
  let x=e.clientX+16, y=e.clientY-12;
  if(x+250>window.innerWidth) x=e.clientX-266;
  if(y+140>window.innerHeight) y=e.clientY-154;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}
function hideTooltip(){ document.getElementById('tooltip').style.display='none'; }"""

new_show_tooltip = """function hideTooltip(){ document.getElementById('tooltip').style.display='none'; }"""

src = src.replace(old_show_tooltip, new_show_tooltip)

# ─────────────────────────────────────────────
# 11. 在 switchClass 的 then 回调中添加 renderMap()
# ─────────────────────────────────────────────
old_switch = """  loadCurrentClassDataAsync().then(()=>{
    groupCollapsed = {};
    unitDetailOpen = {};
    buildStudentPanel();
    const firstStu = GROUPS[0]?.members[0];
    curStudent = firstStu || '';
    if(curStudent) selectStudent(curStudent);
    updateAllStudentProgress();
    updateClassSelect();
    logAction('class', '切换到班级「' + getCurrentClassName() + '」');
  });
}"""

new_switch = """  loadCurrentClassDataAsync().then(()=>{
    groupCollapsed = {};
    unitDetailOpen = {};
    buildStudentPanel();
    const firstStu = GROUPS[0]?.members[0];
    curStudent = firstStu || '';
    if(curStudent) selectStudent(curStudent);
    updateAllStudentProgress();
    updateClassSelect();
    renderMap();
    logAction('class', '切换到班级「' + getCurrentClassName() + '」');
  });
}"""

src = src.replace(old_switch, new_switch)

# ─────────────────────────────────────────────
# 12. 在 resetCurrent 中添加 renderMap()
# ─────────────────────────────────────────────
old_reset = """  masteredMap[curStudent]=new Set();
  saveData();
  updateStats(); updateDetail();
  updateStudentRowProgress(curStudent);
}"""

new_reset = """  masteredMap[curStudent]=new Set();
  saveData();
  updateStats(); updateDetail();
  updateStudentRowProgress(curStudent);
  updateAllStudentProgress();
  renderMap();
}"""

src = src.replace(old_reset, new_reset)

# ─────────────────────────────────────────────
# 13. 修改 map-wrap 的背景色（CSS 中已设置为 #87CEEB）
# ─────────────────────────────────────────────
# 已在第2步中处理

# ─────────────────────────────────────────────
# 14. 写出 v16 文件
# ─────────────────────────────────────────────
with open('/home/ubuntu/mathkg/五年级数学知识图谱_v16.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("✅ v16 生成完成！")
print(f"文件大小: {len(src)} 字节")
