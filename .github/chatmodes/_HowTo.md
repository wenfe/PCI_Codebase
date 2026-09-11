# Usage examples:


## Preconditions:
 - The Azure Dev Ops MCP server must be running (If not go to the file .vscode/mcp.json and press start - further instructions at the bottom of this guide)
 - Sequential thinking feature must be running (If not go to the file .vscode/mcp.json and press start)
 - The Azure DevOps Server and the respective Markdown file (e.g. story-creation.chatmode.md) must be attached to the copilot as context.
 - The Agent mode should be choosen (Do not use cutome modes, they do not work with mcp servers yet)
 - Claude Sonnet 4 model should be used (gpt models will produce useless outcomes)


## Create a user stroy:
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Title: "New Flashware size limit from 64Gb to 100Gb"

Keywords: flashware size, size limit, 64 Gigabyte, fileSizeChecker

Repository: vsmds-flashware-origin-service, vsmds-flashware-odxfchecker-service

Description: Currently, there is a file size limit of 64 gigabytes for uploading flashware. This is to be increased to 100 gigabytes. To this end, the odxf checker is to be adapted and the origin service is also to be searched for code locations to see if anything else needs to be adapted here. In addition, the error messages and API definitions in the respective services are to be adapted. Please also formulate meaningful scenarios for manual tests.

Also make sure to read the complete content of the attached file story-creation.chatmode.md, process its content, and follow the rules and guidelines outlined in the file for conducting the research and creating the story accordingly.
```

## Enhance existing user story:
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Please enhance the user story with ID 302001. Make sure to conduct detailed research in related work items, the wiki, and the following repositories:
- vsmds-flashware-origin-service
- vsmds-flashware-oxfchecker-service
Also make sure to read the complete content of the attached file story-enhancement.chatmode.md, process its content, and follow the rules and guidelines outlined in the file for conducting the research and enhancing the story accordingly.
```

## Do the user story breakdown into smaller tasks
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Please break down the user story with ID 302001 into smaller tasks. Make sure to conduct detailed research in related work items, the wiki, and the following repositories:
vsmds-flashware-origin-service
vsmds-flashware-oxfchecker-service
Also make sure to read the complete content of the attached file story-breakdown.chatmode.md, process its content, and follow the rules and guidelines outlined in the file for conducting the research and breaking down the story accordingly
```

## Let the copilot implement a task from azure dev ops
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Please follow the guidelines in the attached file task-implementation.chatmode.md. The task that you should implement ist Task 302013. Make sure to conduct detailed research as described in task-implementation.chatmode.md
Make sure to read the complete content of the attached file task-implementation.chatmode.md, process its content, and strictly follow the rules and guidelines outlined in the file!
```

## Do a pull request code review 
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Please follow the guidelines in the attached file codereview-creation.chatmode.md. The Pull Request that you should review has the ID 312812. Make sure to conduct detailed research as described in codereview-creation.chatmode.md
Make sure to read the complete content of the attached file codereview-creation.chatmode.md, process its content, and strictly follow the rules and guidelines outlined in the file!
```

## Write a wiki documentation
 - make sure the preconditions are met 
 - paste a text like below (with your own user story requirements) in the copilot chat:
```
Please follow the rules and guidelines in the attached file documentation-creation.chatmode.md to change and overall improve the azure dev ops wiki documentation about the flashware file size check. 

Related User Story ID: 302001
Wiki Path with the to be updated documentation: https://dev.azure.com/.../26313/FlashwareSizeChecker
Document Title: FlashwareSizeChecker
Related Repository: vsmds-flashware-odxfchecker-service
Additional Context: We just implemented the User Story 302001 and now the Documentation needs to be updated regarding the changes. While you're updating the documentation, you can also improve or add to other sections (but only on the “FlashwareSizeChecker” page).

Make sure to conduct detailed research as described in documentation-creation.chatmode.md
Make sure to read the complete content of the attached file documentation-creation.chatmode.md, process its content, and strictly follow the rules and guidelines outlined in the file!
```


---------------------

# Azure DevOps MCP Server - Developer Setup Guide

This guide provides step-by-step instructions for developers to install and use the Azure DevOps MCP Server locally with VS Code and GitHub Copilot.


> ⚠️ **IMPORTANT DISCLAIMER - EARLY VERSION WARNING**

> **This is a very early version of the Azure DevOps MCP Server and has not been extensively tested.**

> **⚠️ CRITICAL SAFETY WARNINGS:**

> - **AVOID DESTRUCTIVE OPERATIONS** (delete, overwrite, bulk updates)
> - **USE READ-ONLY OPERATIONS** whenever possible (list, view, search)
> - **BE EXTREMELY CAUTIOUS** with any write operations to Azure DevOps
> - **BACKUP IMPORTANT DATA** before performing any modifications


  

##  Overview
The Azure DevOps MCP Server enables direct integration between VS Code, GitHub Copilot, and Azure DevOps services. It provides access to work items, repositories, builds, releases, test plans, and more through natural language prompts in GitHub Copilot Chat.

  

## Quick Setup for Developers

  

### Prerequisites

  

1. **Visual Studio Code** ([Download](https://code.visualstudio.com/download)) or **VS Code Insiders**

2. **Node.js 20+** ([Download](https://nodejs.org/en/download))

3. **Azure CLI** ([Download](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli))

4. **GitHub Copilot Extension** (Install from VS Code Extensions Marketplace)

5. Access to the `vsmds` Azure DevOps project

  

### Step 1: Authentication Setup

1. Open a terminal (PowerShell/Command Prompt)

2. Log in to Azure DevOps:

   ```bash
   az login
   ```

3. Verify login:

   ```bash
   az account show
   ```

  

### Step 2: Local Project Setup

1. **Create/Navigate to your VS Code project directory**

2. **Create required folders and files:** 

```  
your-project/

   ├── .github/

   │   └── copilot-instructions.md

   └── .vscode/

       └── mcp.json
```


### Step 3: Configure MCP Server

**Create `.vscode/mcp.json`** with the following content:
 

```json
{
  "inputs": [
    {
      "id": "ado_org",
      "type": "promptString",
      "description": "daimler-mic",
      "default": "daimler-mic"
    }
  ],
  "servers": {
    "ado": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@azure-devops/mcp",
        "${input:ado_org}"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}

```

  

### Step 4: Configure Copilot Instructions

**Create `.github/copilot-instructions.md`** with the following content:


```markdown
# Copilot Instructions for Azure DevOps MCP

## Project Scope
- **IMPORTANT**: Only work with the Azure DevOps project named "vsmds"
- Do not access or modify any other Azure DevOps projects
- All queries and operations should be limited to the "vsmds" project only

## Safety Guidelines
- **BE EXTREMELY CAREFUL** with any delete operations in Azure DevOps
- **THIS IS AN EARLY VERSION** - expect bugs and unexpected behavior
- Always confirm before deleting work items, repositories, builds, or any other resources
- When in doubt about deletions, ask for explicit confirmation first
- Prefer updating/modifying over deleting when possible
- **ALWAYS BACKUP** important data before making changes
- **TEST WITH NON-CRITICAL DATA** first to understand the tool's behavior

## Usage
- Use Azure DevOps MCP tools to query and manage resources in the "vsmds" project
- Focus on read operations and safe modifications
- Provide clear, concise information about Azure DevOps resources
- Help with work item management, repository operations, and build/release information

## Commands
When using Azure DevOps commands, always specify the project as "vsmds":
- Example: "List work items for project 'vsmds'"
- Example: "List repositories for project 'vsmds'"
- Example: "Show builds for project 'vsmds'"
```

  

### Step 5: Start the MCP Server

1. **Save both files** (`.vscode/mcp.json` and `.github/copilot-instructions.md`)
2. **Look for the "Start" button** in VS Code (usually appears in the status bar)
3. **Click "Start"** to initialize the MCP server
4. **Enter organization name** when prompted: `daimler-mic`


### Step 6: Enable GitHub Copilot Agent Mode

1. **Open GitHub Copilot Chat** in VS Code (`Ctrl+Shift+I` or `Cmd+Shift+I`)

2. **Switch to Agent Mode**:
   - Look for "Agent Mode" option in the chat interface
   - Or follow the [Agent Mode documentation](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)

  

### Step 7: Select Azure DevOps Tools

1. In Copilot Chat, click **"Select Tools"**
2. **Choose the available Azure DevOps tools** from the list
3. **Confirm your selection**

##  Testing the Setup
Try these sample prompts to verify everything works:
- `"List my ADO projects"`
- `"List repositories for project 'vsmds'"`
- `"Show recent builds for project 'vsmds'"`
- `"List my work items for project 'vsmds'"`
- `"List pull requests for project 'vsmds'"`

  

##  Available Capabilities

Once configured, you have access to: 

### Core Operations

- **Projects**: List and manage Azure DevOps projects
- **Teams**: Retrieve team information

### Work Management
- **Work Items**: Create, read, update, and manage work items
- **Iterations**: List and manage team iterations
- **Backlogs**: View and manage project backlogs
- **Queries**: Execute work item queries

### Source Control
- **Repositories**: List and manage Git repositories
- **Pull Requests**: Create, review, and manage pull requests
- **Branches**: List and manage repository branches
- **Comments**: Add and manage PR comments

### Build & Release
- **Build Definitions**: View and manage build pipelines
- **Builds**: Trigger builds and view build history
- **Releases**: Manage release pipelines and deployments

### Testing
- **Test Plans**: Create and manage test plans
- **Test Cases**: Create and manage test cases
- **Test Results**: View test execution results

### Search
- **Code Search**: Search across your codebase
- **Wiki Search**: Search Azure DevOps wiki content
- **Work Item Search**: Search work items



##  Required Files Summary
**Ensure these files are in your local VS Code project:** 

```

your-project/

├── .github/

│   └── copilot-instructions.md    # Copilot behavior configuration

└── .vscode/

    └── mcp.json                   # MCP server configuration

```

  

##  Best Practices
1. **Always specify project**: Use `"vsmds"` in all commands
2. **SAFETY FIRST**: This is an early version - be extremely cautious with any write operations
3. **Focus on read operations**: Be cautious with create/update/delete operations
4. **Test with non-critical data first**: Never start with important production data
5. **Use specific prompts**: Be clear about what you want to accomplish
6. **Test connectivity**: Start with simple commands like listing projects
7. **Backup before changes**: Always ensure you can recover if something goes wrong

  

##  Additional Resources
- [VS Code Agent Mode Documentation](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode)
- [Azure DevOps REST API Documentation](https://docs.microsoft.com/en-us/rest/api/azure/devops/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
  

---

  

**Note**: This server is in public preview. Features may change before general availability. Always refer to the latest documentation for current information.

