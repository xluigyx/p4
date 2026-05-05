<script>
    import '../app.css';
</script>

<div class="min-h-screen bg-slate-900 text-white font-sans overflow-hidden">
    <!-- Abstract background effect -->
    <div class="fixed inset-0 z-0 opacity-30">
        <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-600 blur-[120px]"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-600 blur-[120px]"></div>
    </div>
    
    <main class="relative z-10 p-6">
        <slot />
    </main>
</div>

<style>
    :global(body) {
        margin: 0;
        background-color: #0f172a;
    }
</style>
