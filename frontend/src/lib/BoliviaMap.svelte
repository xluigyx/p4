<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { gsap } from 'gsap';

  let { resultsByDept = {}, dataMode = 'RRV' } = $props();
  
  let selectedDept = $state(null);
  let mapStyle = $state("transform: scale(1); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);");

  function onClickDept(deptId, deptName, event) {
    if (event) {
        const bbox = event.currentTarget.getBBox();
        const scale = 2.2;
        const tx = 300 - (bbox.x + bbox.width / 2) * scale;
        const ty = 300 - (bbox.y + bbox.height / 2) * scale;
        mapStyle = `transform: translate(${tx}px, ${ty}px) scale(${scale});`;
    }
    selectedDept = { id: deptId, name: deptName };
  }

  // Paths representing the 9 departments of Bolivia
  const depts = [
    { id: 'PA', name: 'Pando', cx: 200, cy: 110, d: "M130,50 L270,40 L310,120 L240,160 L140,140 Z" },
    { id: 'BE', name: 'Beni', cx: 350, cy: 200, d: "M270,40 L450,100 L550,180 L500,320 L300,280 L240,160 L310,120 Z" },
    { id: 'LP', name: 'La Paz', cx: 160, cy: 250, d: "M130,50 L140,140 L240,160 L300,280 L200,380 L100,300 Z" },
    { id: 'CB', name: 'Cochabamba', cx: 320, cy: 350, d: "M300,280 L500,320 L450,420 L250,400 L200,380 Z" },
    { id: 'SC', name: 'Santa Cruz', cx: 550, cy: 380, d: "M550,180 L700,250 L750,450 L550,550 L450,420 L500,320 Z" },
    { id: 'OR', name: 'Oruro', cx: 180, cy: 420, d: "M200,380 L250,400 L280,480 L150,500 L120,450 Z" },
    { id: 'PT', name: 'Potosí', cx: 220, cy: 550, d: "M280,480 L350,550 L250,680 L100,600 L150,500 Z" },
    { id: 'CH', name: 'Chuquisaca', cx: 380, cy: 500, d: "M250,400 L450,420 L550,550 L400,600 L350,550 L280,480 Z" },
    { id: 'TJ', name: 'Tarija', cx: 400, cy: 620, d: "M350,550 L400,600 L550,550 L450,700 L300,650 Z" }
  ];

  const candColors = {
    'Tyrion': '#38bdf8', // cyan-400
    'Daenerys': '#2563eb', // blue-600
    'Robert': '#8b5cf6', // violet-500
    'Sansa': '#d946ef', // fuchsia-500
    'Empate': '#64748b' // slate-500
  };

  function getDeptColor(deptId) {
    const votes = resultsByDept[deptId];
    if (!votes) return 'rgba(255,255,255,0.02)'; 
    let max = -1;
    let winner = null;
    for (const cand in votes) {
      if (votes[cand] > max) {
        max = votes[cand];
        winner = cand;
      } else if (votes[cand] === max) {
        winner = 'Empate';
      }
    }
    return candColors[winner] || 'rgba(255,255,255,0.02)';
  }

  $effect(() => {
    if (resultsByDept) {
        depts.forEach(dpt => {
            gsap.to(`.dept-${dpt.id}`, {
                fill: getDeptColor(dpt.id),
                duration: 1.2,
                ease: "power2.out"
            });
        });
    }
  });

  onMount(() => {
    // Animating the map components
    gsap.from('.dpto', { scale: 0, stagger: 0.05, ease: 'back.out' });

    gsap.from("text.dept-label", {
        opacity: 0,
        y: 10,
        duration: 1,
        delay: 0.5,
        stagger: 0.05,
        ease: "power2.out"
    });
  });
</script>

<div class="relative w-full h-full overflow-hidden rounded-[2.5rem] bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]">
  <svg viewBox="0 0 800 800" class="w-full h-full cursor-pointer overflow-visible" style={mapStyle}>
    <defs>
      <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>

    {#each depts as dpt}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <path 
        d={dpt.d} 
        stroke="#1e293b" 
        stroke-width="3" 
        stroke-linejoin="round"
        stroke-linecap="round"
        class="dpto dept-{dpt.id} hover:brightness-125 hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all duration-300"
        onclick={(e) => onClickDept(dpt.id, dpt.name, e)} 
        style="fill: transparent; transform-origin: {dpt.cx}px {dpt.cy}px;"
      />
      <text 
        x={dpt.cx} 
        y={dpt.cy} 
        text-anchor="middle"
        alignment-baseline="middle"
        class="dept-label text-[12px] font-black uppercase tracking-widest pointer-events-none fill-white/80"
        style="filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.8));">
        {dpt.name}
      </text>
    {/each}
  </svg>

  {#if selectedDept}
    <div class="absolute right-0 top-0 h-full w-96 bg-[#0a0b10]/80 backdrop-blur-md shadow-[-20px_0_50px_rgba(0,0,0,0.5)] p-8 overflow-y-auto border-l border-white/10" in:fly={{ x: 400, duration: 600, ease: 'power3.out' }} out:fade={{ duration: 300 }}>
      <button class="mb-8 text-slate-400 hover:text-cyan-400 font-bold tracking-widest text-sm flex items-center gap-2 transition-colors" onclick={() => { selectedDept = null; mapStyle = "transform: scale(1); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);"; }}>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        CERRAR PANEL
      </button>
      
      <h2 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 mb-2">{selectedDept.name}</h2>
      <p class="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-10 border-b border-white/10 pb-4 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> {dataMode} MODE
      </p>
      
      <div class="space-y-6">
        {#each ['Tyrion', 'Daenerys', 'Robert', 'Sansa'] as cand}
          {@const vts = (resultsByDept[selectedDept.id] && resultsByDept[selectedDept.id][cand]) || 0}
          <div class="group">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-black text-slate-200 tracking-wider uppercase">{cand}</span>
              <span class="text-sm font-mono text-white/80">{vts.toLocaleString()}</span>
            </div>
            <div class="h-2 w-full bg-[#0a0b10] rounded-full overflow-hidden border border-white/10">
              <div class="h-full transition-all duration-1000 relative" style="width: {vts > 0 ? Math.min((vts/1500)*100, 100) : 0}%; background-color: {candColors[cand]}">
                 <div class="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.3)_50%,transparent_75%,transparent_100%)] bg-[length:10px_10px] animate-[pan_2s_linear_infinite]"></div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
