import React from "react";

const Header = ({ title }) => {
  return (
    <header style={{ padding: "20px", textAlign: "center", backgroundColor: "#f4f4f4" }}>
      <h1 style={{ fontFamily: "'Arial', sans-serif", color: "#007BFF" }}>{title}</h1>
    </header>
  );
};
    
export default Header;