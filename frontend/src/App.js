import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState(""); // State for search query
  const [results, setResults] = useState([]); // State for search results
  const [loading, setLoading] = useState(false); // State for loading indicator
  const [error, setError] = useState(null); // State for error messages

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/search?query=${query}`);
      if (!response.ok) {
        throw new Error("Failed to fetch search results");
      }
      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Local Search Engine</h1>
      <div style={{ marginBottom: "20px" }}>
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
          onClick={handleSearch}
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
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <div>
        {results.length > 0 ? (
          <ul>
            {results.map((result, index) => (
              <li key={index} style={{ marginBottom: "10px" }}>
                <strong>{result.title}</strong>
                <p>{result.snippet}</p>
              </li>
            ))}
          </ul>
        ) : (
          !loading && !error && <p>No results found.</p>
        )}
      </div>
    </div>
  );
}

export default App;