"""
Data Preparation Guide - Interactive file preparation assistance.

This module provides step-by-step guidance for preparing files for processing,
including game detection, path selection, and validation.
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..dynamic_progress import log


class DataPreparationGuide:
    """Interactive guide for preparing data for processing."""
    
    def __init__(self, console: Optional[Console] = None, mod_manager: str = None):
        """
        Initialize the data preparation guide.
        
        Args:
            console: Rich console for formatted output
            mod_manager: User's preferred mod manager
        """
        self.console = console
        self.mod_manager = mod_manager or "Unknown"
        self.detected_games = {}
        self.detected_managers = {}
        
    def run_preparation_guide(self) -> Dict[str, Any]:
        """
        Run the complete data preparation walkthrough.
        
        Returns:
            Dictionary with prepared paths and configuration
        """
        try:
            self._show_preparation_overview()
            
            # Step 1: Game Detection and Selection
            game_info = self._detect_and_select_game()
            
            # Step 2: Source Folder (Game Data) Selection
            source_path = self._guide_source_folder_selection(game_info)
            
            # Step 3: Generated Files Selection
            generated_path = self._guide_generated_files_selection(game_info)
            
            # Step 4: Output Location Selection
            output_path = self._guide_output_location_selection()
            
            # Step 5: Validation and Summary
            return self._validate_and_summarize(source_path, generated_path, output_path, game_info)
            
        except KeyboardInterrupt:
            self._print("Setup cancelled by user.", "yellow")
            return {}
        except Exception as e:
            self._print(f"Setup failed: {e}", "red")
            return {}
    
    def _show_preparation_overview(self):
        """Show overview of what the preparation process involves."""
        
        if RICH_AVAILABLE and self.console:
            overview_panel = Panel(
                "[bold bright_white]📁 File Preparation Guide[/bold bright_white]\n\n"
                
                "[bold yellow]🎯 What We Need From You:[/bold yellow]\n"
                "We need to know about 3 folders to organize your mod files perfectly:\n\n"
                
                "[bold green]1. 📂 Source Folder (Game Data)[/bold green]\n"
                "   • This is your game's original Data folder\n"
                "   • Contains vanilla game files (Skyrim.esm, textures, etc.)\n"
                "   • We use this to detect what's new vs what's modified\n"
                "   • Example: C:\\Steam\\steamapps\\common\\Skyrim Special Edition\\Data\n\n"
                
                "[bold blue]2. 🔧 Generated Folder (Your Mod Files)[/bold blue]\n"
                "   • BodySlide output, new mod files, etc.\n"
                "   • Files you want to organize and optimize\n"
                "   • Can be BodySlide output, downloaded mods, custom content\n"
                "   • Example: C:\\Users\\You\\Documents\\My Games\\Skyrim\\BodySlide\\Output\n\n"
                
                "[bold magenta]3. 📁 Output Folder (Results Location)[/bold magenta]\n"
                "   • Where we'll create organized mod packages\n"
                "   • We'll create subfolders automatically\n"
                "   • Should have plenty of free space (3x your mod size)\n"
                "   • Example: C:\\ModPackages\\MyOrganizedMods\n\n"
                
                "[bold cyan]🎉 The Result:[/bold cyan]\n"
                "Professional mod packages with BSA/BA2 archives, ESP files,\n"
                "and installation instructions - ready for your mod manager!\n\n"
                
                "[bold yellow]💡 Don't worry - we'll help you find each folder step by step![/bold yellow]",
                border_style="bright_white",
                padding=(1, 2),
                title="🗂️ Preparation Overview"
            )
            self.console.print(overview_panel)
            self.console.print()
        else:
            print("📁 File Preparation Guide")
            print("=" * 40)
            print()
            print("🎯 What We Need From You:")
            print("We need to know about 3 folders:")
            print()
            print("1. 📂 Source Folder - Your game's Data folder")
            print("2. 🔧 Generated Folder - Your mod files to process")
            print("3. 📁 Output Folder - Where to save results")
            print()
            print("💡 We'll help you find each folder step by step!")
            print()
    
    def _detect_and_select_game(self) -> Dict[str, Any]:
        """Detect available games and let user select one."""
        
        self._print("🔍 Detecting your games...", "blue")
        
        # Detect games
        self.detected_games = self._detect_games()
        
        if not self.detected_games:
            self._print("No games auto-detected. We'll help you find them manually.", "yellow")
            return self._manual_game_selection()
        
        # Show detected games
        self._show_detected_games()
        
        # Let user select
        if len(self.detected_games) == 1:
            game_name = list(self.detected_games.keys())[0]
            if self._ask_yes_no(f"Use detected game: {game_name}?", True):
                return self._create_game_info(game_name, self.detected_games[game_name])
        
        # Multiple games or user declined - show selection
        return self._interactive_game_selection()
    
    def _detect_games(self) -> Dict[str, str]:
        """Detect installed games and their paths."""
        
        detected = {}
        
        # Common game installation patterns
        games_to_detect = {
            'Skyrim Special Edition': [
                'Skyrim Special Edition',
                'The Elder Scrolls V Skyrim Special Edition'
            ],
            'Skyrim Anniversary Edition': [
                'Skyrim Anniversary Edition',
                'The Elder Scrolls V Skyrim Anniversary Edition'
            ],
            'Fallout 4': [
                'Fallout 4',
                'Fallout4'
            ],
            'Skyrim Legendary Edition': [
                'Skyrim',
                'The Elder Scrolls V Skyrim'
            ]
        }
        
        # Check Steam paths
        steam_paths = self._get_steam_paths()
        for steam_path in steam_paths:
            common_path = Path(steam_path) / "steamapps" / "common"
            if common_path.exists():
                for game_name, folder_names in games_to_detect.items():
                    for folder_name in folder_names:
                        game_path = common_path / folder_name
                        if game_path.exists() and (game_path / "Data").exists():
                            detected[game_name] = str(game_path)
                            break
        
        # Check other common paths
        other_paths = [
            Path("C:/Games"),
            Path("D:/Games"),
            Path("C:/Program Files (x86)"),
            Path("C:/Program Files")
        ]
        
        for base_path in other_paths:
            if base_path.exists():
                for game_name, folder_names in games_to_detect.items():
                    if game_name not in detected:  # Don't duplicate
                        for folder_name in folder_names:
                            game_path = base_path / folder_name
                            if game_path.exists() and (game_path / "Data").exists():
                                detected[game_name] = str(game_path)
                                break
        
        return detected
    
    def _get_steam_paths(self) -> List[str]:
        """Get possible Steam installation paths."""
        
        paths = []
        
        if platform.system() == "Windows":
            # Common Windows Steam paths
            steam_paths = [
                "C:/Program Files (x86)/Steam",
                "C:/Program Files/Steam",
                Path.home() / "Steam"
            ]
            
            # Check registry for Steam path
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                    install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    steam_paths.insert(0, install_path)
            except (ImportError, FileNotFoundError, OSError):
                pass
            
            paths.extend([str(p) for p in steam_paths if Path(p).exists()])
        
        else:
            # Linux/macOS Steam paths
            linux_paths = [
                Path.home() / ".steam" / "steam",
                Path.home() / ".local" / "share" / "Steam"
            ]
            paths.extend([str(p) for p in linux_paths if p.exists()])
        
        return paths
    
    def _show_detected_games(self):
        """Show detected games to the user."""
        
        if RICH_AVAILABLE and self.console:
            games_table = Table(title="🎮 Detected Games")
            games_table.add_column("Game", style="cyan", no_wrap=True)
            games_table.add_column("Path", style="green")
            games_table.add_column("Status", style="yellow")
            
            for game_name, game_path in self.detected_games.items():
                # Validate the game path
                data_path = Path(game_path) / "Data"
                status = "✅ Ready" if data_path.exists() else "❌ No Data folder"
                games_table.add_row(game_name, game_path, status)
            
            self.console.print(games_table)
            self.console.print()
        else:
            print("🎮 Detected Games:")
            for i, (game_name, game_path) in enumerate(self.detected_games.items(), 1):
                data_path = Path(game_path) / "Data"
                status = "✅ Ready" if data_path.exists() else "❌ No Data folder"
                print(f"  {i}. {game_name}")
                print(f"     Path: {game_path}")
                print(f"     Status: {status}")
            print()
    
    def _interactive_game_selection(self) -> Dict[str, Any]:
        """Let user interactively select a game."""
        
        game_names = list(self.detected_games.keys()) + ["Other (manual selection)"]
        
        self._print("🎯 Which game would you like to work with?", "blue")
        
        if RICH_AVAILABLE and self.console:
            for i, name in enumerate(game_names, 1):
                self.console.print(f"  [bold]{i}.[/bold] {name}")
            self.console.print()
            
            while True:
                try:
                    choice = int(Prompt.ask("Your choice", default="1")) - 1
                    if 0 <= choice < len(game_names):
                        break
                    else:
                        self.console.print("[red]Please enter a valid number[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number[/red]")
        else:
            for i, name in enumerate(game_names, 1):
                print(f"  {i}. {name}")
            print()
            
            while True:
                try:
                    choice = int(input("Your choice [1]: ") or "1") - 1
                    if 0 <= choice < len(game_names):
                        break
                    else:
                        print("Please enter a valid number")
                except ValueError:
                    print("Please enter a number")
        
        if choice == len(game_names) - 1:  # "Other" selected
            return self._manual_game_selection()
        else:
            selected_game = list(self.detected_games.keys())[choice]
            return self._create_game_info(selected_game, self.detected_games[selected_game])
    
    def _manual_game_selection(self) -> Dict[str, Any]:
        """Handle manual game selection when auto-detection fails."""
        
        self._print("📁 Manual Game Selection", "yellow")
        self._print("Let's find your game manually.", "white")
        
        # Ask for game type
        game_types = [
            "Skyrim Special Edition",
            "Skyrim Anniversary Edition", 
            "Fallout 4",
            "Skyrim Legendary Edition",
            "Other"
        ]
        
        game_type = self._choose_from_list("Which game are you modding?", game_types)
        
        # Ask for game path
        self._print(f"\n📂 Now let's find your {game_type} installation folder.", "blue")
        self._print("This should be the folder that contains the game executable and Data folder.", "white")
        
        if game_type != "Other":
            # Show common paths for this game
            common_paths = self._get_common_paths_for_game(game_type)
            self._print(f"\n💡 Common locations for {game_type}:", "cyan")
            for path in common_paths:
                self._print(f"   • {path}", "dim")
        
        game_path = self._browse_for_directory("Select your game's installation folder")
        
        if game_path:
            return self._create_game_info(game_type, game_path)
        else:
            raise ValueError("Game path selection cancelled")
    
    def _create_game_info(self, game_name: str, game_path: str) -> Dict[str, Any]:
        """Create game info dictionary."""
        
        # Determine game type and file extensions
        if "skyrim" in game_name.lower():
            if "special" in game_name.lower() or "anniversary" in game_name.lower():
                game_type = "skyrim"
                main_esm = "Skyrim.esm"
                archive_ext = ".bsa"
            else:
                game_type = "skyrim"
                main_esm = "Skyrim.esm"
                archive_ext = ".bsa"
        elif "fallout 4" in game_name.lower():
            game_type = "fallout4"
            main_esm = "Fallout4.esm"
            archive_ext = ".ba2"
        else:
            game_type = "unknown"
            main_esm = "Unknown.esm"
            archive_ext = ".bsa"
        
        return {
            'name': game_name,
            'path': game_path,
            'data_path': os.path.join(game_path, "Data"),
            'game_type': game_type,
            'main_esm': main_esm,
            'archive_ext': archive_ext,
            'steam_path': self._get_steam_path_for_game(game_name),
            'gog_path': self._get_gog_path_for_game(game_name),
            'epic_path': self._get_epic_path_for_game(game_name)
        }
    
    def _get_common_paths_for_game(self, game_name: str) -> List[str]:
        """Get common installation paths for a specific game."""
        
        paths = []
        
        if "skyrim special edition" in game_name.lower():
            paths = [
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Special Edition",
                "C:\\Program Files\\Steam\\steamapps\\common\\Skyrim Special Edition",
                "C:\\Games\\Skyrim Special Edition",
                "D:\\Games\\Skyrim Special Edition"
            ]
        elif "skyrim anniversary edition" in game_name.lower():
            paths = [
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim Anniversary Edition",
                "C:\\Program Files\\Steam\\steamapps\\common\\Skyrim Anniversary Edition",
                "C:\\Games\\Skyrim Anniversary Edition"
            ]
        elif "fallout 4" in game_name.lower():
            paths = [
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Fallout 4",
                "C:\\Program Files\\Steam\\steamapps\\common\\Fallout 4",
                "C:\\Games\\Fallout 4",
                "D:\\Games\\Fallout 4"
            ]
        elif "skyrim legendary" in game_name.lower():
            paths = [
                "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Skyrim",
                "C:\\Program Files\\Steam\\steamapps\\common\\Skyrim",
                "C:\\Games\\Skyrim"
            ]
        
        return paths
    
    def _get_steam_path_for_game(self, game_name: str) -> str:
        """Get Steam path for a specific game."""
        # This would return the expected Steam path
        return "Steam path for " + game_name
    
    def _get_gog_path_for_game(self, game_name: str) -> str:
        """Get GOG path for a specific game."""
        return "GOG path for " + game_name
    
    def _get_epic_path_for_game(self, game_name: str) -> str:
        """Get Epic path for a specific game."""
        return "Epic path for " + game_name
    
    def _guide_source_folder_selection(self, game_info: Dict[str, Any]) -> str:
        """Guide user through source folder (game Data) selection."""
        
        if RICH_AVAILABLE and self.console:
            source_panel = Panel(
                f"[bold bright_white]📂 Step 2: {game_info['name']} Data Folder[/bold bright_white]\n\n"
                
                "[bold yellow]🎯 What is the Source Folder?[/bold yellow]\n"
                "This is your game's main Data folder with all the original files.\n"
                "We need this to compare against your mod files.\n\n"
                
                f"[bold green]🔍 Expected Location:[/bold green]\n"
                f"Based on your game selection, it should be:\n"
                f"📁 {game_info['data_path']}\n\n"
                
                "[bold blue]💡 Quick Validation:[/bold blue]\n"
                f"Your Data folder should contain:\n"
                f"✅ {game_info['main_esm']} (main game file)\n"
                "✅ Folders like 'meshes', 'textures', 'scripts'\n"
                f"✅ Several {game_info['archive_ext']} archive files\n\n"
                
                "[dim]💡 Tip: You can drag and drop the folder path here![/dim]",
                border_style="bright_green",
                padding=(1, 2),
                title="📂 Source Folder"
            )
            self.console.print(source_panel)
            self.console.print()
        else:
            print(f"📂 Step 2: {game_info['name']} Data Folder")
            print("=" * 50)
            print()
            print("🎯 What is the Source Folder?")
            print("This is your game's main Data folder with all the original files.")
            print()
            print(f"🔍 Expected Location: {game_info['data_path']}")
            print()
        
        # Check if expected path exists
        expected_path = game_info['data_path']
        if os.path.exists(expected_path) and self._validate_game_data_folder(expected_path, game_info):
            if self._ask_yes_no(f"Use detected Data folder: {expected_path}?", True):
                return expected_path
        
        # Manual selection
        self._print("Let's find your Data folder manually.", "blue")
        
        while True:
            self._print("\n🔍 Options:", "cyan")
            self._print("1. 📁 Browse for Data folder", "white")
            self._print("2. ✏️ Enter path manually", "white")
            self._print("3. ❓ I need help finding it", "white")
            
            choice = self._ask_choice("What would you like to do?", ["1", "2", "3"], "1")
            
            if choice == "1":
                path = self._browse_for_directory("Select your game's Data folder")
                if path and self._validate_game_data_folder(path, game_info):
                    return path
                elif path:
                    self._print("❌ This doesn't look like a valid game Data folder.", "red")
                    if not self._ask_yes_no("Try again?", True):
                        break
            
            elif choice == "2":
                path = self._ask_for_path("Enter the path to your game's Data folder")
                if path and self._validate_game_data_folder(path, game_info):
                    return path
                elif path:
                    self._print("❌ This doesn't look like a valid game Data folder.", "red")
                    if not self._ask_yes_no("Try again?", True):
                        break
            
            elif choice == "3":
                self._show_data_folder_help(game_info)
        
        raise ValueError("Source folder selection cancelled or failed")
    
    def _validate_game_data_folder(self, path: str, game_info: Dict[str, Any]) -> bool:
        """Validate that a path is a valid game Data folder."""
        
        if not os.path.exists(path):
            self._print(f"❌ Path does not exist: {path}", "red")
            return False
        
        if not os.path.isdir(path):
            self._print(f"❌ Path is not a directory: {path}", "red")
            return False
        
        # Check for main ESM file
        main_esm_path = os.path.join(path, game_info['main_esm'])
        if not os.path.exists(main_esm_path):
            self._print(f"❌ Main game file not found: {game_info['main_esm']}", "red")
            return False
        
        # Check for common directories
        required_dirs = ['meshes', 'textures']
        missing_dirs = []
        for dir_name in required_dirs:
            if not os.path.exists(os.path.join(path, dir_name)):
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self._print(f"⚠️ Some expected directories missing: {', '.join(missing_dirs)}", "yellow")
            if not self._ask_yes_no("Continue anyway?", True):
                return False
        
        self._print("✅ Valid game Data folder confirmed!", "green")
        return True
    
    def _guide_generated_files_selection(self, game_info: Dict[str, Any]) -> str:
        """Guide user through generated files selection."""
        
        if RICH_AVAILABLE and self.console:
            generated_panel = Panel(
                "[bold bright_white]🔧 Step 3: Your Files to Process[/bold bright_white]\n\n"
                
                "[bold yellow]🎯 What are 'Generated Files'?[/bold yellow]\n"
                "These are the mod files you want to organize and optimize.\n\n"
                
                "[bold green]📋 Common Examples:[/bold green]\n"
                "• BodySlide output (custom body/armor meshes)\n"
                "• Downloaded mod files from Nexus\n"
                "• Custom textures or meshes you created\n"
                "• Mod collections you want to organize\n\n"
                
                "[bold blue]🔍 BodySlide Users:[/bold blue]\n"
                "Your BodySlide output location depends on your setup:\n"
                "• [bold]MO2 Users:[/bold] MO2 overwrite folder (most common)\n"
                "• [bold]Vortex Users:[/bold] Usually in Vortex staging area\n"
                "• [bold]Manual Users:[/bold] Often mixed in game Data folder\n\n"
                
                "[bold red]⚠️ IMPORTANT for Manual Users:[/bold red]\n"
                "If your BodySlide output is mixed with other loose files in your\n"
                "game Data folder, [bold]our tool cannot separate them![/bold]\n\n"
                
                "[bold yellow]🛠️ Solution - Set Up Clean BodySlide Output:[/bold yellow]\n"
                "1. Open BodySlide\n"
                "2. Click 'Settings' (gear icon)\n"
                "3. Set 'Game Data Path' to a clean folder like:\n"
                "   C:\\BodySlideOutput\\[YourProject]\n"
                "4. Build your outfits there instead\n"
                "5. Use that clean folder as your 'Generated' path\n\n"
                
                "[bold green]💡 Why This Matters:[/bold green]\n"
                "• Our tool compares generated files against vanilla game files\n"
                "• Mixed folders make it impossible to know what's yours\n"
                "• Clean output = perfect classification results\n\n"
                
                "[bold magenta]📁 Other Mod Files:[/bold magenta]\n"
                "• Downloaded mod folder (before installing)\n"
                "• Custom mod you're working on\n"
                "• Collection of loose files to organize\n\n"
                
                "[dim]💡 This folder should contain meshes, textures, or other game files![/dim]",
                border_style="bright_blue",
                padding=(1, 2),
                title="🔧 Generated Files"
            )
            self.console.print(generated_panel)
            self.console.print()
        else:
            print("🔧 Step 3: Your Files to Process")
            print("=" * 40)
            print()
            print("🎯 What are 'Generated Files'?")
            print("These are the mod files you want to organize and optimize.")
            print()
            print("📋 Common Examples:")
            print("• BodySlide output")
            print("• Downloaded mod files")
            print("• Custom content")
            print()
        
        while True:
            self._print("🔍 Options:", "cyan")
            self._print("1. 📁 Browse for folder", "white")
            self._print("2. 🎯 Find BodySlide output", "white")
            self._print("3. 🛠️ Set up clean BodySlide output", "white")
            self._print("4. ✏️ Enter path manually", "white")
            self._print("5. 📋 Show me more examples", "white")
            
            choice = self._ask_choice("What would you like to do?", ["1", "2", "3", "4", "5"], "1")
            
            if choice == "1":
                path = self._browse_for_directory("Select folder with files to process")
                if path and self._validate_generated_files_folder(path):
                    return path
                elif path:
                    self._print("⚠️ This folder seems empty or doesn't contain game files.", "yellow")
                    if not self._ask_yes_no("Use it anyway?", False):
                        continue
                    return path
            
            elif choice == "2":
                path = self._find_bodyslide_output(game_info)
                if path:
                    return path
            
            elif choice == "3":
                self._show_bodyslide_setup_guide()
            
            elif choice == "4":
                path = self._ask_for_path("Enter path to folder with files to process")
                if path and self._validate_generated_files_folder(path):
                    return path
                elif path:
                    self._print("⚠️ This folder seems empty or doesn't contain game files.", "yellow")
                    if not self._ask_yes_no("Use it anyway?", False):
                        continue
                    return path
            
            elif choice == "5":
                self._show_generated_files_examples(game_info)
        
        raise ValueError("Generated files selection cancelled")
    
    def _validate_generated_files_folder(self, path: str) -> bool:
        """Validate that a folder contains processable files."""
        
        if not os.path.exists(path):
            self._print(f"❌ Path does not exist: {path}", "red")
            return False
        
        if not os.path.isdir(path):
            self._print(f"❌ Path is not a directory: {path}", "red")
            return False
        
        # Count files in the directory
        file_count = 0
        game_file_count = 0
        game_extensions = {'.nif', '.dds', '.esp', '.esm', '.esl', '.pex', '.wav', '.fuz', '.bsa', '.ba2'}
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_count += 1
                if any(file.lower().endswith(ext) for ext in game_extensions):
                    game_file_count += 1
        
        if file_count == 0:
            self._print("⚠️ This folder appears to be empty.", "yellow")
            return False
        
        if game_file_count == 0:
            self._print(f"⚠️ Found {file_count} files, but none appear to be game files.", "yellow")
            return False
        
        self._print(f"✅ Found {file_count} total files, {game_file_count} appear to be game files.", "green")
        return True
    
    def _find_bodyslide_output(self, game_info: Dict[str, Any]) -> Optional[str]:
        """Try to find BodySlide output automatically."""
        
        self._print("🔍 Searching for BodySlide output...", "blue")
        
        # Common BodySlide paths
        possible_paths = []
        
        # Documents path
        docs_path = Path.home() / "Documents" / "My Games"
        if "skyrim" in game_info['name'].lower():
            if "special edition" in game_info['name'].lower():
                possible_paths.append(docs_path / "Skyrim Special Edition" / "CalienteTools" / "BodySlide" / "ShapeData")
            elif "anniversary edition" in game_info['name'].lower():
                possible_paths.append(docs_path / "Skyrim Anniversary Edition" / "CalienteTools" / "BodySlide" / "ShapeData")
            else:
                possible_paths.append(docs_path / "Skyrim" / "CalienteTools" / "BodySlide" / "ShapeData")
        elif "fallout 4" in game_info['name'].lower():
            possible_paths.append(docs_path / "Fallout4" / "F4SE" / "Plugins" / "BodySlide" / "ShapeData")
        
        # MO2 overwrite folder (if MO2 is being used)
        if self.mod_manager == "MO2":
            # Try to find MO2 installation
            mo2_paths = [
                Path.home() / "AppData" / "Local" / "ModOrganizer",
                Path("C:/Modding/MO2"),
                Path("C:/Games/MO2")
            ]
            
            for mo2_path in mo2_paths:
                if mo2_path.exists():
                    overwrite_path = mo2_path / "overwrite"
                    if overwrite_path.exists():
                        possible_paths.append(overwrite_path)
        
        # Check each path
        found_paths = []
        for path in possible_paths:
            if path.exists() and self._validate_generated_files_folder(str(path)):
                found_paths.append(str(path))
        
        if not found_paths:
            self._print("❌ No BodySlide output found automatically.", "red")
            self._print("💡 Try using 'Browse for folder' option instead.", "cyan")
            return None
        
        if len(found_paths) == 1:
            path = found_paths[0]
            if self._ask_yes_no(f"Found BodySlide output: {path}\nUse this folder?", True):
                return path
        else:
            self._print(f"Found {len(found_paths)} possible BodySlide locations:", "green")
            for i, path in enumerate(found_paths, 1):
                self._print(f"  {i}. {path}", "white")
            
            choice = self._ask_choice("Which one would you like to use?", 
                                    [str(i) for i in range(1, len(found_paths) + 1)], "1")
            return found_paths[int(choice) - 1]
        
        return None
    
    def _guide_output_location_selection(self) -> str:
        """Guide user through output location selection."""
        
        if RICH_AVAILABLE and self.console:
            output_panel = Panel(
                "[bold bright_white]📁 Step 4: Output Location[/bold bright_white]\n\n"
                
                "[bold yellow]🎯 Where to Save Results?[/bold yellow]\n"
                "This is where we'll create your organized mod packages.\n\n"
                
                "[bold green]💾 Space Requirements:[/bold green]\n"
                "• We need about 3x the size of your generated files\n"
                "• This accounts for temporary processing files\n"
                "• Final packages will be much smaller (compressed)\n\n"
                
                "[bold blue]📦 What We'll Create:[/bold blue]\n"
                "• Professional mod packages (BSA/BA2 + ESP)\n"
                "• Compressed loose files (7z archives)\n"
                "• Installation instructions\n"
                "• Ready for your mod manager!\n\n"
                
                "[bold magenta]📋 Recommended Locations:[/bold magenta]\n"
                "• C:\\ModPackages\n"
                "• D:\\MyMods\\Organized\n"
                "• Desktop\\ProcessedMods\n\n"
                
                "[dim]💡 We'll create subfolders automatically - just pick a base location![/dim]",
                border_style="bright_magenta",
                padding=(1, 2),
                title="📁 Output Location"
            )
            self.console.print(output_panel)
            self.console.print()
        else:
            print("📁 Step 4: Output Location")
            print("=" * 30)
            print()
            print("🎯 Where to Save Results?")
            print("This is where we'll create your organized mod packages.")
            print()
            print("💾 We need about 3x the size of your generated files")
            print("📦 We'll create professional mod packages")
            print()
        
        while True:
            self._print("🔍 Options:", "cyan")
            self._print("1. 📁 Browse for output folder", "white")
            self._print("2. ✏️ Enter path manually", "white")
            self._print("3. 🏠 Use Desktop/ModPackages", "white")
            
            choice = self._ask_choice("Where would you like to save results?", ["1", "2", "3"], "1")
            
            if choice == "1":
                path = self._browse_for_directory("Select output folder for organized mod packages")
                if path:
                    return path
            
            elif choice == "2":
                path = self._ask_for_path("Enter path for output folder")
                if path:
                    # Create directory if it doesn't exist
                    try:
                        os.makedirs(path, exist_ok=True)
                        return path
                    except OSError as e:
                        self._print(f"❌ Cannot create directory: {e}", "red")
            
            elif choice == "3":
                desktop_path = str(Path.home() / "Desktop" / "ModPackages")
                if self._ask_yes_no(f"Create output folder at: {desktop_path}?", True):
                    try:
                        os.makedirs(desktop_path, exist_ok=True)
                        return desktop_path
                    except OSError as e:
                        self._print(f"❌ Cannot create directory: {e}", "red")
        
        raise ValueError("Output location selection cancelled")
    
    def _validate_and_summarize(self, source_path: str, generated_path: str, 
                               output_path: str, game_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all paths and show summary."""
        
        # Validate paths exist
        if not os.path.exists(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")
        if not os.path.exists(generated_path):
            raise ValueError(f"Generated path does not exist: {generated_path}")
        
        # Create output path if needed
        os.makedirs(output_path, exist_ok=True)
        
        # Count files
        generated_file_count = sum(len(files) for _, _, files in os.walk(generated_path))
        
        # Calculate approximate space needed
        try:
            import shutil
            generated_size = sum(os.path.getsize(os.path.join(root, file)) 
                               for root, _, files in os.walk(generated_path) 
                               for file in files)
            generated_size_mb = generated_size / (1024 * 1024)
            
            # Check available space
            free_space = shutil.disk_usage(output_path).free
            free_space_mb = free_space / (1024 * 1024)
            space_needed_mb = generated_size_mb * 3
            
        except Exception:
            generated_size_mb = 0
            free_space_mb = 0
            space_needed_mb = 0
        
        # Show summary
        if RICH_AVAILABLE and self.console:
            summary_panel = Panel(
                "[bold bright_white]📋 Setup Summary[/bold bright_white]\n\n"
                
                f"[bold green]🎮 Game:[/bold green] {game_info['name']}\n"
                f"[bold blue]📂 Source:[/bold blue] {source_path}\n"
                f"[bold yellow]🔧 Generated:[/bold yellow] {generated_path}\n"
                f"[bold magenta]📁 Output:[/bold magenta] {output_path}\n\n"
                
                f"[bold cyan]📊 File Analysis:[/bold cyan]\n"
                f"• Files to process: {generated_file_count:,}\n"
                f"• Generated files size: {generated_size_mb:.1f} MB\n"
                f"• Space needed: ~{space_needed_mb:.1f} MB\n"
                f"• Available space: {free_space_mb:.1f} MB\n\n"
                
                f"[bold {'green' if free_space_mb > space_needed_mb else 'red'}]💾 Space Check: "
                f"{'✅ Sufficient' if free_space_mb > space_needed_mb else '❌ Insufficient'}[/bold {'green' if free_space_mb > space_needed_mb else 'red'}]\n\n"
                
                "[bold yellow]🚀 Ready to Process![/bold yellow]\n"
                "All paths validated and space checked.",
                border_style="bright_green",
                padding=(1, 2),
                title="✅ Setup Complete"
            )
            self.console.print(summary_panel)
        else:
            print("📋 Setup Summary")
            print("=" * 20)
            print(f"🎮 Game: {game_info['name']}")
            print(f"📂 Source: {source_path}")
            print(f"🔧 Generated: {generated_path}")
            print(f"📁 Output: {output_path}")
            print()
            print(f"📊 Files to process: {generated_file_count:,}")
            print(f"💾 Space check: {'✅ OK' if free_space_mb > space_needed_mb else '❌ Low space'}")
            print()
        
        # Return configuration
        return {
            'game_info': game_info,
            'source_path': source_path,
            'generated_path': generated_path,
            'output_path': output_path,
            'file_count': generated_file_count,
            'estimated_size_mb': generated_size_mb,
            'space_needed_mb': space_needed_mb,
            'available_space_mb': free_space_mb,
            'space_sufficient': free_space_mb > space_needed_mb
        }
    
    # Helper methods
    def _print(self, message: str, style: str = "white"):
        """Print message with appropriate styling."""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question."""
        if RICH_AVAILABLE and self.console:
            return Confirm.ask(question, default=default)
        else:
            default_text = "Y/n" if default else "y/N"
            response = input(f"{question} [{default_text}]: ").strip().lower()
            if not response:
                return default
            return response.startswith('y')
    
    def _ask_choice(self, question: str, choices: List[str], default: str) -> str:
        """Ask user to choose from a list of options."""
        if RICH_AVAILABLE and self.console:
            return Prompt.ask(question, choices=choices, default=default)
        else:
            response = input(f"{question} [{'/'.join(choices)}] ({default}): ").strip()
            return response if response in choices else default
    
    def _ask_for_path(self, prompt: str) -> Optional[str]:
        """Ask user to enter a file path."""
        if RICH_AVAILABLE and self.console:
            path = Prompt.ask(f"{prompt}\n💡 Tip: You can drag and drop the folder here")
        else:
            path = input(f"{prompt}\n💡 Tip: You can drag and drop the folder here\nPath: ")
        
        # Clean up the path (remove quotes, etc.)
        if path:
            path = path.strip().strip('"').strip("'")
        
        return path if path else None
    
    def _browse_for_directory(self, title: str) -> Optional[str]:
        """Browse for directory using system dialog."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a root window and hide it
            root = tk.Tk()
            root.withdraw()
            
            # Show directory dialog
            directory = filedialog.askdirectory(title=title)
            
            # Clean up
            root.destroy()
            
            return directory if directory else None
            
        except ImportError:
            # Tkinter not available, fall back to manual entry
            self._print("📁 File browser not available. Please enter path manually.", "yellow")
            return self._ask_for_path(title)
    
    def _choose_from_list(self, question: str, options: List[str]) -> str:
        """Choose from a list of options."""
        if RICH_AVAILABLE and self.console:
            self.console.print(f"\n[bold]{question}[/bold]")
            for i, option in enumerate(options, 1):
                self.console.print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = int(Prompt.ask("Your choice", default="1")) - 1
                    if 0 <= choice < len(options):
                        return options[choice]
                    else:
                        self.console.print("[red]Please enter a valid number[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number[/red]")
        else:
            print(f"\n{question}")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            while True:
                try:
                    choice = int(input("Your choice [1]: ") or "1") - 1
                    if 0 <= choice < len(options):
                        return options[choice]
                    else:
                        print("Please enter a valid number")
                except ValueError:
                    print("Please enter a number")
    
    def _show_data_folder_help(self, game_info: Dict[str, Any]):
        """Show help for finding the Data folder."""
        self._print("\n📚 Help: Finding Your Game's Data Folder", "cyan")
        self._print("=" * 50, "cyan")
        
        # Implementation would show detailed help
        pass
    
    def _show_generated_files_examples(self, game_info: Dict[str, Any]):
        """Show examples of generated files."""
        self._print("\n📋 Examples of Files to Process", "cyan")
        self._print("=" * 40, "cyan")
        
        # Implementation would show detailed examples
        pass
    
    def _show_bodyslide_setup_guide(self):
        """Show detailed guide for setting up clean BodySlide output."""
        if RICH_AVAILABLE and self.console:
            setup_guide = Panel(
                "[bold bright_white]🛠️ Setting Up Clean BodySlide Output[/bold bright_white]\n\n"
                
                "[bold red]⚠️ The Problem:[/bold red]\n"
                "If BodySlide outputs to your game Data folder, it gets mixed with:\n"
                "• Other loose files from mods\n"
                "• Vanilla game files you've extracted\n"
                "• Files from other tools\n\n"
                
                "[bold yellow]❌ Why This Breaks Our Tool:[/bold yellow]\n"
                "Our tool works by comparing YOUR files against VANILLA files.\n"
                "When everything is mixed together, we can't tell what's what!\n\n"
                
                "[bold green]✅ The Solution - Clean Output Folder:[/bold green]\n\n"
                
                "[bold cyan]Step 1: Create a Clean Folder[/bold cyan]\n"
                "• Create: C:\\BodySlideOutput\\MyProject\n"
                "• Or: D:\\Modding\\BodySlide\\CurrentBuild\n"
                "• Any clean, empty folder works!\n\n"
                
                "[bold cyan]Step 2: Configure BodySlide[/bold cyan]\n"
                "1. Open BodySlide\n"
                "2. Click the [bold]Settings[/bold] button (gear icon)\n"
                "3. Find '[bold]Game Data Path[/bold]' setting\n"
                "4. Change it to your clean folder\n"
                "5. Click [bold]OK[/bold] to save\n\n"
                
                "[bold cyan]Step 3: Build Your Outfits[/bold cyan]\n"
                "1. Select your presets as normal\n"
                "2. Click [bold]Build[/bold]\n"
                "3. Files now go to your clean folder!\n"
                "4. Use this folder as 'Generated Files' in our tool\n\n"
                
                "[bold magenta]💡 Pro Tips:[/bold magenta]\n"
                "• Create different folders for different projects\n"
                "• Keep vanilla Data folder untouched\n"
                "• This also makes troubleshooting easier\n"
                "• You can always change back later\n\n"
                
                "[bold blue]🎯 Result:[/bold blue]\n"
                "Perfect file classification and optimal mod packages!",
                border_style="bright_yellow",
                padding=(1, 2),
                title="🛠️ BodySlide Setup Guide"
            )
            self.console.print(setup_guide)
            self.console.print()
            
            if Confirm.ask("Would you like to set up a clean folder now?", default=True):
                suggested_path = "C:\\BodySlideOutput\\MyProject"
                custom_path = Prompt.ask("Enter path for clean BodySlide output", default=suggested_path)
                
                try:
                    import os
                    os.makedirs(custom_path, exist_ok=True)
                    self.console.print(f"[bold green]✅ Created folder: {custom_path}[/bold green]")
                    self.console.print("[bold cyan]💡 Now configure BodySlide to use this folder![/bold cyan]")
                    self.console.print("[dim]Remember: Settings → Game Data Path → Set to this folder[/dim]")
                except Exception as e:
                    self.console.print(f"[red]❌ Could not create folder: {e}[/red]")
                    self.console.print("[yellow]💡 You can create it manually and configure BodySlide yourself[/yellow]")
        else:
            print("\n🛠️ Setting Up Clean BodySlide Output")
            print("=" * 40)
            print()
            print("⚠️ The Problem:")
            print("If BodySlide outputs to your game Data folder, it gets mixed")
            print("with other files and our tool can't separate them!")
            print()
            print("✅ The Solution:")
            print("1. Create a clean folder like: C:\\BodySlideOutput\\MyProject")
            print("2. Open BodySlide → Settings (gear icon)")
            print("3. Change 'Game Data Path' to your clean folder")
            print("4. Build outfits there")
            print("5. Use that folder as 'Generated Files' in our tool")
            print()
            print("💡 This gives you perfect file classification!")
            print()
            
            create_folder = input("Create a clean folder now? [Y/n]: ").strip().lower()
            if create_folder == '' or create_folder.startswith('y'):
                suggested_path = "C:\\BodySlideOutput\\MyProject"
                custom_path = input(f"Enter path [{suggested_path}]: ").strip() or suggested_path
                
                try:
                    import os
                    os.makedirs(custom_path, exist_ok=True)
                    print(f"✅ Created folder: {custom_path}")
                    print("💡 Now configure BodySlide to use this folder!")
                    print("Remember: Settings → Game Data Path → Set to this folder")
                except Exception as e:
                    print(f"❌ Could not create folder: {e}")
                    print("💡 You can create it manually and configure BodySlide yourself")
