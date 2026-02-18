from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from nutrition_agent.tools import NutritionLookupTool


@CrewBase
class NutritionCrew:
    """Nutrition analysis crew for analyzing meals with multiple food items"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def meal_parser(self) -> Agent:
        """Agent that parses meal descriptions and identifies individual food items"""
        return Agent(
            config=self.agents_config['meal_parser'],
            verbose=True,
        )

    @agent
    def nutrition_researcher(self) -> Agent:
        """Agent that looks up nutrition information for each food item"""
        return Agent(
            config=self.agents_config['nutrition_researcher'],
            tools=[NutritionLookupTool()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def nutrition_analyst(self) -> Agent:
        """Agent that aggregates and analyzes total nutrition for the meal"""
        return Agent(
            config=self.agents_config['nutrition_analyst'],
            verbose=True,
        )

    @task
    def parse_meal_task(self) -> Task:
        """Task to parse the meal description and identify all food items"""
        return Task(
            config=self.tasks_config['parse_meal_task'],
        )

    @task
    def research_nutrition_task(self) -> Task:
        """Task to look up nutrition information for each food item"""
        return Task(
            config=self.tasks_config['research_nutrition_task'],
            context=[self.parse_meal_task()],
        )

    @task
    def analyze_nutrition_task(self) -> Task:
        """Task to aggregate and provide comprehensive nutrition analysis"""
        return Task(
            config=self.tasks_config['analyze_nutrition_task'],
            context=[self.parse_meal_task(), self.research_nutrition_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Nutrition analysis crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )


def run_nutrition_agent(meal_description: str):
    """Run the nutrition analysis crew for a meal description."""
    result = NutritionCrew().crew().kickoff(inputs={"meal_description": meal_description})
    return result.raw

