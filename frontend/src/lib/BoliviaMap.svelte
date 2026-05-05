<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { spring } from 'svelte/motion';

  let { resultsByDept = {}, dataMode = 'RRV' } = $props();
  let selectedDept = $state(null);
  let mapStyle = $state("transform: scale(1); transition: transform 0.8s ease;");

  function onClickDept(e, dept) {
    const bbox = e.currentTarget.getBBox();
    const scale = 2.5;
    const tx = 150 - (bbox.x + bbox.width / 2) * scale;
    const ty = 300 - (bbox.y + bbox.height / 2) * scale;
    mapStyle = `transform: translate(${tx}px, ${ty}px) scale(${scale});`;
    selectedDept = dept;
  }
</script>

<div class="relative w-full h-[600px] overflow-hidden rounded-3xl bg-slate-50 border border-slate-200">
  <svg viewBox="0 0 600 700" class="w-full h-full cursor-pointer" style={mapStyle}>
    <!-- Un path representativo simulado con las directivas svelte actualizadas -->
    <path d="M200,300 Q400,100 500,300 T400,600 Q200,600 200,300" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2" onclick={(e) => onClickDept(e, 'Pando')} />
  </svg>

  {#if selectedDept}
    <div class="absolute right-0 top-0 h-full w-80 bg-white/95 backdrop-blur-md shadow-2xl p-6 overflow-y-auto" in:fly={{ x: 300 }}>
      <button class="mb-4 text-slate-400 hover:text-rose-500" onclick={() => { selectedDept = null; mapStyle = "transform: scale(1);"; }}>✕ Cerrar</button>
      <h2 class="text-2xl font-black text-slate-900">{selectedDept}</h2>
      <p class="text-xs font-bold text-slate-400 uppercase tracking-tighter mb-6">{dataMode} MODE</p>
      
      <!-- Métricas del departamento -->
      <div class="space-y-4">
        {#each ['Tyrion', 'Daenerys', 'Robert', 'Sansa'] as cand}
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold text-slate-600">{cand}</span>
            <span class="text-sm font-bold text-slate-900">45.2%</span>
          </div>
          <div class="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-blue-500" style="width: 45.2%"></div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
