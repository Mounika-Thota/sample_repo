"""
Demo script for DocumentationGeneratorAgent.

This script demonstrates how to use the DocumentationGeneratorAgent
to generate different types of documentation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.documentation_generator.documentation_agent import DocumentationGeneratorAgent


def demo_agent_initialization():
    """Demo: Initialize the agent."""
    print("=" * 80)
    print("DEMO 1: Agent Initialization")
    print("=" * 80)

    agent = DocumentationGeneratorAgent()

    print(f"✓ Agent Name: {agent.agent_name}")
    print(f"✓ Supported Doc Types: {', '.join(agent.SUPPORTED_DOC_TYPES)}")
    print()


def demo_code_analysis():
    """Demo: Analyze Python code structure."""
    print("=" * 80)
    print("DEMO 2: Code Analysis")
    print("=" * 80)

    from src.agents.documentation_generator.utils import analyze_python_file

    # Analyze a sample file
    sample_file = project_root / "src" / "agents" / "base_agent" / "base_agent.py"

    if sample_file.exists():
        print(f"Analyzing: {sample_file}")
        analysis = analyze_python_file(str(sample_file))

        print(f"\n✓ File: {analysis['file_path']}")
        print(f"✓ Lines of Code: {analysis.get('lines_of_code', 'N/A')}")

        if analysis.get("classes"):
            print(f"✓ Classes Found: {len(analysis['classes'])}")
            for cls in analysis["classes"]:
                print(f"  - {cls['name']} (methods: {len(cls.get('methods', []))})")

        if analysis.get("functions"):
            print(f"✓ Functions Found: {len(analysis['functions'])}")
    else:
        print(f"Sample file not found: {sample_file}")

    print()


def demo_project_structure():
    """Demo: Scan project structure."""
    print("=" * 80)
    print("DEMO 3: Project Structure Scan")
    print("=" * 80)

    from src.agents.documentation_generator.utils import scan_project_structure

    # Scan a subdirectory
    target_dir = project_root / "src" / "agents"

    if target_dir.exists():
        print(f"Scanning: {target_dir}")
        structure = scan_project_structure(str(target_dir))

        print(f"\n✓ Total Python Files: {structure['total_python_files']}")
        print(f"✓ Total Lines of Code: {structure['total_lines']}")
        print(f"✓ Directories: {', '.join(structure['directories'][:5])}")

        if structure["python_files"]:
            print("\n✓ Sample Python Files:")
            for file in structure["python_files"][:5]:
                print(f"  - {file}")
    else:
        print(f"Target directory not found: {target_dir}")

    print()


def demo_documentation_generation():
    """Demo: Generate documentation (dry run)."""
    print("=" * 80)
    print("DEMO 4: Documentation Generation (Dry Run)")
    print("=" * 80)

    agent = DocumentationGeneratorAgent()

    # Prepare sample analysis data (simulated)
    analysis_results = {
        "target_path": "src/agents/",
        "doc_type": "readme",
        "files_analyzed": 15,
        "total_lines": 2500,
        "file_analyses": [
            {
                "file_path": "src/agents/base_agent/base_agent.py",
                "lines_of_code": 150,
                "classes": [
                    {
                        "name": "BaseAgent",
                        "methods": [
                            {"name": "__init__"},
                            {"name": "process_request"},
                        ],
                    }
                ],
            }
        ],
        "project_structure": {
            "root": "src/agents/",
            "total_python_files": 15,
            "total_lines": 2500,
            "directories": ["base_agent", "user_story_generator"],
            "config_files": [],
        },
    }

    # Prepare context
    context = agent._prepare_documentation_context(
        doc_type="readme",
        analysis_results=analysis_results,
        custom_instructions="Create a brief README",
        additional_context=None,
    )

    print("✓ Context prepared for LLM")
    print(f"✓ Context length: ~{len(context)} characters")
    print("\n✓ Context Preview:")
    print("-" * 80)
    print(context[:500] + "...")
    print("-" * 80)
    print("\n(In real usage, this context would be sent to Azure OpenAI)")
    print()


def demo_full_generation_example():
    """Demo: Full generation example (requires database)."""
    print("=" * 80)
    print("DEMO 5: Full Generation Example")
    print("=" * 80)

    print("Example code to generate documentation:")
    print()

    code_example = """
# Initialize database session
db = SessionLocal()

# Initialize agent
agent = DocumentationGeneratorAgent()

# Generate documentation
result = agent.generate_documentation(
    db=db,
    project_id="demo-project-123",
    doc_type="readme",
    target_path="src/agents/",
    user_id="demo-user-456",
    custom_instructions="Create a brief README for the agents directory"
)

print(f"Status: {result['status']}")
print(f"Documentation:\\n{result['documentation']}")

db.close()
"""

    print(code_example)

    print("\nNote: This requires:")
    print("  - Database connection configured")
    print("  - Azure OpenAI credentials")
    print("  - Valid project_id and user_id")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DOCUMENTATION GENERATOR AGENT DEMO" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    demos = [
        ("Agent Initialization", demo_agent_initialization),
        ("Code Analysis", demo_code_analysis),
        ("Project Structure", demo_project_structure),
        ("Documentation Generation", demo_documentation_generation),
        ("Full Example", demo_full_generation_example),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"✗ Demo {i} failed: {e}")
            print()

        if i < len(demos):
            input("Press Enter to continue to next demo...")
            print("\n")

    print("=" * 80)
    print("Demo completed! Check the docs for more information:")
    print("  - docs/DOCUMENTATION_GENERATOR_USAGE.md")
    print("  - docs/AGENT_EXTENSION_GUIDE.md")
    print("=" * 80)


if __name__ == "__main__":
    main()
