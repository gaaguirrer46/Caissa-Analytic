const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const dbPath = path.join(__dirname, 'caissa.db');
const schemaPath = path.join(__dirname, 'schema.sql');

console.log('--- Inicializando Base de Datos Caissa Analytics ---');
console.log(`Archivo de esquema: ${schemaPath}`);
console.log(`Destino BD: ${dbPath}`);

if (fs.existsSync(dbPath)) {
  fs.unlinkSync(dbPath);
  console.log('Base de datos anterior eliminada.');
}

const sql = fs.readFileSync(schemaPath, 'utf8');
const db = new DatabaseSync(dbPath);

db.exec(sql);
console.log('✓ Esquema y datos semilla aplicados correctamente.\n');

// Verificación de tablas creadas
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;").all();
console.log(`Total de tablas creadas: ${tables.length}`);
tables.forEach(t => console.log(`  - ${t.name}`));

// Consulta de verificación
console.log('\n--- Ejecutando Consulta de Verificación ---');
const query = `
SELECT 
    a.nombre AS Atleta,
    a.rating_clasicas AS Rating_Actual,
    o.descripcion AS Objetivo_SMART,
    o.rating_meta AS Rating_Meta,
    p.evento AS Ultima_Partida,
    p.resultado AS Resultado_Partida,
    at.accuracy AS Precision_Partida
FROM atletas a
LEFT JOIN objetivos_smart o ON a.id = o.id_atleta
LEFT JOIN partidas p ON a.id = p.id_atleta
LEFT JOIN analisis_tecnico_partidas at ON p.id = at.id_partida;
`;

const result = db.prepare(query).all();
console.log(JSON.stringify(result, null, 2));

db.close();
console.log('\n✓ Base de datos caissa.db inicializada con éxito.');
