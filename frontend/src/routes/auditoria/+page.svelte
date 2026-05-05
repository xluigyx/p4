<script>
    import { onMount } from 'svelte';
    
    let logs = [
        { status: 'OK', msg: 'Mesa 10102 procesada por Bot-1' },
        { status: 'ERR', msg: 'Mesa 10502: Acta Manchada - OMITIENDO' },
        { status: 'WARN', msg: 'Mesa 10901: Inconsistencia Aritmética (P1+P2...)' }
    ];
</script>

<div class="min-h-screen bg-[#0b0e14] text-white p-8">
    <h1 class="text-3xl font-bold font-mono mb-8">AUDITORÍA // WAR ROOM</h1>
    
    <div class="grid grid-cols-12 gap-6">
        <!-- Health Check -->
        <div class="col-span-4 space-y-4">
            <div class="bg-[#161b22] p-6 rounded-2xl border border-white/5">
                <h2 class="text-xl font-bold mb-4">Salud del Sistema</h2>
                <div class="flex items-center justify-between p-3 bg-black/40 rounded-xl mb-2">
                    <span class="text-slate-400">Cluster A (Oficial)</span>
                    <span class="text-emerald-500 flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div> Online</span>
                </div>
                <div class="flex items-center justify-between p-3 bg-black/40 rounded-xl">
                    <span class="text-slate-400">Cluster B (RRV)</span>
                    <span class="text-emerald-500 flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div> Sincronizando</span>
                </div>
            </div>
        </div>

        <!-- Terminal OCR -->
        <div class="col-span-8 bg-black/40 p-6 rounded-2xl border border-red-500/20 h-[500px] overflow-y-auto">
            <h2 class="text-red-500 font-mono mb-4">LIVE_OCR_STREAM_LOGS</h2>
            <div class="space-y-2 text-sm font-mono">
                {#each logs as log}
                    <p class="{log.status === 'OK' ? 'text-green-400' : log.status === 'ERR' ? 'text-red-400' : 'text-yellow-400'}">
                        [{log.status}] {log.msg}
                    </p>
                {/each}
            </div>
        </div>

        <!-- Filtro Integridad -->
        <div class="col-span-12 bg-[#161b22] p-6 rounded-2xl border border-white/5 mt-4">
            <h2 class="text-xl font-bold mb-4">Filtro de Integridad</h2>
            <table class="w-full text-left text-sm text-slate-400">
                <thead class="text-xs uppercase bg-black/40 text-slate-300">
                    <tr><th class="p-3">Código Mesa</th><th class="p-3">Oficial</th><th class="p-3">RRV</th><th class="p-3">Diferencia</th><th class="p-3">Estado</th></tr>
                </thead>
                <tbody>
                    <tr class="border-b border-white/5 hover:bg-white/5">
                        <td class="p-3">9050305335016</td><td class="p-3">648</td><td class="p-3">648</td><td class="p-3">0</td>
                        <td class="p-3"><span class="text-green-400 bg-green-400/10 px-2 py-1 rounded">MATCH</span></td>
                    </tr>
                    <tr class="border-b border-white/5 bg-red-500/10 hover:bg-red-500/20">
                        <td class="p-3">9050305335017</td><td class="p-3">500</td><td class="p-3">495</td><td class="p-3 text-red-400">-5</td>
                        <td class="p-3"><span class="text-red-400 bg-red-400/10 px-2 py-1 rounded">MISMATCH</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
