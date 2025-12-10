"""
Hospital Patient Portal - AI Suggestions Module
================================================
This module provides AI-powered health suggestions for patients.

HOW IT WORKS:
------------
1. Rule-based suggestions:
   - Analyzes patient age, visit frequency, diagnosis patterns
   - Provides generic, educational health tips
   - NOT medical diagnoses - clearly labeled as educational

2. Gemini AI Integration (Optional):
   - Uses Google's Gemini AI for more personalized suggestions
   - Falls back to rule-based if AI is unavailable
   - All suggestions are clearly marked as non-medical

IMPORTANT DISCLAIMER:
--------------------
All suggestions are:
- For educational purposes only
- NOT medical diagnoses or treatment plans
- NOT a substitute for professional medical advice
- Clearly labeled as general information
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random


class HealthSuggestionEngine:
    """
    AI-powered health suggestion engine.
    
    Provides personalized (but non-medical) health tips based on:
    - Patient demographics (age, gender)
    - Visit history and patterns
    - General health categories
    """
    
    # Generic health tips by category
    GENERAL_TIPS = [
        "💧 Remember to stay hydrated - aim for 8 glasses of water daily.",
        "🏃 Regular physical activity helps maintain overall health.",
        "😴 Aim for 7-9 hours of quality sleep each night.",
        "🥗 A balanced diet rich in fruits and vegetables supports your immune system.",
        "🧘 Practice stress management techniques like deep breathing or meditation.",
        "👨‍⚕️ Regular check-ups help catch potential issues early.",
        "💊 Always take medications as prescribed by your doctor.",
        "🚭 Avoid smoking and limit alcohol consumption for better health.",
        "🧴 Don't forget to apply sunscreen when going outdoors.",
        "🤲 Wash your hands frequently to prevent infections."
    ]
    
    AGE_SPECIFIC_TIPS = {
        'child': [  # 0-12
            "🥛 Ensure adequate calcium intake for growing bones.",
            "📱 Limit screen time to promote healthy development.",
            "🎮 Balance indoor activities with outdoor play.",
            "💉 Stay up-to-date with childhood vaccinations."
        ],
        'teen': [  # 13-19
            "🧠 Mental health is just as important as physical health.",
            "📚 Maintain a healthy balance between studies and rest.",
            "🍔 Avoid excessive junk food and sugary drinks.",
            "👥 Talk to a trusted adult if you're feeling overwhelmed."
        ],
        'adult': [  # 20-59
            "⚖️ Maintain a healthy weight through diet and exercise.",
            "🩺 Schedule regular health screenings appropriate for your age.",
            "💼 Take breaks during work to reduce sedentary behavior.",
            "❤️ Monitor your blood pressure and cholesterol levels."
        ],
        'senior': [  # 60+
            "🦴 Consider vitamin D and calcium supplements for bone health.",
            "🧩 Stay mentally active with puzzles, reading, or learning.",
            "👨‍👩‍👧‍👦 Stay socially connected for mental well-being.",
            "⚠️ Be mindful of fall risks at home.",
            "💉 Stay current with flu and other recommended vaccinations."
        ]
    }
    
    VISIT_FREQUENCY_TIPS = {
        'frequent': [
            "📋 Consider keeping a health diary to track symptoms.",
            "❓ Don't hesitate to ask questions during your appointments.",
            "📝 Make a list of concerns before each visit."
        ],
        'moderate': [
            "📅 Regular check-ups help maintain your health.",
            "🔔 Set reminders for any follow-up appointments."
        ],
        'rare': [
            "🏥 Consider scheduling a routine health check-up.",
            "📆 Annual check-ups can help detect issues early.",
            "💉 Make sure your vaccinations are up to date."
        ]
    }
    
    CONDITION_TIPS = {
        'diabetes': [
            "🩸 Monitor your blood sugar levels regularly.",
            "🍭 Watch your carbohydrate intake.",
            "👟 Check your feet daily for any cuts or sores."
        ],
        'hypertension': [
            "🧂 Reduce sodium intake in your diet.",
            "🩺 Monitor your blood pressure at home.",
            "😌 Practice relaxation techniques to manage stress."
        ],
        'respiratory': [
            "🌬️ Avoid smoking and secondhand smoke.",
            "🏠 Keep your living space well-ventilated.",
            "🌡️ Monitor air quality, especially during pollution alerts."
        ],
        'cardiac': [
            "❤️ Know the warning signs of heart problems.",
            "🚶 Regular walking helps heart health.",
            "🥑 Include heart-healthy foods in your diet."
        ]
    }
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the suggestion engine.
        
        Args:
            gemini_api_key: Optional API key for Gemini AI integration
        """
        self.gemini_api_key = gemini_api_key
        self.gemini_client = None
        self._genai_import_attempted = False
    
    def _init_gemini(self):
        """Lazy initialization of Gemini client to avoid import issues."""
        if self._genai_import_attempted:
            return
        
        self._genai_import_attempted = True
        
        if self.gemini_api_key:
            try:
                # Set recursion limit higher temporarily for Pydantic schema generation
                import sys
                old_limit = sys.getrecursionlimit()
                sys.setrecursionlimit(3000)
                
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                
                sys.setrecursionlimit(old_limit)
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
                self.gemini_client = None
    
    def _get_age_group(self, age: int) -> str:
        """Determine age group from age."""
        if age < 13:
            return 'child'
        elif age < 20:
            return 'teen'
        elif age < 60:
            return 'adult'
        else:
            return 'senior'
    
    def _get_visit_frequency(self, visit_count: int, months: int = 12) -> str:
        """
        Categorize visit frequency.
        
        Args:
            visit_count: Number of visits
            months: Time period in months
        """
        visits_per_month = visit_count / months if months > 0 else 0
        
        if visits_per_month > 1:
            return 'frequent'
        elif visits_per_month > 0.25:
            return 'moderate'
        else:
            return 'rare'
    
    def _detect_conditions(self, diagnosis_text: str) -> List[str]:
        """
        Detect health categories from diagnosis text.
        
        This is a simple keyword-based detection.
        In a real system, this would use proper medical NLP.
        """
        conditions = []
        diagnosis_lower = diagnosis_text.lower() if diagnosis_text else ""
        
        if any(word in diagnosis_lower for word in ['diabetes', 'glucose', 'insulin', 'blood sugar']):
            conditions.append('diabetes')
        if any(word in diagnosis_lower for word in ['hypertension', 'blood pressure', 'bp', 'cardiac']):
            conditions.append('hypertension')
        if any(word in diagnosis_lower for word in ['asthma', 'respiratory', 'lung', 'breathing', 'copd']):
            conditions.append('respiratory')
        if any(word in diagnosis_lower for word in ['heart', 'cardiac', 'cardiovascular', 'angina']):
            conditions.append('cardiac')
        
        return conditions
    
    def get_rule_based_suggestions(
        self,
        age: int,
        gender: str,
        visit_count: int,
        diagnosis_text: str = "",
        max_suggestions: int = 5
    ) -> List[Dict]:
        """
        Get rule-based health suggestions.
        
        Args:
            age: Patient's age
            gender: Patient's gender
            visit_count: Number of visits in past year
            diagnosis_text: Combined diagnosis text for pattern detection
            max_suggestions: Maximum number of suggestions to return
        
        Returns:
            List of suggestion dictionaries with text and category
        """
        suggestions = []
        
        # Add age-specific tips
        age_group = self._get_age_group(age)
        age_tips = self.AGE_SPECIFIC_TIPS.get(age_group, [])
        for tip in random.sample(age_tips, min(2, len(age_tips))):
            suggestions.append({
                'text': tip,
                'category': 'Age-Appropriate',
                'icon': '👤'
            })
        
        # Add visit frequency tips
        visit_freq = self._get_visit_frequency(visit_count)
        freq_tips = self.VISIT_FREQUENCY_TIPS.get(visit_freq, [])
        for tip in random.sample(freq_tips, min(1, len(freq_tips))):
            suggestions.append({
                'text': tip,
                'category': 'Health Management',
                'icon': '📊'
            })
        
        # Add condition-specific tips
        conditions = self._detect_conditions(diagnosis_text)
        for condition in conditions[:2]:  # Max 2 conditions
            condition_tips = self.CONDITION_TIPS.get(condition, [])
            if condition_tips:
                tip = random.choice(condition_tips)
                suggestions.append({
                    'text': tip,
                    'category': 'Wellness Tip',
                    'icon': '💡'
                })
        
        # Fill remaining slots with general tips
        remaining = max_suggestions - len(suggestions)
        if remaining > 0:
            general_sample = random.sample(self.GENERAL_TIPS, min(remaining, len(self.GENERAL_TIPS)))
            for tip in general_sample:
                suggestions.append({
                    'text': tip,
                    'category': 'General Health',
                    'icon': '✨'
                })
        
        return suggestions[:max_suggestions]
    
    async def get_ai_suggestions_async(
        self,
        patient_summary: str,
        max_suggestions: int = 3
    ) -> List[Dict]:
        """
        Get AI-powered suggestions using Gemini (async version).
        
        Args:
            patient_summary: Brief summary of patient info (non-sensitive)
            max_suggestions: Maximum suggestions to generate
        
        Returns:
            List of AI-generated suggestions
        """
        self._init_gemini()
        
        if not self.gemini_client:
            return []
        
        try:
            prompt = f"""
            You are a health education assistant. Based on the following general patient information, 
            provide {max_suggestions} general health and wellness tips. 
            
            IMPORTANT: 
            - These are NOT medical diagnoses or treatment recommendations
            - These are general educational wellness tips only
            - Do not provide specific medical advice
            - Keep tips general and applicable to anyone in this demographic
            
            Patient summary: {patient_summary}
            
            Provide {max_suggestions} tips in a friendly, encouraging tone. 
            Each tip should be 1-2 sentences.
            Format: One tip per line, starting with an emoji.
            """
            
            response = await self.gemini_client.aio.models.generate_content_async(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            tips = response.text.strip().split('\n')
            suggestions = []
            
            for tip in tips[:max_suggestions]:
                tip = tip.strip()
                if tip:
                    suggestions.append({
                        'text': tip,
                        'category': 'AI Wellness Tip',
                        'icon': '🤖'
                    })
            
            return suggestions
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return []
    
    def get_ai_suggestions(
        self,
        patient_summary: str,
        max_suggestions: int = 3
    ) -> List[Dict]:
        """
        Get AI-powered suggestions using Gemini (sync version).
        
        Args:
            patient_summary: Brief summary of patient info (non-sensitive)
            max_suggestions: Maximum suggestions to generate
        
        Returns:
            List of AI-generated suggestions
        """
        self._init_gemini()
        
        if not self.gemini_client:
            return []
        
        try:
            prompt = f"""
            You are a health education assistant. Based on the following general patient information, 
            provide {max_suggestions} general health and wellness tips. 
            
            IMPORTANT: 
            - These are NOT medical diagnoses or treatment recommendations
            - These are general educational wellness tips only
            - Do not provide specific medical advice
            - Keep tips general and applicable to anyone in this demographic
            
            Patient summary: {patient_summary}
            
            Provide {max_suggestions} tips in a friendly, encouraging tone. 
            Each tip should be 1-2 sentences.
            Format: One tip per line, starting with an emoji.
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            tips = response.text.strip().split('\n')
            suggestions = []
            
            for tip in tips[:max_suggestions]:
                tip = tip.strip()
                if tip:
                    suggestions.append({
                        'text': tip,
                        'category': 'AI Wellness Tip',
                        'icon': '🤖'
                    })
            
            return suggestions
            
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return []
    
    def get_suggestions(
        self,
        age: int,
        gender: str,
        visit_count: int = 0,
        diagnosis_text: str = "",
        use_ai: bool = True,
        max_suggestions: int = 5
    ) -> Dict:
        """
        Get combined health suggestions.
        
        This method combines rule-based and AI suggestions.
        
        Args:
            age: Patient's age
            gender: Patient's gender
            visit_count: Number of visits
            diagnosis_text: Diagnosis text for pattern detection
            use_ai: Whether to include AI suggestions
            max_suggestions: Maximum total suggestions
        
        Returns:
            Dictionary with suggestions and disclaimer
        """
        suggestions = []
        
        # Get rule-based suggestions
        rule_suggestions = self.get_rule_based_suggestions(
            age=age,
            gender=gender,
            visit_count=visit_count,
            diagnosis_text=diagnosis_text,
            max_suggestions=max_suggestions - 2 if use_ai else max_suggestions
        )
        suggestions.extend(rule_suggestions)
        
        # Get AI suggestions if enabled
        self._init_gemini()
        if use_ai and self.gemini_client:
            patient_summary = f"Age: {age}, Gender: {gender}, Recent visits: {visit_count}"
            ai_suggestions = self.get_ai_suggestions(
                patient_summary=patient_summary,
                max_suggestions=2
            )
            suggestions.extend(ai_suggestions)
        
        return {
            'suggestions': suggestions[:max_suggestions],
            'disclaimer': (
                "⚠️ IMPORTANT DISCLAIMER: These suggestions are for general educational "
                "purposes only and are NOT medical advice, diagnoses, or treatment "
                "recommendations. Always consult with your healthcare provider for "
                "medical concerns. This information should not replace professional "
                "medical consultation."
            ),
            'generated_at': datetime.utcnow().isoformat()
        }


# Global instance
suggestion_engine: Optional[HealthSuggestionEngine] = None


def init_suggestion_engine(api_key: Optional[str] = None) -> HealthSuggestionEngine:
    """Initialize the global suggestion engine."""
    global suggestion_engine
    suggestion_engine = HealthSuggestionEngine(gemini_api_key=api_key)
    return suggestion_engine


def get_suggestion_engine() -> HealthSuggestionEngine:
    """Get the global suggestion engine instance."""
    if suggestion_engine is None:
        return init_suggestion_engine()
    return suggestion_engine
