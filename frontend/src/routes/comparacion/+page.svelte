<script>
    import { onMount } from 'svelte';
    import { gsap } from 'gsap';

    onMount(() => {
        gsap.from(".card", { stagger: 0.2, opacity: 0, scale: 0.9, duration: 0.5 });
    });
</script>

<div class="min-h-screen bg-[#0b0e14] text-white p-8">
    <h1 class="text-3xl font-bold font-mono mb-8">CRUCE REFERENCIAL</h1>

    <div class="grid grid-cols-2 gap-8">
      <!-- Tarjeta RRV (Conteo Rápido) -->
      <div class="card bg-[#161b22] p-6 border-l-4 border-blue-500 rounded-xl shadow-lg">
        <h3 class="text-blue-500 font-bold uppercase text-xs mb-4">RRV Cluster B</h3>
        <div class="text-4xl font-black">2,279,194</div>
        <span class="text-slate-400 text-xs italic">Sincronizado vía OCR Bots</span>
      </div>

      <!-- Tarjeta Oficial (Cómputo) -->
      <div class="card bg-[#161b22] p-6 border-l-4 border-emerald-500 rounded-xl shadow-lg">
        <h3 class="text-emerald-500 font-bold uppercase text-xs mb-4">Oficial Cluster A</h3>
        <div class="text-4xl font-black">2,279,194</div>
        <span class="text-slate-400 text-xs italic">Sincronizado vía CSV Oficial</span>
      </div>
    </div>
</div>
