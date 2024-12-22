import React, { useState } from "react";
import Header from "./components/Header";
import SearchInput from "./components/SearchInput";
import ResultsPane from "./components/ResultsPane";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch search results from the backend
  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/search?query=${query}`);
      if (!response.ok) {
        throw new Error("Failed to fetch search results");
      }
      const data = await response.json();
      setResults(
        data.results.map((result) => ({
          title: result.title,
          requirements: result.requirements,
          description: result.description,
          score: result.score,
        }))
      );
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div>
      <Header title="Example Search Engine" />
      <SearchInput query={query} setQuery={setQuery} onSearch={handleSearch} />
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ResultsPane results={results} />
    </div>
  );
}

export default App;