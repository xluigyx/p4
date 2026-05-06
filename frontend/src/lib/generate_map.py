import xml.etree.ElementTree as ET
import json

svg_file = r'd:\GitHub\p4\frontend\src\lib\BoliviaBase.svg'
svelte_file = r'd:\GitHub\p4\frontend\src\lib\BoliviaMap.svelte'

tree = ET.parse(svg_file)
root = tree.getroot()

ns = {'svg': 'http://www.w3.org/2000/svg'}

id_map = {
    'BOL': 'LP',
    'BOO': 'OR',
    'BOP': 'PT',
    'BOT': 'TJ',
    'BOS': 'SC',
    'BOH': 'CH',
    'BON': 'PA',
    'BOB': 'BE',
    'BOC': 'CB'
}

depts = []

# Find paths
features_g = root.find('.//svg:g[@id="features"]', ns)
for path in features_g.findall('svg:path', ns):
    d = path.get('d')
    orig_id = path.get('id')
    name = path.get('name')
    dept_id = id_map.get(orig_id, orig_id)
    depts.append({
        'id': dept_id,
        'name': name,
        'orig_id': orig_id,
        'd': d,
        'cx': 0,
        'cy': 0
    })

# Find label points
labels_g = root.find('.//svg:g[@id="label_points"]', ns)
for circle in labels_g.findall('svg:circle', ns):
    orig_id = circle.get('id')
    cx = float(circle.get('cx'))
    cy = float(circle.get('cy'))
    
    for dept in depts:
        if dept['orig_id'] == orig_id:
            dept['cx'] = cx
            dept['cy'] = cy

json_depts = json.dumps([{'id': d['id'], 'name': d['name'], 'cx': d['cx'], 'cy': d['cy'], 'd': d['d']} for d in depts])

svelte_content = f"""<script>
  import {{ onMount }} from 'svelte';
  import {{ fade, fly }} from 'svelte/transition';
  import {{ gsap }} from 'gsap';

  let {{ resultsByDept = {{}}, dataMode = 'RRV' }} = $props();
  
  let selectedDept = $state(null);
  let mapStyle = $state("transform: scale(1); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);");

  function onClickDept(deptId, deptName, event) {{
    if (event) {{
        const bbox = event.currentTarget.getBBox();
        const scale = 2.2;
        const tx = 500 - (bbox.x + bbox.width / 2) * scale;
        const ty = 500 - (bbox.y + bbox.height / 2) * scale;
        mapStyle = `transform: translate(${{tx}}px, ${{ty}}px) scale(${{scale}});`;
    }}
    selectedDept = {{ id: deptId, name: deptName }};
  }}

  const depts = {json_depts};

  const candColors = {{
    'Tyrion': '#38bdf8', // cyan-400
    'Daenerys': '#2563eb', // blue-600
    'Robert': '#8b5cf6', // violet-500
    'Sansa': '#d946ef', // fuchsia-500
    'Empate': '#64748b' // slate-500
  }};

  function getDeptColor(deptId) {{
    const votes = resultsByDept[deptId];
    if (!votes) return 'rgba(255,255,255,0.02)'; 
    let max = -1;
    let winner = null;
    for (const cand in votes) {{
      if (votes[cand] > max) {{
        max = votes[cand];
        winner = cand;
      }} else if (votes[cand] === max) {{
        winner = 'Empate';
      }}
    }}
    return candColors[winner] || 'rgba(255,255,255,0.02)';
  }}

  $effect(() => {{
    if (resultsByDept) {{
        depts.forEach(dpt => {{
            gsap.to(`.dept-${{dpt.id}}`, {{
                fill: getDeptColor(dpt.id),
                duration: 1.2,
                ease: "power2.out"
            }});
        }});
    }}
  }});

  onMount(() => {{
    gsap.from('.dpto-path', {{ scale: 0, stagger: 0.05, ease: 'back.out' }});

    gsap.from("text.dept-label", {{
        opacity: 0,
        y: 10,
        duration: 1,
        delay: 0.5,
        stagger: 0.05,
        ease: "power2.out"
    }});
  }});
</script>

<div class="relative w-full h-full overflow-hidden rounded-[2.5rem] bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 shadow-[inset_0_0_50px_rgba(0,0,0,0.5)] flex items-center justify-center">
  <svg viewBox="0 0 1000 1000" class="w-full h-full cursor-pointer overflow-visible drop-shadow-[0_0_25px_rgba(6,182,212,0.15)]" style={{mapStyle}}>
    {{#each depts as dpt}}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <path 
        d={{dpt.d}} 
        stroke="#1e293b" 
        stroke-width="2" 
        stroke-linejoin="round"
        stroke-linecap="round"
        class="dpto-path dept-{{dpt.id}} hover:fill-cyan-500 hover:brightness-125 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.6)] transition-colors duration-300"
        onclick={{(e) => onClickDept(dpt.id, dpt.name, e)}} 
        style="fill: transparent; transform-origin: {{dpt.cx}}px {{dpt.cy}}px;"
      />
      <text 
        x={{dpt.cx}} 
        y={{dpt.cy}} 
        text-anchor="middle"
        alignment-baseline="middle"
        class="dept-label text-[14px] font-black uppercase tracking-widest pointer-events-none fill-white"
        style="filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.9));">
        {{dpt.name}}
      </text>
    {{/each}}
  </svg>

  {{#if selectedDept}}
    <div class="absolute right-0 top-0 h-full w-96 bg-[#0a0b10]/80 backdrop-blur-md shadow-[-20px_0_50px_rgba(0,0,0,0.5)] p-8 overflow-y-auto border-l border-white/10" in:fly={{{{ x: 400, duration: 600, ease: 'power3.out' }}}} out:fade={{{{ duration: 300 }}}}>
      <button class="mb-8 text-slate-400 hover:text-cyan-400 font-bold tracking-widest text-sm flex items-center gap-2 transition-colors" onclick={{() => {{ selectedDept = null; mapStyle = "transform: scale(1); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);"; }}}}>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        CERRAR PANEL
      </button>
      
      <h2 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 mb-2">{{selectedDept.name}}</h2>
      <p class="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-10 border-b border-white/10 pb-4 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> {{dataMode}} MODE
      </p>
      
      <div class="space-y-6">
        {{#each ['Tyrion', 'Daenerys', 'Robert', 'Sansa'] as cand}}
          {{@const vts = (resultsByDept[selectedDept.id] && resultsByDept[selectedDept.id][cand]) || 0}}
          <div class="group">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-black text-slate-200 tracking-wider uppercase">{{cand}}</span>
              <span class="text-sm font-mono text-white/80">{{vts.toLocaleString()}}</span>
            </div>
            <div class="h-2 w-full bg-[#0a0b10] rounded-full overflow-hidden border border-white/10">
              <div class="h-full transition-all duration-1000 relative" style="width: {{vts > 0 ? Math.min((vts/1500)*100, 100) : 0}}%; background-color: {{candColors[cand]}}">
                 <div class="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.3)_50%,transparent_75%,transparent_100%)] bg-[length:10px_10px] animate-[pan_2s_linear_infinite]"></div>
              </div>
            </div>
          </div>
        {{/each}}
      </div>
    </div>
  {{/if}}
</div>
"""

with open(svelte_file, 'w', encoding='utf-8') as f:
    f.write(svelte_content)
