"""
Comprehension Checks - Knowledge verification and learning assessment.

This module provides interactive quizzes and knowledge checks to ensure users
understand key concepts before proceeding with real mod processing.
"""

from typing import Dict, List, Optional, Any, Tuple

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from ..dynamic_progress import log


class ComprehensionChecker:
    """Interactive knowledge verification system."""
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the comprehension checker.
        
        Args:
            console: Rich console for formatted output
        """
        self.console = console
        self.question_bank = self._load_question_bank()
    
    def run_knowledge_check(self, topic: str = "general") -> Tuple[int, int, bool]:
        """
        Run a knowledge check on a specific topic.
        
        Args:
            topic: Topic to test (general, classification, installation, etc.)
            
        Returns:
            Tuple of (score, total_questions, passed)
        """
        try:
            if topic not in self.question_bank:
                self._print(f"❌ Unknown topic: {topic}", "red")
                return 0, 0, False
            
            questions = self.question_bank[topic]
            
            if RICH_AVAILABLE and self.console:
                self._show_knowledge_check_intro(topic, len(questions))
            else:
                print(f"🧠 Knowledge Check: {topic.title()}")
                print("=" * 30)
                print()
            
            score = 0
            for i, question in enumerate(questions, 1):
                if self._ask_question(question, i, len(questions)):
                    score += 1
            
            passed = score >= len(questions) * 0.7  # 70% pass rate
            
            self._show_results(score, len(questions), passed, topic)
            
            return score, len(questions), passed
            
        except KeyboardInterrupt:
            self._print("Knowledge check cancelled by user.", "yellow")
            return 0, 0, False
        except Exception as e:
            log(f"Error in knowledge check: {e}", log_type='ERROR')
            self._print("❌ Error in knowledge check", "red")
            return 0, 0, False
    
    def _show_knowledge_check_intro(self, topic: str, num_questions: int):
        """Show introduction to knowledge check."""
        
        topic_info = {
            "general": {
                "title": "General Understanding",
                "description": "Basic concepts and workflow understanding"
            },
            "classification": {
                "title": "File Classification",
                "description": "Understanding how files are categorized"
            },
            "installation": {
                "title": "Installation Process",
                "description": "Proper mod installation procedures"
            },
            "troubleshooting": {
                "title": "Problem Solving",
                "description": "Common issues and solutions"
            }
        }
        
        info = topic_info.get(topic, {"title": topic.title(), "description": "Knowledge verification"})
        
        intro_panel = Panel(
            f"[bold bright_white]🧠 Knowledge Check: {info['title']}[/bold bright_white]\\n\\n"
            
            f"[bold yellow]📚 Topic:[/bold yellow] {info['description']}\\n"
            f"[bold blue]❓ Questions:[/bold blue] {num_questions}\\n"
            f"[bold green]✅ Pass Rate:[/bold green] 70% (get {int(num_questions * 0.7)} correct)\\n\\n"
            
            "[bold cyan]💡 Tips:[/bold cyan]\\n"
            "• Read each question carefully\\n"
            "• Think about what you've learned\\n"
            "• Don't rush - understanding matters\\n"
            "• Ask for help if you're confused\\n\\n"
            
            "[dim]Ready to test your knowledge?[/dim]",
            border_style="bright_blue",
            padding=(1, 2),
            title="🧠 Knowledge Check"
        )
        self.console.print(intro_panel)
        self.console.print()
    
    def _ask_question(self, question: Dict[str, Any], question_num: int, total_questions: int) -> bool:
        """Ask a single question and return if answered correctly."""
        
        if RICH_AVAILABLE and self.console:
            self.console.print(f"[bold cyan]Question {question_num}/{total_questions}:[/bold cyan]")
            self.console.print(f"[bold]{question['question']}[/bold]")
            self.console.print()
            
            # Show choices
            for i, choice in enumerate(question['choices'], 1):
                self.console.print(f"  [bold]{i}.[/bold] {choice}")
            
            self.console.print()
            
            # Get answer
            while True:
                try:
                    answer = IntPrompt.ask("Your answer", choices=[str(i) for i in range(1, len(question['choices']) + 1)])
                    break
                except KeyboardInterrupt:
                    raise
                except:
                    self.console.print("[red]Please enter a valid number[/red]")
            
            # Check answer
            correct = (answer - 1) == question['correct']
            
            if correct:
                self.console.print(f"[bold green]✅ Correct![/bold green] {question['explanation']}")
            else:
                correct_answer = question['choices'][question['correct']]
                self.console.print(f"[bold red]❌ Incorrect.[/bold red] The correct answer is: {correct_answer}")
                self.console.print(f"[yellow]💡 Explanation:[/yellow] {question['explanation']}")
            
            self.console.print()
            return correct
            
        else:
            # Plain text version
            print(f"Question {question_num}/{total_questions}: {question['question']}")
            print()
            for i, choice in enumerate(question['choices'], 1):
                print(f"  {i}. {choice}")
            print()
            
            while True:
                try:
                    answer = int(input("Your answer: ")) - 1
                    if 0 <= answer < len(question['choices']):
                        break
                    else:
                        print("Please enter a valid number")
                except (ValueError, KeyboardInterrupt):
                    print("Please enter a valid number")
            
            correct = answer == question['correct']
            
            if correct:
                print(f"✅ Correct! {question['explanation']}")
            else:
                correct_answer = question['choices'][question['correct']]
                print(f"❌ Incorrect. The correct answer is: {correct_answer}")
                print(f"💡 Explanation: {question['explanation']}")
            
            print()
            return correct
    
    def _show_results(self, score: int, total: int, passed: bool, topic: str):
        """Show knowledge check results."""
        
        percentage = (score / total) * 100 if total > 0 else 0
        
        if RICH_AVAILABLE and self.console:
            if passed:
                result_panel = Panel(
                    f"[bold bright_white]🎉 Knowledge Check Complete![/bold bright_white]\\n\\n"
                    
                    f"[bold green]✅ PASSED![/bold green]\\n\\n"
                    
                    f"[bold cyan]📊 Your Score:[/bold cyan] {score}/{total} ({percentage:.1f}%)\\n"
                    f"[bold blue]🎯 Required:[/bold blue] {int(total * 0.7)}/{total} (70%)\\n\\n"
                    
                    f"[bold yellow]🎓 Topic Mastery:[/bold yellow] {topic.title()}\\n\\n"
                    
                    "[bold green]🚀 You're Ready To:[/bold green]\\n"
                    "• Proceed with confidence\\n"
                    "• Apply your knowledge practically\\n"
                    "• Help others learn these concepts\\n"
                    "• Tackle more advanced topics\\n\\n"
                    
                    "[bold magenta]💡 Keep Learning![/bold magenta]\\n"
                    "Understanding is the foundation of successful modding!",
                    border_style="bright_green",
                    padding=(1, 2),
                    title="✅ Success!"
                )
            else:
                result_panel = Panel(
                    f"[bold bright_white]📚 Knowledge Check Complete[/bold bright_white]\\n\\n"
                    
                    f"[bold yellow]📖 NEEDS REVIEW[/bold yellow]\\n\\n"
                    
                    f"[bold cyan]📊 Your Score:[/bold cyan] {score}/{total} ({percentage:.1f}%)\\n"
                    f"[bold blue]🎯 Required:[/bold blue] {int(total * 0.7)}/{total} (70%)\\n\\n"
                    
                    "[bold red]💡 Recommendations:[/bold red]\\n"
                    "• Review the tutorial sections\\n"
                    "• Practice with example scenarios\\n"
                    "• Ask questions if confused\\n"
                    "• Retake the check when ready\\n\\n"
                    
                    "[bold cyan]🎓 Don't Worry![/bold cyan]\\n"
                    "Learning takes time. Review the material and try again!\\n\\n"
                    
                    "[bold green]🔄 You Can:[/bold green]\\n"
                    "• Continue anyway (with guidance)\\n"
                    "• Review specific topics\\n"
                    "• Get additional help",
                    border_style="bright_yellow",
                    padding=(1, 2),
                    title="📖 Review Needed"
                )
            
            self.console.print(result_panel)
        else:
            print(f"🧠 Knowledge Check Results: {topic.title()}")
            print("=" * 30)
            print()
            print(f"📊 Score: {score}/{total} ({percentage:.1f}%)")
            print(f"🎯 Required: {int(total * 0.7)}/{total} (70%)")
            print()
            
            if passed:
                print("✅ PASSED! You're ready to proceed.")
            else:
                print("📖 NEEDS REVIEW - Consider reviewing the material.")
            print()
    
    def show_available_topics(self) -> List[str]:
        """Show available knowledge check topics."""
        
        if RICH_AVAILABLE and self.console:
            topics_table = Table(title="🧠 Available Knowledge Checks")
            topics_table.add_column("Topic", style="cyan")
            topics_table.add_column("Description", style="white")
            topics_table.add_column("Questions", style="green")
            
            for topic, questions in self.question_bank.items():
                description = {
                    "general": "Basic concepts and workflow",
                    "classification": "File categorization rules",
                    "installation": "Mod installation procedures",
                    "troubleshooting": "Problem solving skills"
                }.get(topic, "Knowledge verification")
                
                topics_table.add_row(topic, description, str(len(questions)))
            
            self.console.print(topics_table)
        else:
            print("🧠 Available Knowledge Checks")
            print("=" * 30)
            for topic, questions in self.question_bank.items():
                print(f"• {topic}: {len(questions)} questions")
            print()
        
        return list(self.question_bank.keys())
    
    def create_custom_quiz(self, questions: List[Dict[str, Any]]) -> Tuple[int, int, bool]:
        """Create and run a custom quiz with provided questions."""
        
        if not questions:
            self._print("❌ No questions provided for custom quiz", "red")
            return 0, 0, False
        
        score = 0
        for i, question in enumerate(questions, 1):
            if self._ask_question(question, i, len(questions)):
                score += 1
        
        passed = score >= len(questions) * 0.7
        self._show_results(score, len(questions), passed, "custom")
        
        return score, len(questions), passed
    
    def _load_question_bank(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load predefined question bank."""
        
        return {
            "general": [
                {
                    "question": "What is the main problem that Safe Resource Packer solves?",
                    "choices": [
                        "Mod conflicts between different mods",
                        "Slow loading times caused by loose files",
                        "Incompatible game versions",
                        "Missing textures in mods"
                    ],
                    "correct": 1,
                    "explanation": "Loose files cause the game engine to read thousands of individual files instead of optimized archives, dramatically slowing loading times."
                },
                {
                    "question": "How much faster can loading times become after optimization?",
                    "choices": [
                        "10-20% faster",
                        "50% faster", 
                        "2x faster",
                        "3x faster or more"
                    ],
                    "correct": 3,
                    "explanation": "By packing loose files into BSA/BA2 archives, loading times typically improve by 3x or more, sometimes reducing 4-minute loads to under 1 minute."
                },
                {
                    "question": "What three folders does the tool need to work properly?",
                    "choices": [
                        "Input, Output, Backup",
                        "Source, Generated, Output",
                        "Game, Mods, Results",
                        "Data, Files, Archive"
                    ],
                    "correct": 1,
                    "explanation": "The tool needs Source (base game files), Generated (your mod files), and Output (where results are saved) to compare and classify files properly."
                }
            ],
            
            "classification": [
                {
                    "question": "What happens to NEW files (that don't exist in the base game)?",
                    "choices": [
                        "They are deleted as unnecessary",
                        "They are kept loose for compatibility",
                        "They are packed into BSA/BA2 archives",
                        "They are compressed separately"
                    ],
                    "correct": 2,
                    "explanation": "NEW files are safe to pack into archives because they don't conflict with existing game files, providing maximum performance benefit."
                },
                {
                    "question": "Why must MODIFIED files (different from base game) stay loose?",
                    "choices": [
                        "They are too large for archives",
                        "They need to override the original files",
                        "They cause crashes in archives",
                        "They load faster when loose"
                    ],
                    "correct": 1,
                    "explanation": "Modified files must stay loose so they can override the original files in the base game archives. If packed, the originals would take precedence."
                },
                {
                    "question": "How does the tool determine if a file is new, modified, or identical?",
                    "choices": [
                        "By file size comparison",
                        "By filename matching",
                        "By SHA1 hash comparison",
                        "By modification date"
                    ],
                    "correct": 2,
                    "explanation": "SHA1 hashing provides cryptographic accuracy in detecting file differences, even tiny changes that other methods might miss."
                }
            ],
            
            "installation": [
                {
                    "question": "In MO2, where should loose files be placed relative to the main mod?",
                    "choices": [
                        "Above the main mod (higher priority)",
                        "Below the main mod (lower priority)", 
                        "In the same mod folder",
                        "In a separate profile"
                    ],
                    "correct": 0,
                    "explanation": "Loose files need higher priority (below in MO2's list) to override the packed files when necessary."
                },
                {
                    "question": "What is the role of the ESP file in your optimized mod?",
                    "choices": [
                        "It contains the actual mod content",
                        "It tells the game to load the BSA/BA2 archives",
                        "It manages loose file conflicts",
                        "It provides installation instructions"
                    ],
                    "correct": 1,
                    "explanation": "The ESP file is the 'brain' that tells the game engine to load your BSA/BA2 archives. Without it, the archives won't be loaded."
                },
                {
                    "question": "After installing an optimized mod, what should you do with the load order?",
                    "choices": [
                        "Nothing, it's automatic",
                        "Move it to the top of the list",
                        "Run LOOT to sort properly",
                        "Disable other similar mods"
                    ],
                    "correct": 2,
                    "explanation": "LOOT ensures your ESP is positioned correctly relative to its dependencies and other mods for optimal compatibility."
                }
            ],
            
            "troubleshooting": [
                {
                    "question": "If you get a 'Permission denied' error, what should you try first?",
                    "choices": [
                        "Restart your computer",
                        "Run the tool as Administrator",
                        "Change the output folder",
                        "Reinstall the tool"
                    ],
                    "correct": 1,
                    "explanation": "Permission errors are often resolved by running as Administrator, which gives the tool necessary file system access."
                },
                {
                    "question": "How much free disk space should you have for processing?",
                    "choices": [
                        "Same size as your mod folder",
                        "2x your mod folder size",
                        "3x your mod folder size",
                        "10x your mod folder size"
                    ],
                    "correct": 2,
                    "explanation": "Processing creates temporary files and compressed archives, requiring about 3x the original mod size, though final results are smaller."
                },
                {
                    "question": "If your game won't start after installing an optimized mod, what should you check first?",
                    "choices": [
                        "Disk space availability",
                        "ESP file is enabled",
                        "Archive file sizes",
                        "Load order position"
                    ],
                    "correct": 1,
                    "explanation": "If the ESP isn't enabled, the game won't load the BSA/BA2 archives, potentially causing missing content or crashes."
                }
            ]
        }
    
    # Helper methods
    def _print(self, message: str, style: str = "white"):
        """Print message with appropriate styling."""
        if RICH_AVAILABLE and self.console:
            self.console.print(message, style=style)
        else:
            print(message)
