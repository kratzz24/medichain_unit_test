"""
Enhanced conversational medical response generator
Provides empathetic, natural language medical guidance similar to talking with a knowledgeable friend
"""

import random

class ConversationalMedicalGuide:
    def __init__(self):
        self.disclaimer_variations = [
            "I'm not a doctor, but I can share some helpful guidance.",
            "While I'm not a medical professional, I can offer some general guidance.",
            "I'm not a doctor, but I can help you understand your symptoms better.",
            "Though I'm not a healthcare provider, I can share some useful insights."
        ]
        
        self.empathy_starters = [
            "Thanks for trusting me with this.",
            "I understand you're concerned about these symptoms.",
            "I can see why these symptoms would be worrying.",
            "Let me help you make sense of what you're experiencing."
        ]
        
        self.condition_intro_phrases = [
            "Your symptoms — {symptoms} — are often linked to conditions like:",
            "Based on what you're describing — {symptoms} — this could be:",
            "These symptoms — {symptoms} — commonly point to:",
            "When someone has {symptoms}, it's typically related to:"
        ]
        
        self.medication_intros = [
            "Since I'm not a doctor, I can only suggest **general over-the-counter (OTC) options** that people commonly use for these symptoms — but it's still best to confirm with a healthcare professional, especially if symptoms worsen.",
            "Here are some **over-the-counter options** that people often find helpful for these symptoms, though you should always check with a healthcare provider:",
            "While I can't prescribe medications, I can share **common OTC remedies** that people use for similar symptoms:",
            "For general guidance on **over-the-counter options** (remembering this isn't medical advice):"
        ]

    def generate_conversational_response(self, diagnosis, confidence, symptoms_text, medical_recommendations, alternative_diagnoses=None):
        """Generate a conversational, empathetic medical response"""
        
        # Start with disclaimer and empathy
        response = f"{random.choice(self.disclaimer_variations)}\n\n"
        
        # Add symptom analysis
        symptom_intro = random.choice(self.condition_intro_phrases).format(symptoms=symptoms_text.lower())
        response += f"{symptom_intro}\n\n"
        
        # Main diagnosis with confidence-based language
        if confidence >= 80:
            confidence_phrase = "most likely"
        elif confidence >= 70:
            confidence_phrase = "quite possibly"
        elif confidence >= 60:
            confidence_phrase = "could be"
        else:
            confidence_phrase = "might be"
        
        response += f"**{diagnosis}** ({confidence_phrase}, based on your symptoms)\n\n"
        
        # Add alternative conditions if available
        if alternative_diagnoses and len(alternative_diagnoses) > 1:
            response += "Other possibilities include:\n\n"
            for alt_diag in alternative_diagnoses[1:4]:  # Show up to 3 alternatives
                alt_name = alt_diag.get('diagnosis', 'Unknown')
                alt_conf = alt_diag.get('confidence', 0)
                if alt_conf >= 0.5:  # Only show if reasonably confident
                    response += f"• **{alt_name}** (also possible)\n\n"
        
        # Add severity warning if needed
        severity = medical_recommendations.get('severity', 'Moderate')
        if severity in ['High', 'Critical', 'Severe'] or 'severe' in diagnosis.lower():
            response += "⚠️ **However, some of your symptoms can also signal something more serious**, so it's important to monitor them carefully.\n\n"
        
        # Immediate care section
        response += "✅ **What you can do now:**\n\n"
        
        # Add treatments/home care
        treatments = medical_recommendations.get('treatments', [])
        if treatments:
            for treatment in treatments[:3]:  # Show top 3 treatments
                response += f"• {treatment}\n\n"
        
        # OTC medications section
        otc_meds = medical_recommendations.get('otc_medications', [])
        if otc_meds:
            response += f"**For symptom relief:**\n\n"
            for med in otc_meds[:4]:  # Show top 4 medications
                response += f"• **{med}** (available without prescription)\n\n"
        
        # Prescription medications if needed
        prescription_meds = medical_recommendations.get('prescription_medications', [])
        if prescription_meds:
            response += "**🩺 Prescription medications** (require doctor visit):\n\n"
            for med in prescription_meds[:3]:
                response += f"• **{med}** (prescription required)\n\n"
        
        # When to see a doctor
        seek_doctor = medical_recommendations.get('seek_doctor', '')
        if seek_doctor:
            response += f"👨‍⚕️ **See a doctor immediately** {seek_doctor}\n\n"
        
        # Safety reminders
        response += "⚠️ **Important safety notes:**\n\n"
        response += "• Don't combine multiple medications without medical advice\n\n"
        response += "• If symptoms worsen or feel unusual, seek medical attention right away\n\n"
        response += "• This guidance is for general information only - not a substitute for professional medical advice\n\n"
        
        # Duration expectation
        duration = medical_recommendations.get('typical_duration', 'Varies')
        if duration != 'Varies':
            response += f"🕐 **Typical recovery time:** {duration}\n\n"
        
        # Engaging follow-up question
        follow_up_questions = [
            "Do you have any other symptoms like fever, chills, or difficulty breathing? That would help narrow it down further.",
            "Are there any other symptoms you're experiencing that might help me give you better guidance?",
            "How long have you been experiencing these symptoms? That can help determine the best approach.",
            "Would you like me to also suggest a home care routine (hydration, rest, diet) to go along with these recommendations?"
        ]
        
        response += f"👉 {random.choice(follow_up_questions)}"
        
        return response

    def generate_medication_focused_response(self, diagnosis, symptoms_text, medical_recommendations):
        """Generate a medication-focused conversational response"""
        
        response = f"{random.choice(self.empathy_starters)} {random.choice(self.medication_intros)}\n\n"
        
        response += f"For your symptoms (**{symptoms_text.lower()}**):\n\n"
        
        # Group medications by symptom type
        otc_meds = medical_recommendations.get('otc_medications', [])
        
        # Pain and fever
        pain_meds = [med for med in otc_meds if any(word in med.lower() for word in ['acetaminophen', 'ibuprofen', 'tylenol', 'advil', 'pain', 'fever'])]
        if pain_meds:
            response += "**For headache & body aches:**\n\n"
            for med in pain_meds[:2]:
                response += f"• *{med}*\n\n"
        
        # Respiratory symptoms
        respiratory_meds = [med for med in otc_meds if any(word in med.lower() for word in ['cough', 'decongestant', 'throat', 'mucus', 'chest'])]
        if respiratory_meds:
            response += "**For respiratory symptoms:**\n\n"
            for med in respiratory_meds[:2]:
                response += f"• *{med}*\n\n"
        
        # Nasal symptoms
        nasal_meds = [med for med in otc_meds if any(word in med.lower() for word in ['nasal', 'runny', 'congestion', 'antihistamine', 'allergy'])]
        if nasal_meds:
            response += "**For runny nose & congestion:**\n\n"
            for med in nasal_meds[:2]:
                response += f"• *{med}*\n\n"
        
        # Other symptoms
        other_meds = [med for med in otc_meds if not any(word in med.lower() for word in ['acetaminophen', 'ibuprofen', 'cough', 'nasal', 'runny', 'congestion'])]
        if other_meds:
            response += "**Additional relief:**\n\n"
            for med in other_meds[:2]:
                response += f"• *{med}*\n\n"
        
        # Prescription note
        prescription_meds = medical_recommendations.get('prescription_medications', [])
        if prescription_meds:
            response += "**🩺 Stronger medications** (require doctor prescription):\n\n"
            for med in prescription_meds[:2]:
                response += f"• *{med}* (prescription required)\n\n"
        
        # Safety warnings
        response += "⚠️ **Important notes:**\n\n"
        response += "• Don't combine too many medicines at once without medical advice\n\n"
        response += "• Avoid Ibuprofen if you have stomach ulcers or kidney problems\n\n"
        
        seek_doctor = medical_recommendations.get('seek_doctor', '')
        if seek_doctor:
            response += f"• {seek_doctor.capitalize()}\n\n"
        
        response += "👉 Would you like me to also suggest a **home care routine** (hydration, rest, diet) to go along with the medicines? That way you'll have a complete care plan, not just medications."
        
        return response

# Global instance
conversational_guide = ConversationalMedicalGuide()
