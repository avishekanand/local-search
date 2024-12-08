
# **Local Search Engine**

This is a simple local search engine with a React frontend and a FastAPI backend. Follow the steps below to set up and start the project.

---

## **Prerequisites**

- **Docker** and **Docker Compose** installed
- Node.js and npm (for local frontend testing, optional)
- A terminal for running commands

---

## **Project Structure**

```
project-root/
├── backend/          # FastAPI backend code
├── frontend/         # React frontend code
├── docker-compose.yml
```

---

## **Steps to Run**

### **1. Clone the Repository**
```bash
git clone <repository_url>
cd project-root
```

---

### **2. Start the Backend and Frontend (Docker)**

Run the following command from the project root to start both services using Docker Compose:
```bash
docker compose up
```

- **Backend:** Runs at [http://localhost:8000](http://localhost:8000)
- **Frontend:** Runs at [http://localhost:3000](http://localhost:3000)

---

### **3. Backend (FastAPI)**

#### **Direct Access**
To test the backend independently:
1. Navigate to the `backend/` directory.
2. Start the backend server (if not using Docker):
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

#### **Test API**
- Open your browser or use `curl` to test the `/search` endpoint:
  ```bash
  curl "http://localhost:8000/search?query=test"
  ```

---

### **4. Frontend (React)**

#### **Start Locally (Optional)**
If you prefer running the frontend locally without Docker:
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### **5. Troubleshooting**

#### **CORS Issues**
Ensure the FastAPI backend allows cross-origin requests. The CORS middleware is already configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### **Frontend Not Rendering**
- Verify the React frontend is pointing to the correct backend URL in `frontend/src/utils/api.js`:
  ```javascript
  export const fetchSearchResults = async (query) => {
      const response = await fetch(`http://localhost:8000/search?query=${query}`);
      return response.json();
  };
  ```

#### **Clear Docker Cache**
If services are not starting correctly:
```bash
docker compose down
docker system prune -af
docker compose up
```

---

### **6. Verify Functionality**

- Open [http://localhost:3000](http://localhost:3000) in your browser.
- Enter a query in the search box and see the results from the backend.

---
