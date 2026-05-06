import { MongoClient } from 'mongodb';
import pg from 'pg';

const { Pool } = pg;

export async function load() {
    const fallback = { 
        oficial: { total: 0, candidatos: { Lannister: 0, Targaryen: 0, Baratheon: 0, Stark: 0 } },
        rrv: { total: 0, candidatos: { Lannister: 0, Targaryen: 0, Baratheon: 0, Stark: 0 } },
        logs: [],
        status: "DB_OFFLINE"
    };

    const candMap = { 'P1': 'Lannister', 'P2': 'Targaryen', 'P3': 'Baratheon', 'P4': 'Stark' };

    try {
        let oficialData = { total: 0, candidatos: { Lannister: 0, Targaryen: 0, Baratheon: 0, Stark: 0 } };
        let rrvData = { total: 0, candidatos: { Lannister: 0, Targaryen: 0, Baratheon: 0, Stark: 0 } };
        let auditLogs = [];
        
        // MongoDB (Oficial) Connection
        try {
            const mongoClient = new MongoClient(process.env.DB_OFICIAL || 'mongodb://db_oficial:27017/oficial_db', { serverSelectionTimeoutMS: 2000 });
            await mongoClient.connect();
            const db = mongoClient.db();
            const agg = await db.collection('actas_oficiales').aggregate([
                { $group: { 
                    _id: null, 
                    Lannister: { $sum: "$votos.lannister" },
                    Targaryen: { $sum: "$votos.targaryen" },
                    Baratheon: { $sum: "$votos.baratheon" },
                    Stark: { $sum: "$votos.stark" }
                } }
            ]).toArray();
            
            if (agg.length > 0) {
                const doc = agg[0];
                oficialData.candidatos['Lannister'] = doc.Lannister || 0;
                oficialData.candidatos['Targaryen'] = doc.Targaryen || 0;
                oficialData.candidatos['Baratheon'] = doc.Baratheon || 0;
                oficialData.candidatos['Stark'] = doc.Stark || 0;
                oficialData.total = (doc.Lannister || 0) + (doc.Targaryen || 0) + (doc.Baratheon || 0) + (doc.Stark || 0);
            }

            const docs = await db.collection('actas_oficiales').find({}).limit(5396).toArray();
            auditLogs = docs.map((d, i) => ({
                id: d.id_acta || `ACT-${i}`,
                time: `10:${String(Math.floor((i/60)%60)).padStart(2, '0')}:${String(i%60).padStart(2, '0')}`,
                source: d.source || 'CSV',
                link: '#',
                status: d.status || 'EXITO',
                reason: d.reason || '-'
            }));

            await mongoClient.close();
        } catch (e) {
            console.error("Error MongoDB (Oficial):", e);
        }

        // PostgreSQL (RRV) Connection
        try {
            const pgPool = new Pool({ connectionString: process.env.DB_RAPIDO || 'postgresql://postgres:bolivia_vota@db_rapido:5432/rrv_db', connectionTimeoutMillis: 2000 });
            const res = await pgPool.query('SELECT candidato, SUM(votos) as total FROM transcripciones GROUP BY candidato');
            res.rows.forEach(row => {
                const name = candMap[row.candidato] || row.candidato;
                const v = parseInt(row.total) || 0;
                if (rrvData.candidatos[name] !== undefined) {
                    rrvData.candidatos[name] += v;
                    rrvData.total += v;
                }
            });
            await pgPool.end();
        } catch (e) {
            console.error("Error PostgreSQL (RRV):", e);
        }

        return { 
            oficial: oficialData, 
            rrv: rrvData, 
            logs: auditLogs,
            status: "OK" 
        };
    } catch (error) {
        console.error("Fallo inesperado:", error);
        return fallback;
    }
}