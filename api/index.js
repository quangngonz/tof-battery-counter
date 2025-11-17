import express from 'express';
import routes from './routes.js';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());
app.use(cors());

// Serve favicon
app.use(
  '/favicon.ico',
  express.static(path.join(__dirname, 'public', 'favicon.ico'))
);

app.get('/', (req, res) => {
  res.send('Battery Counter API');
});

app.use(routes);

// For local development
if (process.env.NODE_ENV !== 'production') {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
}

// Export for Vercel
export default app;
