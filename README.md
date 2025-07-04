# vision-llm-brand-compliance

A workflow to automatically assess image compliance against a brand’s guidelines (logo usage, safe‑zone, colors, typography) using a vision language model. 


An overview of the pipeline:
![Screenshot 2025-05-10 at 12 52 03 PM](https://github.com/user-attachments/assets/29f6a40c-e031-407a-b9ef-f2e9bc991423)



## Features
- Parses a brand‑kit (PDF format) to extract rules (logo, safe‑zone, color palette, typography).
- Builds a custom system prompt based on the rules for a vision language model.  
- Sends image + system prompt to Mistral’s VLM API and outputs JSON scores.  
- Returns a score (Range 0 - 4) with reasoning for each category.  
- Containerized with Docker.

## Local Development
1. Clone the repo
2. Create a .env file and inside the file set:
   ```bash
   MISTRAL_API_KEY = "add your API key here"
3. Build the docker image
   ```bash
   docker build -t brand-backend .
4. Run the container
   ```bash
   docker run --rm -p 8000:8000 --env-file .env brand-backend
5. Test with Postman
   - Create a POST request to http://localhost:8000/check_brand_guidelines.
   - Under "Body" select form‑data and add 2 keys (brand_kit and image). Upload the data of type "File"
   - Hit send and get the response. 
       
