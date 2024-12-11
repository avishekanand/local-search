import React from "react";
import "../styles/ResultPane.css";

const ResultsPane = ({ results }) => {
  return (
    <div style={{ padding: "20px" }}>
      {results.length > 0 ? (
        <ul style={{ listStyleType: "none", padding: 0 }}>
          {results.map((result, index) => (
            <li
              key={index}
              style={{
                marginBottom: "20px",
                padding: "15px",
                border: "1px solid #ddd",
                borderRadius: "8px",
                backgroundColor: "#f9f9f9",
              }}
            >
              <strong style={{ color: "#007BFF", fontSize: "18px", fontWeight: "bold" }}>
                {result.title}
              </strong>
              <p style={{ margin: "10px 0", fontSize: "14px", color: "#333" }}>
                {result.description}
              </p>
              <p style={{ margin: "5px 0", fontSize: "14px", color: "#333" }}>
                <strong>Requirements:</strong> {result.requirements}
              </p>
              <small style={{ fontSize: "12px", color: "#555" }}>
                Relevance Score: {result.score.toFixed(2)}
              </small>
            </li>
          ))}
        </ul>
      ) : (
        <p>No results found.</p>
      )}
    </div>
  );
};

export default ResultsPane;