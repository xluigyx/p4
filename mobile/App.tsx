import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import * as SQLite from 'expo-sqlite';
import NetInfo from '@react-native-community/netinfo';
// import { Camera } from 'expo-camera'; // Un-comment when adding real camera

const API_URL = 'http://192.168.100.192:8000/api/upload';

// Abrir la base de datos de SQLite
const db = SQLite.openDatabaseSync('actas.db');

export default function App() {
  const [transcription, setTranscription] = useState('');
  const [status, setStatus] = useState('Online');
  const [queueCount, setQueueCount] = useState(0);

  useEffect(() => {
    // Inicializar tabla
    db.execAsync(
      `CREATE TABLE IF NOT EXISTS actas_queue (
        id TEXT PRIMARY KEY,
        imageUri TEXT NOT NULL,
        transcription TEXT,
        timestamp TEXT NOT NULL
      );`
    ).then(() => {
      updateQueueCount();
    }).catch(e => console.error("Error creating table", e));

    // Escuchar cambios de red
    const unsubscribe = NetInfo.addEventListener(state => {
      setStatus(state.isConnected ? 'Online' : 'Offline');
      if (state.isConnected) {
        syncPendingData();
      }
    });

    return () => unsubscribe();
  }, []);

  const updateQueueCount = async () => {
    try {
      const result = await db.getAllAsync<{count: number}>('SELECT COUNT(*) as count FROM actas_queue;');
      setQueueCount(result[0]?.count || 0);
    } catch (e) {
      console.error("Error al contar", e);
    }
  };

  const handleCapture = async () => {
    // Simulación: en producción se usaría la URI de la cámara de Expo
    const mockImageUri = `file://dummy/path/acta_${Date.now()}.jpg`;
    const newId = Date.now().toString();
    const timestamp = new Date().toISOString();

    try {
      // 1. Guardar en SQLite (Offline-First)
      await db.runAsync(
        'INSERT INTO actas_queue (id, imageUri, transcription, timestamp) VALUES (?, ?, ?, ?);',
        [newId, mockImageUri, transcription, timestamp]
      );
      
      setTranscription('');
      updateQueueCount();
      Alert.alert("Éxito", "Acta guardada localmente en SQLite.");

      // 2. Intentar Sincronizar Inmediatamente si hay Red
      if (status === 'Online') {
        syncPendingData();
      }
    } catch (error) {
      console.error("Error al guardar acta en SQLite", error);
    }
  };

  const syncPendingData = async () => {
    try {
      const queue = await db.getAllAsync<any>('SELECT * FROM actas_queue ORDER BY timestamp ASC;');
      if (queue.length === 0) return;

      for (const acta of queue) {
        try {
          // Enviar por multipart a FastAPI
          const formData = new FormData();
          
          formData.append("file", {
              uri: acta.imageUri,
              name: `acta_${acta.id}.jpg`,
              type: 'image/jpeg'
          } as any);
          
          formData.append("transcription", acta.transcription || '');

          const response = await fetch(API_URL, {
            method: 'POST',
            body: formData,
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          if (!response.ok) {
             throw new Error(`Server error: ${response.status}`);
          }

          // Si el envío fue exitoso, eliminar de SQLite
          await db.runAsync('DELETE FROM actas_queue WHERE id = ?;', [acta.id]);

        } catch (err) {
          console.warn(`Falló subida de acta ${acta.id}, se mantendrá en SQLite...`, err);
          // Si falla, se queda en la DB para la próxima sincronización
        }
      }

      updateQueueCount();

    } catch (e) {
      console.error("Error en sincronización batch", e);
    }
  };

  return (
    <View style={styles.container}>
      <View style={[styles.header, { backgroundColor: status === 'Online' ? '#10b981' : '#ef4444' }]}>
        <Text style={styles.headerText}>{status === 'Online' ? '✅ En Línea - Sincronizando' : '⚠️ Fuera de Línea - Modo Local'}</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Escáner Oficial</Text>
        
        <View style={styles.cameraPlaceholder}>
          <Text style={styles.cameraText}>[ Vista de la Cámara ]</Text>
        </View>

        <TextInput
          style={styles.input}
          placeholder="Transcripción de emergencia (Opcional)"
          placeholderTextColor="#666"
          value={transcription}
          onChangeText={setTranscription}
          multiline
        />

        <TouchableOpacity style={styles.button} onPress={handleCapture}>
          <Text style={styles.buttonText}>Capturar Acta</Text>
        </TouchableOpacity>

        <View style={styles.queueContainer}>
          <Text style={styles.queueText}>Cola SQLite pendiente: {queueCount} actas</Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' },
  header: { paddingTop: 50, paddingBottom: 15, alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.3, shadowRadius: 5 },
  headerText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  content: { padding: 20 },
  title: { fontSize: 26, fontWeight: '800', color: 'white', marginBottom: 20, textAlign: 'center', letterSpacing: 1 },
  cameraPlaceholder: { height: 250, backgroundColor: '#1e293b', borderRadius: 15, justifyContent: 'center', alignItems: 'center', marginBottom: 20, borderWidth: 1, borderColor: '#334155' },
  cameraText: { color: '#64748b', fontSize: 16 },
  input: { backgroundColor: '#1e293b', color: 'white', padding: 15, borderRadius: 10, minHeight: 80, textAlignVertical: 'top', marginBottom: 20, borderWidth: 1, borderColor: '#334155' },
  button: { backgroundColor: '#3b82f6', padding: 18, borderRadius: 12, alignItems: 'center', shadowColor: '#3b82f6', shadowOpacity: 0.4, shadowRadius: 10, shadowOffset: {width: 0, height: 4} },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 18 },
  queueContainer: { marginTop: 30, padding: 15, backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 10, borderWidth: 1, borderColor: 'rgba(255, 255, 255, 0.1)' },
  queueText: { color: '#fbbf24', textAlign: 'center', fontWeight: '600' }
});
