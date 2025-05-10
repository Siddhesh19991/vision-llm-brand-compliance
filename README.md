# vision-llm-brand-compliance

A workflow to automatically assess image compliance against a brand’s guidelines (logo usage, safe‑zone, colors, typography) using a vision language model. 


An overview of the pipeline:



## Features
- Parses a brand‑kit (PDF format) to extract rules (logo, safe‑zone, color palette, typography)  
- Builds a custom system prompt based on the rules for a vision language model  
- Sends image + system prompt to Mistral’s VLM API and parses JSON scores  
- Returns a 0–4 score with reasoning for each category  
- Fully containerized with Docker

## Local Development
1. Clone the repo
2. Create a .env file and inside the file set:
   ```bash
   MISTRAL_API_KEY = "add your API key here"
4. Build the docker image
   ```bash
   docker build -t brand-backend .
6. Run the container
   ```bash
   docker run --rm -p 8000:8000 --env-file .env brand-backend
8. Test with Postman
   - Create a POST request to http://localhost:8000/check_brand_guidelines.
   - Under "Body" select form‑data and add 2 keys (brand_kit and image). Upload the data of type "File"
   - Hit send and get the response. 
       
