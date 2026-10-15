import { createContext, useState, useContext } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState({ username: "test" });

    async function login(username, password) {
        // Gonna replace with real auth api
        if (username === "test" && password === "password") {
            setUser({ username });
            return true;
        } else {
            return false;
        }
    }

    function logout() {
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}