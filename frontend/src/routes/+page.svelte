<script>
  import { onMount, onDestroy } from 'svelte';
  import { gsap } from 'gsap';
  import BoliviaMap from '$lib/BoliviaMap.svelte';

  export let data;
  export let params;

  let modo = 'RRV'; // Switch: RRV o OFICIAL
  let logs = []; 
  
  // Health checks
  let health = {
    db_rapido: 'ONLINE',
    db_oficial: 'ONLINE'
  };
  let healthInterval;

  // Simulated votes for demonstration
  let mockVotesRRV = {
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

  let mockVotesOficial = {
    'PA': { Tyrion: 510, Daenerys: 210, Robert: 105, Sansa: 52 },
    'BE': { Tyrion: 305, Daenerys: 810, Robert: 102, Sansa: 105 },
    'LP': { Tyrion: 410, Daenerys: 305, Robert: 920, Sansa: 210 },
    'CB': { Tyrion: 355, Daenerys: 405, Robert: 210, Sansa: 810 },
    'SC': { Tyrion: 820, Daenerys: 205, Robert: 310, Sansa: 105 },
    'OR': { Tyrion: 105, Daenerys: 205, Robert: 155, Sansa: 410 },
    'PT': { Tyrion: 210, Daenerys: 205, Robert: 205, Sansa: 105 },
    'CH': { Tyrion: 310, Daenerys: 410, Robert: 105, Sansa: 205 },
    'TJ': { Tyrion: 105, Daenerys: 105, Robert: 510, Sansa: 210 }
  };

  $: currentVotes = modo === 'RRV' ? mockVotesRRV : mockVotesOficial;

  function toggleModo() {
    modo = modo === 'RRV' ? 'OFICIAL' : 'RRV';
    gsap.to(".map-container", { duration: 0.5, filter: "hue-rotate(90deg)", yoyo: true, repeat: 1 });
  }

  function simulateHealthCheck() {
    // Simulando estado de base de datos
    health.db_rapido = Math.random() > 0.95 ? 'OFFLINE' : 'ONLINE';
    health.db_oficial = Math.random() > 0.98 ? 'OFFLINE' : 'ONLINE';
  }

  onMount(() => {
    gsap.from(".card", { stagger: 0.2, opacity: 0, y: 20 });
    healthInterval = setInterval(simulateHealthCheck, 3000);
  });
  
  onDestroy(() => {
    clearInterval(healthInterval);
  });
</script>

<div class="min-h-screen bg-[#0b0e14] text-white p-8">
  <div class="flex justify-between items-center mb-10">
    <div>
      <h1 class="text-3xl font-bold font-mono">ANTIGRAVITY // DEPLOY_MODE: {modo}</h1>
      <div class="flex gap-4 mt-3">
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase tracking-widest text-slate-400">DB_RRV (5434):</span>
          <span class={`px-2 py-1 text-xs font-bold rounded ${health.db_rapido === 'ONLINE' ? 'bg-green-500/20 text-green-400 border border-green-500/50' : 'bg-red-500/20 text-red-400 border border-red-500/50 blink'}`}>
            {health.db_rapido}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs uppercase tracking-widest text-slate-400">DB_OFICIAL (5433):</span>
          <span class={`px-2 py-1 text-xs font-bold rounded ${health.db_oficial === 'ONLINE' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50' : 'bg-red-500/20 text-red-400 border border-red-500/50 blink'}`}>
            {health.db_oficial}
          </span>
        </div>
      </div>
    </div>
    
    <button on:click={toggleModo} class="bg-blue-600 px-6 py-2 rounded-full font-bold hover:bg-blue-500 transition shadow-[0_0_15px_rgba(37,99,235,0.5)]">
      CAMBIAR A {modo === 'RRV' ? 'OFICIAL' : 'RRV'}
    </button>
  </div>

  <div class="grid grid-cols-12 gap-6">
    <!-- MAPA INTERACTIVO (Simplificado) -->
    <div class="card col-span-8 bg-[#161b22] rounded-3xl p-10 border border-white/5 map-container relative">
      {#if (modo === 'RRV' && health.db_rapido === 'OFFLINE') || (modo === 'OFICIAL' && health.db_oficial === 'OFFLINE')}
        <div class="absolute inset-0 bg-red-900/20 backdrop-blur-sm rounded-3xl flex items-center justify-center z-10 border-2 border-red-500">
           <h2 class="text-4xl font-black text-red-500 font-mono tracking-widest bg-black/50 px-8 py-4 rounded-xl border border-red-500/50">SYSTEM OFFLINE</h2>
        </div>
      {/if}
      <div class="text-center text-slate-500 mb-4 uppercase tracking-widest text-xs">Distribución Territorial - Fuente: {modo}</div>
      <div class="h-[600px] flex items-center justify-center border-2 border-dashed border-white/10 rounded-2xl overflow-hidden">
         <BoliviaMap resultsByDept={currentVotes} dataMode={modo} />
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
            <p class="text-blue-400">[AUDIT] Bot-Ráfaga detectado en SCZ. Bloqueo preventivo de IP.</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .blink {
    animation: blinker 1s linear infinite;
  }
  @keyframes blinker {
    50% { opacity: 0; }
  }
</style>
