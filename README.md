# CADSCRIBE Canvas Creator - AI-Powered CAD Platform

A complete AI-powered parametric CAD design platform with advanced 3D visualization and cloud-based processing. Built with React frontend, FastAPI backend, MongoDB database, and AWS S3 storage.

## 🏗️ Architecture

This project uses a modern cloud architecture:

1. **Frontend** → React + TypeScript + Three.js (3D visualization)
2. **Backend** → FastAPI + MongoDB (API and database)  
3. **Storage** → AWS S3 (file storage and CDN)
4. **Processing** → EC2 workers (CAD model generation)
5. **3D Engine** → OpenCascade.js (STEP/IGES native support)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- MongoDB (local or MongoDB Atlas)
- AWS S3 bucket (for file storage)
- Modern web browser with WebGL support

### 1. Frontend (React)

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The React app will be available at `http://localhost:5173`

### 2. Backend (FastAPI + MongoDB)

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

### 3. CAD Service (FastAPI + FreeCAD)

```bash
# Navigate to cad-service directory
cd cad-service

# Install Python dependencies
pip install -r requirements.txt

# Start CAD microservice
uvicorn cad_api:app --reload --port 9000
```

The CAD service will be available at `http://localhost:9000`

## 🎨 Features

### Core Functionality
- **Advanced 3D Viewer**: Three.js + OpenCascade.js for native STEP/IGES/STL/OBJ support
- **AI Chat Interface**: Conversational CAD design with project-based chat history
- **File Management**: AWS S3 integration with secure download URLs
- **Multi-Format Support**: STL, STEP, IGES, OBJ, FCSTD format handling
- **Real-time Collaboration**: Project sharing and chat persistence
- **Material System**: PBR materials with customizable finishes and wireframe modes

### UI/UX Features
- **Responsive Design**: Mobile-first responsive layout
- **Dark/Light Themes**: Automatic theme switching with system preference
- **Linen Texture Background**: Smooth scrolling with subtle linen pattern
- **Loading States**: Comprehensive loading indicators and error handling
- **Keyboard Shortcuts**: G (Generate), F (Fit View), S (Screenshot)
- **Accessibility**: ARIA labels and keyboard navigation

### Technical Features
- **Authentication**: JWT-based auth with React Context
- **API Integration**: Axios-based API client with retry logic
- **Offline Fallback**: Automatic fallback to demo data when offline
- **Performance**: Code splitting and lazy loading
- **Type Safety**: Full TypeScript implementation

## 🎨 Design System

### Color Palette
- **Primary**: `hsl(234, 89%, 54%)` - Modern blue
- **Secondary**: `hsl(142, 86%, 28%)` - Professional green  
- **Accent**: `hsl(25, 95%, 53%)` - Energetic orange

### Components
- **Shadcn/ui**: Complete component library with custom variants
- **Custom Buttons**: Hero, workspace, and outline variants
- **Responsive Grid**: CSS Grid-based workspace layout
- **Animations**: Smooth transitions and micro-interactions

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # Shadcn/ui components
│   ├── Navigation.tsx   # Main navigation
│   ├── Footer.tsx       # Site footer
│   ├── LandingPage.tsx  # Homepage content
│   └── ThreeViewer.tsx  # 3D model viewer
├── contexts/            # React contexts
│   ├── AuthContext.tsx  # Authentication state
│   └── ThemeContext.tsx # Theme management
├── pages/               # Application pages
│   ├── auth/           # Authentication pages
│   ├── WorkspacePage.tsx # Main workspace
│   ├── FeaturesPage.tsx
│   ├── AboutPage.tsx
│   └── DevNotes.tsx    # Developer documentation
├── services/           # API services
│   └── api.ts         # Axios configuration and endpoints
└── hooks/             # Custom React hooks
    └── use-toast.ts   # Toast notifications
```

## 🛠 API Integration

### Environment Variables
```bash
# Add to .env.local
VITE_API_URL=http://localhost:3001/api  # Mock server
# VITE_API_URL=https://api.cadscribe.app  # Production
```

### Mock Server
The included `mock-server.js` provides realistic API responses for development:

```bash
# Start mock server
node mock-server.js

# Available endpoints:
# POST /api/auth/login
# POST /api/auth/signup  
# GET  /api/projects
# POST /api/projects/:id/generate
# POST /api/projects/:id/messages
# POST /api/contact
```

### Demo Mode
Use the "Workspace Demo" button on the landing page to instantly access the workspace with sample data - no signup required.

## 🎮 User Guide

### Getting Started
1. Visit the landing page at `/`
2. Click "Workspace Demo" for instant access, or sign up for a new account
3. Create a new project or select an existing one
4. Start chatting with the AI to generate CAD models

### Workspace Layout
- **Left Sidebar**: Project list and navigation
- **Chat Panel**: Conversation history and input
- **3D Viewer**: Interactive model preview with toolbar
- **Inspector**: Parameters, materials, and export options

### Keyboard Shortcuts
- `G`: Open generate modal
- `F`: Fit model to view
- `S`: Take screenshot
- `Esc`: Exit fullscreen mode

### CAD Engines
- **CadQuery**: Python-based parametric modeling
- **OpenSCAD**: Functional programming for 3D
- **FreeCAD**: Python scripting for FreeCAD
- **JSCAD**: JavaScript computational design

## 🔧 Development

### Code Quality
```bash
npm run lint        # ESLint checks
npm run type-check  # TypeScript validation
npm run format      # Prettier formatting
```

### Testing
```bash
npm run test        # Jest unit tests
npm run test:e2e    # Playwright E2E tests
```

### Building
```bash
npm run build       # Production build
npm run preview     # Preview production build
```

## 🚀 Deployment Plan

### Cloud 1 - React Frontend
**Deployment Target**: Netlify / Vercel
- Build command: `npm run build`
- Output directory: `dist/`
- Environment variables:
  ```bash
  VITE_API_URL=https://backend.cadscribe.app
  VITE_CAD_SERVICE_URL=https://cad-service.cadscribe.app
  ```

### Cloud 2 - FastAPI Backend + MongoDB
**Deployment Target**: Render / Railway + MongoDB Atlas
- Runtime: Python 3.8+
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  ```bash
  MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/cadscribe
  ```

### Cloud 3 - CAD Microservice
**Deployment Target**: Separate container with FreeCAD installed
- Runtime: Python 3.8+ with FreeCAD
- Docker image: Custom image with FreeCAD dependencies
- Start command: `uvicorn cad_api:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  ```bash
  FREECAD_PATH=/usr/lib/freecad/lib
  OUTPUT_STORAGE_PATH=/app/generated_models
  ```

### Environment Configuration
```bash
# Frontend (.env.production)
VITE_API_URL=https://backend.cadscribe.app
VITE_CAD_SERVICE_URL=https://cad-service.cadscribe.app

# Backend (.env)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/cadscribe
CORS_ORIGINS=https://cadscribe.app,https://www.cadscribe.app

# CAD Service (.env)
FREECAD_PATH=/usr/lib/freecad/lib
OUTPUT_STORAGE_PATH=/app/generated_models
STORAGE_BUCKET=cadscribe-models
```

## 🔮 Next Steps

See `/dev-notes` page in the app for detailed integration guides:

1. **OpenAI Integration**: Replace mock generation with real AI
2. **Cloud CAD Rendering**: Set up Docker-based rendering services  
3. **Real Database**: Implement PostgreSQL schema
4. **File Storage**: Configure S3-compatible storage
5. **WebSocket**: Add real-time collaboration features

## 📄 License

This project is for demonstration purposes. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📞 Support

- Email: support@cadscribe.app
- Documentation: `/dev-notes` page
- Issues: GitHub Issues tab

---

Built with ❤️ using React, TypeScript, Three.js, and Tailwind CSS.