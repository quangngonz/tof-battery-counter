import express from 'express';
import routes from './routes.js';
import cors from 'cors';

const app = express();
app.use(express.json());
app.use(cors());

app.get('/', (req, res) => {
  res.send('Battery Counter API');
});

app.use(routes);

app.listen(3000, () => console.log('🚀 Server running on port 3000'));
