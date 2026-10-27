import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { initializeUI, providerPopupStrategy } from "@firebase-oss/ui-core";

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

if (!firebaseConfig.apiKey) {
    throw new Error(
        "Missing Firebase config. Copy frontend/.env.example to frontend/.env and fill in your Firebase web app values."
    );
}

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

export const ui = initializeUI({
    app,
    auth,
    behaviors: [providerPopupStrategy()],
});
