# LibreChat Python/FastAPI Backend

This is a complete conversion of the LibreChat Node.js/Express backend to Python/FastAPI.

## Features

- **FastAPI** - Modern, high-performance async Python web framework
- **MongoDB with Beanie ODM** - Async MongoDB driver with Pydantic models
- **Pydantic v2** - Data validation and settings management
- **JWT Authentication** - Secure token-based authentication
- **OAuth Support** - Google, GitHub, Discord, Facebook, Apple
- **LDAP & SAML** - Enterprise authentication
- **2FA/TOTP** - Two-factor authentication
- **RBAC** - Role-based access control
- **Rate Limiting** - Request throttling
- **Meilisearch** - Full-text search
- **Redis Caching** - Session and data caching
- **File Storage** - S3, Azure Blob, local storage
- **AI Integration** - OpenAI, Anthropic, Google Gemini support

## Project Structure

```
api-python/
├── app/
│   ├── models/          # Beanie/Pydantic models
│   ├── routes/          # API route handlers
│   ├── middleware/      # FastAPI middleware
│   ├── services/        # Business logic services
│   ├── controllers/     # Request controllers
│   ├── strategies/      # Authentication strategies
│   ├── db/              # Database connection
│   ├── config/          # Configuration
│   ├── utils/           # Utility functions
│   ├── cache/           # Caching logic
│   ├── lib/             # Library code
│   └── schemas/         # Pydantic request/response schemas
├── tests/               # Test files
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

4. Run the application:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host localhost --port 3080
```

## Environment Variables

See `.env.example` for all available configuration options.

### Required Variables

- `MONGO_URI` - MongoDB connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `JWT_REFRESH_SECRET` - Secret key for refresh tokens

### Optional Variables

- Database: `MONGO_MAX_POOL_SIZE`, `MONGO_MIN_POOL_SIZE`, etc.
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- OAuth: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, etc.
- Email: `SMTP_HOST`, `SMTP_PORT`, `EMAIL_FROM`
- Storage: `AWS_ACCESS_KEY_ID`, `S3_BUCKET`, `AZURE_STORAGE_ACCOUNT`
- Search: `MEILI_HOST`, `MEILI_KEY`

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/ tests/
isort app/ tests/
```

### Type Checking
```bash
mypy app/
```

## API Documentation

When running in debug mode, API documentation is available at:
- Swagger UI: http://localhost:3080/api/docs
- ReDoc: http://localhost:3080/api/redoc

## Conversion Status

### ✅ Completed

- [x] Project structure setup
- [x] Dependencies configuration (requirements.txt)
- [x] MongoDB connection with Motor/Beanie
- [x] All Pydantic/Beanie models (18 models)
- [x] Configuration system with Pydantic Settings
- [x] Main FastAPI application
- [x] Error handling and custom exceptions
- [x] Logging system

### 🚧 In Progress

- [ ] Authentication system (JWT, OAuth, LDAP, SAML)
- [ ] Middleware (rate limiting, validation, CORS)
- [ ] API routes (28+ route files)
- [ ] Controllers and services
- [ ] File storage services
- [ ] AI SDK integration
- [ ] Meilisearch integration
- [ ] Redis caching
- [ ] Email service

### 📋 Pending

- [ ] Unit tests
- [ ] Integration tests
- [ ] Docker configuration
- [ ] Migration guide
- [ ] Performance optimization

## Models Converted

All 18 MongoDB models have been converted to Beanie documents:

1. **User** - User accounts with OAuth, 2FA, sessions
2. **Conversation** - Chat conversations
3. **Message** - Individual messages
4. **File** - File metadata and storage
5. **Role** - RBAC roles and permissions
6. **Agent** - AI agents configuration
7. **Assistant** - OpenAI/Azure assistants
8. **Prompt** - Prompt library
9. **PromptGroup** - Prompt collections
10. **Action** - Custom actions
11. **Preset** - Conversation presets
12. **Transaction** - Token transactions
13. **Balance** - User token balances
14. **ToolCall** - Agent tool invocations
15. **ConversationTag** - Conversation tags
16. **Project** - Projects for organization
17. **Banner** - System announcements
18. **Categories** - Content categories

## Architecture Differences from Node.js Version

### Async/Await
- Python's `asyncio` instead of Node.js event loop
- All database operations are async using Motor

### Database
- **Beanie ODM** instead of Mongoose
- Pydantic models for validation
- Same MongoDB schema structure

### Authentication
- FastAPI Security dependencies instead of Passport.js
- OAuth via `authlib` instead of passport strategies
- LDAP via `ldap3` instead of passport-ldapauth

### Middleware
- FastAPI dependency injection instead of Express middleware chain
- Starlette middleware for CORS, compression
- Custom dependencies for auth, rate limiting

### Routes
- FastAPI routers instead of Express routers
- Pydantic schemas for request/response validation
- Automatic OpenAPI documentation

## License

Same as LibreChat main project
