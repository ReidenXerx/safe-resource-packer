"""
Adaptive welcome system for personalized user experiences.

This module provides context-aware welcome messages and onboarding flows
tailored to the user's experience level and detected system configuration.
"""

from typing import Dict, Optional, Any
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm, Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .first_time_detector import FirstTimeDetector
from .user_profiler import UserProfiler


class AdaptiveWelcome:
    """Provides adaptive welcome experiences based on user profile."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the adaptive welcome system.
        
        Args:
            console: Rich console instance for formatted output
        """
        self.console = console
        self.detector = FirstTimeDetector()
        self.profiler = UserProfiler()
        
    def show_welcome(self, force_onboarding: bool = False) -> Dict[str, Any]:
        """
        Show appropriate welcome message and gather user preferences.
        
        Args:
            force_onboarding: Force full onboarding even for returning users
            
        Returns:
            User preferences and configuration
        """
        welcome_type = self.detector.get_welcome_message_type()
        
        if force_onboarding or welcome_type == 'first_time':
            return self._show_first_time_welcome()
        elif welcome_type == 'returning_beginner':
            return self._show_returning_beginner_welcome()
        else:
            return self._show_experienced_welcome()
    
    def _show_first_time_welcome(self) -> Dict[str, Any]:
        """Show comprehensive first-time user welcome and setup."""
        
        if RICH_AVAILABLE and self.console:
            welcome_panel = Panel(
                "[bold bright_white]🎮 Welcome to Safe Resource Packer![/bold bright_white]\n\n"
                
                "[bold yellow]🎯 What This Tool Does (In Simple Terms):[/bold yellow]\n"
                "• Takes your scattered mod files and organizes them\n"
                "• Makes your game load 3x faster with fewer crashes\n"
                "• Creates professional mod packages ready for sharing\n"
                "• Keeps your important file overrides safe\n\n"
                
                "[bold green]🎓 First Time Here?[/bold green]\n"
                "Perfect! We'll guide you through everything step-by-step.\n"
                "No technical knowledge required - just follow along!\n\n"
                
                "[bold red]⚠️ CRITICAL for BodySlide Users:[/bold red]\n"
                "If you've built BodySlide directly into your game Data folder,\n"
                "those files are now [bold]mixed with other content[/bold] and our tool\n"
                "[bold]cannot separate them[/bold]. We'll teach you how to set up\n"
                "clean BodySlide output for future builds!\n\n"
                
                "[bold blue]🔍 Let's Start by Understanding Your Setup:[/bold blue]\n"
                "We'll quickly detect your games and mod manager to\n"
                "provide personalized guidance just for you.\n\n"
                
                "[dim]💡 This will only take 2-3 minutes and makes everything easier![/dim]",
                border_style="bright_green",
                padding=(1, 2),
                title="🌟 First Time Setup"
            )
            self.console.print(welcome_panel)
            self.console.print()
        else:
            print("🎮 Welcome to Safe Resource Packer!")
            print()
            print("🎯 What This Tool Does:")
            print("• Takes your scattered mod files and organizes them")
            print("• Makes your game load 3x faster with fewer crashes")
            print("• Creates professional mod packages")
            print()
            print("🎓 First time here? We'll guide you through everything!")
            print()
        
        # Offer system detection
        if self._ask_yes_no("Would you like us to detect your games and mod manager automatically?", True):
            return self._run_system_detection_setup()
        else:
            return self._run_manual_setup()
    
    def _show_returning_beginner_welcome(self) -> Dict[str, Any]:
        """Show welcome for returning beginner users."""
        
        profile = self.detector.load_user_profile()
        usage_count = profile.get('usage_count', 0)
        mod_manager = profile.get('mod_manager', 'Unknown')
        
        if RICH_AVAILABLE and self.console:
            welcome_panel = Panel(
                f"[bold bright_white]👋 Welcome Back![/bold bright_white]\n\n"
                
                f"[bold green]🎯 Your Progress:[/bold green]\n"
                f"• You've used the tool {usage_count} time{'s' if usage_count != 1 else ''}\n"
                f"• Your mod manager: {mod_manager}\n"
                f"• Experience level: {profile.get('experience_level', 'Beginner')}\n\n"
                
                "[bold blue]🚀 Ready to Continue?[/bold blue]\n"
                "We'll remember your preferences and make this even easier!\n\n"
                
                "[bold yellow]💡 New Features:[/bold yellow]\n"
                "• Even faster processing\n"
                "• Better error handling\n"
                "• Improved guidance\n\n"
                
                "[dim]Tip: You can always ask for help or tutorials anytime![/dim]",
                border_style="bright_blue",
                padding=(1, 2),
                title="🔄 Welcome Back"
            )
            self.console.print(welcome_panel)
            self.console.print()
        else:
            print(f"👋 Welcome back! (Used {usage_count} times)")
            print(f"Your mod manager: {mod_manager}")
            print()
        
        # Check if they want to update preferences
        if self._ask_yes_no("Would you like to update your preferences or continue with current settings?", False):
            return self._run_preference_update()
        else:
            return profile
    
    def _show_experienced_welcome(self) -> Dict[str, Any]:
        """Show streamlined welcome for experienced users."""
        
        profile = self.detector.load_user_profile()
        
        if RICH_AVAILABLE and self.console:
            welcome_panel = Panel(
                "[bold bright_white]🚀 Safe Resource Packer[/bold bright_white]\n\n"
                
                f"[bold green]Quick Status:[/bold green]\n"
                f"• Mod Manager: {profile.get('mod_manager', 'Unknown')}\n"
                f"• Primary Game: {profile.get('preferred_game', 'Unknown')}\n"
                f"• Total Runs: {profile.get('usage_count', 0)}\n\n"
                
                "[bold blue]Ready to process?[/bold blue] All systems ready!\n\n"
                
                "[dim]💡 Press 'h' anytime for help, 't' for tutorials[/dim]",
                border_style="bright_cyan",
                padding=(1, 2),
                title="⚡ Ready to Go"
            )
            self.console.print(welcome_panel)
        else:
            print("🚀 Safe Resource Packer - Ready to go!")
            print(f"Mod Manager: {profile.get('mod_manager', 'Unknown')}")
            print()
        
        return profile
    
    def _run_system_detection_setup(self) -> Dict[str, Any]:
        """Run automatic system detection and setup."""
        
        if RICH_AVAILABLE and self.console:
            self.console.print("[bold blue]🔍 Detecting your system setup...[/bold blue]")
        else:
            print("🔍 Detecting your system setup...")
        
        # Detect mod managers
        detected_managers = self.profiler.detect_mod_managers()
        detected_games = self.profiler.detect_games()
        
        # Show detection results
        self._show_detection_results(detected_managers, detected_games)
        
        # Get recommendations
        recommendations = self.profiler.get_recommended_setup(detected_managers, detected_games)
        
        # Confirm recommendations with user
        confirmed_prefs = self._confirm_recommendations(recommendations, detected_managers, detected_games)
        
        # Create and save profile
        profile = self.profiler.create_initial_profile()
        profile.update(confirmed_prefs)
        
        self.detector.set_user_preferences(
            experience_level=confirmed_prefs.get('experience_level'),
            mod_manager=confirmed_prefs.get('mod_manager'),
            preferred_game=confirmed_prefs.get('preferred_game')
        )
        
        # Offer tutorial
        if self._should_offer_tutorial(confirmed_prefs):
            profile['wants_tutorial'] = self._ask_yes_no(
                "Would you like a guided tutorial to learn the basics?", True
            )
        
        return profile
    
    def _show_detection_results(self, managers: Dict[str, Optional[str]], 
                               games: Dict[str, Optional[str]]):
        """Show system detection results to user."""
        
        found_managers = {k: v for k, v in managers.items() if v is not None}
        found_games = {k: v for k, v in games.items() if v is not None}
        
        if RICH_AVAILABLE and self.console:
            results_panel = Panel(
                "[bold bright_white]🔍 Detection Results[/bold bright_white]\n\n"
                
                f"[bold green]🎮 Mod Managers Found ({len(found_managers)}):[/bold green]\n" +
                (("\n".join([f"• {name}: {path}" for name, path in found_managers.items()]) + "\n\n") if found_managers else "• None detected\n\n") +
                
                f"[bold blue]🎯 Games Found ({len(found_games)}):[/bold blue]\n" +
                (("\n".join([f"• {name}: {path}" for name, path in found_games.items()]) + "\n\n") if found_games else "• None detected\n\n") +
                
                "[dim]💡 We'll use this information to provide personalized guidance[/dim]",
                border_style="bright_white",
                padding=(1, 2)
            )
            self.console.print(results_panel)
            self.console.print()
        else:
            print("\n🔍 Detection Results:")
            print(f"Mod Managers Found: {len(found_managers)}")
            for name, path in found_managers.items():
                print(f"  • {name}: {path}")
            print(f"Games Found: {len(found_games)}")
            for name, path in found_games.items():
                print(f"  • {name}: {path}")
            print()
    
    def _confirm_recommendations(self, recommendations: Dict[str, str],
                               detected_managers: Dict[str, Optional[str]],
                               detected_games: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Confirm recommendations with user and allow customization."""
        
        confirmed = {}
        
        # Confirm mod manager
        if detected_managers:
            available_managers = [name for name, path in detected_managers.items() if path is not None]
            if available_managers:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[bold green]🎮 Recommended Mod Manager: {recommendations['mod_manager']}[/bold green]")
                else:
                    print(f"🎮 Recommended Mod Manager: {recommendations['mod_manager']}")
                
                if len(available_managers) > 1:
                    if self._ask_yes_no(f"Use {recommendations['mod_manager']} as your mod manager?", True):
                        confirmed['mod_manager'] = recommendations['mod_manager']
                    else:
                        # Let them choose from available options
                        confirmed['mod_manager'] = self._choose_from_list(
                            "Which mod manager would you prefer?", 
                            available_managers + ['Manual']
                        )
                else:
                    confirmed['mod_manager'] = recommendations['mod_manager']
            else:
                confirmed['mod_manager'] = 'Manual'
        else:
            confirmed['mod_manager'] = 'Manual'
        
        # Confirm primary game
        if detected_games:
            available_games = [name for name, path in detected_games.items() if path is not None]
            if available_games:
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[bold blue]🎯 Recommended Primary Game: {recommendations['primary_game']}[/bold blue]")
                else:
                    print(f"🎯 Recommended Primary Game: {recommendations['primary_game']}")
                
                if len(available_games) > 1:
                    if self._ask_yes_no(f"Use {recommendations['primary_game']} as your primary game?", True):
                        confirmed['preferred_game'] = recommendations['primary_game']
                    else:
                        confirmed['preferred_game'] = self._choose_from_list(
                            "Which game do you mod most often?",
                            available_games
                        )
                else:
                    confirmed['preferred_game'] = recommendations['primary_game']
            else:
                confirmed['preferred_game'] = 'Unknown'
        else:
            confirmed['preferred_game'] = 'Unknown'
        
        # Set experience level based on mod manager choice
        if confirmed['mod_manager'] == 'MO2':
            confirmed['experience_level'] = 'intermediate'
        elif confirmed['mod_manager'] in ['Vortex', 'NMM']:
            confirmed['experience_level'] = 'beginner'
        else:
            confirmed['experience_level'] = 'beginner'
        
        return confirmed
    
    def _should_offer_tutorial(self, preferences: Dict[str, Any]) -> bool:
        """Determine if we should offer tutorial based on preferences."""
        return preferences.get('experience_level', 'beginner') == 'beginner'
    
    def _run_manual_setup(self) -> Dict[str, Any]:
        """Run manual setup for users who declined auto-detection."""
        
        if RICH_AVAILABLE and self.console:
            self.console.print("[bold yellow]📋 Manual Setup[/bold yellow]")
            self.console.print("Let's gather some basic information to personalize your experience.\n")
        else:
            print("📋 Manual Setup")
            print("Let's gather some basic information.\n")
        
        # Ask for mod manager preference
        mod_managers = ['MO2', 'Vortex', 'NMM', 'Manual', 'Other']
        mod_manager = self._choose_from_list(
            "Which mod manager do you use?", 
            mod_managers
        )
        
        # Ask for primary game
        games = ['Skyrim Special Edition', 'Skyrim Anniversary Edition', 'Fallout 4', 'Skyrim Legendary Edition', 'Other']
        preferred_game = self._choose_from_list(
            "Which game do you mod most often?",
            games
        )
        
        # Determine experience level
        if mod_manager == 'MO2':
            experience_level = 'intermediate'
        else:
            experience_level = 'beginner'
        
        # Create profile
        profile = {
            'mod_manager': mod_manager,
            'preferred_game': preferred_game,
            'experience_level': experience_level,
            'setup_method': 'manual'
        }
        
        # Save preferences
        self.detector.set_user_preferences(
            experience_level=experience_level,
            mod_manager=mod_manager,
            preferred_game=preferred_game
        )
        
        # Offer tutorial
        if experience_level == 'beginner':
            profile['wants_tutorial'] = self._ask_yes_no(
                "Would you like a guided tutorial to learn the basics?", True
            )
        
        return profile
    
    def _run_preference_update(self) -> Dict[str, Any]:
        """Update existing user preferences."""
        
        profile = self.detector.load_user_profile()
        
        if RICH_AVAILABLE and self.console:
            self.console.print("[bold blue]🔧 Update Preferences[/bold blue]\n")
        else:
            print("🔧 Update Preferences\n")
        
        # Show current preferences and ask for updates
        current_manager = profile.get('mod_manager', 'Unknown')
        if self._ask_yes_no(f"Change mod manager from {current_manager}?", False):
            mod_managers = ['MO2', 'Vortex', 'NMM', 'Manual', 'Other']
            profile['mod_manager'] = self._choose_from_list(
                "Which mod manager do you use?", 
                mod_managers
            )
        
        current_game = profile.get('preferred_game', 'Unknown')
        if self._ask_yes_no(f"Change primary game from {current_game}?", False):
            games = ['Skyrim Special Edition', 'Skyrim Anniversary Edition', 'Fallout 4', 'Skyrim Legendary Edition', 'Other']
            profile['preferred_game'] = self._choose_from_list(
                "Which game do you mod most often?",
                games
            )
        
        # Save updated preferences
        self.detector.save_user_profile(profile)
        
        return profile
    
    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question with appropriate interface."""
        if RICH_AVAILABLE and self.console:
            return Confirm.ask(question, default=default)
        else:
            default_text = "Y/n" if default else "y/N"
            response = input(f"{question} [{default_text}]: ").strip().lower()
            if not response:
                return default
            return response.startswith('y')
    
    def _choose_from_list(self, question: str, options: list) -> str:
        """Choose from a list of options with appropriate interface."""
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
