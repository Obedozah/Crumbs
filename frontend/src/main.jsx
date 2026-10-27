import { createRoot } from 'react-dom/client'
import { StrictMode } from 'react'
import { BrowserRouter } from 'react-router-dom'
import { FirebaseUIProvider } from '@firebase-oss/ui-react'
import { ui } from './lib/firebase.js'
import { AuthProvider } from './context/AuthContext.jsx'
import '@firebase-oss/ui-styles/dist.min.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
        <FirebaseUIProvider ui={ui}>
            <AuthProvider>
                <App />
            </AuthProvider>
        </FirebaseUIProvider>
    </BrowserRouter>
  </StrictMode>,
)
