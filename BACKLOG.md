# Backlog

## Completed Items

- ✅ Verified Python 3.12.10 installed (meets 3.10+ requirement)
- ✅ Verified Docker installation and running status
- ✅ Built Docker containers:
  - magentic-ui-vnc-browser:latest
  - magentic-ui-python-env:latest
- ✅ Frontend built successfully
- ✅ Configuration file (config.yaml) set up with Azure AI credentials
- ✅ Web UI accessible at `http://localhost:8081`
- ✅ Downloaded and installed FFmpeg (added to PATH)
- ✅ Resolved dependency conflict with pyee (upgraded to 13.0.0)
- ✅ Fixed Azure OpenAI model configuration with proper model_info settings
- ✅ Updated sample scripts to use Azure configuration from config.yaml

## Issues and Warnings

### Command Line Issues

```bash
TypeError: Parameter.make_metavar() missing 1 required positional argument: 'ctx'
```

### Browser Connection Issues

```
Connection failed: WebSocket error: connect ECONNREFUSED 127.0.0.1:55056
```

This appears when using the WebSurfer agent. The Playwright browser instance is having trouble connecting via WebSocket.

## TODO Items

### Critical (Blocking Functionality)

- Fix CLI issues with `magentic` command (parameter formatting, help output)

### Other Issues

- Document command usage and available options
- Create proper error handling for API failures
- Set up automated testing to validate functionality
- Improve Docker container startup performance