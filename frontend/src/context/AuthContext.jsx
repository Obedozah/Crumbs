import { createContext, useState, useContext } from "react";

const AuthContext = createContext();

const STORAGE_KEY = "crumbs-user";

function loadUser() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY));
    } catch {
        return null;
    }
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(loadUser);

    function saveUser(nextUser) {
        setUser(nextUser);
        try {
            if (nextUser) {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(nextUser));
            } else {
                localStorage.removeItem(STORAGE_KEY);
            }
        } catch {
            // storage unavailable, user just won't persist across refreshes
        }
    }

    // Pseudo auth for now: any email/password works.
    // Gonna replace with real auth api
    async function login(email, _password) {
        saveUser({ email });
        return true;
    }

    async function register(email, _password) {
        saveUser({ email });
        return true;
    }

    async function loginWithGoogle() {
        saveUser({ email: "demo@crumbs.app" });
        return true;
    }

    function logout() {
        saveUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, login, register, loginWithGoogle, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
