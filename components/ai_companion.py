"""
AI Code Companion - A playful mascot that provides friendly coding tips
"""
import streamlit as st
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

class AICompanion:
    """Playful AI code companion mascot"""
    
    def __init__(self, name: str = "CodeBuddy"):
        self.name = name
        self.personality_traits = [
            "cheerful", "encouraging", "witty", "supportive", 
            "curious", "helpful", "playful", "wise"
        ]
        self.current_mood = random.choice(["excited", "focused", "creative", "analytical"])
        
    def get_companion_avatar(self) -> str:
        """Get ASCII art avatar for the companion"""
        avatars = {
            "excited": """
    ╭─────╮
    │ ◕ ◕ │  Hi there!
    │  ︶  │  Ready to code?
    ╰─────╯
    """,
            "focused": """
    ╭─────╮
    │ ● ● │  Let's focus
    │  ─  │  and build!
    ╰─────╯
    """,
            "creative": """
    ╭─────╮
    │ ★ ★ │  Time to get
    │  ∪  │  creative!
    ╰─────╯
    """,
            "analytical": """
    ╭─────╮
    │ ◐ ◑ │  Analyzing...
    │  ○  │  Found insights!
    ╰─────╯
    """
        }
        return avatars.get(self.current_mood, avatars["excited"])
    
    def get_welcome_message(self) -> str:
        """Get a personalized welcome message"""
        messages = [
            f"Hello! I'm {self.name}, your friendly coding companion! 🎯",
            f"Hey there, developer! {self.name} here to help you code better! ✨",
            f"Welcome back! {self.name} is excited to assist you today! 🚀",
            f"Ready to write some amazing code? {self.name} is here to guide you! 💫"
        ]
        return random.choice(messages)
    
    def get_coding_tip(self, context: str = "general") -> Dict[str, str]:
        """Get coding tips based on context"""
        tips_database = {
            "general": [
                {
                    "title": "💡 Clean Code Tip",
                    "tip": "Write code like you're telling a story - make it readable for humans, not just computers!",
                    "emoji": "📚"
                },
                {
                    "title": "🎯 Focus Tip", 
                    "tip": "Break big problems into small, manageable pieces. Rome wasn't built in a day!",
                    "emoji": "🧩"
                },
                {
                    "title": "🔍 Debug Tip",
                    "tip": "When debugging, explain your code to a rubber duck (or me!). Speaking out loud helps!",
                    "emoji": "🦆"
                },
                {
                    "title": "⚡ Performance Tip",
                    "tip": "Premature optimization is the root of all evil. Make it work first, then make it fast!",
                    "emoji": "🏃‍♂️"
                }
            ],
            "python": [
                {
                    "title": "🐍 Python Pro Tip",
                    "tip": "Use list comprehensions for cleaner code: [x*2 for x in range(10)] beats a for loop!",
                    "emoji": "✨"
                },
                {
                    "title": "🔧 Python Style",
                    "tip": "Follow PEP 8! Beautiful is better than ugly, simple is better than complex.",
                    "emoji": "🎨"
                }
            ],
            "javascript": [
                {
                    "title": "⚡ JS Wisdom",
                    "tip": "Use const by default, let when you need to reassign, avoid var like yesterday's code!",
                    "emoji": "📝"
                },
                {
                    "title": "🎭 Async Magic",
                    "tip": "Embrace async/await! It makes asynchronous code look synchronous and readable.",
                    "emoji": "🪄"
                }
            ],
            "review": [
                {
                    "title": "👀 Code Review Wisdom",
                    "tip": "Review code like you're reading poetry - look for beauty, clarity, and meaning!",
                    "emoji": "📖"
                },
                {
                    "title": "🤝 Team Player",
                    "tip": "Be kind in code reviews. We're all learning, and constructive feedback builds great teams!",
                    "emoji": "💫"
                }
            ]
        }
        
        context_tips = tips_database.get(context, tips_database["general"])
        return random.choice(context_tips)
    
    def get_encouragement(self, situation: str = "coding") -> str:
        """Get encouraging messages for different situations"""
        encouragements = {
            "coding": [
                "You're doing great! Every line of code is a step forward! 🌟",
                "Keep going! The best developers started exactly where you are now! 💪",
                "Coding is like solving puzzles - and you're getting better at it! 🧩",
                "Remember: every expert was once a beginner. You've got this! 🚀"
            ],
            "debugging": [
                "Bugs are just features in disguise! You'll crack this one! 🐛➡️✨",
                "Every bug you fix makes you a stronger developer! Keep hunting! 🕵️‍♂️",
                "The best debuggers are patient detectives. Follow the clues! 🔍",
                "This bug doesn't stand a chance against your determination! 💥"
            ],
            "learning": [
                "Learning never stops in programming - and that's the exciting part! 📚",
                "Every new concept you master opens doors to amazing possibilities! 🚪✨",
                "Embrace the confusion - it means you're growing! 🌱",
                "You're building an amazing skillset, one concept at a time! 🏗️"
            ],
            "stuck": [
                "Feeling stuck? Take a break, walk around, come back fresh! 🚶‍♂️",
                "Sometimes the best solution comes when you step away from the screen! ☕",
                "Every developer gets stuck. The key is persistence and asking for help! 🤝",
                "This challenge is just your brain getting stronger! 💪🧠"
            ]
        }
        
        situation_encouragements = encouragements.get(situation, encouragements["coding"])
        return random.choice(situation_encouragements)
    
    def get_daily_challenge(self) -> Dict[str, str]:
        """Get a fun daily coding challenge"""
        challenges = [
            {
                "title": "🎯 Code Golf Challenge",
                "challenge": "Write the shortest function to reverse a string without using built-in reverse!",
                "difficulty": "Medium",
                "hint": "Think about string slicing or loops!"
            },
            {
                "title": "🧩 Logic Puzzle",
                "challenge": "Create a function that finds the second largest number in a list!",
                "difficulty": "Easy",
                "hint": "Sort or use max with conditions!"
            },
            {
                "title": "🌟 Creative Coding",
                "challenge": "Build a function that generates ASCII art for any single digit!",
                "difficulty": "Hard",
                "hint": "Use nested loops and pattern matching!"
            },
            {
                "title": "🔄 Refactor Quest",
                "challenge": "Take any old code and make it 50% more readable!",
                "difficulty": "Medium",
                "hint": "Better names, comments, and structure!"
            }
        ]
        return random.choice(challenges)
    
    def get_mood_based_response(self, user_action: str) -> str:
        """Get response based on current mood and user action"""
        responses = {
            "excited": {
                "code_translation": "Wow! Code translation is like being a polyglot programmer! Let's make magic happen! ✨",
                "code_review": "Code review time! I love finding ways to make code even better! 🔍💫",
                "documentation": "Documentation is like writing love letters to future developers! Let's do this! 💝",
                "analysis": "Time to dive deep into the code! I'm excited to see what insights we'll discover! 🕵️‍♂️"
            },
            "focused": {
                "code_translation": "Let's focus and translate this code with precision and care! 🎯",
                "code_review": "Time for a thorough, methodical code review. Every detail matters! 🔬",
                "documentation": "Clear, comprehensive documentation requires focus. Let's create something great! 📚",
                "analysis": "Deep analysis mode activated. Let's examine every aspect systematically! 🧠"
            },
            "creative": {
                "code_translation": "Code translation is an art form! Let's paint with different programming languages! 🎨",
                "code_review": "Let's approach this review with fresh eyes and creative solutions! 💡",
                "documentation": "Time to craft documentation that's both informative and beautiful! ✍️",
                "analysis": "Let's explore this code from unique angles and find creative insights! 🌈"
            },
            "analytical": {
                "code_translation": "Let's analyze the structure and translate it with logical precision! 📊",
                "code_review": "Systematic review time! We'll catch every detail with analytical precision! 📈",
                "documentation": "Let's document this methodically, covering every important aspect! 📋",
                "analysis": "Perfect! Analysis is my specialty. Let's dissect this code thoroughly! 🔬"
            }
        }
        
        mood_responses = responses.get(self.current_mood, responses["excited"])
        return mood_responses.get(user_action, "Let's do something amazing together! 🚀")
    
    def get_progress_celebration(self, achievement: str) -> str:
        """Celebrate user achievements"""
        celebrations = {
            "code_completed": [
                "🎉 Amazing work! You just created something awesome!",
                "🌟 That code looks fantastic! You're on fire!",
                "🚀 Boom! Another successful coding session in the books!",
                "✨ Beautiful code! You should be proud of what you've built!"
            ],
            "bug_fixed": [
                "🐛➡️✅ Bug squashed! You're becoming a debugging ninja!",
                "🎯 Perfect fix! That bug didn't stand a chance!",
                "🔧 Excellent debugging skills! Problem solved elegantly!",
                "💥 Another bug bites the dust! Great problem-solving!"
            ],
            "learning_milestone": [
                "📚🎓 Knowledge level up! You're growing so fast!",
                "🧠💡 New concept mastered! Your skills are expanding!",
                "🌱🌟 Look how much you've learned! Keep growing!",
                "🎯📈 Another milestone reached! You're unstoppable!"
            ]
        }
        
        achievement_celebrations = celebrations.get(achievement, celebrations["code_completed"])
        return random.choice(achievement_celebrations)
    
    def should_show_tip(self) -> bool:
        """Decide if companion should show a tip (random chance)"""
        return random.random() < 0.3  # 30% chance
    
    def update_mood(self, user_activity: str):
        """Update companion mood based on user activity"""
        mood_map = {
            "active_coding": "excited",
            "reviewing_code": "analytical", 
            "creative_work": "creative",
            "focused_work": "focused"
        }
        
        if user_activity in mood_map:
            self.current_mood = mood_map[user_activity]
        else:
            # Random mood change occasionally
            if random.random() < 0.1:  # 10% chance
                self.current_mood = random.choice(["excited", "focused", "creative", "analytical"])

def render_companion_widget(companion: AICompanion, context: str = "general"):
    """Render the companion widget in sidebar or main area"""
    
    with st.container():
        st.markdown("### 🤖 Your AI Companion")
        
        # Show avatar
        st.code(companion.get_companion_avatar(), language=None)
        
        # Show mood and greeting
        st.markdown(f"**Mood:** {companion.current_mood.title()} ✨")
        
        # Show context-appropriate response
        if context in ["code_translation", "code_review", "documentation", "analysis"]:
            response = companion.get_mood_based_response(context)
            st.info(response)
        
        # Show random tip
        if companion.should_show_tip():
            tip = companion.get_coding_tip(context)
            st.success(f"**{tip['title']}** {tip['emoji']}\n\n{tip['tip']}")
        
        # Daily challenge section
        if st.button("🎯 Daily Challenge", key=f"challenge_{context}"):
            challenge = companion.get_daily_challenge()
            st.markdown(f"""
            **{challenge['title']}**
            
            **Challenge:** {challenge['challenge']}
            
            **Difficulty:** {challenge['difficulty']}
            
            **Hint:** {challenge['hint']}
            """)
        
        # Encouragement button
        if st.button("💪 Need Encouragement?", key=f"encourage_{context}"):
            encouragement = companion.get_encouragement("coding")
            st.balloons()
            st.success(encouragement)

def render_companion_chat():
    """Render an interactive chat with the companion"""
    st.markdown("### 💬 Chat with Your Companion")
    
    # Initialize chat history
    if "companion_chat" not in st.session_state:
        st.session_state.companion_chat = []
        companion = AICompanion()
        st.session_state.companion_chat.append({
            "role": "companion",
            "message": companion.get_welcome_message()
        })
    
    # Display chat history
    for chat in st.session_state.companion_chat:
        if chat["role"] == "user":
            st.markdown(f"**You:** {chat['message']}")
        else:
            st.markdown(f"**🤖 CodeBuddy:** {chat['message']}")
    
    # Chat input
    user_input = st.text_input("Ask me anything about coding!", key="companion_chat_input")
    
    if st.button("Send") and user_input:
        # Add user message
        st.session_state.companion_chat.append({
            "role": "user", 
            "message": user_input
        })
        
        # Generate companion response
        companion = AICompanion()
        
        # Simple response logic based on keywords
        if any(word in user_input.lower() for word in ["stuck", "help", "difficult"]):
            response = companion.get_encouragement("stuck")
        elif any(word in user_input.lower() for word in ["bug", "error", "debug"]):
            response = companion.get_encouragement("debugging")
        elif any(word in user_input.lower() for word in ["tip", "advice", "how"]):
            tip = companion.get_coding_tip()
            response = f"{tip['title']} {tip['emoji']}\n\n{tip['tip']}"
        else:
            responses = [
                "That's interesting! Tell me more about what you're working on! 🤔",
                "I love your curiosity! Keep asking great questions! ✨",
                "Every question is a step toward better understanding! 🎯",
                "You're thinking like a true developer! Keep it up! 🚀"
            ]
            response = random.choice(responses)
        
        st.session_state.companion_chat.append({
            "role": "companion",
            "message": response
        })
        
        st.rerun()

def show_companion_stats():
    """Show fun stats about the companion and user interaction"""
    st.markdown("### 📊 Companion Stats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Tips Shared Today", 
            st.session_state.get("tips_shared", 0),
            delta="Keep learning!"
        )
    
    with col2:
        st.metric(
            "Encouragements Given", 
            st.session_state.get("encouragements_given", 0),
            delta="Stay motivated!"
        )
    
    with col3:
        st.metric(
            "Coding Sessions", 
            st.session_state.get("coding_sessions", 0),
            delta="Keep coding!"
        )