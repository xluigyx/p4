<script>
    import '../app.css';
    let { children, data } = $props();
</script>

<div class="min-h-screen bg-[#05050f] text-white font-sans overflow-hidden flex flex-col">
    <!-- Abstract Midnight Glass background effect -->
    <div class="fixed inset-0 z-0 opacity-40 pointer-events-none">
        <div class="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] rounded-full bg-cyan-600 blur-[150px]"></div>
        <div class="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] rounded-full bg-fuchsia-600 blur-[150px]"></div>
    </div>
    
    <main class="relative z-10 flex-1 p-8">
        {@render children()}
    </main>

    <footer class="relative z-10 border-t border-white/5 bg-black/20 backdrop-blur-md py-6 px-8 mt-auto">
        <div class="flex justify-between items-center max-w-7xl mx-auto">
            <p class="text-xs font-mono text-slate-500 tracking-widest uppercase">Sistema de Cómputo Distribuido</p>
            <div class="flex items-center gap-3 group cursor-pointer">
                <div class="h-[1px] w-8 bg-gradient-to-r from-transparent to-cyan-500/50 group-hover:w-16 transition-all duration-500"></div>
                <p class="text-sm font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-fuchsia-500 tracking-widest uppercase"></p>
                <div class="h-[1px] w-8 bg-gradient-to-l from-transparent to-fuchsia-500/50 group-hover:w-16 transition-all duration-500"></div>
            </div>
        </div>
    </footer>
</div>

<style>
    :global(body) {
        margin: 0;
        background-color: #05050f;
    }
</style>
