# Contributing to Wilsons-Raiders

We welcome and appreciate your contributions to Wilsons-Raiders! Your help is vital for improving the project, fixing bugs, and adding new features. Please take a moment to review this document to understand how you can best contribute.

## Code of Conduct

We are committed to providing a friendly, safe, and welcoming environment for all. Please review our [Code of Conduct](CODE_OF_CONDUCT.md - *Link to be updated if a specific CoC file exists*) which outlines the expectations for participation in our community.

## How to Contribute

There are several ways you can contribute to Wilsons-Raiders:

### Bug Reports

*   **Check existing issues**: Before submitting a new bug report, please check if the issue has already been reported in our [issue tracker](https://github.com/your-org/wilsons-raiders/issues).
*   **Provide detailed information**: When reporting a bug, please include:
    *   A clear and concise description of the bug.
    *   Steps to reproduce the behavior.
    *   Expected behavior.
    *   Screenshots or error messages, if applicable.
    *   Your operating system and Wilsons-Raiders version.

### Feature Requests

*   **Check existing requests**: Look through existing feature requests to see if your idea has already been proposed.
*   **Describe your idea**: Clearly articulate the feature you'd like to see, why it's valuable, and how it would work.

### Pull Requests (Code Contributions)

1.  **Fork the repository**: Start by forking the Wilsons-Raiders repository to your GitHub account.
2.  **Clone your fork**:
    ```bash
    git clone https://github.com/your-username/wilsons-raiders.git
    cd wilsons-raiders
    ```
3.  **Create a new branch**:
    ```bash
    git checkout -b feature/your-feature-name
    ```
    or
    ```bash
    git checkout -b bugfix/issue-number
    ```
4.  **Set up your development environment**: Refer to the [Quickstart Guide](QUICKSTART.md) for instructions on setting up your local development environment.
5.  **Make your changes**: Implement your bug fix or feature.
6.  **Write tests**: Ensure your changes are covered by appropriate unit or integration tests. See [Testing Guidelines](#testing-guidelines) below.
7.  **Run tests**: Verify that all existing tests pass with your changes.
8.  **Commit your changes**: Follow the [Commit Message Guidelines](#commit-message-guidelines).
9.  **Push to your fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
10. **Open a Pull Request**: Submit a pull request to the `main` branch of the original Wilsons-Raiders repository. Provide a clear description of your changes.

## Development Setup

For detailed instructions on setting up your development environment, including prerequisites and initial configuration, please see the [Quickstart Guide](QUICKSTART.md) and the [Configuration Guide](CONFIGURATION.md).

## Coding Style and Guidelines

*   **Python**: We adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style. Please use a linter (e.g., `flake8` or `pylint`) to ensure compliance.
*   **Docstrings**: All functions, classes, and modules should have clear and concise docstrings.
*   **Type Hinting**: Utilize Python type hints for better code clarity and maintainability.

## Testing Guidelines

*   **Unit Tests**: All new features and bug fixes should be accompanied by unit tests covering the new or changed logic.
*   **Test Framework**: We use `pytest` for testing.
*   **Running Tests**: To run the test suite, navigate to the project root and execute:
    ```bash
    pytest
    ```

## Commit Message Guidelines

We follow a conventional commit message format. This helps with automatic changelog generation and understanding the purpose of each commit.

Examples:
*   `feat: add new agent for OSINT data collection`
*   `fix(core): prevent null pointer exception in state manager`
*   `docs: update quickstart guide with docker instructions`

## Sign Your Commits

We require all contributors to sign off on their commits, indicating that they agree to the Developer Certificate of Origin (DCO). This is a statement that you have the right to submit the code you are contributing.

To sign off, add `-s` or `--signoff` to your `git commit` command:

```bash
git commit -s -m "feat: your descriptive commit message"
```

## Further Questions?

If you have any questions or need further clarification, please don't hesitate to open an issue or reach out to the project maintainers.