const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');


const DATASTREAMS = [
  { UUID: '1002345', color: { r: 0, g: 0, b: 255 }, type: 'sine' },
  { UUID: '299345', color: { r: 255, g: 0, b: 0 }, type: 'square' }
];


function generateSineWave(time, frequency = 1.0, amplitude = 1.0, sampleRate = 60) {
  return amplitude * Math.sin(2 * Math.PI * frequency * time / sampleRate);
}

function generateSquareWave(time, frequency = 1.0, amplitude = 1.0, sampleRate = 60) {
  return ((Math.floor(time / (sampleRate / (2 * frequency))) % 2) === 0) ? amplitude : -amplitude;
}


const app = express();
app.use(cors({ origin: 'http://localhost:4200' }));


app.get('/v1/get_devices', (req, res) => {
  const response = {
    datastreams: DATASTREAMS.map(ds => ({ UUID: ds.UUID, color: ds.color }))
  };
  res.json(response);
});


const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/v1/subscribe_ws' });

wss.on('connection', (ws) => {
  console.log('Client connected to WebSocket');

  let sendDataInterval = null;

  ws.on('message', (message) => {
    const command = message.toString().trim().split(/\s+/);
    if (command.length === 0) return;

    const uuidSet = new Set(DATASTREAMS.map(ds => ds.UUID));
    const uuids = command.filter(token => uuidSet.has(token));
    if (uuids.length === 0) {
      ws.send(JSON.stringify({ error: 'No valid UUIDs provided' }));
      return;
    }

    const sampleRate = parseInt(command[command.length - 2]) || 60;
    const outputFormat = command[command.length - 1] || 'json';

    const selectedDatastreams = DATASTREAMS.filter(ds => uuids.includes(ds.UUID));
    const deviceOrder = selectedDatastreams.map(ds => ds.UUID);

    if (sendDataInterval) clearInterval(sendDataInterval);

    sendDataInterval = setInterval(() => {
      const realTimestamp = Date.now() / 1000;

      const dataRow = selectedDatastreams.map(ds => {
        return ds.type === 'sine'
          ? parseFloat(generateSineWave(realTimestamp).toFixed(3))
          : generateSquareWave(realTimestamp);
      });

      const sampleData = {
        timestamp: parseFloat(realTimestamp.toFixed(3)),
        datastreams: deviceOrder,
        data: [dataRow]
      };

      if (outputFormat === 'json') {
        ws.send(JSON.stringify(sampleData));
      } else if (outputFormat === 'csv') {
        const csvData = `${sampleData.timestamp},${dataRow.join(',')}`;
        ws.send(csvData);
      }
    }, 1000 / sampleRate);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    if (sendDataInterval) clearInterval(sendDataInterval);
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
  });
});

const PORT = 8080;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT} (HTTP & WebSocket)`);
});

// Graceful Shutdown
function shutdown() {
  console.log('Shutting down...');
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.close(1001, 'Server shutting down');
    }
  });
  server.close(() => {
    console.log('Server stopped cleanly.');
    process.exit(0);
  });
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
