from helper import extract_text_from_page, model_response, parse_llm_json, total_score


def run_chain(brand_kit_path,image_path):
  brand_guideline_info = extract_text_from_page(brand_kit_path)

  # to creat the system prompt to ensure it meets the brand guideline
  text_brand_prompt = f"""
  You are generating a system prompt for a vision‑language model that assesses brand guideline compliance from images.

  Your input is the brand guideline content provided below.  It contains every rule the model must enforce (logo description, misuse rules, safe‑zone, colors, extended colors, typography).  

  **Task:** Produce a system prompt that generates:

  1. Separate labeled sections for each guideline group found in the text.
  2. In each section, restate the exact rules or values from the provided guidelines.
  3. For the **Extended Colors** section, render the data as a **markdown-style table**, with the columns for each percentage label (120%, Base, 80%, 60%, 40%, 20%, 10%) and Create N generic rows (e.g. “Color 1”, “Color 2”, …). 
  4. Do not add any extra commentary, examples, or meta‑language—output only the system prompt text. The system prompt should be in a format that can be directly used by the model to assess brand guideline compliance.

  Brand Guideline Input:
  {brand_guideline_info}
  """
  
  brand_guideline_prompt = model_response(image_path=None,system_prompt= None, text_prompt=text_brand_prompt)

  # the system prompt for the model to analyze the image along with the brand guideline prompt
  system_prompt = f"""
    You are a visual branding expert. You will receive an image and must:
    
        1. Extract all visual elements according to these brand guidelines:
        {brand_guideline_prompt}

        2. Evaluate the image on these four compliance elements (each yields value between 0 to 1 point):  
            • Font style  
            • Logo safe zone  
            • Logo colors  
            • Overall color palette consistency  

        3. Provide one sentence reasoning for each element.  

        4. **Output only** a JSON object with this exact schema:

            ```json
            {{
            "font_style_score": between 0 and 1,
            "logo_safe_zone_score": between 0 and 1,
            "logo_colors_score": between 0 and 1,
            "color_palette_score": between 0 and 1,
            "reasoning": {{
                "font_style": "...",
                "logo_safe_zone": "...",
                "logo_colors": "...",
                "color_palette": "..."
            }}
        }}

        5. Do not add any extra commentary, examples, or meta‑language—output only the JSON object.

    """

  text_prompt = "Analyze the image based on the brand guidelines."

  image_score = model_response(image_path=image_path,system_prompt= system_prompt, text_prompt=text_prompt)

  report_1 = parse_llm_json(image_score)
  report_1 = total_score(report_1)

  return report_1


#if __name__ == "__main__":
#  result = run_chain("Neurons_brand_kit.pdf","neurons_1.png")
#  print(result)
