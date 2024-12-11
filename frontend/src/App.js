// import React, { useState } from "react";

// function App() {
//   const [query, setQuery] = useState(""); // State for search query
//   const [results, setResults] = useState([]); // State for search results
//   const [loading, setLoading] = useState(false); // State for loading indicator
//   const [error, setError] = useState(null); // State for error messages

//   // Fetch search results from the backend
//   const handleSearch = async () => {
//     setLoading(true);
//     setError(null);
//     try {
//       const response = await fetch(`http://localhost:8000/search?query=${query}`);
//       if (!response.ok) {
//         throw new Error("Failed to fetch search results");
//       }
//       const data = await response.json();
//       setResults(
//         data.results.map((result) => ({
//           title: result.title, // Map the title field
//           requirements: result.requirements,
//           description: result.description, // Map the description field
//           score: result.score, // Map the score field
//         }))
//       );

//       console.log("Search Results:", results);
//     } catch (err) {
//       console.error(err);
//       setError(err.message);
//     }
//     setLoading(false);
//   };

//   return (
//     <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
//       <h1>Local Search Engine</h1>
//       <div style={{ marginBottom: "20px" }}>
//         <input
//           type="text"
//           placeholder="Enter your search query"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           style={{
//             padding: "10px",
//             width: "300px",
//             marginRight: "10px",
//             border: "1px solid #ccc",
//             borderRadius: "4px",
//           }}
//         />
//         <button
//           onClick={handleSearch}
//           style={{
//             padding: "10px 15px",
//             backgroundColor: "#007BFF",
//             color: "white",
//             border: "none",
//             borderRadius: "4px",
//             cursor: "pointer",
//           }}
//         >
//           Search
//         </button>
//       </div>
//       {loading && <p>Loading...</p>}
//       {error && <p style={{ color: "red" }}>{error}</p>}
//       <div>
//         {results.length > 0 ? (console.log("Rendering Results") || (
//           <ul>
//             {results.map((result, index) => (
//               <li
//                 key={index}
//                 style={{
//                   marginBottom: "20px",
//                   padding: "15px",
//                   border: "1px solid #ddd",
//                   borderRadius: "8px",
//                   backgroundColor: "#f9f9f9",
//                 }}
//               >
//                 <strong
//                   style={{
//                     color: "#007BFF",
//                     fontSize: "18px",
//                     fontWeight: "bold",
//                     fontFamily: "'Arial', sans-serif",
//                   }}
//                 >
//                   {result.title}
//                 </strong>
//                 <p
//                   style={{
//                     margin: "10px 0 5px 0",
//                     fontFamily: "'Roboto', sans-serif",
//                     fontSize: "14px",
//                     color: "#333",
//                   }}
//                 >
//                   {result.description}
//                 </p>
//                 <p
//                   style={{
//                     margin: "5px 0",
//                     fontFamily: "'Roboto', sans-serif",
//                     fontSize: "14px",
//                     color: "#333",
//                   }}
//                 >
//                   <strong>Requirements:</strong> {result.requirements}
//                 </p>
//                 <small
//                   style={{
//                     display: "block",
//                     marginTop: "10px",
//                     fontSize: "12px",
//                     color: "#555",
//                     fontFamily: "'Arial', sans-serif",
//                   }}
//                 >
//                   Relevance Score: {result.score.toFixed(2)}
//                 </small>
//               </li>
//             ))}
//           </ul>
//         )
//         ) : (
//           !loading && !error && <p>No results found.</p>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;

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
      <Header title="Local Search Engine" />
      <SearchInput query={query} setQuery={setQuery} onSearch={handleSearch} />
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ResultsPane results={results} />
    </div>
  );
}

export default App;