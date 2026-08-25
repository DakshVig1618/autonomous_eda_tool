<h1>Autonomous EDA Tool</h1>
<p>An automated data profiling, anomaly detection, and preprocessing workflow powered by FastAPI, Google Gemini 3.6 Flash, and isolated Docker execution sandboxes.</p>

<hr>

<h2>Overview</h2>
<p>The <strong>Autonomous EDA Tool</strong> streamlines the initial data exploration and preprocessing phase of machine learning projects.</p>
<p>Instead of writing repetitive exploratory data analysis (EDA) scripts and data cleaning code by hand, you can upload any raw CSV or Excel file to automatically generate schema profiles, detect dataset anomalies, customize cleaning rules via an interactive studio, and execute AI-generated Pandas scripts inside a secure Docker container.</p>

<hr>

<h2>Key Features</h2>

<h3>🔍 Automated Schema &amp; Anomaly Profiling</h3>
<ul>
    <li><strong>Dataset Health Summary:</strong> Instant insight into row counts, column metrics, total missing cells, and duplicate rows.</li>
    <li><strong>Anomaly Detection:</strong> Automatically flags columns with high missing rates (&gt;30%), single-value constant columns, and highly correlated numeric pairs (|r| &gt; 0.85).</li>
    <li><strong>Visual Analytics:</strong> Renders data type breakdowns and column-level missing value distributions using interactive ApexCharts.</li>
</ul>

<h3>🧠 AI-Powered Code Generation</h3>
<ul>
    <li><strong>Vectorized Cleaning Pipelines:</strong> Instructs Gemini to write non-looping, memory-efficient Pandas and NumPy transformation code.</li>
    <li><strong>Custom Preference Overrides:</strong> Combines user choices (such as specific mean/median/mode imputation, one-hot encoding, or column dropping) with intelligent default recommendations.</li>
    <li><strong>Pure Script Generation:</strong> Strips markdown backticks to return clean, runnable Python code.</li>
</ul>

<h3>🐳 Isolated Docker Sandbox</h3>
<ul>
    <li><strong>Network-Isolated Execution:</strong> Runs generated code with <code>--network none</code> to prevent unintended outbound network traffic.</li>
    <li><strong>Automated Image Management:</strong> Detects whether the <code>ai-preprocessing-sandbox</code> image exists on your machine and builds it automatically if missing.</li>
    <li><strong>Unbuffered Real-Time Logs:</strong> Uses <code>PYTHONUNBUFFERED=1</code> to stream container execution logs directly to the browser dashboard.</li>
</ul>

<h3>💻 Fast, Lightweight Interface</h3>
<ul>
    <li><strong>No Node/NPM Dependency:</strong> Built using Python-backed Jinja2 templates, Tailwind CSS, and vanilla JavaScript.</li>
    <li><strong>Clean Folder Separation:</strong> Distinct separation between backend API routes and frontend presentation templates.</li>
    <li><strong>Direct File Export:</strong> Streams the processed dataset (<code>cleaned_&lt;filename&gt;.csv</code>) straight back to your browser.</li>
</ul>

<hr>

<h2>Project Structure</h2>
<pre><code>ai_preprocessing_tool/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── manager.py       # Gemini API orchestration &amp; clean output handler
│   │   │   ├── prompts.py       # System prompts and instructions
│   │   │   └── scanner.py       # EDA scanner &amp; anomaly detection logic
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── process.py   # Transformation request router
│   │   │       └── upload.py    # File upload and download router
│   │   ├── sandbox/
│   │   │   ├── Dockerfile.env   # Execution container environment definition
│   │   │   └── docker_exec.py   # Container execution manager
│   │   └── main.py              # FastAPI app initialization and route mounts
│   ├── uploads/                 # Storage directory for uploaded &amp; cleaned files
│   ├── .env                     # Environment variables (API keys)
│   └── requirements.txt         # Backend dependencies
└── frontend/
    ├── static/
    │   ├── css/
    │   │   └── style.css        # Dashboard visual styling
    │   └── js/
    │       ├── dashboard.js     # Studio interactive logic &amp; chart rendering
    │       └── upload.js        # File upload &amp; dropzone handlers
    └── templates/
        ├── dashboard.html       # EDA studio &amp; execution view
        └── index.html           # Upload landing page</code></pre>

<hr>

<h2>Prerequisites</h2>
<p>Before setting up the project locally, ensure you have the following installed:</p>
<ul>
    <li><strong>Python 3.10</strong> or higher</li>
    <li><strong>Docker Desktop</strong> (must be running in the background)</li>
    <li>A <strong>Google Gemini API Key</strong> (obtainable from <a href="https://aistudio.google.com/">Google AI Studio</a>)</li>
</ul>

<hr>

<h2>Local Setup &amp; Quickstart</h2>

<h3>1. Clone the Repository &amp; Configure .env</h3>
<p>Clone the repository to your local machine:</p>
<pre><code>git clone https://github.com/your-username/autonomous-eda-tool.git
cd autonomous-eda-tool</code></pre>

<p>Create a <code>.env</code> file inside the <code>backend/</code> directory:</p>
<pre><code># File location: backend/.env
GEMINI_API_KEY=your_actual_gemini_api_key_here</code></pre>

<h3>2. Set Up Virtual Environment &amp; Install Dependencies</h3>
<p>Navigate into the <code>backend/</code> folder, set up a virtual environment, and install the required dependencies:</p>
<pre><code>cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt</code></pre>

<h3>3. Run the Backend Server</h3>
<p>Start the Uvicorn development server from inside the <code>backend/</code> directory:</p>
<pre><code>uvicorn app.main:app --reload --port 8000</code></pre>

<h3>4. Open the Web Application</h3>
<p>Open your browser and go to:</p>
<ul>
    <li><strong>App UI:</strong> <code>http://127.0.0.1:8000</code></li>
    <li><strong>API Documentation:</strong> <code>http://127.0.0.1:8000/docs</code></li>
</ul>

<blockquote>
    <p><strong>Note:</strong> On your first processing run, the application will automatically build the required Docker sandbox image if it is not already present on your system.</p>
</blockquote>

<hr>

