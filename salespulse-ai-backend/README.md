# SalesPulse AI Backend

SalesPulse AI is a multi-channel communication backend designed to facilitate seamless interactions across various messaging platforms. This FastAPI application serves as the core backend for managing user interactions, campaigns, and analytics.

## Project Structure

```
salespulse-ai-backend
├── src
│   ├── main.py                  # Entry point of the FastAPI application
│   ├── config                   # Configuration settings
│   ├── api                      # API routes and endpoints
│   ├── models                   # Database models
│   ├── schemas                  # Pydantic schemas for data validation
│   ├── services                 # Business logic and external integrations
│   ├── integrations             # Third-party service integrations
│   ├── core                     # Core functionalities like logging and error handling
│   ├── db                       # Database session management
│   └── middleware               # Middleware for authentication and logging
├── tests                        # Unit and integration tests
├── alembic                      # Database migration scripts
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore file
├── requirements.txt             # Project dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/salespulse-ai-backend.git
   cd salespulse-ai-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy the `.env.example` to `.env` and fill in the required values.

## Running the Application

To start the FastAPI application, run:
```
uvicorn src.main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **Health Check**
  - `GET /health`: Check the status of the service.

- **Message Generation**
  - `POST /generate-message`: Generate follow-up messages based on lead data.

- **Channel Messaging**
  - Endpoints for sending messages via various channels (WhatsApp, SMS, Email).

- **Webhooks**
  - Handle incoming webhooks from Twilio for WhatsApp and SMS.

## Testing

To run the tests, use:
```
pytest
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.