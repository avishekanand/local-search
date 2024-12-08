export const fetchSearchResults = async (query) => {
    const response = await fetch(`http://localhost:8000/search?query=${query}`);
    if (!response.ok) {
        throw new Error("Failed to fetch search results");
    }
    return response.json();
};