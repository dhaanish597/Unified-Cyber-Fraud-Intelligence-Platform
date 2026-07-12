# Unified Cyber-Fraud Intelligence Platform

The Unified Cyber-Fraud Intelligence Platform bridges the gap between siloed cybersecurity logs (SIEM) and financial transaction fraud models. By fusing network-level cyber compromise signals with real-time transactional behavior and graph-based entity relationships, this platform delivers unparalleled fraud detection. Our approach catches sophisticated, multi-channel attacks that traditional models miss, increasing true positive detection rates while maintaining a strict 0.5% false positive budget—ultimately saving money and preserving customer trust.

## Documentation

* [Architecture Diagram](Docs/architecture.md): A visual representation of the built slice versus the deck-only production layer.
* [PS2 Coverage](Docs/ps2_coverage.md): Mapping of PS2 expected outcomes to exact UI elements and API endpoints.

## How to Run

Follow these steps from a clean clone to run the entire pipeline from data generation to the web UI.

### 1. Data Generation
Generate the raw transactional and synthetic cyber overlay data.
```bash
python data/generate_data.py
```

### 2. Network Graph Features (Overlay)
Compute node embeddings and PageRank features based on the transaction network.
```bash
python graph/compute_graph.py
```

### 3. Model Training
Train the tabular LightGBM model, the Isolation Forest for anomaly detection, and evaluate the fusion uplift.
```bash
python ml/train.py
```

### 4. Run the API
Start the FastAPI backend that serves the Risk Engine.
```bash
cd api
uvicorn main:app --reload --port 8000
```

### 5. Run the Web App
Start the Vite/React frontend dashboard.
```bash
cd web
npm install
npm run dev
```

## Deployment

### API Deployment (Render/Docker)
The `api/Dockerfile` contains the exact instructions to build and run the backend. 
To deploy to a service like Render:
1. Connect your GitHub repository to Render.
2. Select **New Web Service**.
3. Choose the repository and specify the `api` folder as the Root Directory.
4. Render will automatically detect the `Dockerfile` and build it.

### Web Deployment (Vercel)
To deploy the frontend to Vercel:
1. Install the Vercel CLI: `npm i -g vercel`
2. Navigate to the web directory: `cd web`
3. Run `vercel` and follow the prompts to link the project.
4. Run `vercel --prod` to deploy to production.
Alternatively, you can connect the GitHub repo directly in the Vercel Dashboard, specifying `web` as the Root Directory and using `npm run build` as the Build Command.
