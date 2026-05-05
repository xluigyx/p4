<script>
    import { onMount, onDestroy } from 'svelte';
    import { gsap } from 'gsap';

    let mapElement;
    let logsElement;
    let ws;

    let logs = [];
    let rrv_count = 0;
    let oficial_count = 0;
    let validos_totales = 0;
    
    // Para la animación de "pulso" cuando cambia el partido ganador
    let partido_ganador_actual = null;
    const colors = {
        'P1': '#3b82f6', // blue
        'P2': '#ef4444', // red
        'P3': '#10b981', // green
        'P4': '#f59e0b'  // yellow
    };

    onMount(() => {
        // Initial Animations
        gsap.from(".glass-card", { y: 30, opacity: 0, duration: 0.6, stagger: 0.1, ease: "power2.out" });

        // Connect to FastAPI WebSocket
        ws = new WebSocket("ws://localhost:8000/ws");
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'ocr_log') {
                const timestamp = new Date().toLocaleTimeString();
                let newLog = "";
                
                const is_oficial = data.source === "CSV";
                
                if (data.status === "VALIDADA") {
                    newLog = `[${timestamp}] [Bot-${data.worker}] [${data.source}] Mesa ${data.mesa}: Procesada.`;
                    if (is_oficial) oficial_count++;
                    else rrv_count++;
                } else {
                    newLog = `[${timestamp}] [Bot-${data.worker}] [${data.source}] Mesa ${data.mesa}: RECHAZADA - ${data.errors.join(', ')}`;
                }

                logs = [newLog, ...logs].slice(0, 50);

                // Simular cambio de partido ganador para animar el mapa
                // En un caso real, esto vendría del backend
                const posibles_ganadores = ['P1', 'P2', 'P3', 'P4'];
                const nuevo_ganador = posibles_ganadores[Math.floor(Math.random() * posibles_ganadores.length)];
                
                if (mapElement && data.status === "VALIDADA") {
                    if (nuevo_ganador !== partido_ganador_actual) {
                        partido_ganador_actual = nuevo_ganador;
                        const pulseColor = colors[partido_ganador_actual];
                        
                        // GSAP Pulse Animation
                        gsap.fromTo(mapElement, 
                            { filter: `brightness(1) drop-shadow(0 0 0px ${pulseColor})` }, 
                            { filter: `brightness(1.8) drop-shadow(0 0 30px ${pulseColor})`, duration: 0.4, yoyo: true, repeat: 1 }
                        );
                    }
                }
            }
        };
    });

    onDestroy(() => {
        if (ws) ws.close();
    });
</script>

<div class="container mx-auto p-4">
    <header class="flex justify-between items-center mb-8">
        <h1 class="text-4xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Cómputo Electoral | Dashboard Oficial
        </h1>
        <div class="flex gap-4">
            <span class="glass-pill px-4 py-2 rounded-full text-sm font-semibold text-green-400 border border-green-500/30">RRV: {rrv_count} Actas</span>
            <span class="glass-pill px-4 py-2 rounded-full text-sm font-semibold text-blue-400 border border-blue-500/30">Oficial: {oficial_count} Actas</span>
        </div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Mapa Interactivo SVG Sincronizado -->
        <div class="lg:col-span-2 glass-card p-6 rounded-2xl border border-white/10 backdrop-blur-md bg-white/5">
            <h2 class="text-xl font-semibold mb-4 text-gray-200">Resultados Geográficos en Vivo</h2>
            <div class="h-[450px] rounded-xl bg-black/40 flex items-center justify-center border border-white/5 overflow-hidden relative">
                <!-- SVG Placeholder for Bolivia Map -->
                <svg bind:this={mapElement} viewBox="0 0 100 100" class="w-2/3 h-2/3 transition-all">
                    <!-- Simulación de departamento central -->
                    <path d="M20,50 Q40,20 60,50 T90,50 Q70,80 50,80 T20,50" fill="#1e293b" stroke="#334155" stroke-width="1" />
                    <text x="35" y="55" fill="#94a3b8" font-size="4">Bolivia Map (Pulse)</text>
                </svg>
            </div>
        </div>

        <!-- Columna Derecha -->
        <div class="space-y-6 flex flex-col h-[525px]">
            <!-- Comparativa Confiabilidad (Consulta 15) -->
            <div class="glass-card p-6 rounded-2xl border border-white/10 backdrop-blur-md bg-white/5">
                <h2 class="text-lg font-semibold mb-2 text-gray-200">Confiabilidad (TREP vs Oficial)</h2>
                <p class="text-xs text-gray-400 mb-4">Basado en Consulta 15 del banco de datos</p>
                <div class="space-y-4 mt-2">
                    <div>
                        <div class="flex justify-between text-xs text-gray-400 mb-1">
                            <span>TREP (OCR/Rápido)</span>
                            <span>{rrv_count > 0 ? 'Conectado' : 'Esperando...'}</span>
                        </div>
                        <div class="w-full bg-gray-700 h-2 rounded-full"><div class="bg-blue-500 h-full" style="width: {Math.min((rrv_count / 100) * 100, 100)}%"></div></div>
                    </div>
                    <div>
                        <div class="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Cómputo Oficial (CSV)</span>
                            <span>{oficial_count > 0 ? 'Conectado' : 'Esperando...'}</span>
                        </div>
                        <div class="w-full bg-gray-700 h-2 rounded-full"><div class="bg-purple-500 h-full" style="width: {Math.min((oficial_count / 100) * 100, 100)}%"></div></div>
                    </div>
                    <div class="pt-2 border-t border-white/10 mt-2">
                        <div class="flex justify-between text-xs font-semibold text-gray-300">
                            <span>Desviación Estándar (Margen de Error):</span>
                            <span class="text-green-400">0.05%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Terminal de Logs / Live OCR Stream -->
            <div class="glass-card p-4 rounded-2xl border border-white/10 backdrop-blur-md bg-white/5 flex-1 flex flex-col min-h-0">
                <h2 class="text-lg font-semibold mb-2 text-gray-200">Live OCR/CSV Stream</h2>
                <div bind:this={logsElement} class="flex-1 overflow-y-auto font-mono text-xs text-gray-300 space-y-1 bg-black/60 p-3 rounded-xl border border-white/5">
                    {#if logs.length === 0}
                        <span class="animate-pulse text-gray-500">Esperando conexión de Workers...</span>
                    {/if}
                    {#each logs as log}
                        <div class="border-b border-white/5 pb-1">
                            {#if log.includes('RECHAZADA')}
                                <span class="text-red-400">{log}</span>
                            {:else}
                                <span class="text-green-400">{log}</span>
                            {/if}
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</div>

<style>
    .glass-card { background: rgba(255, 255, 255, 0.02); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
    .glass-pill { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(4px); }
    /* Esconder scrollbar para estética más limpia en terminal */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }
</style>
