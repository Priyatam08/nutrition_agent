#!/usr/bin/env python
import warnings

from nutrition_agent.crew import run_nutrition_agent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    print("🥗 AI Nutrition Agent")
    print("Type 'exit' to quit.\n")

    while True:
        meal_description = input("Enter your meal description: ")

        if meal_description.lower() == "exit":
            break

        result = run_nutrition_agent(meal_description)

        print("\n--- Nutrition Analysis ---\n")
        print(result)
        print("\n--------------------------\n")


if __name__ == "__main__":
    run()
