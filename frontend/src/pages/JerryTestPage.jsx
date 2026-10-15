import React, { useState } from "react";

export default function JerryTestPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function makeUser(event) {
    event.preventDefault();

    const body = new URLSearchParams({
      email,
      password,
    });

    const response = await fetch("http://localhost:5000/createUser", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body,
    });

    const data = await response.json();
    console.log(data);
  }

  return (
    <>
      <h1>Jerry Test Page</h1>

      <h2>Make User Form</h2>

      <form onSubmit={makeUser}>
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <br />


        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />

        <button type="submit">Submit</button>
      </form>

      <h2>Login Form</h2>
    </>
  );
}