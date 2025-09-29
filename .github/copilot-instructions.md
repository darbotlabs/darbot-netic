# GitHub Copilot Instructions for Magentic-UI

This document provides guidance for GitHub Copilot when working on the Magentic-UI codebase.

## Project Overview

Magentic-UI is a research prototype that provides a human-centered interface powered by a multi-agent system built on Microsoft AutoGen. The system can browse the web, execute code, and analyze files with human oversight and control.

### Core Architecture

The system follows a **multi-agent architecture** with specialized agents:

- **Orchestrator**: Lead agent that handles co-planning, delegates tasks, and manages workflow
- **WebSurfer**: Web browsing agent with advanced browser control capabilities  
- **Coder**: Code execution agent with Docker container environment
- **FileSurfer**: File analysis agent with document conversion capabilities
- **UserProxy**: Represents human user interactions

### Key Technologies

- **Python 3.10+**: Primary language
- **AutoGen**: Multi-agent framework (`autogen-agentchat`, `autogen-core`, `autogen-ext`)
- **FastAPI**: Backend web framework
- **Playwright**: Browser automation for WebSurfer agent
- **Docker**: Containerized code execution environment
- **Pydantic**: Data validation and settings management
- **AsyncIO**: Asynchronous programming patterns
- **SQLModel/Alembic**: Database ORM and migrations
- **React/Gatsby**: Frontend (in `frontend/` directory)

## Directory Structure

```
src/magentic_ui/
├── agents/           # Agent implementations (coder, web_surfer, file_surfer, users)
├── backend/          # FastAPI backend and CLI
├── teams/            # Team orchestration logic
├── docker/           # Docker container definitions
├── eval/             # Evaluation benchmarks and utilities
├── learning/         # Plan learning and retrieval
└── tools/            # Utility tools and functions
```

## Coding Conventions

### General Guidelines

- **Type Hints**: Always use comprehensive type hints with modern Python typing
- **Async/Await**: Prefer async patterns for I/O operations and agent communications
- **Pydantic Models**: Use Pydantic for configuration classes and data validation
- **Error Handling**: Include proper exception handling, especially for agent communications
- **Logging**: Use `loguru` for structured logging with appropriate log levels

### Agent Development

When working with agents:

- Inherit from `BaseChatAgent` for new agent types
- Implement required methods: `on_messages`, `save_state`, `load_state`, `on_reset`
- Use `ComponentModel` pattern for agent configuration
- Follow the established prompt engineering patterns in `_prompts.py` files
- Ensure thread-safe operations for concurrent agent execution

### Code Style

- **Formatting**: Use `ruff format` (configured in pyproject.toml)
- **Linting**: Follow `ruff` rules for code quality
- **Type Checking**: Code must pass `pyright` strict mode
- **Line Length**: 120 characters maximum
- **Imports**: Group imports (standard library, third-party, local)

### Naming Conventions

- **Classes**: PascalCase (e.g., `CoderAgent`, `WebSurferConfig`)
- **Functions/Methods**: snake_case (e.g., `save_state`, `process_message`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: Leading underscore (`_internal_method`)

## Testing Patterns

### Test Structure

- Tests are located in `tests/` directory
- Use `pytest` with `pytest-asyncio` for async tests
- Maintain high test coverage (use `pytest-cov`)

### Writing Tests

```python
import pytest
from magentic_ui.agents._coder import CoderAgent

@pytest.mark.asyncio
async def test_coder_agent_execution():
    """Test that demonstrates async testing pattern."""
    agent = CoderAgent(name="test_coder", model_client=mock_client)
    result = await agent.on_messages(messages)
    assert result is not None
```

### Testing Guidelines

- **Unit Tests**: Test individual agent methods and utilities
- **Integration Tests**: Test agent interactions and workflows
- **Mocking**: Mock external dependencies (LLM clients, Docker, browsers)
- **Fixtures**: Use pytest fixtures for common test setup
- **Async Testing**: Always use `@pytest.mark.asyncio` for async test functions

## Best Practices

### Agent Communication

- Use structured message types from `autogen_agentchat.messages`
- Handle `CancellationToken` for graceful cancellation
- Implement proper state management with `save_state`/`load_state`
- Use appropriate error handling for network and LLM failures

### Performance Considerations

- **Docker Operations**: Cache Docker images and reuse containers when possible
- **LLM Calls**: Implement retries and rate limiting
- **Browser Automation**: Use efficient selectors and minimize page loads
- **Async Operations**: Don't block the event loop with synchronous operations

### Security Guidelines

- **Input Validation**: Validate all user inputs and agent responses
- **Code Execution**: Ensure code execution happens in isolated Docker containers
- **File Access**: Restrict file system access to designated directories
- **Web Browsing**: Implement appropriate safeguards for web interactions

### Configuration Management

- Use `pydantic-settings` for environment-based configuration
- Support multiple LLM providers (OpenAI, Azure OpenAI, Ollama)
- Configuration files should be in YAML format
- Provide sensible defaults for all optional settings

## Common Patterns

### Agent Configuration Pattern

```python
class AgentConfig(BaseModel):
    name: str
    model_client: ComponentModel
    description: str = "Default description"
    # Additional config fields

class Agent(BaseChatAgent, Component[AgentConfig]):
    @classmethod
    def _from_config(cls, config: AgentConfig) -> Self:
        return cls(
            name=config.name,
            model_client=ChatCompletionClient.load_component(config.model_client),
            # ... other parameters
        )
```

### Prompt Engineering Pattern

- Store prompts in dedicated `_prompts.py` files
- Use f-strings or template functions for dynamic content
- Include examples and clear instructions in prompts
- Structure prompts for JSON responses when needed

### Error Handling Pattern

```python
try:
    result = await some_agent_operation()
except CancellationError:
    logger.info("Operation cancelled")
    raise
except Exception as e:
    logger.error(f"Agent operation failed: {e}")
    # Handle gracefully or re-raise
```

## Development Workflow

### Local Development

1. Install dependencies: `uv sync --all-extras` or `pip install -e .`
2. Run checks: `poe check` (formatting, linting, type checking, tests)
3. Install Playwright: `playwright install` (for web agent development)
4. Start development server: `magentic ui --port 8081`

### Quality Assurance

Before submitting changes:

- Run `poe fmt` to format code
- Run `poe lint` to check code quality
- Run `poe pyright` for type checking
- Run `poe test` for full test suite
- Ensure Docker is available for integration tests

### Documentation

- Update docstrings for new/modified functions
- Include type hints in all function signatures
- Update relevant README files for new features
- Add inline comments for complex logic only when necessary

## Dependencies

### Core Dependencies

- `autogen-agentchat==0.5.7`: Agent chat functionality
- `autogen-core==0.5.7`: Core AutoGen framework  
- `autogen-ext==0.5.7`: Extended functionality (Docker, web, file operations)
- `fastapi[standard]`: Web framework for backend API
- `playwright==1.51`: Browser automation
- `pydantic`: Data validation and configuration
- `docker`: Container management

### Development Dependencies

- `pytest`: Testing framework
- `ruff`: Code formatting and linting
- `pyright`: Type checking
- `poethepoet`: Task runner

## Troubleshooting

### Common Issues

- **Docker not available**: Ensure Docker is installed and running
- **Browser automation issues**: Run `playwright install` to install browser binaries
- **Type checking errors**: Ensure all imports have proper type stubs
- **Async context issues**: Use proper async context managers for agent operations

Remember to maintain the human-in-the-loop philosophy of Magentic-UI - always provide mechanisms for user oversight and control in new features.