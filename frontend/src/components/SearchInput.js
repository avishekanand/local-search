import React from "react";

const SearchInput = ({ query, setQuery, onSearch }) => {
  return (
    <div style={{ textAlign: "center", margin: "20px" }}>
      <input
        type="text"
        placeholder="Enter your search query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          padding: "10px",
          width: "300px",
          marginRight: "10px",
          border: "1px solid #ccc",
          borderRadius: "4px",
        }}
      />
      <button
        onClick={onSearch}
        style={{
          padding: "10px 15px",
          backgroundColor: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Search
      </button>
    </div>
  );
};

export default SearchInput;