# Hospital Triage Specialist Recommendation API

This is a minimal FastAPI service that leverages a Large Language Model (LLM) to recommend a specialist department in a hospital based on patient's gender, age, and reported symptoms.

## Features

* **Intelligent Recommendations:** Uses Google Gemini via Langchain to provide relevant department suggestions.
* **FastAPI:** Built on a modern, fast (high-performance) web framework.
* **Pydantic Validation:** Ensures robust input and output data validation.
* **Containerization Ready:** Easy to package and deploy.

## Prerequisites

* Python 3.9+
* `pip` (Python package installer)

## Installation

1.  **Clone the repository (if applicable) or create the project structure:**
    ```bash
    git clone https://github.com/Andi-Fuad/technical-test.git
    cd technical-test/case 3
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

**Important Update:** Ensure your `langchain`, `langchain-core`, `langchain-google-genai` packages are up to date to avoid import errors and ensure compatibility:
```bash
pip install --upgrade langchain langchain-core langchain-google-genai
```

## API Key Setup

1.  **Obtain Google Gemini API Key:**
    * Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
    * Create or select an existing API key.
2.  **Create `.env` file:**
    In the root directory of your project, create a file named `.env` and add your API key:
    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    ```
    **Important:** Do not commit your `.env` file to version control. It's already included in the `.gitignore` for this project.

## Determine Gemini Models
If you have specific Gemini model that you want to try, Update main.py: Open main.py and replace the placeholder GEMINI_MODEL_ID = "models/gemini-1.5-flash" with the exact Model ID you want (e.g., GEMINI_MODEL_ID = "models/gemini-1.0-pro").

If you don't have any specific Gemini model that you want to try, then you don't have to change anything.

**> Note:**  Some models might not be available due to regional or billing restrictions.

## How to Run

Once you've set up your virtual environment and API key:

1.  **Start the FastAPI application using Uvicorn:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    * `main`: Refers to the `main.py` file.
    * `app`: Refers to the `FastAPI()` instance named `app` inside `main.py`.
    * `--reload`: Automatically reloads the server on code changes (useful during development).
    * `--host 0.0.0.0`: Makes the server accessible from other devices on your network.
    * `--port 8000`: Runs the server on port 8000.

    You should see output similar to:
    ```
    INFO:     Uvicorn running on [http://0.0.0.0:8000](http://0.0.0.0:8000) (Press CTRL+C to quit)
    INFO:     Started reloader process [xxxxx]
    INFO:     Started server process [xxxxx]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

## How to Test

You can test the API using `curl`, Postman, Insomnia, or by accessing the interactive API documentation provided by FastAPI (Swagger UI/ReDoc).

1.  **Access Interactive Docs (Swagger UI):** <br>
    This is the easiest way to test your API locally:
    1. **Access Swagger UI:** Open your web browser and navigate to: http://localhost:8000/docs
    2. **Expand the Endpoint:** Click on the POST /recommend endpoint to expand its details.
    3. **Try it Out:** Click the "Try it out" button on the right side of the endpoint description.
    4. **Edit Request Body:** You can now edit the example value in the "Request body" field. Modify the gender, age, and symptoms to your desired test values.
        Example: 
        ```bash
        {
          "gender": "female",
          "age": 62,
          "symptoms": [
            "pusing", "mual", "sulit berjalan"
          ]
        }
        ```
    5. **Execute:** Click the "Execute" button to send the request.
    6. **View Response:** The recommended_department will be displayed in the "Response body" section below, along with the HTTP status code.

2.  **Example `curl` Command:** <br>
    Open a new terminal (**bash**) and run:
    ```bash
    curl -X POST "http://localhost:8000/recommend" \
         -H "Content-Type: application/json" \
         -d '{
               "gender": "female",
               "age": 62,
               "symptoms": ["pusing", "mual", "sulit berjalan"]
             }'
    ```

    **Expected Output:**
    ```json
    {
      "recommended_department": "Neurology"
    }
    ```

    **Another Example:**
    ```bash
    curl -X POST "http://localhost:8000/recommend" \
         -H "Content-Type: application/json" \
         -d '{
               "gender": "male",
               "age": 35,
               "symptoms": ["batuk", "sesak nafas", "demam tinggi"]
             }'
    ```

    **Expected Output (e.g.):**
    ```json
    {
      "recommended_department": "Pulmonology/Respiratory"
    }
    ```

## Error Handling

* **Invalid Input:** FastAPI's Pydantic validation will automatically return a `422 Unprocessable Entity` error for invalid JSON payloads.
* **Internal Server Errors:** If the LLM call fails or returns an unexpected format, the service will return a `500 Internal Server Error`.
