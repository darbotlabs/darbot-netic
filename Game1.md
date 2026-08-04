## 🏁 **Pre-Quest Requirements Check**
### Objectives:
- [ ] Verify system compatibility
- [ ] Install core dependencies

### Tasks:
1. **System Check**
   ```bash
   # Check Python version (needs 3.10+)
   python --version
   ```

2. **Docker Installation**
   - Windows/Mac: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux: Install Docker Engine
   ```bash
   # Verify Docker is running
   docker --version
   docker ps
   ```

3. **Windows Users Only: WSL2 Setup**
   ```bash
   # Install WSL2
   wsl --install
   # Configure Docker Desktop for WSL2
   # Go to Docker Desktop Settings > Resources > WSL Integration
   ```

### 🔍 **Validation Checkpoint 1**
```bash
# Run all checks
python --version | grep -E "3\.(1[0-3])"  # Should show 3.10-3.13
docker run hello-world  # Should print success message
# Windows only: 
wsl --list --verbose  # Should show WSL2 distro
```

---

## 🚀 **Level 1: Repository Setup**
### Objectives:
- [ ] Clone repository
- [ ] Set up Python environment

### Tasks:
1. **Clone the Repository**
   ```bash
   git clone https://github.com/microsoft/magentic-ui.git
   cd magentic-ui
   ```

2. **Install UV Package Manager**
   ```bash
   # Install uv (recommended for faster setup)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or use pip: pip install uv
   ```

3. **Create Virtual Environment**
   ```bash
   uv venv --python=3.12 .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   uv sync --all-extras
   ```

### 🔍 **Validation Checkpoint 2**
```bash
# Check virtual environment
which python | grep ".venv"
# Check uv installation
uv --version
# Check key dependencies
python -c "import autogen_agentchat; print('✅ Core dependencies installed')"
```

---

## 🏗️ **Level 2: Build Docker Containers**
### Objectives:
- [ ] Build required Docker images
- [ ] Verify container functionality

### Tasks:
1. **Build Browser Container**
   ```bash
   docker build -t magentic-ui-vnc-browser:latest ./src/magentic_ui/docker/magentic-ui-browser-docker
   ```

2. **Build Python Environment Container**
   ```bash
   docker build -t magentic-ui-python-env:latest ./src/magentic_ui/docker/magentic-ui-python-env
   ```

### 🔍 **Validation Checkpoint 3**
```bash
# List Docker images
docker images | grep magentic-ui
# Should show both containers:
# - magentic-ui-vnc-browser:latest
# - magentic-ui-python-env:latest
```

---

## 🎨 **Level 3: Frontend Setup**
### Objectives:
- [ ] Build the web interface
- [ ] Configure environment variables

### Tasks:
1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Frontend Dependencies**
   ```bash
   # Ensure yarn is installed
   npm install -g yarn
   yarn install
   ```

3. **Create Environment Configuration**
   ```bash
   cp .env.default .env.development
   # Edit .env.development and set:
   # GATSBY_API_URL=http://localhost:8081/api
   ```

4. **Build Frontend**
   ```bash
   yarn build
   cd ..  # Return to root directory
   ```

### 🔍 **Validation Checkpoint 4**
```bash
# Check build output
ls frontend/public/index.html
# Verify environment file
grep GATSBY_API_URL frontend/.env.development
```

---

## 🔑 **Level 4: API Configuration**
### Objectives:
- [ ] Configure API keys
- [ ] Set up model clients

### Tasks:
1. **Set OpenAI API Key** (Option A: Environment Variable)
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # Add to .bashrc/.zshrc for persistence
   ```

2. **Create Custom Configuration** (Option B: Config File)
   ```bash
   # Create config.yaml in project root
   cat > config.yaml << 'EOF'
   model_config: &client
     provider: OpenAIChatCompletionClient
     config:
       model: gpt-4o
       api_key: "your-api-key-here"
       max_retries: 10

   orchestrator_client: *client
   coder_client: *client
   web_surfer_client: *client
   file_surfer_client: *client
   action_guard_client: *client
   EOF
   ```

### 🔍 **Validation Checkpoint 5**
```bash
# Test API key
python -c "import os; assert os.getenv('OPENAI_API_KEY'), 'API key not set'"
# Or check config file
test -f config.yaml && echo "✅ Config file exists"
```

---

## 🎯 **Level 5: Launch Magentic-UI**
### Objectives:
- [ ] Start the application
- [ ] Verify all services running

### Tasks:
1. **Start Magentic-UI**
   ```bash
   # Basic launch
   magentic ui --port 8081
   
   # Or with custom config
   magentic ui --port 8081 --config config.yaml
   ```

2. **Open Web Interface**
   - Navigate to: http://localhost:8081
   - You should see the Magentic-UI interface

### 🔍 **Validation Checkpoint 6**
```bash
# Check if server is running
curl http://localhost:8081/health || echo "Server check"
# Check Docker containers are running
docker ps | grep -E "(vnc-browser|python-env)"
```

---

## 🏆 **Bonus Level: Advanced Features**
### Optional Objectives:
- [ ] Test sample agents
- [ ] Configure memory/learning features

### Tasks:
1. **Test Sample Scripts**
   ```bash
   # Test individual agents
   python samples/sample_coder.py --work_dir debug
   python samples/sample_web_surfer.py
   python samples/sample_file_surfer.py --work-dir debug
   ```

2. **Enable Plan Learning** (Optional)
   ```bash
   # In your launch command
   magentic ui --port 8081 --retrieve-relevant-plans hint
   ```

### 🔍 **Final Boss Validation**
```bash
# Full system test
echo "Testing Magentic-UI Setup..."
python -c "
import sys
print('✅ Python', sys.version.split()[0])
"
docker ps --format "table {{.Image}}\t{{.Status}}" | grep magentic-ui
curl -s http://localhost:8081 > /dev/null && echo "✅ Web UI accessible"
echo "🎉 Setup Complete! Visit http://localhost:8081"
```

---

## 🆘 **Troubleshooting Scrolls**

### Common Issues:
1. **Docker Permission Denied**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Port Already in Use**
   ```bash
   # Use different port
   magentic ui --port 8082
   ```

3. **Frontend Build Fails**
   ```bash
   # Clean and rebuild
   cd frontend
   rm -rf node_modules .cache public
   yarn install
   yarn build
   ```

### 📝 **Quest Complete Checklist**
- [ ] All validation checkpoints passed
- [ ] Web UI accessible at http://localhost:8081
- [ ] Sample task working (try: "What's the weather today?")
- [ ] Browser view showing in right panel
- [ ] No error messages in console

🎊 **Congratulations! You've successfully set up Magentic-UI!**