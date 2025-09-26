from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from .tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage


class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attention"""
    name: str = Field(description="The name of the company")
    ticker: str = Field(description="The ticker stock symbol of the company")
    reason: str = Field(description="The reason why the company is trending in the news")


class TrendingCompanyList(BaseModel):
    companies: List[TrendingCompany] = Field(description="A list of trending companies in the news")


class TrendingCompanyResearch(BaseModel):
    """Detailed research on a company"""
    name: str = Field(description="The name of the company")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")
    

class TrendingCompanyResearchList(BaseModel):
    """A list of detailed research on companies"""
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


@CrewBase
class StockRecommendation():
    """StockRecommendation crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], 
            tools=[SerperDevTool()], # type: ignore[index]
            verbose=True,
            memory=True,
        )
        
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], 
            tools=[SerperDevTool()], # type: ignore[index]
            verbose=True
        )
        
    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'],
            verbose=True,
            tools=[PushNotificationTool()], # type: ignore[index]
            memory=True,
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )
    
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True,
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            # Long-term memory for persistent storage across sessions
            long_term_memory = LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            # Short-term memory for current context using RAG
            short_term_memory = ShortTermMemory(
                storage = RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model_name": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),            # Entity memory for tracking key information about entities
            entity_memory = EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "config": {
                            "model": 'text-embedding-3-small'
                        }
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),
        )
