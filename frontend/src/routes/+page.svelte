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
    { id: 3, type: 'WARN', message: 'Mesa 10901: Inconsistencia Aritmética (P1+P2...)', status: 'Ilegible' },
    { id: 4, type: 'AUDIT', message: 'Bot-Ráfaga detectado en SCZ. Bloqueo IP.', status: 'Sistema' },
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

  function deleteLog(id) {
    logs = logs.filter(l => l.id !== id);
  }

  function invalidateLog(id) {
    logs = logs.map(l => l.id === id ? { ...l, type: 'ERR', status: 'Invalidada', message: l.message + ' [INVALIDADA POR AUDITORÍA]' } : l);
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

<!-- SNIPPETS -->
{#snippet homeTab()}
  <div class="space-y-6 tab-content">
    <div class="p-10 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 shadow-[0_0_50px_rgba(6,182,212,0.1)] relative overflow-hidden group">
      <div class="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-fuchsia-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
      <h2 class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-500 mb-6 tracking-tighter">PROYECTO ANTIGRAVITY</h2>
      <p class="text-slate-300 leading-relaxed text-xl font-light max-w-3xl">
        El sistema distribuido de cómputo electoral más avanzado y resiliente. Diseñado con una arquitectura de microservicios orientada a eventos para procesar ráfagas de OCR y asegurar tolerancia a fallos extrema en los clústeres Oficial y RRV.
      </p>
      
      <div class="grid grid-cols-3 gap-8 mt-12">
         <div class="p-8 rounded-2xl bg-black/50 border border-cyan-500/30 text-center shadow-[inset_0_0_20px_rgba(6,182,212,0.1)] hover:border-cyan-400 transition-colors">
            <h3 class="text-cyan-400 font-mono text-sm tracking-widest mb-3">TRANSPARENCIA</h3>
            <p class="text-4xl font-black text-white">100%</p>
         </div>
         <div class="p-8 rounded-2xl bg-black/50 border border-fuchsia-500/30 text-center shadow-[inset_0_0_20px_rgba(217,70,239,0.1)] hover:border-fuchsia-400 transition-colors">
            <h3 class="text-fuchsia-400 font-mono text-sm tracking-widest mb-3">SALUD GLOBAL</h3>
            <p class="text-4xl font-black {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'text-green-400 drop-shadow-[0_0_10px_rgba(74,222,128,0.5)]' : 'text-red-400'}">
               {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'ÓPTIMA' : 'DEGRADADA'}
            </p>
         </div>
         <div class="p-8 rounded-2xl bg-black/50 border border-yellow-500/30 text-center shadow-[inset_0_0_20px_rgba(234,179,8,0.1)] hover:border-yellow-400 transition-colors">
            <h3 class="text-yellow-400 font-mono text-sm tracking-widest mb-3">ACTAS INGRESADAS</h3>
            <p class="text-4xl font-black text-white">5,396</p>
         </div>
      </div>
    </div>
  </div>
{/snippet}

{#snippet mapTab()}
  <div class="tab-content relative map-container h-full">
    <div class="p-8 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10 h-[700px] flex flex-col items-center justify-center relative overflow-hidden">
      {#if (modo === 'RRV' && health.db_rapido === 'OFFLINE') || (modo === 'OFICIAL' && health.db_oficial === 'OFFLINE')}
        <div class="absolute inset-0 bg-red-950/80 backdrop-blur-xl flex items-center justify-center z-10 border-4 border-red-500/50">
           <div class="text-center">
             <h2 class="text-7xl font-black text-red-500 font-mono tracking-widest drop-shadow-[0_0_25px_rgba(239,68,68,1)]">OFFLINE</h2>
             <p class="text-red-300 mt-4 tracking-widest uppercase text-xl font-bold">Clúster inaccesible en la red</p>
           </div>
        </div>
      {/if}
      <div class="absolute top-8 left-8 text-slate-500 uppercase tracking-widest text-sm font-bold bg-black/40 px-4 py-2 rounded-full border border-white/10">
         Fuente de Datos: <span class="text-white">{modo}</span>
      </div>
      <div class="w-full h-full pt-12">
         <BoliviaMap resultsByDept={currentVotes} dataMode={modo} />
      </div>
    </div>
  </div>
{/snippet}

{#snippet chartsTab()}
  <div class="space-y-6 tab-content">
     <div class="p-10 rounded-3xl bg-white/5 backdrop-blur-2xl border border-white/10">
       <div class="flex justify-between items-end mb-10 border-b border-white/10 pb-6">
          <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Comparativa Global</h2>
          <span class="px-4 py-2 bg-blue-500/20 text-blue-300 text-sm font-bold rounded-full border border-blue-500/30">MODO: {modo}</span>
       </div>
       
       <div class="space-y-8">
         {#each Object.entries(totalVotes) as [cand, votes]}
           <div class="relative group">
             <div class="flex justify-between mb-3">
               <span class="font-black text-xl text-slate-100 tracking-wide">{cand}</span>
               <span class="font-mono text-cyan-400 text-xl">{votes.toLocaleString()} votos</span>
             </div>
             <div class="h-6 w-full bg-black/60 rounded-full overflow-hidden border border-white/10 shadow-inner">
               <div class="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-1000 ease-out relative group-hover:shadow-[0_0_20px_rgba(6,182,212,0.5)]" style="width: {(votes/maxVotes)*100}%">
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
     <div class="p-8 rounded-3xl bg-black/60 backdrop-blur-2xl border border-white/10 h-[700px] flex flex-col shadow-[0_0_30px_rgba(0,0,0,0.5)]">
       <div class="flex justify-between items-center mb-6 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-2xl font-black text-fuchsia-400 font-mono tracking-widest">>> SYSTEM_AUDIT_LOG</h2>
           <div class="flex gap-2 mt-4">
             {#each ['ALL', 'Válida', 'Manchada', 'Ilegible', 'Sistema', 'Invalidada'] as f}
               <button onclick={() => logFilter = f} class="px-3 py-1 text-xs font-bold uppercase tracking-wider rounded-full border transition-all {logFilter === f ? 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/50 shadow-[0_0_10px_rgba(217,70,239,0.3)]' : 'bg-transparent text-slate-500 border-white/10 hover:border-white/30 hover:text-slate-300'}">{f}</button>
             {/each}
           </div>
         </div>
         <span class="px-4 py-1.5 bg-fuchsia-500/20 text-fuchsia-300 text-sm font-bold rounded-full border border-fuchsia-500/30 animate-pulse self-start">LIVE STREAM</span>
       </div>
       <div class="flex-1 overflow-y-auto space-y-4 pr-4 custom-scrollbar">
          {#each filteredLogs as log (log.id)}
             <div class="p-5 rounded-2xl bg-white/5 border border-white/10 flex items-start justify-between group hover:border-white/30 transition-all hover:bg-white/10">
                <div>
                   <div class="flex items-center gap-4 mb-2">
                     <span class="text-xs font-black px-3 py-1 rounded-full uppercase tracking-wider
                       {log.type === 'OK' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 
                        log.type === 'ERR' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                        log.type === 'WARN' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 
                        'bg-blue-500/20 text-blue-400 border border-blue-500/30'}">
                       {log.type}
                     </span>
                     <span class="text-slate-400 text-sm font-mono bg-black/50 px-2 py-0.5 rounded">ID: {log.id.toString().padStart(4, '0')}</span>
                   </div>
                   <p class="text-slate-200 text-lg font-mono mt-2">{log.message}</p>
                </div>
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
                  <button onclick={() => invalidateLog(log.id)} class="px-3 py-2 text-xs font-black uppercase tracking-widest text-orange-400 hover:text-white hover:bg-orange-500 rounded-xl transition-all border border-orange-500/50 shadow-lg">
                    INVALIDAR
                  </button>
                  <button onclick={() => deleteLog(log.id)} class="p-2 text-red-400 hover:text-white hover:bg-red-500 rounded-xl transition-all border border-red-500/50 shadow-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                </div>
             </div>
          {/each}
          {#if filteredLogs.length === 0}
            <div class="h-full flex items-center justify-center text-slate-500 font-mono">
              [ NO LOGS MATCHING FILTER ]
            </div>
          {/if}
       </div>
     </div>
  </div>
{/snippet}

{#snippet infraTab()}
  <div class="tab-content grid grid-cols-2 gap-8 h-[700px]">
     <!-- Oficial Cluster -->
     <div class="p-10 rounded-3xl bg-white/5 backdrop-blur-2xl border {health.db_oficial === 'ONLINE' ? 'border-blue-500/40 shadow-[0_0_40px_rgba(59,130,246,0.15)]' : 'border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.2)]'} relative overflow-hidden flex flex-col">
       {#if health.db_oficial === 'ONLINE'}
         <div class="absolute -right-20 -top-20 w-64 h-64 bg-blue-500/20 blur-[80px] rounded-full"></div>
       {/if}
       <div class="flex justify-between items-start mb-8 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-3xl font-black text-white">CLÚSTER OFICIAL</h2>
           <p class="text-blue-400 font-mono text-sm mt-2 tracking-widest">PORT: 5433 // POSTGRES</p>
         </div>
         <div class="px-5 py-2 rounded-full font-black text-sm uppercase tracking-widest {health.db_oficial === 'ONLINE' ? 'bg-blue-500 text-white shadow-[0_0_20px_rgba(59,130,246,0.8)]' : 'bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.8)] blink'}">
           {health.db_oficial}
         </div>
       </div>
       <div class="space-y-6 flex-1">
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Persistencia</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">Consistencia Estricta</span>
         </div>
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Latencia Media</span>
           <span class="text-xl font-black {health.db_oficial === 'ONLINE' ? 'text-green-400' : 'text-slate-500'}">12ms</span>
         </div>
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Conexiones</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">24/100</span>
         </div>
       </div>
     </div>

     <!-- RRV Cluster -->
     <div class="p-10 rounded-3xl bg-white/5 backdrop-blur-2xl border {health.db_rapido === 'ONLINE' ? 'border-fuchsia-500/40 shadow-[0_0_40px_rgba(217,70,239,0.15)]' : 'border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.2)]'} relative overflow-hidden flex flex-col">
       {#if health.db_rapido === 'ONLINE'}
         <div class="absolute -right-20 -top-20 w-64 h-64 bg-fuchsia-500/20 blur-[80px] rounded-full"></div>
       {/if}
       <div class="flex justify-between items-start mb-8 border-b border-white/10 pb-6">
         <div>
           <h2 class="text-3xl font-black text-white">CLÚSTER RRV</h2>
           <p class="text-fuchsia-400 font-mono text-sm mt-2 tracking-widest">PORT: 5434 // POSTGRES</p>
         </div>
         <div class="px-5 py-2 rounded-full font-black text-sm uppercase tracking-widest {health.db_rapido === 'ONLINE' ? 'bg-fuchsia-500 text-white shadow-[0_0_20px_rgba(217,70,239,0.8)]' : 'bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.8)] blink'}">
           {health.db_rapido}
         </div>
       </div>
       <div class="space-y-6 flex-1">
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Persistencia</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">Velocidad / Append</span>
         </div>
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Latencia Media</span>
           <span class="text-xl font-black {health.db_rapido === 'ONLINE' ? 'text-green-400' : 'text-slate-500'}">3ms</span>
         </div>
         <div class="flex justify-between items-center bg-black/40 p-4 rounded-xl border border-white/5">
           <span class="text-slate-400 text-sm uppercase tracking-widest">Conexiones</span>
           <span class="text-white text-sm font-bold bg-white/10 px-3 py-1 rounded">89/500</span>
         </div>
       </div>
     </div>
  </div>
{/snippet}

<!-- MAIN LAYOUT -->
<div class="min-h-screen bg-[#05050f] text-white p-8 font-sans selection:bg-cyan-500/30">
  
  <!-- Header Control Panel -->
  <div class="header-card mb-8 p-6 rounded-3xl bg-white/5 backdrop-blur-xl border border-white/10 flex justify-between items-center shadow-lg">
    <div class="flex items-center gap-6">
      <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-400 to-fuchsia-500 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
      </div>
      <div>
        <h1 class="text-3xl font-black tracking-tight">ANTIGRAVITY <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">SYSTEM</span></h1>
        <div class="flex gap-3 mt-2">
          <span class="text-xs uppercase tracking-widest text-slate-400 font-bold bg-black/30 px-2 py-0.5 rounded">V.4.0.0</span>
          <span class="text-xs uppercase tracking-widest text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">LIVE</span>
        </div>
      </div>
    </div>
    
    <div class="flex items-center gap-6">
      <div class="text-right">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">DEPLOY MODE</p>
        <p class="text-xl font-black {modo === 'RRV' ? 'text-fuchsia-400' : 'text-blue-400'}">{modo}</p>
      </div>
      <button onclick={toggleModo} class="group relative px-8 py-4 rounded-2xl font-black text-white transition-all overflow-hidden bg-white/5 border border-white/10 hover:border-white/30">
        <div class="absolute inset-0 bg-gradient-to-r {modo === 'RRV' ? 'from-blue-600 to-cyan-500' : 'from-fuchsia-600 to-purple-500'} opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <span class="relative z-10">CAMBIAR A {modo === 'RRV' ? 'OFICIAL' : 'RRV'}</span>
      </button>
    </div>
  </div>

  <div class="grid grid-cols-12 gap-8">
    <!-- Navigation Sidebar -->
    <div class="col-span-3 space-y-3">
      <button onclick={() => switchTab('home')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'home' ? 'bg-gradient-to-r from-cyan-500/20 to-transparent border-cyan-500/50 text-white shadow-[0_0_15px_rgba(6,182,212,0.2)]' : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'}">
        <span class="mr-3">📍</span> Proyecto Home
      </button>
      <button onclick={() => switchTab('map')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'map' ? 'bg-gradient-to-r from-blue-500/20 to-transparent border-blue-500/50 text-white shadow-[0_0_15px_rgba(59,130,246,0.2)]' : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'}">
        <span class="mr-3">🗺️</span> Centro de Cómputo
      </button>
      <button onclick={() => switchTab('charts')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'charts' ? 'bg-gradient-to-r from-indigo-500/20 to-transparent border-indigo-500/50 text-white shadow-[0_0_15px_rgba(99,102,241,0.2)]' : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'}">
        <span class="mr-3">⚖️</span> Comparativa
      </button>
      <button onclick={() => switchTab('logs')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'logs' ? 'bg-gradient-to-r from-fuchsia-500/20 to-transparent border-fuchsia-500/50 text-white shadow-[0_0_15px_rgba(217,70,239,0.2)]' : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'}">
        <span class="mr-3">📑</span> Auditoría de Actas
      </button>
      <button onclick={() => switchTab('infra')} class="w-full text-left px-6 py-5 rounded-2xl font-bold transition-all border {activeTab === 'infra' ? 'bg-gradient-to-r from-purple-500/20 to-transparent border-purple-500/50 text-white shadow-[0_0_15px_rgba(168,85,247,0.2)]' : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:text-white'}">
        <span class="mr-3">🖥️</span> Infraestructura
      </button>
    </div>

    <!-- Main Content Area -->
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
</div>

<style>
  @keyframes pan {
    from { background-position: 0 0; }
    to { background-position: 20px 20px; }
  }
  .blink {
    animation: blinker 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  @keyframes blinker {
    50% { opacity: 0.5; }
  }
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.4);
  }
</style>
