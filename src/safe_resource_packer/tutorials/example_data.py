"""
Example Data - Safe practice scenarios and test data for learning.

This module provides realistic but safe example scenarios that users can
practice with to learn the tool without risking their actual mod files.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, TaskID
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..dynamic_progress import log


class ExampleDataGenerator:
    """Generates safe practice scenarios for learning."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the example data generator.
        
        Args:
            console: Rich console for formatted output
        """
        self.console = console
        self.temp_dir = None
        self.scenarios = self._load_scenarios()
    
    def create_practice_scenario(self, scenario_name: str = "bodyslide_basics") -> Dict[str, str]:
        """
        Create a safe practice scenario with example files.
        
        Args:
            scenario_name: Which scenario to create
            
        Returns:
            Dictionary with paths to created folders
        """
        try:
            if scenario_name not in self.scenarios:
                raise ValueError(f"Unknown scenario: {scenario_name}")
            
            scenario = self.scenarios[scenario_name]
            self._print(f"🎯 Creating practice scenario: {scenario['name']}", "cyan")
            
            # Create temporary directory structure
            self.temp_dir = tempfile.mkdtemp(prefix="safe_resource_packer_tutorial_")
            
            paths = {
                'base': self.temp_dir,
                'source': os.path.join(self.temp_dir, 'GameData'),
                'generated': os.path.join(self.temp_dir, 'GeneratedFiles'),
                'output': os.path.join(self.temp_dir, 'Output')
            }
            
            # Create directory structure
            for path in paths.values():
                os.makedirs(path, exist_ok=True)
            
            # Generate scenario files
            self._generate_source_files(paths['source'], scenario)
            self._generate_generated_files(paths['generated'], scenario)
            
            # Create instruction file
            self._create_scenario_instructions(paths['base'], scenario, paths)
            
            self._print("✅ Practice scenario created successfully!", "green")
            return paths
            
        except Exception as e:
            log(f"Error creating practice scenario: {e}", log_type='ERROR')
            self._print("❌ Failed to create practice scenario", "red")
            return {}
    
    def _generate_source_files(self, source_path: str, scenario: Dict[str, Any]):
        """Generate realistic source (base game) files."""
        
        source_files = scenario.get('source_files', [])
        
        for file_info in source_files:
            file_path = os.path.join(source_path, file_info['path'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create file with appropriate content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info.get('content', f"# {file_info['path']}\\n"))
    
    def _generate_generated_files(self, generated_path: str, scenario: Dict[str, Any]):
        """Generate realistic generated (mod) files."""
        
        generated_files = scenario.get('generated_files', [])
        
        for file_info in generated_files:
            file_path = os.path.join(generated_path, file_info['path'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create file with appropriate content and classification
            content = file_info.get('content', f"# Generated: {file_info['path']}\\n")
            
            # Add classification hint as comment
            classification = file_info.get('expected_classification', 'pack')
            content += f"# Expected classification: {classification}\\n"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def _create_scenario_instructions(self, base_path: str, scenario: Dict[str, Any], paths: Dict[str, str]):
        """Create instruction file for the scenario."""
        
        instructions = f"""
# {scenario['name']} - Practice Scenario

## Overview
{scenario.get('description', 'A practice scenario for learning Safe Resource Packer.')}

## Folder Structure
- **Source (Game Data):** {paths['source']}
  - Contains {len(scenario.get('source_files', []))} base game files
  - Represents your game's Data folder

- **Generated Files:** {paths['generated']}  
  - Contains {len(scenario.get('generated_files', []))} mod files
  - Represents files you want to process

- **Output:** {paths['output']}
  - Where your results will be saved
  - Currently empty, will be filled by the tool

## Expected Results
{scenario.get('expected_results', 'Process these files to see the classification in action!')}

## Learning Objectives
{scenario.get('learning_objectives', 'Practice using the Safe Resource Packer with safe example data.')}

## Next Steps
1. Use the Safe Resource Packer tool
2. Set Source Folder to: {paths['source']}
3. Set Generated Folder to: {paths['generated']}
4. Set Output Folder to: {paths['output']}
5. Run the processing and observe the results!

## Cleanup
This is a temporary practice scenario. You can safely delete the entire folder:
{base_path}
"""
        
        instruction_file = os.path.join(base_path, 'README_SCENARIO.txt')
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write(instructions.strip())
    
    def show_available_scenarios(self) -> List[str]:
        """Show available practice scenarios."""
        
        if RICH_AVAILABLE and self.console:
            scenarios_panel = Panel(
                "[bold bright_white]🎯 Available Practice Scenarios[/bold bright_white]\\n\\n" +
                "\\n".join([
                    f"[bold green]{key}[/bold green] - {scenario['name']}\\n"
                    f"  {scenario.get('description', 'No description available')}\\n"
                    f"  Files: {len(scenario.get('generated_files', []))} generated, "
                    f"{len(scenario.get('source_files', []))} source\\n"
                    for key, scenario in self.scenarios.items()
                ]),
                border_style="bright_blue",
                padding=(1, 2),
                title="🎓 Practice Scenarios"
            )
            self.console.print(scenarios_panel)
        else:
            print("🎯 Available Practice Scenarios")
            print("=" * 35)
            for key, scenario in self.scenarios.items():
                print(f"• {key} - {scenario['name']}")
                print(f"  {scenario.get('description', 'No description')}")
                print()
        
        return list(self.scenarios.keys())
    
    def cleanup_scenario(self, scenario_paths: Dict[str, str]) -> bool:
        """Clean up a practice scenario."""
        
        try:
            import shutil
            if 'base' in scenario_paths and os.path.exists(scenario_paths['base']):
                shutil.rmtree(scenario_paths['base'])
                self._print("🧹 Practice scenario cleaned up successfully!", "green")
                return True
            return False
        except Exception as e:
            log(f"Error cleaning up scenario: {e}", log_type='ERROR')
            self._print("❌ Failed to clean up practice scenario", "red")
            return False
    
    def _load_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined practice scenarios."""
        
        return {
            "bodyslide_basics": {
                "name": "BodySlide Basics",
                "description": "Simple BodySlide-style scenario with meshes and textures",
                "learning_objectives": "Learn to distinguish between new and modified files",
                "expected_results": "Most meshes will be packed, some textures kept loose",
                "source_files": [
                    {
                        "path": "Skyrim.esm",
                        "content": "# Main game file\\nVersion=1.0\\n"
                    },
                    {
                        "path": "meshes/actors/character/character assets/skeleton.nif",
                        "content": "# Original skeleton mesh\\nOriginal=true\\n"
                    },
                    {
                        "path": "textures/actors/character/female/femalebody_1.dds",
                        "content": "# Original female body texture\\nOriginal=true\\n"
                    },
                    {
                        "path": "meshes/armor/iron/ironarmor.nif",
                        "content": "# Original iron armor mesh\\nOriginal=true\\n"
                    }
                ],
                "generated_files": [
                    {
                        "path": "meshes/actors/character/character assets/skeleton.nif",
                        "content": "# Modified skeleton with custom proportions\\nModified=true\\nBodySlideGenerated=true\\n",
                        "expected_classification": "loose"
                    },
                    {
                        "path": "meshes/armor/custom/customarmor_0.nif",
                        "content": "# New custom armor mesh\\nNew=true\\nBodySlideGenerated=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "meshes/armor/custom/customarmor_1.nif", 
                        "content": "# New custom armor variant\\nNew=true\\nBodySlideGenerated=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/actors/character/female/femalebody_1.dds",
                        "content": "# Modified female body texture\\nModified=true\\nCustomTexture=true\\n",
                        "expected_classification": "loose"
                    },
                    {
                        "path": "textures/armor/custom/customarmor_d.dds",
                        "content": "# New custom armor diffuse texture\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/armor/custom/customarmor_n.dds",
                        "content": "# New custom armor normal texture\\nNew=true\\n", 
                        "expected_classification": "pack"
                    }
                ]
            },
            
            "texture_overhaul": {
                "name": "Texture Overhaul",
                "description": "Texture replacement scenario with mixed new and modified files",
                "learning_objectives": "Understand texture classification and override behavior",
                "expected_results": "New textures packed, modified textures kept loose",
                "source_files": [
                    {
                        "path": "Fallout4.esm",
                        "content": "# Main game file\\nVersion=1.0\\n"
                    },
                    {
                        "path": "textures/landscape/grass01.dds",
                        "content": "# Original grass texture\\nOriginal=true\\n"
                    },
                    {
                        "path": "textures/architecture/building01_d.dds",
                        "content": "# Original building diffuse\\nOriginal=true\\n"
                    },
                    {
                        "path": "textures/clutter/book01.dds",
                        "content": "# Original book texture\\nOriginal=true\\n"
                    }
                ],
                "generated_files": [
                    {
                        "path": "textures/landscape/grass01.dds",
                        "content": "# 4K grass texture replacement\\nModified=true\\nHighRes=true\\n",
                        "expected_classification": "loose"
                    },
                    {
                        "path": "textures/landscape/grass01_n.dds",
                        "content": "# New grass normal map\\nNew=true\\nHighRes=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/architecture/building01_d.dds",
                        "content": "# 4K building diffuse replacement\\nModified=true\\nHighRes=true\\n",
                        "expected_classification": "loose"
                    },
                    {
                        "path": "textures/architecture/building01_s.dds",
                        "content": "# New building specular map\\nNew=true\\nHighRes=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/custom/newdecoration_d.dds",
                        "content": "# Completely new decoration texture\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/custom/newdecoration_n.dds",
                        "content": "# New decoration normal map\\nNew=true\\n",
                        "expected_classification": "pack"
                    }
                ]
            },
            
            "mixed_content": {
                "name": "Mixed Content Pack",
                "description": "Complex scenario with meshes, textures, scripts, and sounds",
                "learning_objectives": "Handle diverse file types and complex classification scenarios",
                "expected_results": "Mixed classification based on file types and modifications",
                "source_files": [
                    {
                        "path": "Skyrim.esm",
                        "content": "# Main game file\\nVersion=1.0\\n"
                    },
                    {
                        "path": "meshes/weapons/sword.nif",
                        "content": "# Original sword mesh\\nOriginal=true\\n"
                    },
                    {
                        "path": "scripts/PlayerScript.pex",
                        "content": "# Original player script\\nOriginal=true\\n"
                    },
                    {
                        "path": "sound/fx/swing.wav",
                        "content": "# Original swing sound\\nOriginal=true\\n"
                    }
                ],
                "generated_files": [
                    {
                        "path": "meshes/weapons/sword.nif",
                        "content": "# Modified sword with better geometry\\nModified=true\\n",
                        "expected_classification": "loose"
                    },
                    {
                        "path": "meshes/weapons/customsword.nif",
                        "content": "# Brand new custom sword\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "textures/weapons/customsword_d.dds",
                        "content": "# New sword texture\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "scripts/CustomScript.pex",
                        "content": "# New custom script\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "sound/fx/customswing.wav",
                        "content": "# New custom swing sound\\nNew=true\\n",
                        "expected_classification": "pack"
                    },
                    {
                        "path": "interface/customui.swf",
                        "content": "# New UI element\\nNew=true\\n",
                        "expected_classification": "pack"
                    }
                ]
            }
        }
    
    # Helper methods
    def _print(self, message: str, style: str = "white"):
        """Print message with appropriate styling."""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            print(message)
