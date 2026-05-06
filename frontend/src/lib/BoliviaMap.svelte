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

  // Simplified pseudo-realistic paths for Bolivia departments
  const depts = [
    { id: 'PA', name: 'Pando', d: "M100,50 C180,30 250,50 300,80 C320,120 280,180 200,160 C120,180 80,120 100,50 Z" },
    { id: 'BE', name: 'Beni', d: "M300,80 C400,60 500,100 550,180 C580,250 500,350 400,320 C320,350 250,280 200,160 C280,180 320,120 300,80 Z" },
    { id: 'LP', name: 'La Paz', d: "M100,50 C80,120 120,180 200,160 C250,280 180,380 120,350 C60,380 20,250 100,50 Z" },
    { id: 'CB', name: 'Cochabamba', d: "M200,160 C250,280 320,350 400,320 C380,400 300,450 250,420 C180,450 150,380 120,350 C180,380 250,280 200,160 Z" },
    { id: 'SC', name: 'Santa Cruz', d: "M400,320 C500,350 580,250 550,180 C600,200 750,300 700,450 C650,550 550,600 450,500 C400,550 300,450 380,400 C400,320 400,320 400,320 Z" },
    { id: 'OR', name: 'Oruro', d: "M120,350 C180,380 150,450 200,480 C180,550 100,550 80,450 C60,380 80,400 120,350 Z" },
    { id: 'PT', name: 'Potosí', d: "M80,450 C100,550 180,550 200,480 C250,580 200,650 150,650 C80,650 50,550 80,450 Z" },
    { id: 'CH', name: 'Chuquisaca', d: "M200,480 C250,420 300,450 380,400 C400,550 450,500 500,550 C450,650 300,600 250,580 C200,650 180,550 200,480 Z" },
    { id: 'TJ', name: 'Tarija', d: "M250,580 C300,600 450,650 500,550 C550,600 500,700 400,700 C300,700 250,650 250,580 Z" }
  ];

  const candColors = {
    'Tyrion': '#38bdf8', // light blue
    'Daenerys': '#f43f5e', // rose
    'Robert': '#eab308', // yellow
    'Sansa': '#a855f7', // purple
    'Empate': '#64748b' // slate
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

  // Update map colors reactively
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
    // Drawing effect
    const paths = document.querySelectorAll('.bolivia-path');
    paths.forEach(path => {
      const length = path.getTotalLength();
      gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
      gsap.to(path, {
        strokeDashoffset: 0,
        duration: 2,
        ease: "power3.inOut",
        stagger: 0.1
      });
    });

    gsap.from("text.dept-label", {
        opacity: 0,
        y: 10,
        duration: 1,
        delay: 1.5,
        stagger: 0.05,
        ease: "power2.out"
    });
  });
</script>

<div class="relative w-full h-full overflow-hidden rounded-[2.5rem] bg-black/20 border border-white/5 shadow-[inset_0_0_50px_rgba(0,0,0,0.5)]">
  <!-- Interactive Map -->
  <svg viewBox="0 0 800 800" class="w-full h-full cursor-pointer overflow-visible" style={mapStyle}>
    <!-- Glow filter for paths -->
    <defs>
      <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    </defs>

    {#each depts as dpt}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <path 
        d={dpt.d} 
        stroke="#334155" 
        stroke-width="3" 
        stroke-linejoin="round"
        stroke-linecap="round"
        class="dept-{dpt.id} bolivia-path hover:brightness-125 hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all duration-300"
        onclick={(e) => onClickDept(dpt.id, dpt.name, e)} 
        style="fill: transparent; transform-origin: center;"
      />
      
      {@const cx = (dpt.d.match(/M\s*(\d+),/)?.[1] || 400) * 1 + 20}
      {@const cy = (dpt.d.match(/M\s*\d+,(\d+)/)?.[1] || 400) * 1 + 20}
      
      <text 
        x={cx} 
        y={cy} 
        class="dept-label text-[10px] font-black uppercase tracking-widest pointer-events-none fill-white/70"
        style="filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.8));">
        {dpt.name}
      </text>
    {/each}
  </svg>

  <!-- Side Panel for Selected Department -->
  {#if selectedDept}
    <div class="absolute right-0 top-0 h-full w-96 bg-[#05050f]/80 backdrop-blur-2xl shadow-[-20px_0_50px_rgba(0,0,0,0.5)] p-8 overflow-y-auto border-l border-white/10" in:fly={{ x: 400, duration: 600, ease: 'power3.out' }} out:fade={{ duration: 300 }}>
      <button class="mb-8 text-slate-400 hover:text-rose-400 font-bold tracking-widest text-sm flex items-center gap-2 transition-colors" onclick={() => { selectedDept = null; mapStyle = "transform: scale(1); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);"; }}>
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        CERRAR PANEL
      </button>
      
      <h2 class="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">{selectedDept.name}</h2>
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
            <div class="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
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
