<script>
  import { onMount } from 'svelte';
  import { gsap } from 'gsap';

  let modo = 'RRV'; // Switch: RRV o OFICIAL[cite: 2]
  let logs = []; // Aquí caerán los logs de los bots

  function toggleModo() {
    modo = modo === 'RRV' ? 'OFICIAL' : 'RRV';
    // Animación de transición "Stitch"[cite: 2]
    gsap.to(".map-container", { duration: 0.5, filter: "hue-rotate(90deg)", yoyo: true, repeat: 1 });
  }

  onMount(() => {
    gsap.from(".card", { stagger: 0.2, opacity: 0, y: 20 });
  });
</script>

<div class="min-h-screen bg-[#0b0e14] text-white p-8">
  <div class="flex justify-between items-center mb-10">
    <h1 class="text-3xl font-bold font-mono">ANTIGRAVITY // DEPLOY_MODE: {modo}</h1>
    
    <!-- SWITCH RRV / OFICIAL[cite: 2] -->
    <button on:click={toggleModo} class="bg-blue-600 px-6 py-2 rounded-full font-bold hover:bg-blue-500 transition">
      CAMBIAR A {modo === 'RRV' ? 'OFICIAL' : 'RRV'}
    </button>
  </div>

  <div class="grid grid-cols-12 gap-6">
    <!-- MAPA INTERACTIVO (Simplificado) -->
    <div class="col-span-8 bg-[#161b22] rounded-3xl p-10 border border-white/5 map-container">
      <div class="text-center text-slate-500 mb-4 uppercase tracking-widest text-xs">Distribución Territorial</div>
      <div class="h-[500px] flex items-center justify-center border-2 border-dashed border-white/10 rounded-2xl">
         <!-- Aquí inserta tu SVG de Bolivia con IDs por depto[cite: 2] -->
         <span class="text-blue-400 animate-pulse">Mapa de Bolivia Activo (GSAP Ready)</span>
      </div>
    </div>

    <!-- LIVE LOGS DE LOS BOTS[cite: 2] -->
    <div class="col-span-4 space-y-6">
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
