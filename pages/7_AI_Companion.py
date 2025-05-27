"""
AI Companion Page - Interactive coding companion with tips and encouragement
"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ai_companion import AICompanion, render_companion_widget, render_companion_chat, show_companion_stats
from components.sidebar import render_sidebar

def main():
    st.set_page_config(
        page_title="AI Companion - Developer Productivity Suite",
        page_icon="🤖",
        layout="wide"
    )
    
    # Custom CSS for companion page
    st.markdown("""
    <style>
    .companion-header {
        background: linear-gradient(90deg, #2F80ED, #56CCF2);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .companion-card {
        background: #F6F8FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2F80ED;
        margin-bottom: 1rem;
    }
    
    .mood-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: #28A745;
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    
    .tip-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Initialize companion
    if "ai_companion" not in st.session_state:
        st.session_state.ai_companion = AICompanion("CodeBuddy")
    
    companion = st.session_state.ai_companion
    
    # Header
    st.markdown("""
    <div class="companion-header">
        <h1>🤖 Meet Your AI Coding Companion</h1>
        <p>Your friendly guide to better coding, learning, and development!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Welcome section
        st.markdown("### 👋 Welcome to Your Coding Journey!")
        
        welcome_msg = companion.get_welcome_message()
        st.info(welcome_msg)
        
        # Companion avatar and mood
        st.markdown("### 🎭 Meet CodeBuddy")
        avatar_col, mood_col = st.columns([1, 2])
        
        with avatar_col:
            st.code(companion.get_companion_avatar(), language=None)
        
        with mood_col:
            st.markdown(f"""
            <div class="companion-card">
                <h4>Current Mood: <span class="mood-indicator">{companion.current_mood.title()}</span></h4>
                <p>Your companion adapts to help you with different coding activities!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Interactive sections
        tab1, tab2, tab3, tab4 = st.tabs(["💡 Daily Tips", "💬 Chat", "🎯 Challenges", "📊 Stats"])
        
        with tab1:
            st.markdown("### 💡 Coding Wisdom")
            
            # Tip categories
            tip_category = st.selectbox(
                "Choose a topic for tips:",
                ["general", "python", "javascript", "review"],
                format_func=lambda x: {
                    "general": "🌟 General Coding",
                    "python": "🐍 Python",  
                    "javascript": "⚡ JavaScript",
                    "review": "👀 Code Review"
                }[x]
            )
            
            if st.button("🎲 Get Random Tip"):
                tip = companion.get_coding_tip(tip_category)
                st.markdown(f"""
                <div class="tip-box">
                    <h4>{tip['title']} {tip['emoji']}</h4>
                    <p>{tip['tip']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Show encouragement section
            st.markdown("### 💪 Need Some Encouragement?")
            
            situation = st.selectbox(
                "What's your current situation?",
                ["coding", "debugging", "learning", "stuck"],
                format_func=lambda x: {
                    "coding": "💻 Just Coding",
                    "debugging": "🐛 Debugging Issues", 
                    "learning": "📚 Learning New Things",
                    "stuck": "😅 Feeling Stuck"
                }[x]
            )
            
            if st.button("✨ Get Encouragement"):
                encouragement = companion.get_encouragement(situation)
                st.balloons()
                st.success(encouragement)
                
                # Update stats
                if "encouragements_given" not in st.session_state:
                    st.session_state.encouragements_given = 0
                st.session_state.encouragements_given += 1
        
        with tab2:
            render_companion_chat()
        
        with tab3:
            st.markdown("### 🎯 Daily Coding Challenges")
            
            if st.button("🎲 Get New Challenge"):
                challenge = companion.get_daily_challenge()
                
                difficulty_color = {
                    "Easy": "🟢",
                    "Medium": "🟡", 
                    "Hard": "🔴"
                }
                
                st.markdown(f"""
                <div class="companion-card">
                    <h4>{challenge['title']}</h4>
                    <p><strong>Difficulty:</strong> {difficulty_color.get(challenge['difficulty'], '⚪')} {challenge['difficulty']}</p>
                    <p><strong>Challenge:</strong> {challenge['challenge']}</p>
                    <p><strong>💡 Hint:</strong> {challenge['hint']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Challenge completion
            st.markdown("### ✅ Completed a Challenge?")
            if st.button("🎉 Mark Challenge Complete"):
                celebration = companion.get_progress_celebration("code_completed")
                st.balloons()
                st.success(celebration)
                
                # Update stats
                if "coding_sessions" not in st.session_state:
                    st.session_state.coding_sessions = 0
                st.session_state.coding_sessions += 1
        
        with tab4:
            show_companion_stats()
            
            # Progress tracking
            st.markdown("### 📈 Your Coding Journey")
            
            # Simple progress metrics
            total_interactions = (
                st.session_state.get("tips_shared", 0) + 
                st.session_state.get("encouragements_given", 0) + 
                st.session_state.get("coding_sessions", 0)
            )
            
            if total_interactions > 0:
                st.progress(min(total_interactions / 50, 1.0))
                st.caption(f"Journey Progress: {total_interactions}/50 interactions")
            
            # Achievement badges
            st.markdown("### 🏆 Achievements")
            
            achievements = []
            if st.session_state.get("tips_shared", 0) >= 5:
                achievements.append("📚 Tip Collector")
            if st.session_state.get("encouragements_given", 0) >= 3:
                achievements.append("💪 Motivation Seeker") 
            if st.session_state.get("coding_sessions", 0) >= 2:
                achievements.append("🚀 Active Coder")
            
            if achievements:
                for achievement in achievements:
                    st.success(f"🎖️ {achievement}")
            else:
                st.info("Complete more activities to unlock achievements! 🌟")
    
    with col2:
        # Companion widget in sidebar
        render_companion_widget(companion, "general")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🔄 Change Mood", key="change_mood"):
            companion.update_mood("active_coding")
            st.success(f"Mood updated to: {companion.current_mood.title()}!")
            st.rerun()
        
        if st.button("💡 Random Tip", key="random_tip"):
            tip = companion.get_coding_tip()
            st.info(f"**{tip['title']}**\n\n{tip['tip']}")
            
            # Update stats
            if "tips_shared" not in st.session_state:
                st.session_state.tips_shared = 0
            st.session_state.tips_shared += 1
        
        # Companion settings
        st.markdown("### ⚙️ Companion Settings")
        
        new_name = st.text_input("Rename your companion:", value=companion.name)
        if st.button("Update Name") and new_name:
            companion.name = new_name
            st.success(f"Companion renamed to {new_name}! 🎉")
        
        # Show current companion info
        st.markdown(f"""
        **Name:** {companion.name}  
        **Current Mood:** {companion.current_mood.title()}  
        **Personality:** Helpful & Encouraging
        """)

if __name__ == "__main__":
    main()