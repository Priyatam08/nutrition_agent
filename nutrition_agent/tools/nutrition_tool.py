from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import json


class NutritionLookupInput(BaseModel):
    """Input schema for NutritionLookupTool."""
    food_item: str = Field(
        ...,
        description="The name of the food item as a plain string (e.g., 'chicken breast'). Do NOT send JSON or dictionary."
    )


class NutritionLookupTool(BaseTool):
    name: str = "nutrition_lookup"
    description: str = (
        "Look up detailed nutrition information for a specific food item.\n\n"
        "IMPORTANT:\n"
        "- food_item must be a plain string.\n"
        "- Example: \"chicken breast\"\n"
        "- Do NOT send JSON.\n"
        "- Do NOT send dictionary."
    )
    args_schema: Type[BaseModel] = NutritionLookupInput

    def _run(self, food_item: str) -> str:
        """
        Look up nutrition information for a food item using USDA FoodData Central API.
        Returns formatted nutrition data including calories, macronutrients, and key micronutrients.
        """
        try:
            # USDA FoodData Central API endpoint (free, no API key required)
            # Using the Foundation Foods endpoint for common foods
            base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            
            params = {
                "query": food_item,
                "pageSize": 1,
                "dataType": ["Foundation", "SR Legacy"],  # Foundation and Standard Reference foods
                "api_key": "DEMO_KEY"  # Demo key works for basic queries
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("foods") and len(data["foods"]) > 0:
                    food = data["foods"][0]
                    
                    # Extract nutrition information
                    nutrition_info = {
                        "food_name": food.get("description", food_item),
                        "fdc_id": food.get("fdcId", "N/A"),
                    }
                    
                    # Extract nutrients
                    nutrients = {}
                    for nutrient in food.get("foodNutrients", []):
                        nutrient_name = nutrient.get("nutrientName", "")
                        value = nutrient.get("value", 0)
                        unit = nutrient.get("unitName", "")
                        
                        # Key nutrients to extract
                        key_nutrients = [
                            "Energy", "Protein", "Total lipid (fat)", "Carbohydrate, by difference",
                            "Fiber, total dietary", "Sugars, total including NLEA",
                            "Calcium, Ca", "Iron, Fe", "Potassium, K", "Sodium, Na",
                            "Vitamin C, total ascorbic acid", "Vitamin A, RAE"
                        ]
                        
                        if any(key in nutrient_name for key in key_nutrients):
                            nutrients[nutrient_name] = f"{value} {unit}" if value else "0 {unit}"
                    
                    # Format the response
                    result = f"Nutrition Information for: {nutrition_info['food_name']}\n\n"
                    result += "MACRONUTRIENTS:\n"
                    result += f"  Calories: {nutrients.get('Energy', 'N/A')}\n"
                    result += f"  Protein: {nutrients.get('Protein', 'N/A')}\n"
                    result += f"  Total Fat: {nutrients.get('Total lipid (fat)', 'N/A')}\n"
                    result += f"  Carbohydrates: {nutrients.get('Carbohydrate, by difference', 'N/A')}\n"
                    result += f"  Fiber: {nutrients.get('Fiber, total dietary', 'N/A')}\n"
                    result += f"  Sugars: {nutrients.get('Sugars, total including NLEA', 'N/A')}\n\n"
                    
                    result += "MICRONUTRIENTS:\n"
                    result += f"  Calcium: {nutrients.get('Calcium, Ca', 'N/A')}\n"
                    result += f"  Iron: {nutrients.get('Iron, Fe', 'N/A')}\n"
                    result += f"  Potassium: {nutrients.get('Potassium, K', 'N/A')}\n"
                    result += f"  Sodium: {nutrients.get('Sodium, Na', 'N/A')}\n"
                    result += f"  Vitamin C: {nutrients.get('Vitamin C, total ascorbic acid', 'N/A')}\n"
                    result += f"  Vitamin A: {nutrients.get('Vitamin A, RAE', 'N/A')}\n"
                    
                    return result
                else:
                    return f"No nutrition data found for '{food_item}'. Please try a more specific food name or check the spelling."
            else:
                return f"Error fetching nutrition data: HTTP {response.status_code}. Please try again or use a different food name."
                
        except requests.exceptions.RequestException as e:
            return f"Network error while fetching nutrition data: {str(e)}. Please try again."
        except Exception as e:
            return f"Error processing nutrition data: {str(e)}. Please try again with a different food item."

