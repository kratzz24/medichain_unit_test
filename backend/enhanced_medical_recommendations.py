import json

# Enhanced comprehensive medical recommendations database
MEDICAL_RECOMMENDATIONS = {
    "Flu": {
        "otc_medications": [
            "Acetaminophen (Tylenol) 500mg every 6 hours for fever and aches",
            "Ibuprofen (Advil, Motrin) 400mg every 8 hours for inflammation",
            "Dextromethorphan (Robitussin DM) 15-30mg every 4-6 hours for dry cough",
            "Guaifenesin (Mucinex) 400mg every 12 hours for productive cough",
            "Zinc lozenges within first 24 hours"
        ],
        "prescription_medications": [
            "Oseltamivir (Tamiflu) 75mg twice daily for 5 days if started within 48 hours",
            "Zanamivir (Relenza) inhaled powder for severe cases"
        ],
        "treatments": [
            "Complete bed rest for 7-10 days",
            "Increase fluid intake to 10-12 glasses daily",
            "Warm salt water gargling 3-4 times daily",
            "Humidifier or steam inhalation sessions",
            "Chicken soup for comfort and hydration"
        ],
        "seek_doctor": "if fever >101.5°F for more than 3 days, difficulty breathing, severe dehydration, or symptoms worsen after initial improvement",
        "severity": "Moderate",
        "confidence_boost": 85,
        "typical_duration": "7-10 days"
    },
    "Common Cold": {
        "otc_medications": [
            "Pseudoephedrine (Sudafed) 30-60mg every 4-6 hours for congestion",
            "Loratadine (Claritin) 10mg daily for runny nose",
            "Throat lozenges with menthol every 2 hours as needed",
            "Vitamin C 500-1000mg daily",
            "Saline nasal spray as needed"
        ],
        "prescription_medications": [],
        "treatments": [
            "Adequate rest and sleep (8+ hours)",
            "Warm liquids (tea, broth, warm water with honey)",
            "Saline nasal rinse 2-3 times daily",
            "Honey (1-2 teaspoons) for cough relief",
            "Avoid dairy if mucus production increases"
        ],
        "seek_doctor": "only if symptoms persist beyond 10 days, develop high fever, or experience severe sinus pain",
        "severity": "Mild",
        "confidence_boost": 90,
        "typical_duration": "7-10 days"
    },
    "COVID-19": {
        "otc_medications": [
            "Acetaminophen for fever (preferred over ibuprofen initially)",
            "Throat lozenges for sore throat",
            "Cough suppressants for dry cough",
            "Electrolyte solutions for hydration"
        ],
        "prescription_medications": [
            "Paxlovid (nirmatrelvir-ritonavir) if high-risk and within 5 days",
            "Molnupiravir for eligible patients",
            "Bebtelovimab (monoclonal antibody) if recommended"
        ],
        "treatments": [
            "Strict isolation for 5-10 days",
            "Monitor oxygen levels with pulse oximeter if available",
            "Prone positioning (lying on stomach) if breathing difficulty",
            "Steam inhalation for congestion",
            "Maintain nutrition with easy-to-digest foods"
        ],
        "seek_doctor": "immediately if difficulty breathing, chest pain, confusion, bluish lips/face, or oxygen saturation below 95%",
        "severity": "Moderate to High",
        "confidence_boost": 88,
        "typical_duration": "5-14 days"
    },
    "Pneumonia": {
        "otc_medications": [
            "Acetaminophen 650mg every 6 hours for fever",
            "Expectorant (Guaifenesin) to help clear mucus"
        ],
        "prescription_medications": [
            "Antibiotics: Amoxicillin 500mg 3x daily or Azithromycin Z-pack",
            "Bronchodilators (Albuterol) if wheezing present",
            "Prednisone for severe inflammation if prescribed"
        ],
        "treatments": [
            "Complete bed rest until fever subsides",
            "Increase fluid intake significantly (12+ glasses daily)",
            "Chest physiotherapy and deep breathing exercises",
            "Use of incentive spirometer if provided",
            "Oxygen therapy if oxygen levels are low"
        ],
        "seek_doctor": "immediately required - pneumonia needs medical evaluation and prescription antibiotics. Hospitalization may be necessary",
        "severity": "High",
        "confidence_boost": 92,
        "typical_duration": "1-3 weeks with proper treatment"
    },
    "Migraine": {
        "otc_medications": [
            "Ibuprofen 400-600mg at first sign of headache",
            "Acetaminophen 1000mg every 6 hours",
            "Aspirin 325-650mg with caffeine",
            "Excedrin Migraine (combination formula)",
            "Magnesium supplements 400mg daily for prevention"
        ],
        "prescription_medications": [
            "Sumatriptan (Imitrex) 50-100mg for acute episodes",
            "Rizatriptan (Maxalt) 5-10mg dissolving tablets",
            "Propranolol 40-80mg daily for prevention",
            "Topiramate for frequent migraines"
        ],
        "treatments": [
            "Rest in completely dark, quiet room",
            "Cold compress on forehead and temples",
            "Regular sleep schedule (same bedtime/wake time)",
            "Identify and avoid personal triggers",
            "Relaxation techniques and stress management"
        ],
        "seek_doctor": "if headaches occur >4 times per month, are severe/debilitating, or accompanied by vision changes, weakness, or confusion",
        "severity": "Moderate",
        "confidence_boost": 87,
        "typical_duration": "4-72 hours"
    },
    "Bronchitis": {
        "otc_medications": [
            "Dextromethorphan 15-30mg every 4-6 hours for dry cough",
            "Guaifenesin (Mucinex) 400mg every 12 hours for productive cough",
            "Ibuprofen 400mg every 8 hours for inflammation",
            "Honey 1-2 teaspoons for natural cough suppression",
            "Throat lozenges for throat irritation"
        ],
        "prescription_medications": [
            "Antibiotics only if bacterial infection confirmed (rare)",
            "Bronchodilator inhalers (Albuterol) if wheezing present",
            "Short course of Prednisone for severe inflammation"
        ],
        "treatments": [
            "Complete rest and avoid physical exertion",
            "Humidifier or frequent steam inhalation",
            "Warm liquids throughout the day",
            "Absolutely avoid smoking and secondhand smoke",
            "Breathing exercises to clear airways"
        ],
        "seek_doctor": "if cough persists beyond 3 weeks, coughing up blood, high fever develops, or signs of pneumonia appear",
        "severity": "Moderate",
        "confidence_boost": 89,
        "typical_duration": "1-3 weeks"
    },
    "Asthma": {
        "otc_medications": [
            "Epinephrine auto-injector (EpiPen) for severe attacks - prescription required",
            "Primatene Mist (limited OTC bronchodilator) - use sparingly"
        ],
        "prescription_medications": [
            "Albuterol (ProAir, Ventolin) rescue inhaler 2 puffs every 4-6 hours as needed",
            "Inhaled corticosteroids (Flovent, Pulmicort) for daily control",
            "Long-acting bronchodilators (Salmeterol) for severe asthma",
            "Leukotriene modifiers (Montelukast) for allergy-related asthma"
        ],
        "treatments": [
            "Strict avoidance of known triggers (allergens, smoke, etc.)",
            "Use rescue inhaler exactly as prescribed",
            "Daily peak flow monitoring if recommended",
            "Written asthma action plan from healthcare provider",
            "Regular cleaning to reduce dust mites and allergens"
        ],
        "seek_doctor": "immediately if severe breathing difficulty, inability to speak in full sentences, rescue inhaler not providing relief, or peak flow in red zone",
        "severity": "Moderate to High",
        "confidence_boost": 91,
        "typical_duration": "Chronic condition requiring ongoing management"
    },
    "Tonsillitis": {
        "otc_medications": [
            "Ibuprofen 400mg every 8 hours for pain and inflammation",
            "Acetaminophen 650mg every 6 hours for fever",
            "Throat lozenges with benzocaine for numbing",
            "Throat sprays (Chloraseptic) for pain relief",
            "Warm salt water for gargling"
        ],
        "prescription_medications": [
            "Antibiotics if streptococcal: Amoxicillin 500mg 3x daily for 10 days",
            "Penicillin VK 250mg 4x daily if amoxicillin allergy",
            "Stronger pain medications (Tylenol #3) for severe cases"
        ],
        "treatments": [
            "Warm salt water gargling every 2-3 hours",
            "Cold foods and drinks for comfort (ice cream, popsicles)",
            "Complete voice rest when possible",
            "Humidifier for comfortable breathing",
            "Soft foods that are easy to swallow"
        ],
        "seek_doctor": "if difficulty swallowing liquids, severe pain preventing eating/drinking, or symptoms persist beyond 3-4 days",
        "severity": "Moderate",
        "confidence_boost": 86,
        "typical_duration": "3-7 days with appropriate treatment"
    }
}

def get_enhanced_medical_recommendations(diagnosis):
    """Get comprehensive medical recommendations with confidence boosting"""
    diagnosis_clean = diagnosis.strip()
    
    # Direct match first
    if diagnosis_clean in MEDICAL_RECOMMENDATIONS:
        return MEDICAL_RECOMMENDATIONS[diagnosis_clean]
    
    # Fuzzy matching for similar conditions
    for condition in MEDICAL_RECOMMENDATIONS:
        if condition.lower() in diagnosis_clean.lower() or diagnosis_clean.lower() in condition.lower():
            return MEDICAL_RECOMMENDATIONS[condition]
    
    # Default comprehensive recommendations for unknown conditions
    return {
        "otc_medications": [
            "Acetaminophen 650mg every 6 hours for pain/fever as needed",
            "Ibuprofen 400mg every 8 hours for inflammation",
            "Stay well-hydrated with clear fluids",
            "Electrolyte solutions if dehydrated"
        ],
        "prescription_medications": [
            "Consult healthcare provider for condition-specific medications",
            "May require diagnostic tests for proper treatment"
        ],
        "treatments": [
            "Adequate rest and sleep (8+ hours daily)",
            "Maintain good nutrition with balanced meals",
            "Monitor symptoms and track changes",
            "Follow up with healthcare provider for evaluation"
        ],
        "seek_doctor": "if symptoms worsen, persist beyond expected timeframe, or new concerning symptoms develop",
        "severity": "Requires medical evaluation",
        "confidence_boost": 75,
        "typical_duration": "Varies - depends on underlying condition"
    }

if __name__ == "__main__":
    # Test the function
    test_diagnosis = "Flu"
    recommendations = get_enhanced_medical_recommendations(test_diagnosis)
    print(f"Enhanced recommendations for {test_diagnosis}:")
    print(json.dumps(recommendations, indent=2))
