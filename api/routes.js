import express from 'express';
import { logBattery, getLogs } from './routes/log.js';
import { getStats } from './routes/stats.js';

const router = express.Router();

router.get('/logs', getLogs);
router.post('/log', logBattery);
router.get('/stats', getStats);

export default router;
