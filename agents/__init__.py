from .nmap_agent import run_nmap
from .whatweb_agent import run_whatweb

__all__ = ['run_nmap', 'run_whatweb']

# Register all available agents
AGENTS = {
    "nmap": {
        "task": run_nmap,
        "tool": "nmap",
        "args": ["-sSV -p-"]
    },
    "whatweb": {
        "task": run_whatweb,
        "tool": "whatweb",
        "args": ["--log-json=-"]
    }
}

def get_agent(name):
    """Get agent configuration by name"""
    return AGENTS.get(name)

def list_agents():
    """List all available agents"""
    return AGENTS 