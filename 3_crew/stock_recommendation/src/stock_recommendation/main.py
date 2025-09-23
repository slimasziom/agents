#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from stock_recommendation.crew import StockRecommendation

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()


def run():
    """
    Run the crew.
    """
    inputs = {
        'sector': 'Technology'
    }
    
    try:
        result = StockRecommendation().crew().kickoff(inputs=inputs)

        print(F"\n\n=== FINAL DECISION ===\n\n")
        print(result.raw)
        
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    run()
