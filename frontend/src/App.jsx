// App shell: routes between the marketing Landing page and the live SOC Dashboard.
// Thin by design — all data + rendering live in views/ and components/.

import { useState } from 'react';
import Landing from './views/Landing';
import Dashboard from './views/Dashboard';

export default function App() {
  const [view, setView] = useState('landing');   // 'landing' | 'dashboard'
  return view === 'landing'
    ? <Landing onEnter={() => setView('dashboard')} />
    : <Dashboard onExit={() => setView('landing')} />;
}
