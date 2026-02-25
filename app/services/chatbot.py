"""
AI Farming Chatbot - Multilingual keyword-based assistant
"""

from typing import List, Dict, Optional

RESPONSES: Dict[str, Dict] = {
    "en": {
        "disease": {
            "prevent": "To prevent diseases: Use disease-free seeds, practice crop rotation, maintain proper spacing, water at the base, and remove infected plants immediately.",
            "treat": "For disease treatment: Apply appropriate fungicides, remove infected leaves, improve air circulation, and ensure proper nutrition.",
            "default": "I can help identify crop diseases. Upload a leaf image in the Predict section. Common diseases include bacterial spot, early blight, and late blight.",
        },
        "fertilizer": "For {crop}, use {fert}. Apply every 2–3 weeks during the growing season and water thoroughly after application.",
        "watering": {
            "tomato": "For tomatoes: Deep watering 2–3 times per week. Water at the base to keep leaves dry.",
            "potato": "For potatoes: Keep soil consistently moist but not waterlogged. Water once a week deeply.",
            "default": "General rule: Water early morning or evening, 1–2 inches per week. Check soil moisture before watering.",
        },
        "pest": "For pest control: Start with neem oil or insecticidal soap for mild infestations. For severe cases, use approved pesticides and always follow label instructions.",
        "harvest": "Harvest crops at the right time: Tomatoes when fully red, potatoes when leaves yellow, corn when kernels are milky. Store in a cool, dry place.",
        "soil": "Improve soil health by adding compost, practicing crop rotation, and testing pH levels annually. Most crops prefer pH 6.0–7.0.",
        "default": "I can help with crop diseases 🌿, watering 💧, fertilizers, pests 🐛, harvest tips, and soil health. What would you like to know?",
        "suggestions": ["How to prevent crop diseases?", "Best fertilizer for tomatoes?", "How often to water crops?", "Natural pest control tips?"],
    },
    "hi": {
        "disease": {
            "prevent": "रोग रोकने के लिए: रोगमुक्त बीज उपयोग करें, फसल चक्र अपनाएं, उचित दूरी बनाए रखें, जड़ में पानी दें, और संक्रमित पौधों को तुरंत हटाएं।",
            "treat": "रोग उपचार के लिए: उचित फफूंदनाशक लगाएं, संक्रमित पत्तियां हटाएं, हवा का प्रवाह सुधारें और उचित पोषण सुनिश्चित करें।",
            "default": "मैं फसल रोगों की पहचान में मदद कर सकता हूँ। Predict सेक्शन में पत्ती की फोटो अपलोड करें। सामान्य रोग: जीवाणु धब्बा, अगेती झुलसा, पछेती झुलसा।",
        },
        "fertilizer": "{crop} के लिए {fert} उर्वरक उपयोग करें। बढ़वार के मौसम में हर 2-3 सप्ताह में लगाएं।",
        "watering": {
            "tomato": "टमाटर: सप्ताह में 2-3 बार गहरा पानी दें। पत्तियों को सूखा रखने के लिए जड़ में पानी दें।",
            "potato": "आलू: मिट्टी को लगातार नम रखें लेकिन जलभराव न हो। सप्ताह में एक बार गहरा पानी दें।",
            "default": "सामान्य नियम: सुबह या शाम पानी दें, सप्ताह में 1-2 इंच। पानी देने से पहले मिट्टी की नमी जांचें।",
        },
        "pest": "कीट नियंत्रण: हल्के प्रकोप के लिए नीम का तेल या कीटनाशक साबुन उपयोग करें। गंभीर मामलों में अनुमोदित कीटनाशक का उपयोग करें।",
        "harvest": "सही समय पर फसल काटें: टमाटर पूरा लाल होने पर, आलू जब पत्तियां पीली हों, मक्का जब दाने दूधिया हों। ठंडी और सूखी जगह पर संग्रहित करें।",
        "soil": "मिट्टी सुधार: खाद डालें, फसल चक्र अपनाएं, और सालाना pH जांच करें। अधिकांश फसलें pH 6.0–7.0 पसंद करती हैं।",
        "default": "मैं फसल रोग 🌿, सिंचाई 💧, उर्वरक, कीट 🐛, कटाई और मिट्टी स्वास्थ्य में सहायता कर सकता हूँ। आप क्या जानना चाहते हैं?",
        "suggestions": ["फसल रोग कैसे रोकें?", "टमाटर के लिए सबसे अच्छा उर्वरक?", "फसल को कितनी बार पानी दें?", "प्राकृतिक कीट नियंत्रण?"],
    },
    "mr": {
        "disease": {
            "prevent": "रोग टाळण्यासाठी: रोगमुक्त बियाणे वापरा, पीक फेरपालट करा, योग्य अंतर ठेवा, मुळाशी पाणी द्या, संक्रमित झाडे लगेच काढा.",
            "treat": "रोग उपचार: योग्य बुरशीनाशक वापरा, संक्रमित पाने काढा, हवेचा संचार सुधारा.",
            "default": "पीक रोग ओळखण्यासाठी Predict विभागात पानाचा फोटो अपलोड करा. सामान्य रोग: जिवाणू ठिपके, अगेमर करपा.",
        },
        "fertilizer": "{crop} साठी {fert} खत वापरा. वाढीच्या हंगामात दर 2-3 आठवड्यांनी द्या.",
        "watering": {
            "default": "सकाळी किंवा संध्याकाळी पाणी द्या, आठवड्यात 1-2 इंच. पाणी देण्यापूर्वी माती ओलावा तपासा.",
        },
        "pest": "कीड नियंत्रण: सौम्य प्रादुर्भावासाठी कडुलिंब तेल वापरा. गंभीर प्रकरणी मान्यताप्राप्त कीटकनाशक वापरा.",
        "harvest": "योग्य वेळी काढणी करा: टोमॅटो पूर्ण लाल झाल्यावर, बटाटा पाने पिवळी झाल्यावर. थंड व कोरड्या ठिकाणी साठवा.",
        "soil": "माती सुधारणा: कंपोस्ट घाला, पीक फेरपालट करा, वार्षिक pH तपासा. बहुतेक पिके pH 6.0–7.0 पसंत करतात.",
        "default": "मी पीक रोग 🌿, पाणी 💧, खते, कीड 🐛, काढणी आणि माती आरोग्यावर मदत करू शकतो. आज काय जाणून घ्यायचे?",
        "suggestions": ["पीक रोग कसे टाळावे?", "टोमॅटोसाठी खत कोणते?", "किती वेळा पाणी द्यावे?", "नैसर्गिक कीड नियंत्रण?"],
    },
    "pa": {
        "disease": {
            "prevent": "ਬਿਮਾਰੀ ਰੋਕਣ: ਰੋਗਮੁਕਤ ਬੀਜ ਵਰਤੋ, ਫਸਲ ਚੱਕਰ ਅਪਣਾਓ, ਜੜ੍ਹ ਤੇ ਪਾਣੀ ਦਿਓ, ਸੰਕਰਮਿਤ ਪੌਦੇ ਹਟਾਓ।",
            "treat": "ਬਿਮਾਰੀ ਇਲਾਜ: ਉੱਲੀਨਾਸ਼ਕ ਲਗਾਓ, ਸੰਕਰਮਿਤ ਪੱਤੇ ਹਟਾਓ, ਹਵਾ ਦੀ ਆਵਾਜਾਈ ਸੁਧਾਰੋ।",
            "default": "Predict ਭਾਗ ਵਿੱਚ ਪੱਤੇ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ। ਆਮ ਬਿਮਾਰੀਆਂ: ਬੈਕਟੀਰੀਅਲ ਸਪਾਟ, ਅਰਲੀ ਬਲਾਈਟ।",
        },
        "fertilizer": "{crop} ਲਈ {fert} ਖਾਦ ਵਰਤੋ। ਵਧਣ ਦੇ ਮੌਸਮ ਵਿੱਚ ਹਰ 2-3 ਹਫ਼ਤੇ ਪਾਓ।",
        "watering": {"default": "ਸਵੇਰੇ ਜਾਂ ਸ਼ਾਮ ਨੂੰ ਪਾਣੀ ਦਿਓ, ਹਫ਼ਤੇ ਵਿੱਚ 1-2 ਇੰਚ।"},
        "pest": "ਕੀੜੇ ਨਿਯੰਤਰਣ: ਨਿੰਮ ਦਾ ਤੇਲ ਵਰਤੋ। ਗੰਭੀਰ ਮਾਮਲਿਆਂ ਵਿੱਚ ਮਨਜ਼ੂਰਸ਼ੁਦਾ ਕੀਟਨਾਸ਼ਕ ਵਰਤੋ।",
        "harvest": "ਸਹੀ ਸਮੇਂ ਤੇ ਵਾਢੀ ਕਰੋ। ਠੰਡੀ ਅਤੇ ਸੁੱਕੀ ਜਗ੍ਹਾ ਤੇ ਸਟੋਰ ਕਰੋ।",
        "soil": "ਖਾਦ ਪਾਓ, ਫਸਲ ਚੱਕਰ ਅਪਣਾਓ। pH 6.0–7.0 ਰੱਖੋ।",
        "default": "ਮੈਂ ਫਸਲ ਰੋਗ 🌿, ਸਿੰਚਾਈ 💧, ਖਾਦ, ਕੀੜੇ 🐛 ਬਾਰੇ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਕੀ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?",
        "suggestions": ["ਫਸਲ ਰੋਗ ਕਿਵੇਂ ਰੋਕੀਏ?", "ਕਿਹੜੀ ਖਾਦ ਵਰਤੀਏ?", "ਕੀੜੇ ਕਿਵੇਂ ਨਿਯੰਤਰਿਤ ਕਰੀਏ?"],
    },
    "te": {
        "disease": {
            "prevent": "వ్యాధులు నివారించడానికి: వ్యాధి-రహిత విత్తనాలు వాడండి, పంట మార్పిడి పాటించండి, సరైన దూరం ఉంచండి.",
            "treat": "వ్యాధి చికిత్స: తగిన శిలీంద్రనాశకాలు వాడండి, సోకిన ఆకులు తొలగించండి.",
            "default": "Predict విభాగంలో ఆకు చిత్రం అప్‌లోడ్ చేయండి. సాధారణ వ్యాధులు: బాక్టీరియల్ స్పాట్, ఎర్లీ బ్లైట్.",
        },
        "fertilizer": "{crop} కోసం {fert} ఎరువు వాడండి. పెరుగుదల సీజన్‌లో 2-3 వారాలకు ఒకసారి వాడండి.",
        "watering": {"default": "ఉదయం లేదా సాయంత్రం నీరు పెట్టండి, వారానికి 1-2 అంగుళాలు."},
        "pest": "తెగుళ్ల నియంత్రణ: వేప నూనె లేదా కీటకనాశక సబ్బు వాడండి.",
        "harvest": "సరైన సమయంలో కోయండి. చల్లని, పొడి చోటులో నిల్వ చేయండి.",
        "soil": "కంపోస్ట్ వేయండి, పంట మార్పిడి పాటించండి. pH 6.0–7.0 ఉంచండి.",
        "default": "పంట వ్యాధులు 🌿, నీటిపారుదల 💧, ఎరువులు, తెగుళ్లు 🐛 గురించి సహాయం చేయగలను. ఏమి తెలుసుకోవాలి?",
        "suggestions": ["పంట వ్యాధులు ఎలా నివారించాలి?", "ఏ ఎరువు వాడాలి?", "తెగుళ్లను ఎలా నియంత్రించాలి?"],
    },
    "ta": {
        "disease": {
            "prevent": "நோய் தடுக்க: நோயற்ற விதைகளை பயன்படுத்துங்கள், பயிர் சுழற்சி பின்பற்றுங்கள், சரியான இடைவெளி வையுங்கள்.",
            "treat": "நோய் சிகிச்சை: பூஞ்சாண கொல்லிகளை பயன்படுத்துங்கள், பாதிக்கப்பட்ட இலைகளை அகற்றுங்கள்.",
            "default": "Predict பகுதியில் இலை படம் பதிவேற்றுங்கள். பொதுவான நோய்கள்: பாக்டீரியா புள்ளி, ஆரம்ப கருகல்.",
        },
        "fertilizer": "{crop} க்கு {fert} உரம் பயன்படுத்துங்கள். வளர்ச்சி பருவத்தில் 2-3 வாரங்களுக்கு ஒரு முறை தாருங்கள்.",
        "watering": {"default": "காலை அல்லது மாலையில் நீர் பாய்ச்சுங்கள், வாரம் 1-2 அங்குலம்."},
        "pest": "பூச்சி கட்டுப்பாடு: வேப்பெண்ணெய் அல்லது பூச்சிக்கொல்லி சோப்பைப் பயன்படுத்துங்கள்.",
        "harvest": "சரியான நேரத்தில் அறுவடை செய்யுங்கள். குளிரான, உலர்ந்த இடத்தில் சேமியுங்கள்.",
        "soil": "உரம் சேருங்கள், பயிர் சுழற்சி பின்பற்றுங்கள். pH 6.0–7.0 பராமரியுங்கள்.",
        "default": "பயிர் நோய்கள் 🌿, நீர்ப்பாசனம் 💧, உரங்கள், பூச்சிகள் 🐛 பற்றி உதவ முடியும். என்ன தெரிந்துகொள்ள விரும்புகிறீர்கள்?",
        "suggestions": ["பயிர் நோய்களை தடுப்பது எப்படி?", "எந்த உரம் பயன்படுத்தலாம்?", "பூச்சிகளை கட்டுப்படுத்துவது எப்படி?"],
    },
    "kn": {
        "disease": {
            "prevent": "ರೋಗ ತಡೆಗಟ್ಟಲು: ರೋಗ-ಮುಕ್ತ ಬೀಜಗಳನ್ನು ಬಳಸಿ, ಬೆಳೆ ತಿರುಗಿಸಿ, ಸರಿಯಾದ ಅಂತರ ಕಾಪಾಡಿ.",
            "treat": "ರೋಗ ಚಿಕಿತ್ಸೆ: ಶಿಲೀಂಧ್ರನಾಶಕ ಹಾಕಿ, ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆಯಿರಿ.",
            "default": "Predict ವಿಭಾಗದಲ್ಲಿ ಎಲೆಯ ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ. ಸಾಮಾನ್ಯ ರೋಗಗಳು: ಬ್ಯಾಕ್ಟೀರಿಯಲ್ ಸ್ಪಾಟ್, ಅರ್ಲಿ ಬ್ಲೈಟ್.",
        },
        "fertilizer": "{crop} ಗೆ {fert} ಗೊಬ್ಬರ ಬಳಸಿ. ಬೆಳವಣಿಗೆ ಸೀಜನ್‌ನಲ್ಲಿ 2-3 ವಾರಕ್ಕೊಮ್ಮೆ ಹಾಕಿ.",
        "watering": {"default": "ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ನೀರು ಹಾಕಿ, ವಾರಕ್ಕೆ 1-2 ಇಂಚು."},
        "pest": "ಕೀಟ ನಿಯಂತ್ರಣ: ಬೇವಿನ ಎಣ್ಣೆ ಬಳಸಿ. ತೀವ್ರ ಸಂದರ್ಭದಲ್ಲಿ ಅನುಮೋದಿತ ಕೀಟನಾಶಕ ಬಳಸಿ.",
        "harvest": "ಸರಿಯಾದ ಸಮಯದಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಿ. ತಂಪಾದ, ಒಣಗಿದ ಜಾಗದಲ್ಲಿ ಸಂಗ್ರಹಿಸಿ.",
        "soil": "ಕಾಂಪೋಸ್ಟ್ ಹಾಕಿ, ಬೆಳೆ ತಿರುಗಿಸಿ. pH 6.0–7.0 ನಿರ್ವಹಿಸಿ.",
        "default": "ಬೆಳೆ ರೋಗಗಳು 🌿, ನೀರಾವರಿ 💧, ಗೊಬ್ಬರ, ಕೀಟಗಳು 🐛 ಬಗ್ಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ಏನು ತಿಳಿಯಬೇಕು?",
        "suggestions": ["ಬೆಳೆ ರೋಗಗಳನ್ನು ತಡೆಯುವುದು ಹೇಗೆ?", "ಯಾವ ಗೊಬ್ಬರ ಬಳಸಬೇಕು?", "ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸುವುದು ಹೇಗೆ?"],
    },
    "gu": {
        "disease": {
            "prevent": "રોગ અટકાવવા: રોગ-મુક્ત બીજ વાપરો, પાક ફેરબદલ કરો, યોગ્ય અંતર રાખો, ચેપી છોડ તરત દૂર કરો.",
            "treat": "રોગ ઉપચાર: ફૂગનાશક લગાવો, ચેપી પાંદડા દૂર કરો, હવા ઉજાસ સુધારો.",
            "default": "Predict વિભાગમાં પાંદડાનો ફોટો અપલોડ કરો. સામાન્ય રોગ: બેક્ટેરિયલ સ્પોટ, અર્લી બ્લાઇટ.",
        },
        "fertilizer": "{crop} માટે {fert} ખાતર વાપરો. વૃદ્ધિ ઋતુમાં 2-3 અઠવાડિયે આપો.",
        "watering": {"default": "સવારે કે સાંજે પાણી આપો, અઠવાડિયે 1-2 ઇંચ. પાણી આપતાં પહેલાં ભેજ ચકાસો."},
        "pest": "જીવાત નિયંત્રણ: લીમડાનું તેલ વાપરો. ગંભીર ઉપદ્રવ હોય તો મંજૂર જંતુનાશક વાપરો.",
        "harvest": "સમયસર લણણી કરો. ઠંડી અને સૂકી જગ્યાએ સંગ્રહ કરો.",
        "soil": "ખાતર ઉમેરો, પાક ફેરબદલ કરો. pH 6.0–7.0 જાળવો.",
        "default": "પાક રોગ 🌿, સિંચાઈ 💧, ખાતર, જીવાત 🐛, કાપણી અને જમીન સ્વાસ્થ્ય વિશે મદદ કરી શકું. શું જાણવું છે?",
        "suggestions": ["પાક રોગ કેવી રીતે અટકાવવો?", "ટામેટા માટે ખાતર કયું?", "છોડને કેટલું પાણી આપવું?"],
    },
}

FERTILIZERS = {
    "tomato": "NPK 10-10-10 with micronutrients",
    "potato": "high potassium (NPK 5-10-15)",
    "corn": "nitrogen-rich (NPK 46-0-0 urea)",
    "wheat": "nitrogen and phosphorus blend",
    "rice": "NPK 20-20-0 with zinc",
    "default": "balanced NPK 10-10-10",
}


class FarmingChatbot:
    """Multilingual AI Chatbot for farming assistance"""

    def __init__(self):
        self.conversation_history = []

    async def chat(self, user_message: str, context: dict | None = None) -> dict:
        lang = (context or {}).get("language", "en")
        # Fall back to English if lang not supported
        if lang not in RESPONSES:
            lang = "en"
        crop = (context or {}).get("crop_type", "")
        response = self._generate_response(user_message.lower(), lang, crop)
        self.conversation_history.append({"user": user_message, "bot": response["answer"]})
        return response

    def _generate_response(self, message: str, lang: str, crop: str) -> dict:
        R = RESPONSES[lang]
        fert = FERTILIZERS.get(crop.lower(), FERTILIZERS["default"]) if crop else FERTILIZERS["default"]

        # Disease
        if any(w in message for w in ["disease", "sick", "spot", "blight", "yellow", "infected", "रोग", "बीमारी",
                                       "ਬਿਮਾਰੀ", "వ్యాధి", "நோய்", "ರೋಗ", "રોગ", "आजार", "पीक रोग"]):
            if any(w in message for w in ["prevent", "रोक", "ਰੋਕ", "నివారణ", "தடு", "ತಡೆ", "અટક", "टाळ"]):
                return {"answer": R["disease"]["prevent"], "suggestions": R.get("suggestions", []), "type": "disease"}
            if any(w in message for w in ["treat", "cure", "उपचार", "ਇਲਾਜ", "చికిత్స", "சிகிச்சை", "ಚಿಕಿತ್ಸೆ", "ઉપચાર"]):
                return {"answer": R["disease"]["treat"], "suggestions": R.get("suggestions", []), "type": "disease"}
            return {"answer": R["disease"]["default"], "suggestions": R.get("suggestions", []), "type": "disease"}

        # Fertilizer
        if any(w in message for w in ["fertil", "npk", "nutrient", "feed", "उर्वरक", "ਖਾਦ", "ఎరువు", "உரம்", "ಗೊಬ್ಬರ", "ખાતર", "खत"]):
            crop_label = crop if crop else ("tomato" if "tomato" in message or "टमाटर" in message else "your crop")
            answer = R["fertilizer"].format(crop=crop_label, fert=fert)
            return {"answer": answer, "suggestions": R.get("suggestions", []), "type": "fertilizer"}

        # Watering
        if any(w in message for w in ["water", "irrigat", "moisture", "पानी", "ਪਾਣੀ", "నీరు", "நீர்", "ನೀರು", "पाणी", "સિંચ"]):
            watering = R.get("watering", {})
            crop_key = crop.lower() if crop and crop.lower() in watering else "default"
            answer = watering.get(crop_key, watering.get("default", ""))
            return {"answer": answer, "suggestions": R.get("suggestions", []), "type": "watering"}

        # Pest
        if any(w in message for w in ["pest", "insect", "bug", "aphid", "कीट", "ਕੀੜ", "తెగులు", "பூச்சி", "ಕೀಟ", "જીવાત", "कीड"]):
            return {"answer": R["pest"], "suggestions": R.get("suggestions", []), "type": "pest"}

        # Harvest
        if any(w in message for w in ["harvest", "pick", "कटाई", "ਵਾਢੀ", "కోత", "அறுவடை", "ಕೊಯ್ಲು", "లణ", "कापणी"]):
            return {"answer": R["harvest"], "suggestions": R.get("suggestions", []), "type": "harvest"}

        # Soil
        if any(w in message for w in ["soil", "earth", "मिट्टी", "ਮਿੱਟੀ", "నేల", "மண்", "ಮಣ್ಣು", "माती", "જમીન"]):
            return {"answer": R["soil"], "suggestions": R.get("suggestions", []), "type": "soil"}

        return {"answer": R["default"], "suggestions": R.get("suggestions", []), "type": "general"}

    def get_conversation_history(self) -> list:
        return self.conversation_history


# Global instance
farming_chatbot = FarmingChatbot()
