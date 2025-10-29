<<<<<<< HEAD
from crewai import Agent
from core.managers.ai_manager import AIManager
from core.managers.bounty_program_manager import BountyProgramManager
import asyncio

class ProgramSelectorAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Strategic Bug Bounty Program Analyst',
            goal='Analyze and select the most probable and profitable bug bounty programs to target.',
            backstory='You are a world-class bug bounty hunter with a knack for finding high-impact vulnerabilities. You think strategically, prioritizing targets not just by payout, but by the likelihood of finding critical bugs based on program scope, age, and technology stack.',
            verbose=True
        )
        self.ai_manager = AIManager()
        self.program_manager = BountyProgramManager()

    def select_programs(self):
        """Fetches all opportunities and uses the LLM to select the best ones."""
        
        # Get all opportunities from the program manager
        opportunities = asyncio.run(self.program_manager.get_all_opportunities())

        if not opportunities:
            return "No bug bounty programs were found to analyze."

        prompt = f"""
        You are a world-class bug bounty hunter with a knack for finding high-impact vulnerabilities. Your goal is to select the most profitable and probable opportunities from the list below.

        Your decision-making must be driven by two factors: **High Reward** and **High Probability of Finding Bugs**.

        Analyze the following list of bug bounty programs. Consider these factors:
        - **Payouts**: Are the maximum payouts high? This indicates the value the company places on security.
        - **Scope**: Is the scope wide (e.g., wildcard domains *.example.com)? Wide scopes mean a larger, less-tested attack surface.
        - **Technology**: Does the program use new, complex, or niche technologies that are more likely to be buggy?
        - **Program Age/Updates**: Are the programs new or recently updated? These are often less hardened than older, more mature programs.

        Here are the available opportunities:
        {opportunities}

        Based on your analysis, provide a ranked list of the top 3 programs to target. For each program, provide a 1-2 sentence justification explaining why it's a prime target based on the principles of high reward and high probability. Respond in a structured JSON format like this: {{'recommendations': [{{'program_name': '<name>', 'justification': '<your_reasoning>'}}]}}.
        """
        
        return self.ai_manager._call_llm(prompt, system_prompt="You are a strategic bug bounty hunter.", task_type='prioritization')

=======
"""Program Selector Agent

Bug bounty program selection and prioritization agent specializing in:
- Program discovery and filtering based on criteria
- Reward potential and ROI analysis
- Scope and asset analysis
- Success probability estimation
- Program reputation and responsiveness assessment

Version: 2.0.0
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from secret_manager import SecretManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ProgramSelectorAgent:
    """Bug bounty program selection and prioritization agent.

    Analyzes bug bounty programs to identify optimal targets based on
    reward potential, scope, success probability, and strategic fit.

    Attributes:
        cost_tier: LLM model selection strategy
        secrets: Vault integration for credentials
        model: Selected LLM model
        llm_api_key: OpenAI API key from Vault
    """

    COST_TIERS = {
        'economic': 'gpt-3.5-turbo',
        'balanced': 'gpt-4',
        'high-performance': 'gpt-4o'
    }

    PLATFORMS = ['hackerone', 'bugcrowd', 'intigriti', 'yeswehack', 'synack', 'hackenproof']

    PROGRAM_TYPES = ['public', 'private', 'vdp', 'managed']

    ASSET_TYPES = [
        'web_application', 'mobile_app', 'api', 'infrastructure',
        'source_code', 'hardware', 'blockchain', 'iot'
    ]

    SELECTION_CRITERIA = [
        'reward_potential', 'scope_breadth', 'response_time',
        'success_probability', 'competition_level', 'reputation'
    ]

    def __init__(self, cost_tier: str = 'balanced'):
        """Initialize Program Selector Agent.

        Args:
            cost_tier: Model selection strategy

        Raises:
            ValueError: If cost_tier invalid
            RuntimeError: If Vault initialization fails
        """
        if cost_tier not in self.COST_TIERS:
            raise ValueError(f"Invalid cost_tier: {cost_tier}")

        self.cost_tier = cost_tier
        self.secrets = SecretManager()
        self.llm_api_key = self.secrets.get_secret('wilsons-raiders/creds', 'OPENAI_API_KEY')

        if not self.llm_api_key:
            raise RuntimeError("Failed to retrieve OPENAI_API_KEY")

        self.model = self._select_model()
        logger.info(f"ProgramSelectorAgent initialized: model={self.model}")

    def _select_model(self) -> str:
        """Select LLM model based on cost tier."""
        return self.COST_TIERS[self.cost_tier]

    def execute_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute program selection workflow.

        Args:
            data: Task specification containing:
                - platforms: Bug bounty platforms to search
                - criteria: Selection criteria and priorities
                - filters: Program filters (reward_min, asset_types, etc.)
                - hunter_profile: Hunter skills and experience
                - time_budget: Available time investment
                - risk_tolerance: Comfort with private/managed programs

        Returns:
            Dict containing:
                - recommended_programs: Prioritized list of programs
                - program_analysis: Detailed analysis per program
                - roi_estimates: Expected ROI calculations
                - competition_analysis: Competition level assessment
                - strategic_recommendations: Target selection strategy
                - status: Task completion status

        Raises:
            ValueError: If required parameters missing
            RuntimeError: If program selection fails
        """
        platforms = data.get('platforms', self.PLATFORMS)
        criteria = data.get('criteria', self.SELECTION_CRITERIA)
        filters = data.get('filters', {})
        hunter_profile = data.get('hunter_profile', {})
        time_budget = data.get('time_budget', 'medium')
        risk_tolerance = data.get('risk_tolerance', 'medium')

        logger.info(f"Executing program selection (platforms={platforms}, criteria={criteria})")

        # TODO: Implement program selection logic
        # Program Discovery:
        # - Fetch programs from HackerOne, Bugcrowd, Intigriti APIs
        # - Parse program pages and extract metadata
        # - Filter by: public/private status, VDP vs bounty, managed programs
        # - Extract: rewards, scope, submission stats, response times

        # Reward Analysis:
        # - Minimum, maximum, and average bounties
        # - Historical payout data and trends
        # - Reward-to-vulnerability-type mapping
        # - Special bonus programs and multipliers

        # Scope Analysis:
        # - Asset inventory and technology stack
        # - In-scope vs out-of-scope boundaries
        # - Attack surface size estimation
        # - Scope complexity and diversity

        # Competition Analysis:
        # - Active hunter count and participation rate
        # - Recent submission volume and acceptance rate
        # - Saturation level (easy vulns likely found)
        # - Competitive advantage opportunities

        # Success Probability:
        # - Hunter skill alignment with program needs
        # - Technology stack familiarity
        # - Vulnerability type specialization match
        # - Historical success rate in similar programs

        # Program Reputation:
        # - Response time to submissions (MTTR)
        # - Triage quality and fairness
        # - Payment reliability and speed
        # - Communication quality
        # - Dispute resolution history

        # ROI Calculation:
        # - Expected value: (avg_bounty * success_prob) / time_investment
        # - Consider: research time, testing time, report writing
        # - Factor in: competition, scope complexity, learning curve
        # - Risk adjustment: payment reliability, scope changes

        # Strategic Fit:
        # - Alignment with hunter goals (learning, income, reputation)
        # - Portfolio diversification (avoid platform/sector concentration)
        # - Relationship building opportunities
        # - Long-term potential (private invites, recurring targets)

        # Prioritization:
        # - Multi-criteria decision analysis (MCDA)
        # - Weighted scoring based on hunter priorities
        # - Rank programs by expected value and strategic fit
        # - Provide top recommendations with justification

        return {
            'status': 'not_implemented',
            'message': 'Full program selection logic pending implementation',
            'platforms': platforms,
            'criteria': criteria,
            'filters': filters,
            'hunter_profile': hunter_profile,
            'recommended_programs': [],
            'program_analysis': {},
            'roi_estimates': {},
            'competition_analysis': {},
            'strategic_recommendations': []
        }
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
