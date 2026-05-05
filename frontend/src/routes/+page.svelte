<script>
  import { onMount } from 'svelte';
  import { gsap } from 'gsap';
  import BoliviaMap from '$lib/BoliviaMap.svelte';

  export let data;
  export let params;

  let modo = 'RRV'; // Switch: RRV o OFICIAL
  let logs = []; 

  // Simulated votes for demonstration
  let mockVotes = {
    'PA': { Tyrion: 500, Daenerys: 200, Robert: 100, Sansa: 50 },
    'BE': { Tyrion: 300, Daenerys: 800, Robert: 100, Sansa: 100 },
    'LP': { Tyrion: 400, Daenerys: 300, Robert: 900, Sansa: 200 },
    'CB': { Tyrion: 350, Daenerys: 400, Robert: 200, Sansa: 800 },
    'SC': { Tyrion: 800, Daenerys: 200, Robert: 300, Sansa: 100 },
    'OR': { Tyrion: 100, Daenerys: 200, Robert: 150, Sansa: 400 },
    'PT': { Tyrion: 200, Daenerys: 200, Robert: 200, Sansa: 100 },
    'CH': { Tyrion: 300, Daenerys: 400, Robert: 100, Sansa: 200 },
    'TJ': { Tyrion: 100, Daenerys: 100, Robert: 500, Sansa: 200 }
  };

  function toggleModo() {
    modo = modo === 'RRV' ? 'OFICIAL' : 'RRV';
    gsap.to(".map-container", { duration: 0.5, filter: "hue-rotate(90deg)", yoyo: true, repeat: 1 });
  }

  onMount(() => {
    gsap.from(".card", { stagger: 0.2, opacity: 0, y: 20 });
  });
</script>

<div class="min-h-screen bg-[#0b0e14] text-white p-8">
  <div class="flex justify-between items-center mb-10">
    <h1 class="text-3xl font-bold font-mono">ANTIGRAVITY // DEPLOY_MODE: {modo}</h1>
    
    <button on:click={toggleModo} class="bg-blue-600 px-6 py-2 rounded-full font-bold hover:bg-blue-500 transition">
      CAMBIAR A {modo === 'RRV' ? 'OFICIAL' : 'RRV'}
    </button>
  </div>

  <div class="grid grid-cols-12 gap-6">
    <!-- MAPA INTERACTIVO (Simplificado) -->
    <div class="card col-span-8 bg-[#161b22] rounded-3xl p-10 border border-white/5 map-container">
      <div class="text-center text-slate-500 mb-4 uppercase tracking-widest text-xs">Distribución Territorial</div>
      <div class="h-[600px] flex items-center justify-center border-2 border-dashed border-white/10 rounded-2xl overflow-hidden">
         <BoliviaMap resultsByDept={mockVotes} dataMode={modo} />
      </div>
    </div>

    <!-- LIVE LOGS DE LOS BOTS -->
    <div class="card col-span-4 space-y-6">
      <div class="bg-black/40 p-6 rounded-2xl border border-red-500/20 h-[600px] overflow-y-auto">
        <h2 class="text-red-500 font-mono mb-4">LIVE_OCR_STREAM_LOGS</h2>
        <div class="space-y-2 text-xs font-mono">
            <p class="text-green-400">[OK] Mesa 10102 procesada por Bot-1</p>
            <p class="text-red-400">[ERR] Mesa 10502: Acta Manchada - OMITIENDO</p>
            <p class="text-yellow-400">[WARN] Mesa 10901: Inconsistencia Aritmética (P1+P2...)</p>
        </div>
      </div>
    </div>
  </div>
</div>
