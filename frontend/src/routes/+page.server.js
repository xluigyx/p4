export async function load({ fetch }) {
    try {
        const res = await fetch("http://backend:8000/api/health");
        if (res.ok) {
            const healthData = await res.json();
            return {
                health: healthData
            };
        }
    } catch (e) {
        console.error("Failed to fetch health from backend:", e);
    }
    
    // Fallback if backend is not reachable
    return {
        health: { db_rapido: 'OFFLINE', db_oficial: 'OFFLINE' }
    };
}
