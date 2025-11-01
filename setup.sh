#!/bin/bash

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting CADSCRIBE setup...${NC}\n"

# Create .env files if they don't exist
echo -e "${YELLOW}Setting up environment files...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << EOL
VITE_API_URL=http://localhost:8000
EOL
    echo "Created frontend .env"
fi

if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOL
# Database Configuration
MONGODB_URI=mongodb://127.0.0.1:27017/cadscribe
DATABASE_NAME=cadscribe

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Service URLs
CAD_SERVICE_URL=http://localhost:9000

# Security
SECRET_KEY=your-secret-key-change-in-production
DEBUG=false

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Storage
UPLOAD_DIR=uploads
GENERATED_MODELS_DIR=generated_models
EOL
    echo "Created backend .env"
fi

# Install frontend dependencies
echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
npm install

# Install backend dependencies
echo -e "\n${YELLOW}Installing backend dependencies...${NC}"
cd backend
python -m pip install -r requirements.txt
cd ..

# Install CAD service dependencies
echo -e "\n${YELLOW}Installing CAD service dependencies...${NC}"
cd cad-service
python -m pip install -r requirements.txt
cd ..

# Create required directories
echo -e "\n${YELLOW}Creating required directories...${NC}"
mkdir -p backend/uploads backend/generated_models cad-service/generated_models

# Check MongoDB installation
echo -e "\n${YELLOW}Checking MongoDB installation...${NC}"
if command -v mongod &> /dev/null; then
    echo "MongoDB is installed"
    # Start MongoDB if not running (platform specific)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mongodb-community
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start mongodb
    elif [[ "$OSTYPE" == "msys" ]]; then
        net start MongoDB
    fi
else
    echo "MongoDB is not installed. Please install MongoDB first."
    echo "Windows: choco install mongodb"
    echo "macOS: brew install mongodb-community"
    echo "Linux: sudo apt install mongodb"
fi

# Check FreeCAD installation
echo -e "\n${YELLOW}Checking FreeCAD installation...${NC}"
if command -v freecad &> /dev/null; then
    echo "FreeCAD is installed"
else
    echo "FreeCAD is not installed. Please install FreeCAD first."
    echo "Windows: choco install freecad"
    echo "macOS: brew install freecad"
    echo "Linux: sudo apt install freecad"
fi

echo -e "\n${GREEN}Setup completed!${NC}"
echo -e "\nTo start the services:"
echo "1. Start backend: cd backend && python main.py"
echo "2. Start CAD service: cd cad-service && python cad_api.py"
echo "3. Start frontend: npm run dev"
echo -e "\nMake sure to update the API keys in backend/.env:"
echo "- OPENAI_API_KEY from https://platform.openai.com/api-keys"
echo "- GEMINI_API_KEY from https://makersuite.google.com/app/apikey"