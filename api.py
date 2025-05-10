from helper import extract_text_from_page, model_response, parse_llm_json, total_score
from script import run_chain
from fastapi import FastAPI, UploadFile, File
import os


app = FastAPI()

#creating a temp directory to save the uploaded files
os.makedirs("temp", exist_ok=True)


@app.post("/check_brand_guidelines")
async def check_brand_guidelines(brand_kit: UploadFile = File(...) , image: UploadFile = File(...)):

    # Save the uploaded files to a temporary location
    brand_kit_path = os.path.join("temp", brand_kit.filename)
    image_path = os.path.join("temp", image.filename)

    with open(brand_kit_path, "wb") as f:
        f.write(await brand_kit.read())
    
    with open(image_path, "wb") as f:
        f.write(await image.read())
      
    try:
      report = run_chain(brand_kit_path, image_path)
    except Exception as e:
      return {"error": "An error occurred while processing the request. Details: " + str(e)}

    return report




