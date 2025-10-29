from abc import ABC, abstractmethod
import logging

class Workflow(ABC):
    """
    Base class for all workflow phases in WilsonsRaider-ChimeraEdition.
    Defines the standard interface and extensibility hooks.
    """
    def __init__(self, context=None):
        """
        Initialize the workflow with optional context (engagement/task details).
        """
        self.context = context or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.results = None
        self.errors = []

    @abstractmethod
    def plan(self):
        """
        Analyze context and prepare the workflow plan (tools, steps, objectives).
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def execute(self):
        """
        Execute the workflow phase. Must be implemented by subclasses.
        Should update self.results and handle errors internally.
        """
        pass

    @abstractmethod
    def report(self):
        """
        Generate a structured report of the workflow results.
        Must be implemented by subclasses.
        """
        pass

    def handle_error(self, error):
        """
        Standardized error handling for workflow phases.
        Logs and stores errors for later reporting.
        """
        self.logger.error(f"Error in {self.__class__.__name__}: {error}")
        self.errors.append(str(error))

    def get_status(self):
        """
        Return current status, including errors and partial results.
        """
        return {
            'workflow': self.__class__.__name__,
            'results': self.results,
            'errors': self.errors
        }
