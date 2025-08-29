# Multi-Agent Routing System Diagrams

This folder contains Mermaid diagrams for presenting the Ryoma AI multi-agent routing system architecture.

## Available Diagrams

### 1. **multi-agent-routing-clean.mmd** - Main System Overview
- **Best for:** High-level system architecture presentations
- **Shows:** Complete flow from user input through agent routing to final output
- **Key Features:** LLM-based router, 4 specialized agents, data integration
- **Use in PPT:** Perfect for explaining the overall system to stakeholders

### 2. **routing-decision-clean.mmd** - Decision Flow
- **Best for:** Technical deep-dive presentations  
- **Shows:** How the LLM router analyzes and classifies different types of questions
- **Key Features:** Real examples, confidence scoring, feedback loops
- **Use in PPT:** Great for demonstrating the intelligence of the routing system

### 3. **agent-overview-clean.mmd** - Agent Capabilities
- **Best for:** Feature showcase and capability demonstrations
- **Shows:** Detailed breakdown of each agent's capabilities and use cases
- **Key Features:** Examples, supported technologies, advanced features
- **Use in PPT:** Perfect for showing the breadth of system capabilities

## How to Use in PowerPoint

### Option 1: Online Mermaid Editor
1. Copy the .mmd file content
2. Go to [Mermaid Live Editor](https://mermaid.live/)
3. Paste the content
4. Export as PNG or SVG
5. Insert the image into PowerPoint

### Option 2: VS Code Extension
1. Install "Mermaid Preview" extension in VS Code
2. Open the .mmd file
3. Use Command Palette: "Mermaid Preview: Show Preview"
4. Right-click the preview and save as image

### Option 3: CLI Tool (if you have mermaid-cli installed)
```bash
npx @mermaid-js/mermaid-cli -i multi-agent-routing-clean.mmd -o routing-system.png
```

## Diagram Customization

### Colors Used
- **User/Input:** Blue (`#e3f2fd`, `#1976d2`)
- **Router/Logic:** Purple (`#f3e5f5`, `#7b1fa2`)  
- **Agents:** Green (`#e8f5e8`, `#388e3c`)
- **Data Sources:** Orange (`#fff8e1`, `#f57c00`)
- **Output/Results:** Pink (`#fce4ec`, `#c2185b`)

### Modifying for Your Presentation
- Change colors by editing the `classDef` sections
- Add your company logo/branding colors
- Modify text to match your terminology
- Add or remove agents based on your implementation

## Presentation Tips

### For Executive Audience
- Use **multi-agent-routing-clean.mmd** 
- Focus on business value and capabilities
- Emphasize "intelligent routing" and "specialized experts"

### For Technical Audience  
- Use **routing-decision-clean.mmd**
- Highlight LLM classification accuracy
- Discuss confidence scoring and fallback mechanisms

### For Product Demo
- Use **agent-overview-clean.mmd**
- Show concrete examples and use cases
- Demonstrate the variety of supported operations

## Key Talking Points

1. **Intelligence:** LLM-powered routing eliminates manual agent selection
2. **Specialization:** Each agent is optimized for specific types of tasks
3. **Scalability:** Easy to add new agents and capabilities
4. **Performance:** Vector search and catalog indexing for fast database operations
5. **User Experience:** Natural language interface with context-aware responses

## File Structure
```
architecture/
├── multi-agent-routing-clean.mmd     # Main system overview
├── routing-decision-clean.mmd        # Decision flow details
├── agent-overview-clean.mmd          # Agent capabilities
├── multi-agent-routing-system.mmd   # Original detailed version
├── routing-decision-flow.mmd         # Original detailed version  
├── agent-capabilities-overview.mmd   # Original detailed version
└── README-diagrams.md               # This file
```

The "*-clean.mmd" files are optimized for Mermaid parsers and presentations, while the original files contain more detailed information but may have parsing issues in some tools.