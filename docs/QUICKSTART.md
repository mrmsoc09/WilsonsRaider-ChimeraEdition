# Quickstart Guide

This guide provides the fastest way to get Wilsons-Raiders up and running for initial exploration and use. For more detailed information, please refer to the [User Guide](USER_GUIDE.md) and [Configuration Guide](CONFIGURATION.md).

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Git**: For cloning the repository.
*   **Docker and Docker Compose**: For containerized deployment (recommended).
*   **Python 3.10+** (Optional, for native execution or development setup): If not using Docker.
*   **`pip`**: Python package installer (if using native Python).

## 2. Clone the Repository

First, clone the Wilsons-Raiders repository to your local machine:

```bash
git clone https://github.com/your-org/wilsons-raiders.git
cd wilsons-raiders
```

## 3. Environment Setup

Wilsons-Raiders uses environment variables for sensitive information and flexible configuration.

1.  **Copy the example environment file**:
    ```bash
    cp .env.example .env
    ```
2.  **Edit `.env`**: Open the newly created `.env` file and fill in the necessary API keys and configuration values. Refer to `API_KEYS_GUIDE.md` (if available) for details on obtaining these keys.

## 4. Install Dependencies (if not using Docker)

If you plan to run Wilsons-Raiders directly (without Docker), install the Python dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run the Application

### Using Docker Compose (Recommended)

For the easiest setup, use Docker Compose:

```bash
docker-compose up -d
```
This command will build (if necessary) and start all required services in detached mode.

### Native Execution (Advanced)

If you're running natively, you can start the main application:

```bash
python wilsons_raiders.py
# Or if there's a specific entry point like app/main.py
# python app/main.py
```

## 6. Accessing the System

Once the application is running, you can typically access the UI or interact with the CLI as follows:

*   **Web UI**: (If applicable) Navigate to `http://localhost:8000` (or the port configured in your `.env` file).
*   **CLI**: (If applicable) Run commands like `python dev_cli.py [command]`.

## Next Steps

*   **[User Guide](USER_GUIDE.md)**: For a comprehensive understanding of all features and functionalities.
*   **[Configuration Guide](CONFIGURATION.md)**: To fine-tune your Wilsons-Raiders deployment.
*   **[Troubleshooting](FAQ.md)**: If you encounter any issues during setup.