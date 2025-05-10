import pandas as pd
import numpy as np
import os
import json
import pymupdf
import re
import base64
import mimetypes
from mistralai import Mistral
from dotenv import load_dotenv
import logging


# setting up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
#    filename="app.log",       
#    filemode="a"              
)

logger = logging.getLogger(__name__)


############################# brand kit pdf extraction ###############################
# Table of contents information
def toc(pdf_path):

  try:
    doc = pymupdf.open(pdf_path)
  except Exception as e:
    raise RuntimeError(f"Failed to open PDF '{pdf_path}': {e}")

  # Finding the page number of the table of contents
  toc_page_index = None
  for i in range(len(doc)):
    text = doc.load_page(i).get_text()
    if re.search(r'Table of Contents', text, re.IGNORECASE):
      toc_page_index = i
      break

  #print(toc_page_index)

  if toc_page_index is None:
    logger.info("Table of contents page was not found")
    raise ValueError("Could not find a page containing 'Table of Contents'")

  text = ""
  page = doc.load_page(toc_page_index) 
  text += page.get_text()
  lines = text.strip().split('\n')

  # titles and page number extraction based on toc
  toc_dict = {}
  for line in lines:
    match = re.match(r'^(\d{2})([A-Za-z].+)', line.strip()) # to find lines that start with a number
    if match:
      page = int(match.group(1))
      title = match.group(2).strip()
      toc_dict[title] = page  # add the title and page number to a dic 
  
  if not toc_dict:
    raise ValueError(f"No TOC entries found in '{pdf_path}'.")

  return toc_dict


# Extracting all the infromation from the pages based on the table of contents 
def extract_text_from_page(pdf_path):
  
  toc_dict = toc(pdf_path) 

  doc = pymupdf.open(pdf_path)
  page_texts = {} # saving the text content for each page in a dic 

  for page_num in range(len(toc_dict)):
    
    page = doc.load_page(list(toc_dict.values())[page_num]-1)  

    page_texts[list(toc_dict.keys())[page_num]] = page.get_text()
  
 
  return json.dumps(page_texts, indent=2)



############################# model setup ###############################

# source: https://docs.mistral.ai/capabilities/vision/
# Encode the image to base64 (Needed for Mistral API)
def encode_image(image_path):

    """Encode the image to base64."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
      raise ValueError("Unknown image MIME type")
    
    with open(image_path, "rb") as img_file:
      b64_img = base64.b64encode(img_file.read()).decode("utf-8")
    
    return f"data:{mime_type};base64,{b64_img}"

# Call Mistral API and get the response
def model_response(system_prompt, text_prompt,image_path = None):

    load_dotenv() 

    # Retrieve the API key 
    #api_key = ""
    api_key = os.getenv("MISTRAL_API_KEY")

    if api_key is None:
      raise ValueError("API key not found. Please set the MISTRAL_API_KEY environment variable.")

    # Specify model
    model = "pixtral-12b-2409"

    # Initialize the Mistral client
    client = Mistral(api_key=api_key)

    # Define the messages for the chat
    if image_path is None:
        messages = [
            {
                "role": "user",
                "content": text_prompt
            }
        ]
    else:
        image_data_url = encode_image(image_path)
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": image_data_url
                    }
                ]
            }
        ]

    # Get the chat response
    try:
      chat_response = client.chat.complete(
          model=model,
          messages=messages
      )
      logger.info("Mistral API response received successfully")
    except Exception as e:
      logger.info("Mistral API response failed")
      raise RuntimeError(f"Failed to get response from Mistral API: {e}")

    # Print the content of the response
    return chat_response.choices[0].message.content


############################# Output refinement ###############################

# To insure that the output from the LLM algins with the JSON format
def parse_llm_json(output):

    # Removing whitespace
    text = output.strip()
    # Remove the first and last lines with backticks
    if text.startswith("```"):
      lines = text.splitlines()
      # first line that doesn’t start with ```
      start = 1
      # last line that doesn’t start with ```
      end = len(lines) - 1
      text = "\n".join(lines[start:end])

    try:
      return json.loads(text)
      logger.info("parse_llm_json succeeded")
    except json.JSONDecodeError as e:
      logger.info("parse_llm_json failed")
      raise ValueError(f"Failed to parse JSON: {e}")
  

# Calculate the total score based on the 4 seperate scores
def total_score(report):

  # validating the JSON output by the model
  keys = ["font_style_score","logo_safe_zone_score","logo_colors_score","color_palette_score"]

  for k in keys:
    if k not in report:
      logger.info("Missing key in the report")
      raise KeyError(f"Missing score key '{k}' in report. Please rerun the model.")
    if not (0 <= report[k] <= 1):
      logger.info("Key/s is out of range")
      raise ValueError(f"Score '{k}' is out of range. Expected between 0 and 1.Please rerun the model.")
    if not isinstance(report[k], (int, float)):
      logger.info("The value of key/s is not a number ")
      raise TypeError(f"Score '{k}' is not a number.Please rerun the model.")

  report["total_score"] = sum([
      report["font_style_score"],
      report["logo_safe_zone_score"],
      report["logo_colors_score"],
      report["color_palette_score"]
  ])

  if report["total_score"] > 4:
    logger.info("The total score is out of range")
    raise ValueError(f"Total score is out of range. Expected between 0 and 4.Please rerun the model.")

  logger.info("Values in the report are valid")
  return report