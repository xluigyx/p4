<script>
  import { onMount, onDestroy } from 'svelte';
  import { gsap } from 'gsap';
  import { invalidateAll } from '$app/navigation';
  import BoliviaMap from '$lib/BoliviaMap.svelte';

  let { data } = $props();

  let modo = $state('RRV');
  let activeTab = $state('home'); 

  // Health checks using data from +page.server.js
  let health = $derived(data.health || { db_rapido: 'ONLINE', db_oficial: 'ONLINE' });
  let healthInterval;

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

  let currentVotes = $derived(modo === 'RRV' ? mockVotesRRV : mockVotesOficial);

  let logs = $state([
    { id: 1, type: 'OK', message: 'Mesa 10102 procesada por Bot-1', status: 'Válida' },
    { id: 2, type: 'ERR', message: 'Mesa 10502: Acta Manchada - OMITIENDO', status: 'Manchada' },
    { id: 3, type: 'ERR', message: 'Mesa 10503: Acta Rota - OMITIENDO', status: 'Rota' },
    { id: 4, type: 'WARN', message: 'Mesa 10901: Inconsistencia Aritmética', status: 'Ilegible' },
    { id: 5, type: 'AUDIT', message: 'Bot-Ráfaga detectado en SCZ. Bloqueo IP.', status: 'Sistema' },
  ]);

  let logFilter = $state('ALL');

  let filteredLogs = $derived(logs.filter(log => {
    if (logFilter === 'ALL') return true;
    return log.status === logFilter;
  }));

  let totalVotes = $derived.by(() => {
    let totals = { Tyrion: 0, Daenerys: 0, Robert: 0, Sansa: 0 };
    for (let dept in currentVotes) {
      for (let cand in currentVotes[dept]) {
        if (totals[cand] !== undefined) {
          totals[cand] += currentVotes[dept][cand];
        }
      }
    }
    return totals;
  });

  let maxVotes = $derived(Math.max(...Object.values(totalVotes), 1));

  function toggleModo() {
    modo = modo === 'RRV' ? 'OFICIAL' : 'RRV';
    gsap.to(".map-container", { duration: 0.5, filter: "hue-rotate(90deg)", yoyo: true, repeat: 1 });
  }

  function switchTab(tabId) {
    activeTab = tabId;
  }

  $effect(() => {
    if (activeTab) {
      gsap.fromTo(".tab-content", 
        { opacity: 0, y: 30, scale: 0.98 }, 
        { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: "power3.out" }
      );
    }
  });

  onMount(() => {
    gsap.from(".header-card", { opacity: 0, y: -20, duration: 0.8, ease: "power3.out" });
    healthInterval = setInterval(() => {
      invalidateAll();
    }, 3000);
  });
  
  onDestroy(() => {
    if (healthInterval) clearInterval(healthInterval);
  });
</script>

{#snippet homeTab()}
  <div class="space-y-6 tab-content">
    <div class="p-10 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 shadow-[0_0_50px_rgba(6,182,212,0.1)] relative overflow-hidden group">
      <div class="absolute inset-0 bg-gradient-to-br from-cyan-400/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
      <h2 class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 mb-6 tracking-tighter">ANTIGRAVITY SYSTEM v4.0</h2>
      <p class="text-slate-300 leading-relaxed text-xl font-light max-w-3xl relative z-10">
        Plataforma de cómputo electoral de élite con Midnight Glassmorphism y tolerancia a fallos extrema.
      </p>
      
      <div class="grid grid-cols-3 gap-8 mt-12 relative z-10">
         <div class="p-8 rounded-2xl bg-[#0a0b10] border border-cyan-400/30 text-center shadow-[inset_0_0_20px_rgba(6,182,212,0.1)] hover:border-cyan-400 transition-colors">
            <h3 class="text-cyan-400 font-mono text-sm tracking-widest mb-3">TRANSPARENCIA</h3>
            <p class="text-4xl font-black text-white">100%</p>
         </div>
         <div class="p-8 rounded-2xl bg-[#0a0b10] border border-blue-600/30 text-center shadow-[inset_0_0_20px_rgba(37,99,235,0.1)] hover:border-blue-600 transition-colors">
            <h3 class="text-blue-500 font-mono text-sm tracking-widest mb-3">ESTADO GENERAL</h3>
            <p class="text-4xl font-black {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'text-green-400 drop-shadow-[0_0_10px_rgba(74,222,128,0.5)]' : 'text-red-400'}">
               {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'ÓPTIMA' : 'DEGRADADA'}
            </p>
         </div>
         <div class="p-8 rounded-2xl bg-[#0a0b10] border border-white/10 text-center shadow-[inset_0_0_20px_rgba(255,255,255,0.05)] hover:border-white/30 transition-colors">
            <h3 class="text-slate-400 font-mono text-sm tracking-widest mb-3">ACTAS INGRESADAS</h3>
            <p class="text-4xl font-black text-white">5,396</p>
         </div>
      </div>
    </div>
  </div>
{/snippet}

{#snippet mapTab()}
  <div class="tab-content relative map-container h-full">
    <div class="p-8 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 h-[700px] flex flex-col items-center justify-center relative overflow-hidden">
      {#if (modo === 'RRV' && health.db_rapido === 'OFFLINE') || (modo === 'OFICIAL' && health.db_oficial === 'OFFLINE')}
        <div class="absolute inset-0 bg-red-950/80 backdrop-blur-xl flex items-center justify-center z-10 border-4 border-red-500/50">
           <div class="text-center">
             <h2 class="text-7xl font-black text-red-500 font-mono tracking-widest drop-shadow-[0_0_25px_rgba(239,68,68,1)]">OFFLINE</h2>
             <p class="text-red-300 mt-4 tracking-widest uppercase text-xl font-bold">Clúster inaccesible en la red</p>
           </div>
        </div>
      {/if}
      <div class="absolute top-8 left-8 text-slate-500 uppercase tracking-widest text-sm font-bold bg-[#0a0b10]/40 px-4 py-2 rounded-full border border-white/10 z-10">
         Fuente de Datos: <span class="text-cyan-400">{modo}</span>
      </div>
      <div class="w-full h-full pt-12">
         <BoliviaMap resultsByDept={currentVotes} dataMode={modo} />
      </div>
    </div>
  </div>
{/snippet}

{#snippet chartsTab()}
  <div class="space-y-6 tab-content">
     <div class="p-10 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border border-white/10">
       <div class="flex justify-between items-end mb-10 border-b border-white/10 pb-6">
          <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">Comparativa Global</h2>
          <span class="px-4 py-2 bg-blue-600/20 text-blue-400 text-sm font-bold rounded-full border border-blue-600/30">MODO: {modo}</span>
       </div>
       
       <div class="space-y-8">
         {#each Object.entries(totalVotes) as [cand, votes]}
           <div class="relative group">
             <div class="flex justify-between mb-3">
               <span class="font-black text-xl text-slate-100 tracking-wide">{cand}</span>
               <span class="font-mono text-cyan-400 text-xl">{votes.toLocaleString()} votos</span>
             </div>
             <div class="h-6 w-full bg-[#0a0b10] rounded-full overflow-hidden border border-white/10 shadow-inner">
               <div class="h-full bg-gradient-to-r from-cyan-400 to-blue-600 rounded-full transition-all duration-1000 ease-out relative group-hover:shadow-[0_0_20px_rgba(6,182,212,0.5)]" style="width: {(votes/maxVotes)*100}%">
                 <div class="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%,transparent_100%)] bg-[length:20px_20px] animate-[pan_2s_linear_infinite]"></div>
               </div>
             </div>
           </div>
         {/each}
       </div>
     </div>
  </div>
{/snippet}

{#snippet logsTab()}
  <div class="tab-content">
     <div class="p-8 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 h-[700px] flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.5)]">
       <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-2xl font-black text-cyan-400 font-mono tracking-widest">>> AUDITORÍA DE ACTAS</h2>
           <div class="flex gap-2 mt-4">
             {#each ['ALL', 'Manchada', 'Rota', 'Ilegible', 'Válida'] as f}
               <button onclick={() => logFilter = f} class="px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full border transition-all {logFilter === f ? 'bg-cyan-400/20 text-cyan-300 border-cyan-400/50 shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'bg-transparent text-slate-500 border-white/10 hover:border-white/30 hover:text-slate-300'}">{f}</button>
             {/each}
           </div>
         </div>
         <span class="px-4 py-1.5 bg-blue-600/20 text-blue-400 text-sm font-bold rounded-full border border-blue-600/30 animate-pulse self-start">RÁFAGA BOT</span>
       </div>
       
       <div class="overflow-x-auto">
         <table class="w-full text-left text-slate-300 text-sm">
           <thead class="text-xs uppercase bg-[#0a0b10] text-slate-400 border-b border-white/10">
             <tr>
               <th scope="col" class="px-6 py-3">ID</th>
               <th scope="col" class="px-6 py-3">Estado</th>
               <th scope="col" class="px-6 py-3">Mensaje del Bot</th>
               <th scope="col" class="px-6 py-3">Acción</th>
             </tr>
           </thead>
           <tbody>
             {#each filteredLogs as log (log.id)}
               <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                 <td class="px-6 py-4 font-mono">{log.id.toString().padStart(4, '0')}</td>
                 <td class="px-6 py-4">
                   <span class="px-2 py-1 rounded text-xs font-bold {log.status === 'Manchada' || log.status === 'Rota' ? 'bg-red-500/20 text-red-400' : log.status === 'Válida' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}">
                     {log.status}
                   </span>
                 </td>
                 <td class="px-6 py-4">{log.message}</td>
                 <td class="px-6 py-4">
                   {#if log.type === 'ERR'}
                     <span class="text-xs font-bold text-red-400 uppercase">Rechazada</span>
                   {:else}
                     <span class="text-xs font-bold text-slate-500 uppercase">-</span>
                   {/if}
                 </td>
               </tr>
             {/each}
           </tbody>
         </table>
         {#if filteredLogs.length === 0}
            <div class="py-10 text-center text-slate-500 font-mono">
              [ NO HAY ACTAS QUE COINCIDAN CON EL FILTRO ]
            </div>
         {/if}
       </div>
     </div>
  </div>
{/snippet}

{#snippet infraTab()}
  <div class="tab-content grid grid-cols-2 gap-8 h-[700px]">
     <!-- Oficial Cluster -->
     <div class="p-10 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border {health.db_oficial === 'ONLINE' ? 'border-cyan-400/40 shadow-[0_0_40px_rgba(6,182,212,0.15)]' : 'border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.2)]'} relative overflow-hidden flex flex-col">
       <div class="flex justify-between items-start mb-8 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-3xl font-black text-white">CLÚSTER OFICIAL</h2>
           <p class="text-cyan-400 font-mono text-sm mt-2 tracking-widest">PORT: 5433 // POSTGRES</p>
         </div>
         <div class="relative flex items-center justify-center w-12 h-12">
            {#if health.db_oficial === 'ONLINE'}
              <span class="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-20 animate-ping"></span>
              <span class="relative inline-flex rounded-full h-4 w-4 bg-green-500 shadow-[0_0_10px_#22c55e]"></span>
            {:else}
              <span class="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-20 animate-ping"></span>
              <span class="relative inline-flex rounded-full h-4 w-4 bg-red-500 shadow-[0_0_10px_#ef4444]"></span>
            {/if}
         </div>
       </div>
       <div class="space-y-6 flex-1">
         <div class="flex justify-between items-center bg-[#0a0b10] p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Estado</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">{health.db_oficial}</span>
         </div>
         <div class="flex justify-between items-center bg-[#0a0b10] p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Consistencia</span>
           <span class="text-cyan-400 text-sm font-bold">Estricta</span>
         </div>
       </div>
     </div>

     <!-- RRV Cluster -->
     <div class="p-10 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border {health.db_rapido === 'ONLINE' ? 'border-blue-600/40 shadow-[0_0_40px_rgba(37,99,235,0.15)]' : 'border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.2)]'} relative overflow-hidden flex flex-col">
       <div class="flex justify-between items-start mb-8 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-3xl font-black text-white">CLÚSTER RRV</h2>
           <p class="text-blue-500 font-mono text-sm mt-2 tracking-widest">PORT: 5434 // POSTGRES</p>
         </div>
         <div class="relative flex items-center justify-center w-12 h-12">
            {#if health.db_rapido === 'ONLINE'}
              <span class="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-20 animate-ping"></span>
              <span class="relative inline-flex rounded-full h-4 w-4 bg-green-500 shadow-[0_0_10px_#22c55e]"></span>
            {:else}
              <span class="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-20 animate-ping"></span>
              <span class="relative inline-flex rounded-full h-4 w-4 bg-red-500 shadow-[0_0_10px_#ef4444]"></span>
            {/if}
         </div>
       </div>
       <div class="space-y-6 flex-1">
         <div class="flex justify-between items-center bg-[#0a0b10] p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Estado</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">{health.db_rapido}</span>
         </div>
         <div class="flex justify-between items-center bg-[#0a0b10] p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Velocidad</span>
           <span class="text-blue-500 text-sm font-bold">Alta / Append Only</span>
         </div>
       </div>
     </div>
  </div>
{/snippet}

<div class="min-h-screen bg-[#0a0b10] text-white p-8 font-sans selection:bg-cyan-400/30">
  
  <div class="header-card mb-8 p-6 rounded-3xl bg-[#0a0b10]/60 backdrop-blur-md border border-white/10 flex justify-between items-center shadow-[0_0_20px_rgba(0,0,0,0.5)]">
    <div class="flex items-center gap-6">
      <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      </div>
      <div>
        <h1 class="text-3xl font-black tracking-tight">ANTIGRAVITY <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">SYSTEM</span></h1>
        <div class="flex gap-3 mt-2">
          <span class="text-xs uppercase tracking-widest text-slate-400 font-bold bg-[#0a0b10] px-2 py-0.5 rounded border border-white/10">V.4.0</span>
          <span class="text-xs uppercase tracking-widest text-cyan-400 font-bold bg-cyan-400/10 px-2 py-0.5 rounded border border-cyan-400/20">LIVE</span>
        </div>
      </div>
    </div>
    
    <div class="flex items-center gap-6">
      <div class="text-right">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">DEPLOY MODE</p>
        <p class="text-xl font-black {modo === 'RRV' ? 'text-blue-500' : 'text-cyan-400'}">{modo}</p>
      </div>
      <button onclick={toggleModo} class="group relative px-8 py-4 rounded-2xl font-black text-white transition-all overflow-hidden bg-[#0a0b10] border border-white/10 hover:border-cyan-400/50">
        <div class="absolute inset-0 bg-gradient-to-r {modo === 'RRV' ? 'from-cyan-400 to-blue-600' : 'from-blue-600 to-cyan-400'} opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        <span class="relative z-10 text-cyan-400 group-hover:text-white transition-colors">CAMBIAR A {modo === 'RRV' ? 'OFICIAL' : 'RRV'}</span>
      </button>
    </div>
  </div>

  <div class="grid grid-cols-12 gap-8">
    <div class="col-span-3 space-y-3">
      <button onclick={() => switchTab('home')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'home' ? 'bg-cyan-400/10 border-cyan-400/50 text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]' : 'bg-[#0a0b10] border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'}">
        <span class="mr-3">📍</span> Home
      </button>
      <button onclick={() => switchTab('map')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'map' ? 'bg-blue-600/10 border-blue-600/50 text-white shadow-[0_0_15px_rgba(37,99,235,0.2)]' : 'bg-[#0a0b10] border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'}">
        <span class="mr-3">🗺️</span> Centro de Cómputo
      </button>
      <button onclick={() => switchTab('charts')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'charts' ? 'bg-cyan-400/10 border-cyan-400/50 text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]' : 'bg-[#0a0b10] border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'}">
        <span class="mr-3">⚖️</span> Comparativa
      </button>
      <button onclick={() => switchTab('logs')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'logs' ? 'bg-blue-600/10 border-blue-600/50 text-white shadow-[0_0_15px_rgba(37,99,235,0.2)]' : 'bg-[#0a0b10] border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'}">
        <span class="mr-3">📑</span> Auditoría
      </button>
      <button onclick={() => switchTab('infra')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'infra' ? 'bg-cyan-400/10 border-cyan-400/50 text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]' : 'bg-[#0a0b10] border-white/10 text-slate-400 hover:bg-white/5 hover:text-white'}">
        <span class="mr-3">🖥️</span> Infraestructura
      </button>
    </div>

    <div class="col-span-9">
      {#if activeTab === 'home'}
        {@render homeTab()}
      {:else if activeTab === 'map'}
        {@render mapTab()}
      {:else if activeTab === 'charts'}
        {@render chartsTab()}
      {:else if activeTab === 'logs'}
        {@render logsTab()}
      {:else if activeTab === 'infra'}
        {@render infraTab()}
      {/if}
    </div>
  </div>

  <footer class="mt-12 text-center text-slate-500 font-mono text-sm py-4 border-t border-white/10">
    Hecho por Antigravity
  </footer>
</div>

<style>
  @keyframes pan {
    from { background-position: 0 0; }
    to { background-position: 20px 20px; }
  }
</style>
