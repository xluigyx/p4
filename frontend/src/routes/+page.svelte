<script>
  import { onMount, onDestroy } from 'svelte';
  import { gsap } from 'gsap';
  import { invalidateAll } from '$app/navigation';
  import BoliviaMap from '$lib/BoliviaMap.svelte';

  let { data } = $props();

  let modo = $state('RRV');
  let activeTab = $state('home'); 
  let healthInterval;

  // Health checks using data from +page.server.js
  let health = $derived({ 
    db_rapido: data.status === 'OK' ? 'ONLINE' : 'OFFLINE', 
    db_oficial: data.status === 'OK' ? 'ONLINE' : 'OFFLINE', 
    backend: data.status === 'OK' ? 'ONLINE' : 'OFFLINE' 
  });

  let mockVotesRRV = $state({
    'LP': { Lannister: 1200, Targaryen: 800, Baratheon: 400, Stark: 150 },
    'SC': { Lannister: 500, Targaryen: 1500, Baratheon: 200, Stark: 800 },
    'CB': { Lannister: 800, Targaryen: 600, Baratheon: 300, Stark: 100 },
    'OR': { Lannister: 300, Targaryen: 200, Baratheon: 100, Stark: 50 },
    'PT': { Lannister: 250, Targaryen: 250, Baratheon: 100, Stark: 50 },
    'TJ': { Lannister: 150, Targaryen: 400, Baratheon: 200, Stark: 100 },
    'CH': { Lannister: 200, Targaryen: 300, Baratheon: 100, Stark: 50 },
    'BE': { Lannister: 100, Targaryen: 400, Baratheon: 150, Stark: 200 },
    'PA': { Lannister: 50, Targaryen: 100, Baratheon: 50, Stark: 80 }
  });

  let mockVotesOficial = $state({
    'LP': { Lannister: 1210, Targaryen: 805, Baratheon: 400, Stark: 150 },
    'SC': { Lannister: 505, Targaryen: 1510, Baratheon: 202, Stark: 800 },
    'CB': { Lannister: 800, Targaryen: 600, Baratheon: 300, Stark: 100 },
    'OR': { Lannister: 300, Targaryen: 200, Baratheon: 100, Stark: 50 },
    'PT': { Lannister: 252, Targaryen: 255, Baratheon: 100, Stark: 50 },
    'TJ': { Lannister: 150, Targaryen: 400, Baratheon: 200, Stark: 100 },
    'CH': { Lannister: 200, Targaryen: 300, Baratheon: 100, Stark: 50 },
    'BE': { Lannister: 100, Targaryen: 400, Baratheon: 150, Stark: 200 },
    'PA': { Lannister: 50, Targaryen: 100, Baratheon: 50, Stark: 80 }
  });

  let currentVotes = $derived(modo === 'RRV' ? mockVotesRRV : mockVotesOficial);

  let logs = $derived(data.logs && data.logs.length > 0 ? data.logs : []);

  let displayLogs = $derived(logs);

  let totalVotes = $derived.by(() => {
    let totals = { Lannister: 0, Targaryen: 0, Baratheon: 0, Stark: 0 };
    const src = modo === 'RRV' ? data.rrv.candidatos : data.oficial.candidatos;
    return src;
  });

  let processed = $derived(data.actasRecibidas || 0);
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
    <div class="p-10 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 relative overflow-hidden group">
      <div class="absolute inset-0 bg-gradient-to-br from-[#FFD700]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000"></div>
      <h2 class="text-5xl font-black text-slate-100 mb-6 tracking-tighter drop-shadow-md">CONSEJO DE PONIENTE</h2>
      <p class="text-slate-400 leading-relaxed text-xl font-light max-w-3xl relative z-10">
        Plataforma de monitoreo de élite con alta disponibilidad y tolerancia a fallos extrema.
      </p>
      
      <div class="grid grid-cols-3 gap-8 mt-12 relative z-10">
         <div class="p-8 rounded-xl bg-[#0f172a] border border-white/5 text-center shadow-inner hover:border-[#FFD700]/30 transition-colors">
            <h3 class="text-slate-500 font-bold text-sm tracking-widest mb-3">TRANSPARENCIA</h3>
            <p class="text-4xl font-black text-slate-200">100%</p>
         </div>
         <div class="p-8 rounded-xl bg-[#0f172a] border border-white/5 text-center shadow-inner hover:border-[#FFD700]/30 transition-colors">
            <h3 class="text-[#FFD700] font-bold text-sm tracking-widest mb-3">ESTADO GENERAL</h3>
            <p class="text-4xl font-black {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.3)]' : 'text-rose-500'}">
               {health.db_rapido === 'ONLINE' && health.db_oficial === 'ONLINE' ? 'ÓPTIMA' : 'DEGRADADA'}
            </p>
         </div>
         <div class="p-8 rounded-xl bg-[#0f172a] border border-white/5 text-center shadow-inner hover:border-[#FFD700]/30 transition-colors">
            <h3 class="text-slate-500 font-bold text-sm tracking-widest mb-3">ACTAS INGRESADAS</h3>
            <p class="text-4xl font-black text-slate-200">5,396</p>
         </div>
      </div>
    </div>
  </div>
{/snippet}

{#snippet mapTab()}
  <div class="tab-content relative map-container h-full">
    <div class="p-8 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 h-[700px] flex flex-col items-center justify-center relative overflow-hidden">
      {#if (modo === 'RRV' && health.db_rapido === 'OFFLINE') || (modo === 'OFICIAL' && health.db_oficial === 'OFFLINE')}
        <div class="absolute inset-0 bg-red-950/80 backdrop-blur-md flex items-center justify-center z-10 border-4 border-rose-500/30">
           <div class="text-center">
             <h2 class="text-7xl font-black text-rose-500 font-mono tracking-widest">OFFLINE</h2>
             <p class="text-rose-400 mt-4 tracking-widest uppercase text-xl font-bold">Clúster inaccesible en la red</p>
           </div>
        </div>
      {/if}
      <div class="absolute top-8 left-8 text-slate-400 uppercase tracking-widest text-sm font-bold bg-[#0f172a] px-4 py-2 rounded-full border border-white/5 z-10 shadow-md">
         Fuente de Datos: <span class="text-[#FFD700]">{modo}</span>
      </div>
      <div class="w-full h-full pt-12 relative z-0">
         <BoliviaMap resultsByDept={data.rrv.candidatos} dataMode={modo} />
      </div>
    </div>
  </div>
{/snippet}

{#snippet chartsTab()}
  <div class="space-y-6 tab-content">
     <div class="p-10 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5">
       <div class="flex justify-between items-end mb-10 border-b border-white/5 pb-6">
          <h2 class="text-3xl font-black text-slate-100">Comparativa Global</h2>
          {#if data.desync}
            <span class="px-4 py-2 bg-rose-500/20 text-rose-500 text-sm font-bold rounded-full border border-rose-500/30 animate-pulse">DESINCRONIZACIÓN DETECTADA</span>
          {:else}
            <span class="px-4 py-2 bg-[#0f172a] text-[#FFD700] text-sm font-bold rounded-full border border-white/5">DB SYNC OK</span>
          {/if}
       </div>
       
       <div class="grid grid-cols-2 gap-12">
         <!-- RRV -->
         <div class="space-y-8">
           <h3 class="text-xl font-bold text-slate-400 mb-6 uppercase tracking-widest border-b border-white/5 pb-2">Votos por Imagen (RRV)</h3>
           {#each Object.entries(data.rrv.candidatos) as [cand, votes]}
             <div class="relative group">
               <div class="flex justify-between mb-3">
                 <span class="font-black text-lg text-slate-200 tracking-wide uppercase">{cand}</span>
                 <span class="font-mono text-slate-400 text-lg">{votes.toLocaleString()}</span>
               </div>
               <div class="h-4 w-full bg-[#0f172a] rounded-full overflow-hidden border border-white/5 shadow-inner">
                 <div class="h-full rounded-full transition-all duration-1000 ease-out" 
                      style="width: {data.rrv.total > 0 ? Math.min((votes/data.rrv.total)*100, 100) : 0}%; background-color: {cand === 'Lannister' ? '#FFD700' : cand === 'Targaryen' ? '#E11D48' : cand === 'Baratheon' ? '#FACC15' : '#94A3B8'}">
                 </div>
               </div>
             </div>
           {/each}
         </div>
         
         <!-- Oficial -->
         <div class="space-y-8 border-l border-white/5 pl-12">
           <h3 class="text-xl font-bold text-slate-400 mb-6 uppercase tracking-widest border-b border-white/5 pb-2">Votos por Registro (Oficial)</h3>
           {#each Object.entries(data.oficial.candidatos) as [cand, votes]}
             <div class="relative group">
               <div class="flex justify-between mb-3">
                 <span class="font-black text-lg text-slate-200 tracking-wide uppercase">{cand}</span>
                 <span class="font-mono text-slate-400 text-lg">{votes.toLocaleString()}</span>
               </div>
               <div class="h-4 w-full bg-[#0f172a] rounded-full overflow-hidden border border-white/5 shadow-inner">
                 <div class="h-full rounded-full transition-all duration-1000 ease-out" 
                      style="width: {data.oficial.total > 0 ? Math.min((votes/data.oficial.total)*100, 100) : 0}%; background-color: {cand === 'Lannister' ? '#FFD700' : cand === 'Targaryen' ? '#E11D48' : cand === 'Baratheon' ? '#FACC15' : '#94A3B8'}">
                 </div>
               </div>
             </div>
           {/each}
         </div>
       </div>
     </div>
  </div>
{/snippet}

{#snippet logsTab()}
  <div class="tab-content">
     <div class="p-8 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 flex flex-col">
       <div class="flex justify-between items-center mb-6 border-b border-white/5 pb-6">
          <div>
            <h2 class="text-2xl font-black text-slate-100 font-mono tracking-widest">BITÁCORA TÉCNICA</h2>
            <p class="text-slate-400 text-sm mt-2 font-mono">Registro inmutable de auditoría procesada.</p>
          </div>
          <span class="px-4 py-1.5 bg-[#0f172a] text-[#FFD700] text-sm font-bold rounded-full border border-white/5 flex items-center gap-2 shadow-sm">
            <span class="w-2 h-2 rounded-full bg-[#FFD700] animate-ping"></span> LIVE SYNC
          </span>
       </div>
       
       <div class="overflow-y-auto max-h-[600px] flex-1 custom-scrollbar pr-2">
         <table class="w-full text-left text-slate-300 text-sm">
           <thead class="text-xs uppercase bg-[#0f172a] text-slate-500 sticky top-0 z-10 shadow-sm">
             <tr>
               <th scope="col" class="px-6 py-4 font-bold">Hora</th>
               <th scope="col" class="px-6 py-4 font-bold">Fuente</th>
               <th scope="col" class="px-6 py-4 font-bold">Acta</th>
               <th scope="col" class="px-6 py-4 font-bold">Resultado</th>
               <th scope="col" class="px-6 py-4 font-bold">Detalle</th>
             </tr>
           </thead>
           <tbody>
             {#each displayLogs as log (log.id)}
               <tr class="border-b border-white/5 hover:bg-white/5 transition-colors">
                 <td class="px-6 py-4 font-mono text-xs text-slate-400">{log.time}</td>
                 <td class="px-6 py-4">
                   <span class="px-2 py-1 rounded text-xs font-bold border bg-rose-500/10 text-rose-400 border-rose-500/20">
                     {log.source}
                   </span>
                 </td>
                 <td class="px-6 py-4"><a href={log.link} class="text-[#FFD700] hover:text-yellow-200 hover:underline font-bold transition-colors">{log.id}</a></td>
                 <td class="px-6 py-4">
                   <div class="flex items-center gap-2">
                     {#if log.status === 'ANULABLE' || log.status === 'OBSERVADA' || log.status === 'MANCHA_DETECTADA'}
                       <svg class="w-4 h-4 {log.status === 'MANCHA_DETECTADA' ? 'text-red-500 scale-125' : 'text-rose-500'} animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                     {/if}
                     <span class="px-2 py-1 rounded text-xs font-bold {log.status === 'EXITO' ? 'bg-emerald-500/10 text-emerald-400' : (log.status === 'ANULABLE' || log.status === 'MANCHA_DETECTADA') ? 'bg-rose-500/10 text-rose-500 border border-rose-500/30' : 'bg-orange-500/10 text-orange-400'}">
                       {log.status}
                     </span>
                   </div>
                 </td>
                 <td class="px-6 py-4 font-mono text-xs {log.status === 'OBSERVADO' ? 'text-orange-400' : 'text-slate-500'}">
                   {log.reason}
                 </td>
               </tr>
             {/each}
           </tbody>
         </table>
         {#if displayLogs.length === 0}
            <div class="py-10 text-center text-slate-500 font-mono">
              [ NO HAY REGISTROS EN LA BITÁCORA ]
            </div>
         {/if}
       </div>
     </div>
  </div>
{/snippet}

{#snippet infraTab()}
  <div class="tab-content flex flex-col gap-6 h-[700px]">
    <div class="grid grid-cols-2 gap-6">
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 flex items-center justify-between">
        <div>
          <h3 class="font-bold text-slate-200 text-lg">MongoDB OF</h3>
          <p class="text-xs text-slate-500 font-mono">PORT: 27017</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full {health.db_oficial === 'ONLINE' ? 'bg-emerald-400' : 'bg-rose-400'} opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 {health.db_oficial === 'ONLINE' ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
          </span>
          <span class="text-sm font-bold {health.db_oficial === 'ONLINE' ? 'text-emerald-500' : 'text-rose-500'}">{health.db_oficial === 'ONLINE' ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 flex items-center justify-between">
        <div>
          <h3 class="font-bold text-slate-200 text-lg">PostgreSQL RRV</h3>
          <p class="text-xs text-slate-500 font-mono">PORT: 5432</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full {health.db_rapido === 'ONLINE' ? 'bg-emerald-400' : 'bg-rose-400'} opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 {health.db_rapido === 'ONLINE' ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
          </span>
          <span class="text-sm font-bold {health.db_rapido === 'ONLINE' ? 'text-emerald-500' : 'text-rose-500'}">{health.db_rapido === 'ONLINE' ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>
    </div>

    <div class="p-8 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 flex-1 flex flex-col">
      <h3 class="font-black text-slate-100 text-xl mb-8">Avance de Procesamiento</h3>
      <div class="space-y-8 flex-1 justify-center flex flex-col">
        <div>
          <div class="flex justify-between mb-2">
            <span class="text-sm font-bold text-slate-400">Reportes RRV recibidos</span>
            <span class="text-sm font-bold text-slate-400">{Math.min(processed, 5396)} / 5396</span>
          </div>
          <div class="w-full bg-[#0f172a] rounded-full h-6 border border-white/5 shadow-inner">
            <div class="bg-emerald-500 h-full rounded-full transition-all duration-1000 shadow-[0_0_15px_rgba(16,185,129,0.3)]" style="width: {Math.min((processed/5396)*100, 100)}%"></div>
          </div>
        </div>
        <div>
          <div class="flex justify-between mb-2">
            <span class="text-sm font-bold text-slate-400">Procesados / Validados</span>
            <span class="text-sm font-bold text-slate-400">{Math.min(processed * 0.95, 5396).toFixed(0)}</span>
          </div>
          <div class="w-full bg-[#0f172a] rounded-full h-6 border border-white/5 shadow-inner">
            <div class="bg-cyan-500 h-full rounded-full transition-all duration-1000" style="width: {Math.min(((processed * 0.95)/5396)*100, 100)}%"></div>
          </div>
        </div>
        <div>
          <div class="flex justify-between mb-2">
            <span class="text-sm font-bold text-slate-400">Pendientes sin reporte / Observados</span>
            <span class="text-sm font-bold text-slate-400">{Math.max(0, 5396 - processed)}</span>
          </div>
          <div class="w-full bg-[#0f172a] rounded-full h-6 border border-white/5 shadow-inner">
            <div class="bg-slate-700 h-full rounded-full transition-all duration-1000" style="width: {Math.max(0, Math.min(((5396 - processed)/5396)*100, 100))}%"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-4 gap-6">
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 text-center">
        <p class="text-xs text-slate-500 font-bold mb-1 tracking-widest">REGISTRADAS</p>
        <p class="text-3xl font-black text-slate-100">5,396</p>
      </div>
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 text-center">
        <p class="text-xs text-slate-500 font-bold mb-1 tracking-widest">RECIBIDAS</p>
        <p class="text-3xl font-black text-blue-400">{data.actasRecibidas}</p>
      </div>
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 text-center">
        <p class="text-xs text-slate-500 font-bold mb-1 tracking-widest">OBSERVADAS</p>
        <p class="text-3xl font-black text-orange-400">{(data.actasRecibidas * 0.05).toFixed(0)}</p>
      </div>
      <div class="p-6 rounded-2xl bg-[#1e293b] shadow-xl border border-white/5 text-center">
        <p class="text-xs text-slate-500 font-bold mb-1 tracking-widest">PENDIENTES</p>
        <p class="text-3xl font-black text-rose-400">{Math.max(5396 - data.actasRecibidas, 0)}</p>
      </div>
    </div>
  </div>
{/snippet}

<div class="min-h-screen bg-[#0f172a] text-slate-200 p-8 font-sans selection:bg-[#FFD700]/30 overflow-x-hidden flex">
  <div class="w-24 shrink-0 flex flex-col items-center py-10 border-r border-white/5 mr-8 h-[calc(100vh-4rem)] sticky top-8 bg-[#1e293b] rounded-3xl shadow-xl">
    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#FFD700] to-yellow-500 flex items-center justify-center shadow-[0_0_20px_rgba(255,215,0,0.4)] mb-12">
      <svg class="w-6 h-6 text-slate-900" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
    </div>
    <div class="flex-1 flex flex-col gap-8 w-full items-center">
      <button onclick={() => switchTab('home')} class="p-3 rounded-xl transition-all duration-300 group {activeTab === 'home' ? 'bg-[#0f172a] text-[#FFD700]' : 'text-slate-500'}">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
      </button>
      <button onclick={() => switchTab('map')} class="p-3 rounded-xl transition-all duration-300 group {activeTab === 'map' ? 'bg-[#0f172a] text-[#FFD700]' : 'text-slate-500'}">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
      </button>
      <button onclick={() => switchTab('charts')} class="p-3 rounded-xl transition-all duration-300 group {activeTab === 'charts' ? 'bg-[#0f172a] text-[#FFD700]' : 'text-slate-500'}">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
      </button>
      <button onclick={() => switchTab('logs')} class="p-3 rounded-xl transition-all duration-300 group {activeTab === 'logs' ? 'bg-[#0f172a] text-[#FFD700]' : 'text-slate-500'}">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
      </button>
      <button onclick={() => switchTab('infra')} class="p-3 rounded-xl transition-all duration-300 group {activeTab === 'infra' ? 'bg-[#0f172a] text-[#FFD700]' : 'text-slate-500'}">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path></svg>
      </button>
    </div>
  </div>

  <div class="flex-1 max-w-[1400px] mx-auto flex flex-col">
    <div class="header-card mb-8 p-6 rounded-2xl bg-[#1e293b] border border-white/5 flex justify-between items-center shadow-xl">
      <div>
        <h1 class="text-3xl font-black tracking-tight text-slate-100">CONSEJO DE <span class="text-[#FFD700]">PONIENTE</span></h1>
        <div class="flex gap-3 mt-2">
          <span class="text-xs uppercase tracking-widest text-slate-400 font-bold bg-[#0f172a] px-2 py-0.5 rounded border border-white/5">V.4.2</span>
          <span class="text-xs uppercase tracking-widest text-emerald-400 font-bold bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-500/20">SINCRO TOTAL</span>
        </div>
      </div>
      <div class="flex items-center gap-6">
        <div class="text-right">
          <p class="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">FUENTE ACTUAL</p>
          <p class="text-xl font-black text-[#FFD700]">{modo}</p>
        </div>
        <button onclick={toggleModo} class="px-6 py-3 rounded-xl font-bold text-slate-900 bg-[#FFD700] hover:bg-yellow-400 shadow-[0_0_15px_rgba(255,215,0,0.3)] transition-all">
          CAMBIAR FUENTE
        </button>
      </div>
    </div>

    <div class="flex-1 relative">
      {#if activeTab === 'home'} {@render homeTab()} 
      {:else if activeTab === 'map'} {@render mapTab()}
      {:else if activeTab === 'charts'} {@render chartsTab()}
      {:else if activeTab === 'logs'} {@render logsTab()}
      {:else if activeTab === 'infra'} {@render infraTab()}
      {/if}
    </div>
  </div>
</div>

<style>
  .custom-scrollbar::-webkit-scrollbar { width: 6px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.3); border-radius: 4px; }
</style>
