import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException

# --- 1. Load Environment Variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- 2. Input Validation: Ensure API Key is Available ---
if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please ensure it's set in a .env file or as an environment variable."
    )

# --- 3. Define Pydantic Models for API Request and Response ---
class PatientInfo(BaseModel):
    """
    Schema for incoming patient information.
    """
    gender: str = Field(..., description="Patient's gender (e.g., 'male', 'female'.")
    age: int = Field(..., description="Patient's age.")
    symptoms: List[str] = Field(..., description="List of patient's reported symptoms (e.g., ['sakit', 'cough', 'headache']).")

class DepartmentRecommendation(BaseModel):
    """
    Schema for the outgoing recommended department.
    """
    recommended_department: str = Field(..., description="The specialist department recommended by the system.")

# --- 4. Langchain Setup for LLM Interaction ---

# Define the expected output schema for the LLM.
class LLMDepartmentOutput(BaseModel):
    recommended_department: str = Field(description="The name of the recommended specialist department.")

# Create an output parser for JSON responses.
parser = JsonOutputParser(pydantic_object=LLMDepartmentOutput)

# Define Gemini Models
# Common alternatives: "models/gemini-1.5-flash"
GEMINI_MODEL_ID = "models/gemini-1.5-flash"

# Initialize the Large Language Model (LLM).
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL_ID, temperature=0.0, google_api_key=GOOGLE_API_KEY)

# Construct the full system message content with embedded format_instructions
system_message_content = (
    "You are a highly experienced and accurate hospital triage assistant. "
    "Your task is to recommend the single most appropriate specialist department based on patient details. "
    "The patient symptoms will be provided in Bahasa Indonesia. "
    "Your response MUST be a JSON object with a single key 'recommended_department' and its value being the department name in English. "
    "Adhere strictly to the following JSON schema:\n"
    f"{parser.get_format_instructions().replace('{', '{{').replace('}', '}}')}\n\n"
    "Example Output: {{'recommended_department': 'Neurology'}}\n\n"
    "Consider common medical departments such as: Cardiology, Dentistry, Dermatology, General Medicine, Neurology, "
    "Neurosurgery, Pathology, Plastic & Reconstruction Surgery, Psychiatry, Radiology, Rehabilitation Medicine, "
    "Orthopaedics, Urology, Emergency, Obstetrics & Gynaecology, Pulmonology/Respiratory, Nephrology, Internal Medicine, "
    "General Surgery, Ophthalmology, ENT (Ear, Nose, Throat), Paediatrics. "
    "If a specific department isn't perfectly clear, choose the most general but appropriate one (e.g., Internal Medicine or Emergency)."
)


# Define the prompt template for the LLM.
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message_content),
    ("human", (
        "Patient Gender: {gender}\n"
        "Patient Age: {age}\n"
        "Patient Symptoms (Bahasa Indonesia): {symptoms}\n\n"
        "Based on this information, what is the recommended department?"
    ))
])

# Create a Langchain chain.
recommendation_chain = prompt | llm | parser

# --- 5. Initialize FastAPI Application ---

app = FastAPI(
    title="Hospital Triage Specialist Recommendation API",
    description="An API that recommends specialist hospital departments based on patient symptoms, gender, and age using a Google Gemini LLM.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- 6. Define the API Endpoint ---

@app.post(
    "/recommend",
    response_model=DepartmentRecommendation,
    summary="Recommend Specialist Department",
    description="Accepts patient gender, age, and a list of symptoms, and returns a recommended specialist department."
)
async def recommend_department(patient_info: PatientInfo):
    """
    Handles POST requests to /recommend to suggest a specialist department.

    Args:
        patient_info (PatientInfo): An object containing patient's gender, age, and symptoms.

    Returns:
        DepartmentRecommendation: An object containing the recommended department name.

    Raises:
        HTTPException: If an error occurs during the LLM recommendation process.
    """
    try:
        chain_input = {
            "gender": patient_info.gender,
            "age": patient_info.age,
            "symptoms": ", ".join(patient_info.symptoms)
        }

        # Invoke the Langchain chain.
        raw_response = await recommendation_chain.ainvoke(chain_input)

        try:
            llm_response = LLMDepartmentOutput(**raw_response)
        except ValidationError as ve:
            raise HTTPException(
                status_code=500,
                detail=f"LLM response validation failed: {ve}"
            )

        recommended_department = llm_response.recommended_department

        return DepartmentRecommendation(recommended_department=recommended_department)

    except OutputParserException as e:
        print(f"Output parsing error: {e}")
        error_detail = f"LLM output could not be parsed. This often means the LLM did not return valid JSON or did not follow the schema. Error: {e}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    except Exception as e:
        print(f"General error during recommendation process: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal server error occurred: {str(e)}. Please check the server logs. "
                   "Ensure the correct LLM model ID is specified and your API key is valid."
        )
