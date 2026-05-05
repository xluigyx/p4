<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  export let resultsByDept = {};
  export let dataMode = 'RRV';
  
  let selectedDept = null;
  let mapStyle = "transform: scale(1); transition: transform 0.8s ease;";

  function onClickDept(deptId, deptName, event) {
    if (event) {
        const bbox = event.currentTarget.getBBox();
        const scale = 2.5;
        const tx = 300 - (bbox.x + bbox.width / 2) * scale;
        const ty = 300 - (bbox.y + bbox.height / 2) * scale;
        mapStyle = `transform: translate(${tx}px, ${ty}px) scale(${scale});`;
    }
    selectedDept = { id: deptId, name: deptName };
  }

  const depts = [
    { id: 'PA', name: 'Pando', d: "M 150,50 L 350,50 L 350,150 L 150,150 Z" },
    { id: 'BE', name: 'Beni', d: "M 350,50 L 650,100 L 650,300 L 450,250 L 350,200 Z" },
    { id: 'LP', name: 'La Paz', d: "M 50,150 L 250,200 L 300,400 L 100,450 Z" },
    { id: 'CB', name: 'Cochabamba', d: "M 250,200 L 450,250 L 400,400 L 300,400 Z" },
    { id: 'SC', name: 'Santa Cruz', d: "M 450,250 L 650,300 L 700,550 L 500,450 Z" },
    { id: 'OR', name: 'Oruro', d: "M 100,450 L 300,400 L 250,550 L 100,550 Z" },
    { id: 'PT', name: 'Potosí', d: "M 100,550 L 350,500 L 400,700 L 150,700 Z" },
    { id: 'CH', name: 'Chuquisaca', d: "M 350,500 L 500,450 L 550,600 L 400,600 Z" },
    { id: 'TJ', name: 'Tarija', d: "M 400,600 L 550,600 L 500,700 L 350,700 Z" }
  ];

  const candColors = {
    'Tyrion': '#3b82f6', // blue
    'Daenerys': '#ef4444', // red
    'Robert': '#eab308', // yellow
    'Sansa': '#8b5cf6', // purple
    'Empate': '#64748b' // slate
  };

  $: getDeptColor = (deptId) => {
    const votes = resultsByDept[deptId];
    if (!votes) return '#cbd5e1'; 
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
    return candColors[winner] || '#cbd5e1';
  };
</script>

<div class="relative w-full h-[600px] overflow-hidden rounded-3xl bg-slate-900 border border-slate-700">
  <svg viewBox="0 0 800 800" class="w-full h-full cursor-pointer" style={mapStyle}>
    {#each depts as dpt}
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <path 
        d={dpt.d} 
        fill={getDeptColor(dpt.id)} 
        stroke="#1e293b" 
        stroke-width="3" 
        class="hover:opacity-80 transition-opacity"
        on:click={(e) => onClickDept(dpt.id, dpt.name, e)} 
      />
      <!-- Etiqueta del departamento (posicionada visualmente) -->
      <text 
        x={(dpt.d.match(/M (\d+),/)[1]) * 1 + 50} 
        y={(dpt.d.match(/M \d+,(\d+)/)[1]) * 1 + 50} 
        class="text-xs font-bold pointer-events-none fill-white drop-shadow-md">{dpt.name}</text>
    {/each}
  </svg>

  {#if selectedDept}
    <div class="absolute right-0 top-0 h-full w-80 bg-slate-800/95 backdrop-blur-md shadow-2xl p-6 overflow-y-auto border-l border-slate-700" in:fly={{ x: 300 }} out:fade>
      <button class="mb-4 text-slate-400 hover:text-rose-500 font-bold" on:click={() => { selectedDept = null; mapStyle = "transform: scale(1);"; }}>✕ Cerrar</button>
      <h2 class="text-2xl font-black text-white">{selectedDept.name}</h2>
      <p class="text-xs font-bold text-slate-400 uppercase tracking-tighter mb-6">{dataMode} MODE</p>
      
      <div class="space-y-4">
        {#each ['Tyrion', 'Daenerys', 'Robert', 'Sansa'] as cand}
          {@const vts = (resultsByDept[selectedDept.id] && resultsByDept[selectedDept.id][cand]) || 0}
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold text-slate-300">{cand}</span>
            <span class="text-sm font-bold text-white">{vts} votos</span>
          </div>
          <div class="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full transition-all duration-1000" style="width: {vts > 0 ? Math.min((vts/1000)*100, 100) : 0}%; background-color: {candColors[cand]}"></div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
