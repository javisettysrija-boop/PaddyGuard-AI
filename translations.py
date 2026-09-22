TRANSLATIONS = {

    "en": {
        "disease_detection": "Disease Detection",
        "history": "History",
        "weather": "Weather",
        "alerts": "Crop Alerts",
        "treatment": "What Should I Do?",
        "symptoms": "Symptoms",
        "cause": "Cause",
        "management": "Management",
        "prevention": "Prevention",
        "farmer_advice": "Farmer Advice",
        "confidence": "Confidence",
        "important": "Important",
        "low_confidence": "The prediction confidence is low. Please upload a clear image of the affected leaf and compare the symptoms before taking action.",
        "ai_prediction": "This is the AI's most likely prediction. Check the symptoms and management information.",
        "no_weather_alert": "No major weather-based crop alert at this time."
    },

    "te": {
        "disease_detection": "వ్యాధి గుర్తింపు",
        "history": "చరిత్ర",
        "weather": "వాతావరణం",
        "alerts": "పంట హెచ్చరికలు",
        "treatment": "నేను ఏమి చేయాలి?",
        "symptoms": "లక్షణాలు",
        "cause": "కారణం",
        "management": "నిర్వహణ",
        "prevention": "నివారణ",
        "farmer_advice": "రైతులకు సూచనలు",
        "confidence": "నమ్మక స్థాయి",
        "important": "ముఖ్యమైన సమాచారం",
        "low_confidence": "గుర్తింపు నమ్మక స్థాయి తక్కువగా ఉంది. ప్రభావిత ఆకును స్పష్టంగా కనిపించేలా మళ్లీ అప్‌లోడ్ చేసి, చర్య తీసుకునే ముందు లక్షణాలను పరిశీలించండి.",
        "ai_prediction": "ఇది AI గుర్తించిన అత్యంత సంభావ్య వ్యాధి. లక్షణాలు మరియు నిర్వహణ సమాచారాన్ని పరిశీలించండి.",
        "no_weather_alert": "ప్రస్తుతం ముఖ్యమైన వాతావరణ ఆధారిత పంట హెచ్చరిక లేదు."
    },

    "hi": {
        "disease_detection": "रोग पहचान",
        "history": "इतिहास",
        "weather": "मौसम",
        "alerts": "फसल चेतावनी",
        "treatment": "मुझे क्या करना चाहिए?",
        "symptoms": "लक्षण",
        "cause": "कारण",
        "management": "प्रबंधन",
        "prevention": "रोकथाम",
        "farmer_advice": "किसानों के लिए सलाह",
        "confidence": "विश्वास स्तर",
        "important": "महत्वपूर्ण जानकारी",
        "low_confidence": "भविष्यवाणी का विश्वास स्तर कम है। प्रभावित पत्ते की एक स्पष्ट तस्वीर अपलोड करें और कार्रवाई करने से पहले लक्षणों की जांच करें।",
        "ai_prediction": "यह AI की सबसे संभावित भविष्यवाणी है। लक्षणों और प्रबंधन की जानकारी देखें।",
        "no_weather_alert": "इस समय मौसम आधारित कोई प्रमुख फसल चेतावनी नहीं है।"
    },

    "kn": {
        "disease_detection": "ರೋಗ ಪತ್ತೆ",
        "history": "ಇತಿಹಾಸ",
        "weather": "ಹವಾಮಾನ",
        "alerts": "ಬೆಳೆ ಎಚ್ಚರಿಕೆಗಳು",
        "treatment": "ನಾನು ಏನು ಮಾಡಬೇಕು?",
        "symptoms": "ಲಕ್ಷಣಗಳು",
        "cause": "ಕಾರಣ",
        "management": "ನಿರ್ವಹಣೆ",
        "prevention": "ತಡೆಗಟ್ಟುವಿಕೆ",
        "farmer_advice": "ರೈತರಿಗೆ ಸಲಹೆ",
        "confidence": "ವಿಶ್ವಾಸ ಮಟ್ಟ",
        "important": "ಪ್ರಮುಖ ಮಾಹಿತಿ",
        "low_confidence": "ಭವಿಷ್ಯವಾಣಿಯ ವಿಶ್ವಾಸ ಮಟ್ಟ ಕಡಿಮೆಯಾಗಿದೆ. ಬಾಧಿತ ಎಲೆಯ ಸ್ಪಷ್ಟ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಮತ್ತು ಕ್ರಮ ಕೈಗೊಳ್ಳುವ ಮೊದಲು ಲಕ್ಷಣಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "ai_prediction": "ಇದು AI ನೀಡಿದ ಅತ್ಯಂತ ಸಂಭವನೀಯ ಭವಿಷ್ಯವಾಣಿ. ಲಕ್ಷಣಗಳು ಮತ್ತು ನಿರ್ವಹಣಾ ಮಾಹಿತಿಯನ್ನು ಪರಿಶೀಲಿಸಿ.",
        "no_weather_alert": "ಪ್ರಸ್ತುತ ಯಾವುದೇ ಪ್ರಮುಖ ಹವಾಮಾನ ಆಧಾರಿತ ಬೆಳೆ ಎಚ್ಚರಿಕೆ ಇಲ್ಲ."
    }
}


def get_translation(language, key):
    """
    Get translated text for the selected language.
    Falls back to English if language or key is not available.
    """

    if language not in TRANSLATIONS:
        language = "en"

    return TRANSLATIONS[language].get(
        key,
        TRANSLATIONS["en"].get(key, key)
    )