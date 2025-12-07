# 🚀 Tarento Enterprise AI Co-Pilot

**A Unified SaaS Platform for Enterprise AI-Powered Automation**

---

## 📋 Project Overview

Tarento Enterprise AI Co-Pilot is a comprehensive SaaS platform that leverages multiple AI agents to automate key workflows across IT services companies. From RFP analysis and proposal generation to Jira analytics, documentation automation, HR processes, and financial operations—all through a flexible, user-friendly interface.

### 🎯 Team: QuardCrew

---

## ✨ Key Features

### 🤖 5 Specialized AI Agents

| Agent | Purpose | Output |
|-------|---------|--------|
| **RFP & Proposal** | Analyze RFPs and generate complete proposals | PDF/DOCX with cost, timeline, compliance |
| **Jira Analytics** | Deep dive into project metrics and performance | Velocity trends, burndown, recommendations |
| **Documentation** | Auto-generate code docs, comments, and tests | API docs, README, unit/integration tests |
| **HR Agent** | Resume screening and onboarding planning | Candidate scorecards, onboarding checklists |
| **Finance Agent** | Invoice validation and expense processing | Invoice approvals, cost analysis, forecasts |

### 🎨 Dual Interface System

- **Form-Based Interface**: Structured inputs for consistent results
- **Chat Interface**: Natural language interactions with real-time refinements
- **Seamless Switching**: Maintain context when switching between interfaces

### 🔐 Enterprise-Ready Security

- Multi-tenant architecture with complete data isolation
- Role-based access control (5 predefined roles)
- Organization and project-level permissions
- Complete audit logging of all actions

### ⚙️ Fully Configurable

- **LLM Selection**: Choose from Gemini models (2.5 Pro, 3)
- **Organization Branding**: Custom logos, colors, themes
- **Agent Configuration**: Per-agent model selection and parameters
- **Dynamic Settings**: Everything configurable without code changes

### 📚 Knowledge Management

- Document upload and automatic parsing
- Vector embeddings with Qdrant
- Semantic search across documents
- Auto-updating knowledge bases

---

## 🏗️ Architecture

### Tech Stack

**Backend**
```
FastAPI (Python) → PostgreSQL + Redis + Qdrant → Google Gemini API
```

**Frontend**
```
React 18 + TypeScript → Material-UI → Redux State Management
```

**Infrastructure**
```
Docker & Kubernetes → CI/CD Pipelines → Cloud Deployment
```

### System Architecture

```
┌─────────────────────────────────────┐
│     Frontend (React + Material-UI)  │
│  ┌─────────────┐  ┌──────────────┐ │
│  │ Form        │  │ Chat         │ │
│  │ Interface   │  │ Interface    │ │
│  └─────────────┘  └──────────────┘ │
└──────────────────┬──────────────────┘
                   │
        ┌──────────▼──────────┐
        │   FastAPI Backend    │
        │   (Services Layer)   │
        └──────────┬───────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐   ┌─────▼──────┐  ┌────▼────┐
│ Agents │   │ PostgreSQL  │  │ Qdrant  │
│        │   │ (Sessions)  │  │(Vectors)│
└────────┘   └─────────────┘  └─────────┘
    │
    └──────────► Google Gemini API
```

---

## 📁 Project Structure

```
tarento-copilot/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST API endpoints
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── services/         # Business logic
│   │   ├── agents/           # AI agent implementations
│   │   ├── utils/            # Helper utilities
│   │   ├── middleware/       # FastAPI middleware
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   └── main.py           # FastAPI application
│   ├── tests/                # Unit and integration tests
│   ├── requirements.txt       # Python dependencies
│   └── docker/
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API clients
│   │   ├── store/            # Redux state management
│   │   ├── types/            # TypeScript types
│   │   ├── hooks/            # Custom React hooks
│   │   ├── styles/           # Global styles
│   │   ├── utils/            # Utility functions
│   │   └── assets/           # Images, icons, fonts
│   ├── tests/                # Unit tests
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── docker-compose.yml        # Local development setup
├── .gitignore
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- PostgreSQL 15+
- Redis 7+
- Qdrant vector database
- Google Gemini API key

### Quick Start

#### Option 1: Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/quardiccrew/tarento-copilot.git
cd tarento-copilot

# Create .env file
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Add your Gemini API key to backend/.env
# GEMINI_API_KEY=your_key_here

# Start all services
docker-compose up

# Access the application
Frontend: http://localhost:5173
API Docs: http://localhost:8000/docs
```

#### Option 2: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Setup database
alembic upgrade head
python seed_data.py

# Start backend
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev
```

### Default Credentials

```
Email: admin@tarento.io
Password: admin@123
```

---

## 📖 Documentation

Comprehensive documentation is available in dedicated guides:

| Document | Purpose |
|----------|---------|
| **[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md)** | Phase-by-phase development plan (40 weeks) |
| **[TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md)** | Complete system architecture and design |
| **[PHASE_1_IMPLEMENTATION.md](./PHASE_1_IMPLEMENTATION.md)** | Detailed implementation guide for Phase 1 |
| **[FEATURES_AND_CONFIGURATION.md](./FEATURES_AND_CONFIGURATION.md)** | Feature specifications and configuration guide |
| **[PROJECT_SUMMARY_AND_QUICK_REFERENCE.md](./PROJECT_SUMMARY_AND_QUICK_REFERENCE.md)** | Quick reference and key information |

---

## 🔑 Core Concepts

### Multi-Tenancy

Each organization gets:
- Complete data isolation
- Custom configurations
- Independent agent settings
- Separate billing
- Custom branding

### Role-Based Access

```
Admin           → Full system access
Org Admin       → Organization management
Project Manager → Project and agent management
User            → Agent execution
Viewer          → Read-only access
```

### Agent Execution Flow

```
User Input (Form/Chat)
    ↓
Validate Input
    ↓
Load Agent Configuration
    ↓
Retrieve Knowledge Base Context
    ↓
Execute with Google Gemini API
    ↓
Format & Store Results
    ↓
Display to User
```

### Knowledge Base Integration

```
Upload Document → Parse & Chunk → Generate Embeddings → Store in Qdrant
                                                              ↓
                            At Execution: Embed Query → Semantic Search → Include Context
```

---

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test
npm run test:e2e
```

### Test Coverage Goals
- Backend: 80%+ coverage
- Frontend: 70%+ coverage
- Critical paths: 100% coverage

---

## 🚢 Deployment

### Production Deployment

```bash
# Build and push Docker images
docker build -t tarento-copilot-backend:latest ./backend
docker build -t tarento-copilot-frontend:latest ./frontend

# Deploy to Kubernetes
kubectl apply -f k8s/

# Verify deployment
kubectl get pods
kubectl logs <pod-name>
```

### Environment Configuration

Create `.env` files for each environment:
- **Development**: `.env.development`
- **Staging**: `.env.staging`
- **Production**: `.env.production`

Key variables to set:
```
ENVIRONMENT=production
DATABASE_URL=postgresql://...
GEMINI_API_KEY=...
SECRET_KEY=...
DEBUG=false
```

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time | < 200ms (p95) |
| Agent Execution | < 5s (p95) |
| Concurrent Users | 1000+ |
| Monthly Executions | 100,000+ |
| Uptime | 99.9% |
| Cache Hit Rate | > 70% |

---

## 🔒 Security

### Authentication
- JWT tokens with refresh mechanism
- Bcrypt password hashing
- Secure session management

### Authorization
- Role-based access control
- Organization isolation
- Audit logging

### Data Protection
- TLS/SSL encryption in transit
- Database encryption at rest
- Parameter-based SQL queries
- Input validation and sanitization

---

## 🤝 Contributing

### Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request with description

### Code Standards

- **Python**: Follow PEP 8 (use Black formatter)
- **TypeScript**: ESLint + Prettier
- **Commits**: Clear, descriptive messages
- **Tests**: Required for all changes

### Running Linters

```bash
# Backend
black backend/
flake8 backend/
mypy backend/

# Frontend
npm run lint
npm run format
```

---

## 📞 Support

### Common Issues

**Q: API not connecting?**
A: Check that backend is running on port 8000 and `VITE_API_BASE_URL` is correct.

**Q: Database migration fails?**
A: Ensure PostgreSQL is running and `DATABASE_URL` is correct.

**Q: Agent execution times out?**
A: Check Gemini API key and rate limits. Increase `request_timeout_seconds` in config.

**Q: High memory usage?**
A: Reduce vector search result limit or implement pagination.

### Getting Help

- Check documentation files
- Review API documentation: http://localhost:8000/docs
- Check logs: `docker-compose logs -f`
- Create an issue on GitHub

---

## 📈 Roadmap

### Phase 1: Foundation (Weeks 1-4) ✅
- [ ] Project setup and architecture
- [ ] Database schema
- [ ] Authentication system
- [ ] Basic API endpoints

### Phase 2: Multi-Tenancy (Weeks 5-7)
- [ ] User and organization management
- [ ] Role-based access control
- [ ] Admin dashboard

### Phase 3: Configuration (Weeks 8-11)
- [ ] Dynamic configuration system
- [ ] Agent management
- [ ] Knowledge base integration

### Phase 4-6: Agent Implementation (Weeks 12-24)
- [ ] RFP & Proposal Agent
- [ ] Jira Analytics Agent
- [ ] Documentation Agent
- [ ] HR Agent
- [ ] Finance Agent

### Phase 7-8: Interfaces & Integration (Weeks 25-32)
- [ ] Form-based interface
- [ ] Chat interface
- [ ] Multi-agent workflows
- [ ] Advanced analytics

### Phase 9-10: Testing & Launch (Weeks 33-40)
- [ ] Comprehensive testing
- [ ] Security audit
- [ ] Performance optimization
- [ ] Production deployment

### Phase 11: Post-Launch (Ongoing)
- [ ] Monitoring and optimization
- [ ] User feedback incorporation
- [ ] New agent development
- [ ] Advanced features

---

## 📜 License

This project is proprietary and belongs to Tarento. All rights reserved.

---

## 👥 Team

**QuardCrew Team**
- Product Strategy
- Backend Development
- Frontend Development
- DevOps & Infrastructure
- QA & Testing

---

## 🎉 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Material-UI](https://mui.com/) - Component library
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python ORM
- [Qdrant](https://qdrant.tech/) - Vector database
- [Google Gemini](https://ai.google.dev/) - LLM models

---

## 📝 Recent Changes

**December 7, 2025**
- [x] Created comprehensive development roadmap
- [x] Designed technical architecture
- [x] Documented Phase 1 implementation
- [x] Created feature and configuration guide
- [x] Created quick reference guide
- [x] Initial project setup and structure

---

## 📞 Contact

For questions or support, please contact:
- **Product**: [contact info]
- **Technical**: [contact info]
- **General**: info@tarento.io

---

**Happy Building! 🚀**

*Last Updated: December 7, 2025*  
*Version: 1.0*  
*Status: Ready for Development*
# tarento-copilot
