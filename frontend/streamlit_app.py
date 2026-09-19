import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st._config.set_option("theme.base", "light")
st._config.set_option("theme.primaryColor", "#0b5ed7")
st._config.set_option("theme.backgroundColor", "#f0f5fa")
st._config.set_option("theme.secondaryBackgroundColor", "#ffffff")
st._config.set_option("theme.textColor", "#1a2332")

st.set_page_config(
    page_title="RetinaScan — DR Screening",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)

TRANSLATIONS = {
    "English": {
        "app_subtitle": "Diabetic Retinopathy Screening System · Team Drift Coders · SIH 2026",
        "patient_registration": "Patient Registration",
        "full_name": "Full Name", "age": "Age", "gender": "Gender",
        "male": "Male", "female": "Female", "other": "Other",
        "diabetes_type": "Diabetes Type", "type1": "Type 1", "type2": "Type 2", "gestational": "Gestational",
        "register_patient": "Register Patient", "patient_registered": "Patient registered", "patient_id": "Patient ID",
        "step1_label": "Step 1 · Patient Identification", "patient_id_input": "Patient ID",
        "patient_id_placeholder": "Register a patient in the sidebar or paste an existing Patient ID",
        "patient_id_info": "Register a patient in the sidebar or paste a Patient ID to continue.",
        "step2_label": "Step 2 · Retinal Image Input", "camera_capture": "Camera Capture", "upload_file": "Upload from File",
        "camera_caption": "Position the eye centrally and capture a clear image.", "capture": "Capture", "retake": "Retake",
        "upload_caption": "Select a retinal fundus image from your device.", "choose_image": "Choose image",
        "selected_image": "Selected Image", "captured_image": "Captured Image", "remove": "Remove",
        "step3_label": "Step 3 · AI Analysis", "run_diagnosis": "Run AI Diagnosis",
        "please_upload": "Capture or upload a retinal image to proceed.", "analyzing": "Analyzing retinal image...",
        "diagnostic_report": "Diagnostic Report", "source": "Source", "model": "Model", "explainability": "Explainability",
        "camera_source": "Camera Capture", "upload_source": "File Upload",
        "grade_normal": "Normal", "grade_normal_title": "No Diabetic Retinopathy Detected",
        "grade_normal_detail": "No signs of DR were identified in this retinal image.",
        "grade_mild": "Early Stage", "grade_mild_title": "Mild Non-Proliferative DR",
        "grade_mild_detail": "Early signs detected. Regular monitoring recommended.",
        "grade_moderate": "Moderate", "grade_moderate_title": "Moderate Non-Proliferative DR",
        "grade_moderate_detail": "Ophthalmology referral recommended.",
        "grade_severe": "Severe", "grade_severe_title": "Severe Non-Proliferative DR",
        "grade_severe_detail": "Urgent ophthalmology referral required.",
        "grade_proliferative": "Critical", "grade_proliferative_title": "Proliferative Diabetic Retinopathy",
        "grade_proliferative_detail": "Immediate specialist intervention required.",
        "dr_grade": "DR Grade", "confidence": "Confidence", "risk_level": "Risk Level",
        "detected_type": "Detected Type",
        "patient_info": "Patient Information",
        "diabetes_label": "Diabetes",
        "invalid_image": "Invalid Image", "not_suitable": "Not Suitable for Diagnosis",
        "not_suitable_detail": "This image does not appear to be a retinal fundus image. Please use a fundus camera or upload a proper retinal image.",
        "referral_recommended": "**Referral Recommended** — Patient should be referred to an ophthalmologist for further evaluation.",
        "no_referral": "**No Immediate Referral Required** — Routine follow-up at the Primary Health Centre is sufficient.",
        "gradcam_section": "Grad-CAM Explainability", "gradcam_caption": "Highlighted regions indicate areas of model attention.",
        "explanation_section": "Clinical Explanation", "probabilities_section": "Class Probabilities",
        "clinical_note": "Clinical Note",
        "no_dr_note": """No signs of Diabetic Retinopathy were detected in this retinal image.
The AI model found no microaneurysms, hemorrhages, or exudates characteristic of DR.

Regular annual retinal screening is still recommended for all patients with diabetes,
as DR can develop silently over time.""",
        "footer": "RetinaScan · Diabetic Retinopathy Screening System<br>Team Drift Coders · Smart India Hackathon 2026",
    },
    "हिन्दी (Hindi)": {
        "app_subtitle": "डायबिटिक रेटिनोपैथी स्क्रीनिंग सिस्टम · टीम ड्रिफ्ट कोडर्स · SIH 2026",
        "patient_registration": "रोगी पंजीकरण", "full_name": "पूरा नाम", "age": "आयु", "gender": "लिंग",
        "male": "पुरुष", "female": "महिला", "other": "अन्य",
        "diabetes_type": "मधुमेह का प्रकार", "type1": "प्रकार 1", "type2": "प्रकार 2", "gestational": "गर्भकालीन",
        "register_patient": "रोगी पंजीकृत करें", "patient_registered": "रोगी पंजीकृत", "patient_id": "रोगी आईडी",
        "step1_label": "चरण 1 · रोगी पहचान", "patient_id_input": "रोगी आईडी",
        "patient_id_placeholder": "साइडबार में रोगी पंजीकृत करें या मौजूदा आईडी पेस्ट करें",
        "patient_id_info": "जारी रखने के लिए साइडबार में रोगी पंजीकृत करें या आईडी पेस्ट करें।",
        "step2_label": "चरण 2 · रेटिना छवि इनपुट", "camera_capture": "कैमरा कैप्चर", "upload_file": "फ़ाइल से अपलोड करें",
        "camera_caption": "आँख को केंद्र में रखें और स्पष्ट छवि लें।", "capture": "कैप्चर करें", "retake": "दोबारा लें",
        "upload_caption": "अपने डिवाइस से रेटिना फंडस छवि चुनें।", "choose_image": "छवि चुनें",
        "selected_image": "चयनित छवि", "captured_image": "कैप्चर की गई छवि", "remove": "हटाएँ",
        "step3_label": "चरण 3 · AI विश्लेषण", "run_diagnosis": "AI निदान चलाएँ",
        "please_upload": "आगे बढ़ने के लिए रेटिना छवि कैप्चर या अपलोड करें।", "analyzing": "रेटिना छवि का विश्लेषण हो रहा है...",
        "diagnostic_report": "निदान रिपोर्ट", "source": "स्रोत", "model": "मॉडल", "explainability": "व्याख्या",
        "camera_source": "कैमरा कैप्चर", "upload_source": "फ़ाइल अपलोड",
        "grade_normal": "सामान्य", "grade_normal_title": "कोई डायबिटिक रेटिनोपैथी नहीं मिली",
        "grade_normal_detail": "इस रेटिना छवि में DR के कोई संकेत नहीं मिले।",
        "grade_mild": "प्रारंभिक चरण", "grade_mild_title": "हल्की नॉन-प्रोलिफरेटिव DR",
        "grade_mild_detail": "प्रारंभिक संकेत मिले। नियमित निगरानी की सलाह दी जाती है।",
        "grade_moderate": "मध्यम", "grade_moderate_title": "मध्यम नॉन-प्रोलिफरेटिव DR",
        "grade_moderate_detail": "नेत्र रोग विशेषज्ञ को रेफर करने की सलाह दी जाती है।",
        "grade_severe": "गंभीर", "grade_severe_title": "गंभीर नॉन-प्रोलिफरेटिव DR",
        "grade_severe_detail": "तत्काल नेत्र रोग विशेषज्ञ रेफरल आवश्यक।",
        "grade_proliferative": "गंभीर", "grade_proliferative_title": "प्रोलिफरेटिव डायबिटिक रेटिनोपैथी",
        "grade_proliferative_detail": "तत्काल विशेषज्ञ उपचार आवश्यक।",
        "dr_grade": "DR ग्रेड", "confidence": "विश्वास", "risk_level": "जोखिम स्तर",
        "detected_type": "पता चला प्रकार",
        "patient_info": "रोगी जानकारी",
        "diabetes_label": "मधुमेह",
        "invalid_image": "अमान्य छवि", "not_suitable": "निदान के लिए उपयुक्त नहीं",
        "not_suitable_detail": "यह छवि रेटिना फंडस छवि प्रतीत नहीं होती। कृपया फंडस कैमरा उपयोग करें या उचित रेटिना छवि अपलोड करें।",
        "referral_recommended": "**रेफरल की सलाह** — रोगी को आगे मूल्यांकन के लिए नेत्र रोग विशेषज्ञ को भेजें।",
        "no_referral": "**तत्काल रेफरल की आवश्यकता नहीं** — प्राथमिक स्वास्थ्य केंद्र में नियमित अनुवर्ती पर्याप्त है।",
        "gradcam_section": "Grad-CAM व्याख्या", "gradcam_caption": "हाइलाइट किए गए क्षेत्र मॉडल के ध्यान को दर्शाते हैं।",
        "explanation_section": "नैदानिक व्याख्या", "probabilities_section": "वर्ग संभावनाएँ",
        "clinical_note": "नैदानिक नोट",
        "no_dr_note": """इस रेटिना छवि में डायबिटिक रेटिनोपैथी के कोई संकेत नहीं मिले।
AI मॉडल को DR की विशेषता वाले माइक्रोएन्यूरिज्म, रक्तस्राव, या एक्सयूडेट नहीं मिले।

मधुमेह वाले सभी रोगियों के लिए वार्षिक रेटिना स्क्रीनिंग की सलाह अभी भी दी जाती है,
क्योंकि DR समय के साथ चुपचाप विकसित हो सकता है।""",
        "footer": "रेटिनास्कैन · डायबिटिक रेटिनोपैथी स्क्रीनिंग सिस्टम<br>टीम ड्रिफ्ट कोडर्स · स्मार्ट इंडिया हैकाथॉन 2026",
    },
    "ଓଡ଼ିଆ (Odia)": {
        "app_subtitle": "ଡାଇବେଟିକ ରେଟିନୋପାଥି ସ୍କ୍ରିନିଂ ସିଷ୍ଟମ · ଟିମ ଡ୍ରିଫ୍ଟ କୋଡର୍ସ · SIH 2026",
        "patient_registration": "ରୋଗୀ ପଞ୍ଜୀକରଣ", "full_name": "ପୂରା ନାମ", "age": "ବୟସ", "gender": "ଲିଙ୍ଗ",
        "male": "ପୁରୁଷ", "female": "ମହିଳା", "other": "ଅନ୍ୟାନ୍ୟ",
        "diabetes_type": "ମଧୁମେହ ପ୍ରକାର", "type1": "ପ୍ରକାର 1", "type2": "ପ୍ରକାର 2", "gestational": "ଗର୍ଭକାଳୀନ",
        "register_patient": "ରୋଗୀ ପଞ୍ଜୀକରଣ କରନ୍ତୁ", "patient_registered": "ରୋଗୀ ପଞ୍ଜୀକୃତ", "patient_id": "ରୋଗୀ ଆଇଡି",
        "step1_label": "ପର୍ଯ୍ୟାୟ 1 · ରୋଗୀ ଚିହ୍ନଟ", "patient_id_input": "ରୋଗୀ ଆଇଡି",
        "patient_id_placeholder": "ସାଇଡବାରରେ ରୋଗୀ ପଞ୍ଜୀକରଣ କରନ୍ତୁ କିମ୍ବା ବିଦ୍ୟମାନ ଆଇଡି ଲେଖନ୍ତୁ",
        "patient_id_info": "ଜାରି ରଖିବା ପାଇଁ ସାଇଡବାରରେ ରୋଗୀ ପଞ୍ଜୀକରଣ କରନ୍ତୁ କିମ୍ବା ଆଇଡି ଲେଖନ୍ତୁ।",
        "step2_label": "ପର୍ଯ୍ୟାୟ 2 · ରେଟିନା ଚିତ୍ର ଇନପୁଟ", "camera_capture": "କ୍ୟାମେରା କ୍ୟାପଚର", "upload_file": "ଫାଇଲରୁ ଅପଲୋଡ କରନ୍ତୁ",
        "camera_caption": "ଆଖିକୁ କେନ୍ଦ୍ରରେ ରଖନ୍ତୁ ଏବଂ ସ୍ପଷ୍ଟ ଚିତ୍ର ନିଅନ୍ତୁ।", "capture": "କ୍ୟାପଚର କରନ୍ତୁ", "retake": "ପୁନଃ ନିଅନ୍ତୁ",
        "upload_caption": "ଆପଣଙ୍କ ଡିଭାଇସରୁ ରେଟିନା ଫଣ୍ଡସ ଚିତ୍ର ଚୟନ କରନ୍ତୁ।", "choose_image": "ଚିତ୍ର ଚୟନ କରନ୍ତୁ",
        "selected_image": "ଚୟନିତ ଚିତ୍ର", "captured_image": "କ୍ୟାପଚର ଚିତ୍ର", "remove": "ଅପସାରଣ କରନ୍ତୁ",
        "step3_label": "ପର୍ଯ୍ୟାୟ 3 · AI ବିଶ୍ଳେଷଣ", "run_diagnosis": "AI ନିର୍ଣ୍ଣୟ ଚଲାନ୍ତୁ",
        "please_upload": "ଆଗକୁ ବଢ଼ିବା ପାଇଁ ରେଟିନା ଚିତ୍ର କ୍ୟାପଚର କିମ୍ବା ଅପଲୋଡ କରନ୍ତୁ।", "analyzing": "ରେଟିନା ଚିତ୍ର ବିଶ୍ଳେଷଣ ଚାଲିଛି...",
        "diagnostic_report": "ନିର୍ଣ୍ଣୟ ରିପୋର୍ଟ", "source": "ଉତ୍ସ", "model": "ମଡେଲ", "explainability": "ବ୍ୟାଖ୍ୟା",
        "camera_source": "କ୍ୟାମେରା କ୍ୟାପଚର", "upload_source": "ଫାଇଲ ଅପଲୋଡ",
        "grade_normal": "ସ୍ୱାଭାବିକ", "grade_normal_title": "କୌଣସି ଡାଇବେଟିକ ରେଟିନୋପାଥି ମିଳିଲା ନାହିଁ",
        "grade_normal_detail": "ଏହି ରେଟିନା ଚିତ୍ରରେ DR ର କୌଣସି ଚିହ୍ନ ମିଳିଲା ନାହିଁ।",
        "grade_mild": "ପ୍ରାରମ୍ଭିକ ପର୍ଯ୍ୟାୟ", "grade_mild_title": "ମୃଦୁ ନନ୍-ପ୍ରୋଲିଫେରେଟିଭ DR",
        "grade_mild_detail": "ପ୍ରାରମ୍ଭିକ ଚିହ୍ନ ମିଳିଲା। ନିୟମିତ ମନିଟରିଂ ସୁପାରିଶ କରାଯାଏ।",
        "grade_moderate": "ମଧ୍ୟମ", "grade_moderate_title": "ମଧ୍ୟମ ନନ୍-ପ୍ରୋଲିଫେରେଟିଭ DR",
        "grade_moderate_detail": "ନେତ୍ର ରୋଗ ବିଶେଷଜ୍ଞଙ୍କୁ ରେଫର କରିବାକୁ ସୁପାରିଶ କରାଯାଏ।",
        "grade_severe": "ଗମ୍ଭୀର", "grade_severe_title": "ଗମ୍ଭୀର ନନ୍-ପ୍ରୋଲିଫେରେଟିଭ DR",
        "grade_severe_detail": "ତୁରନ୍ତ ନେତ୍ର ରୋଗ ବିଶେଷଜ୍ଞ ରେଫର ଆବଶ୍ୟକ।",
        "grade_proliferative": "ସଙ୍କଟପୂର୍ଣ୍ଣ", "grade_proliferative_title": "ପ୍ରୋଲିଫେରେଟିଭ ଡାଇବେଟିକ ରେଟିନୋପାଥି",
        "grade_proliferative_detail": "ତୁରନ୍ତ ବିଶେଷଜ୍ଞ ଚିକିତ୍ସା ଆବଶ୍ୟକ।",
        "dr_grade": "DR ଗ୍ରେଡ", "confidence": "ଆତ୍ମବିଶ୍ୱାସ", "risk_level": "ବିପଦ ସ୍ତର",
        "detected_type": "ଚିହ୍ନଟ ପ୍ରକାର",
        "patient_info": "ରୋଗୀ ସୂଚନା",
        "diabetes_label": "ମଧୁମେହ",
        "invalid_image": "ଅବୈଧ ଚିତ୍ର", "not_suitable": "ନିର୍ଣ୍ଣୟ ପାଇଁ ଉପଯୁକ୍ତ ନୁହେଁ",
        "not_suitable_detail": "ଏହି ଚିତ୍ରଟି ରେଟିନା ଫଣ୍ଡସ ଚିତ୍ର ପରି ଦେଖାଯାଉନାହିଁ। ଦୟାକରି ଫଣ୍ଡସ କ୍ୟାମେରା ବ୍ୟବହାର କରନ୍ତୁ କିମ୍ବା ଉପଯୁକ୍ତ ରେଟିନା ଚିତ୍ର ଅପଲୋଡ କରନ୍ତୁ।",
        "referral_recommended": "**ରେଫର ସୁପାରିଶ** — ରୋଗୀଙ୍କୁ ଆଗକୁ ମୂଲ୍ୟାଙ୍କନ ପାଇଁ ନେତ୍ର ରୋଗ ବିଶେଷଜ୍ଞଙ୍କୁ ପଠାନ୍ତୁ।",
        "no_referral": "**ତୁରନ୍ତ ରେଫର ଆବଶ୍ୟକ ନାହିଁ** — ପ୍ରାଥମିକ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ରରେ ନିୟମିତ ଅନୁସରଣ ଯଥେଷ୍ଟ।",
        "gradcam_section": "Grad-CAM ବ୍ୟାଖ୍ୟା", "gradcam_caption": "ହାଇଲାଇଟ ହୋଇଥିବା ଅଞ୍ଚଳ ମଡେଲର ଧ୍ୟାନ ଦର୍ଶାଏ।",
        "explanation_section": "କ୍ଲିନିକାଲ ବ୍ୟାଖ୍ୟା", "probabilities_section": "ଶ୍ରେଣୀ ସମ୍ଭାବନା",
        "clinical_note": "କ୍ଲିନିକାଲ ନୋଟ",
        "no_dr_note": """ଏହି ରେଟିନା ଚିତ୍ରରେ ଡାଇବେଟିକ ରେଟିନୋପାଥିର କୌଣସି ଚିହ୍ନ ମିଳିଲା ନାହିଁ।
AI ମଡେଲ DR ର ଲକ୍ଷଣ ମାଇକ୍ରୋଆନିଉରିଜିମ, ରକ୍ତସ୍ରାବ, କିମ୍ବା ଏକ୍ସୁଡେଟ ପାଇଲା ନାହିଁ।

ମଧୁମେହ ରୋଗୀମାନଙ୍କ ପାଇଁ ବାର୍ଷିକ ରେଟିନା ସ୍କ୍ରିନିଂ ତଥାପି ସୁପାରିଶ କରାଯାଏ,
କାରଣ DR ସମୟ ସହିତ ଚୁପଚାପ ବିକଶିତ ହୋଇପାରେ।""",
        "footer": "ରେଟିନାସ୍କାନ · ଡାଇବେଟିକ ରେଟିନୋପାଥି ସ୍କ୍ରିନିଂ ସିଷ୍ଟମ<br>ଟିମ ଡ୍ରିଫ୍ଟ କୋଡର୍ସ · ସ୍ମାର୍ଟ ଇଣ୍ଡିଆ ହ୍ୟାକାଥନ 2026",
    },
    "বাংলা (Bengali)": {
        "app_subtitle": "ডায়াবেটিক রেটিনোপ্যাথি স্ক্রিনিং সিস্টেম · টিম ড্রিফট কোডার্স · SIH 2026",
        "patient_registration": "রোগী নিবন্ধন", "full_name": "পূর্ণ নাম", "age": "বয়স", "gender": "লিঙ্গ",
        "male": "পুরুষ", "female": "মহিলা", "other": "অন্যান্য",
        "diabetes_type": "ডায়াবেটিসের ধরন", "type1": "টাইপ 1", "type2": "টাইপ 2", "gestational": "গর্ভকালীন",
        "register_patient": "রোগী নিবন্ধন করুন", "patient_registered": "রোগী নিবন্ধিত", "patient_id": "রোগী আইডি",
        "step1_label": "ধাপ 1 · রোগী সনাক্তকরণ", "patient_id_input": "রোগী আইডি",
        "patient_id_placeholder": "সাইডবারে রোগী নিবন্ধন করুন বা বিদ্যমান আইডি পেস্ট করুন",
        "patient_id_info": "চালিয়ে যেতে সাইডবারে রোগী নিবন্ধন করুন বা আইডি পেস্ট করুন।",
        "step2_label": "ধাপ 2 · রেটিনা চিত্র ইনপুট", "camera_capture": "ক্যামেরা ক্যাপচার", "upload_file": "ফাইল থেকে আপলোড",
        "camera_caption": "চোখ কেন্দ্রে রাখুন এবং একটি স্পষ্ট ছবি তুলুন।", "capture": "ক্যাপচার করুন", "retake": "পুনরায় তুলুন",
        "upload_caption": "আপনার ডিভাইস থেকে একটি রেটিনা ফান্ডাস চিত্র নির্বাচন করুন।", "choose_image": "ছবি নির্বাচন করুন",
        "selected_image": "নির্বাচিত ছবি", "captured_image": "ক্যাপচার করা ছবি", "remove": "সরান",
        "step3_label": "ধাপ 3 · AI বিশ্লেষণ", "run_diagnosis": "AI রোগ নির্ণয় চালান",
        "please_upload": "এগিয়ে যেতে একটি রেটিনা চিত্র ক্যাপচার বা আপলোড করুন।", "analyzing": "রেটিনা চিত্র বিশ্লেষণ করা হচ্ছে...",
        "diagnostic_report": "রোগ নির্ণয় রিপোর্ট", "source": "উৎস", "model": "মডেল", "explainability": "ব্যাখ্যা",
        "camera_source": "ক্যামেরা ক্যাপচার", "upload_source": "ফাইল আপলোড",
        "grade_normal": "স্বাভাবিক", "grade_normal_title": "কোনো ডায়াবেটিক রেটিনোপ্যাথি পাওয়া যায়নি",
        "grade_normal_detail": "এই রেটিনা চিত্রে DR-এর কোনো লক্ষণ পাওয়া যায়নি।",
        "grade_mild": "প্রাথমিক পর্যায়", "grade_mild_title": "হালকা নন-প্রলিফারেটিভ DR",
        "grade_mild_detail": "প্রাথমিক লক্ষণ পাওয়া গেছে। নিয়মিত মনিটরিং সুপারিশ করা হয়।",
        "grade_moderate": "মাঝারি", "grade_moderate_title": "মাঝারি নন-প্রলিফারেটিভ DR",
        "grade_moderate_detail": "চক্ষু বিশেষজ্ঞের কাছে রেফার করার সুপারিশ করা হয়।",
        "grade_severe": "গুরুতর", "grade_severe_title": "গুরুতর নন-প্রলিফারেটিভ DR",
        "grade_severe_detail": "জরুরি চক্ষু বিশেষজ্ঞ রেফারেল প্রয়োজন।",
        "grade_proliferative": "সংকটপূর্ণ", "grade_proliferative_title": "প্রলিফারেটিভ ডায়াবেটিক রেটিনোপ্যাথি",
        "grade_proliferative_detail": "অবিলম্বে বিশেষজ্ঞ হস্তক্ষেপ প্রয়োজন।",
        "dr_grade": "DR গ্রেড", "confidence": "আত্মবিশ্বাস", "risk_level": "ঝুঁকির মাত্রা",
        "detected_type": "সনাক্ত ধরন",
        "patient_info": "রোগীর তথ্য",
        "diabetes_label": "ডায়াবেটিস",
        "invalid_image": "অবৈধ ছবি", "not_suitable": "রোগ নির্ণয়ের জন্য উপযুক্ত নয়",
        "not_suitable_detail": "এই ছবিটি একটি রেটিনা ফান্ডাস ছবি বলে মনে হচ্ছে না। অনুগ্রহ করে একটি ফান্ডাস ক্যামেরা ব্যবহার করুন বা উপযুক্ত রেটিনা ছবি আপলোড করুন।",
        "referral_recommended": "**রেফারেল সুপারিশ** — রোগীকে আরও মূল্যায়নের জন্য চক্ষু বিশেষজ্ঞের কাছে পাঠান।",
        "no_referral": "**তাৎক্ষণিক রেফারেল প্রয়োজন নেই** — প্রাথমিক স্বাস্থ্য কেন্দ্রে নিয়মিত ফলো-আপ যথেষ্ট।",
        "gradcam_section": "Grad-CAM ব্যাখ্যা", "gradcam_caption": "হাইলাইট করা অঞ্চলগুলি মডেলের মনোযোগ নির্দেশ করে।",
        "explanation_section": "ক্লিনিক্যাল ব্যাখ্যা", "probabilities_section": "শ্রেণী সম্ভাবনা",
        "clinical_note": "ক্লিনিক্যাল নোট",
        "no_dr_note": """এই রেটিনা চিত্রে ডায়াবেটিক রেটিনোপ্যাথির কোনো লক্ষণ পাওয়া যায়নি।
AI মডেল DR-এর বৈশিষ্ট্যপূর্ণ মাইক্রোঅ্যানিউরিজম, রক্তক্ষরণ, বা এক্সুডেট পায়নি।

ডায়াবেটিস রোগীদের জন্য বার্ষিক রেটিনা স্ক্রিনিং এখনও সুপারিশ করা হয়,
কারণ DR সময়ের সাথে নিঃশব্দে বিকশিত হতে পারে।""",
        "footer": "রেটিনাস্ক্যান · ডায়াবেটিক রেটিনোপ্যাথি স্ক্রিনিং সিস্টেম<br>টিম ড্রিফট কোডার্স · স্মার্ট ইন্ডিয়া হ্যাকাথন 2026",
    }
}

LANG_OPTIONS = ["English", "हिन्दी (Hindi)", "ଓଡ଼ିଆ (Odia)", "বাংলা (Bengali)"]

if "language" not in st.session_state:
    st.session_state.language = "English"

with st.sidebar:
    st.markdown('<div class="section-label">Language / भाषा</div>', unsafe_allow_html=True)
    st.selectbox(
        "Language",
        LANG_OPTIONS,
        index=LANG_OPTIONS.index(st.session_state.language),
        key="language_selector",
        label_visibility="collapsed"
    )
    st.session_state.language = st.session_state.language_selector

t = TRANSLATIONS[st.session_state.language]

colors = {
    "card_bg": "#ffffff", "text": "#1a2332", "text_muted": "#5a6b7f", "border": "#dce4ee",
    "primary": "#0b5ed7", "primary_light": "#e7f0fb", "primary_dark": "#084298",
    "success": "#0d7a3f", "success_bg": "#e6f5ec",
    "warning": "#b86a00", "warning_bg": "#fff5e6",
    "danger": "#b3261e", "danger_bg": "#fdecea",
}

st.markdown(f"""
<style>
    .stApp {{ background-color: {colors['primary_light']}; }}
    
    .app-header {{
        padding: 1rem 1.25rem;
        background: linear-gradient(135deg, {colors['primary']} 0%, {colors['primary_dark']} 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 14px rgba(11, 94, 215, 0.18);
        flex-wrap: wrap;
    }}
    .app-logo {{
        width: 42px; height: 42px; border-radius: 10px;
        background: rgba(255,255,255,0.18);
        color: #ffffff !important;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; font-weight: 700;
        flex-shrink: 0;
    }}
    .app-title {{ 
        font-size: 1.5rem; 
        font-weight: 700; 
        color: #ffffff !important; 
        margin: 0;
        line-height: 1.2;
    }}
    .app-subtitle {{ 
        font-size: 0.8rem; 
        color: rgba(255,255,255,0.92) !important; 
        margin: 0.25rem 0 0 0;
        line-height: 1.3;
    }}
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
        color: {colors['text']};
    }}
    .app-header h1, .app-header h2 {{
        color: #ffffff !important;
    }}
    
    .section-label {{
        font-size: 0.72rem; font-weight: 700; color: {colors['primary']};
        text-transform: uppercase; letter-spacing: 0.1em;
        margin-bottom: 0.6rem; margin-top: 1.4rem;
    }}
    
    .metric-card {{
        background: {colors['card_bg']}; border: 1px solid {colors['border']};
        border-radius: 10px; padding: 1.25rem; text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .metric-label {{
        font-size: 0.72rem; font-weight: 600; color: {colors['text_muted']};
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;
    }}
    .metric-value {{ 
        font-size: 1.6rem; font-weight: 700; color: {colors['text']}; line-height: 1.1; 
    }}
    
    .result-banner {{
        padding: 1.5rem 2rem; border-radius: 12px; margin: 1rem 0;
        border-left: 5px solid; background: {colors['card_bg']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .result-success {{ background: {colors['success_bg']}; border-color: {colors['success']}; }}
    .result-warning {{ background: {colors['warning_bg']}; border-color: {colors['warning']}; }}
    .result-danger {{ background: {colors['danger_bg']}; border-color: {colors['danger']}; }}
    .result-label {{
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; margin-bottom: 0.3rem; color: {colors['text_muted']};
    }}
    .result-title {{ font-size: 1.5rem; font-weight: 700; margin: 0; color: {colors['text']}; }}
    .result-detail {{ font-size: 0.92rem; color: {colors['text_muted']}; margin-top: 0.5rem; }}
    .detected-type {{
        margin-top: 1rem; padding-top: 1rem;
        border-top: 1px solid rgba(0,0,0,0.08); font-size: 0.9rem;
    }}
    .patient-info {{
        margin-top: 0.5rem; padding-top: 0.5rem;
        font-size: 0.85rem; color: {colors['text_muted']};
    }}
    
    .explain-box {{
        background: {colors['primary_light']}; border-left: 4px solid {colors['primary']};
        border-radius: 8px; padding: 1.25rem; margin: 0.75rem 0;
        font-size: 0.92rem; line-height: 1.65; color: {colors['text']};
        white-space: pre-wrap;
    }}
    
    .footer-note {{
        text-align: center; color: {colors['primary']} !important; 
        font-size: 0.85rem; font-weight: 500;
        margin-top: 3rem; padding: 1.5rem 0;
        border-top: 1px solid {colors['border']};
        letter-spacing: 0.02em;
    }}
    
    div[data-testid="stSidebar"] {{
        background: {colors['card_bg']}; border-right: 1px solid {colors['border']};
    }}
    
    @media (max-width: 768px) {{
        .app-header {{ padding: 0.85rem 1rem; gap: 0.6rem; }}
        .app-logo {{ width: 36px; height: 36px; font-size: 1.2rem; }}
        .app-title {{ font-size: 1.15rem; }}
        .app-subtitle {{ font-size: 0.68rem; }}
        .section-label {{ font-size: 0.65rem; margin-top: 1rem; }}
        .metric-card {{ padding: 0.9rem; }}
        .metric-label {{ font-size: 0.65rem; }}
        .metric-value {{ font-size: 1.2rem !important; }}
        .result-banner {{ padding: 1rem 1.15rem; }}
        .result-title {{ font-size: 1.15rem !important; }}
        .result-detail {{ font-size: 0.82rem; }}
        .detected-type {{ font-size: 0.8rem; }}
        .patient-info {{ font-size: 0.75rem; }}
        .explain-box {{ padding: 0.9rem; font-size: 0.85rem; }}
        .footer-note {{ font-size: 0.72rem; margin-top: 2rem; }}
    }}
    
    @media (max-width: 480px) {{
        .app-title {{ font-size: 1rem; }}
        .app-subtitle {{ font-size: 0.62rem; }}
        .app-logo {{ width: 32px; height: 32px; font-size: 1rem; }}
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="app-header">
    <div class="app-logo">◉</div>
    <div>
        <h1 class="app-title">RetinaScan</h1>
        <p class="app-subtitle">{t['app_subtitle']}</p>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("---")
    st.markdown(f'<div class="section-label">{t["patient_registration"]}</div>', unsafe_allow_html=True)

    if "patient_id" not in st.session_state:
        st.session_state["patient_id"] = ""

    with st.form("patient_form"):
        name = st.text_input(t["full_name"])
        age = st.number_input(t["age"], 1, 120, 55)
        gender = st.selectbox(t["gender"], [t["male"], t["female"], t["other"]])
        diabetes_type = st.selectbox(t["diabetes_type"], [t["type1"], t["type2"], t["gestational"]])
        submit = st.form_submit_button(t["register_patient"], use_container_width=True)

    if submit and name:
        try:
            resp = requests.post(f"{API_URL}/patients", json={
                "name": name, "age": age, "gender": gender, "diabetes_type": diabetes_type
            })
            if resp.status_code == 200:
                pid = resp.json()["patient_id"]
                st.session_state["patient_id"] = pid
                st.success(t["patient_registered"])
                st.caption(t["patient_id"])
                st.code(pid, language=None)
            else:
                st.error(f"Error: {resp.text}")
        except Exception as e:
            st.error(f"Backend not reachable: {e}")

st.markdown(f'<div class="section-label">{t["step1_label"]}</div>', unsafe_allow_html=True)

patient_id = st.text_input(
    t["patient_id_input"],
    value=st.session_state.get("patient_id", ""),
    placeholder=t["patient_id_placeholder"],
    label_visibility="collapsed"
)

if not patient_id:
    st.info(t["patient_id_info"])
    st.stop()

st.markdown(f'<div class="section-label">{t["step2_label"]}</div>', unsafe_allow_html=True)

method = st.radio(
    "Input method",
    [t["camera_capture"], t["upload_file"]],
    horizontal=True,
    label_visibility="collapsed"
)

image_data = None
source = None

if method == t["camera_capture"]:
    st.caption(t["camera_caption"])
    camera_image = st.camera_input(t["capture"], key="camera", label_visibility="collapsed")
    if camera_image is not None:
        image_data = camera_image.getvalue()
        source = "camera"
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(camera_image, caption=t["captured_image"], use_container_width=True)
        with col2:
            st.write("")
            st.write("")
            if st.button(t["retake"], use_container_width=True):
                st.session_state.pop("camera", None)
                st.rerun()
else:
    st.caption(t["upload_caption"])
    uploaded_file = st.file_uploader(
        t["choose_image"],
        type=["jpg", "jpeg", "png"],
        key="upload",
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        image_data = uploaded_file.getvalue()
        source = "upload"
        col1, col2 = st.columns([4, 1])
        with col1:
            st.image(uploaded_file, caption=t["selected_image"], use_container_width=True)
        with col2:
            st.write("")
            st.write("")
            if st.button(t["remove"], use_container_width=True):
                st.session_state.pop("upload", None)
                st.rerun()

st.markdown(f'<div class="section-label">{t["step3_label"]}</div>', unsafe_allow_html=True)

if image_data is None:
    st.info(t["please_upload"])
else:
    if st.button(t["run_diagnosis"], type="primary", use_container_width=True):
        with st.spinner(t["analyzing"]):
            files = {"file": ("retina.jpg", image_data, "image/jpeg")}
            data = {"patient_id": patient_id}
            try:
                resp = requests.post(f"{API_URL}/predict", files=files, data=data, timeout=120)
                if resp.status_code == 200:
                    st.session_state["result"] = resp.json()
                    st.session_state["source"] = source
                else:
                    st.error(f"Backend error: {resp.text}")
            except Exception as e:
                st.error(f"Backend not reachable: {e}")

if "result" in st.session_state:
    r = st.session_state["result"]
    src = st.session_state.get("source", "unknown")
    grade = r["dr_grade"]
    conf = r["confidence"]
    risk = r["risk_level"]

    st.markdown("---")
    st.markdown(f'<div class="section-label">{t["diagnostic_report"]}</div>', unsafe_allow_html=True)

    src_label = t["camera_source"] if src == "camera" else t["upload_source"]
    st.caption(f"{t['source']}: {src_label}  ·  {t['model']}: ResNet50  ·  {t['explainability']}: Grad-CAM")

    not_retinal = r.get("not_retinal", False)

    if not_retinal:
        st.markdown(f"""
        <div class="result-banner result-warning">
            <div class="result-label">{t['invalid_image']}</div>
            <h2 class="result-title">{t['not_suitable']}</h2>
            <div class="result-detail">{t['not_suitable_detail']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        detailed_grade = r.get("detailed_grade", grade)

        if grade == "No DR":
            cls, label, title, detail = ("result-success", t["grade_normal"], t["grade_normal_title"], t["grade_normal_detail"])
        elif grade == "Mild":
            cls, label, title, detail = ("result-success", t["grade_mild"], t["grade_mild_title"], t["grade_mild_detail"])
        elif grade == "Moderate":
            cls, label, title, detail = ("result-warning", t["grade_moderate"], t["grade_moderate_title"], t["grade_moderate_detail"])
        elif grade == "Severe":
            cls, label, title, detail = ("result-danger", t["grade_severe"], t["grade_severe_title"], t["grade_severe_detail"])
        else:
            cls, label, title, detail = ("result-danger", t["grade_proliferative"], t["grade_proliferative_title"], t["grade_proliferative_detail"])

        p_name = r.get("patient_name", "")
        p_age = r.get("patient_age", "")
        p_gender = r.get("patient_gender", "")
        p_diabetes = r.get("patient_diabetes_type", "")

        st.markdown(f"""
        <div class="result-banner {cls}">
            <div class="result-label">{label}</div>
            <h2 class="result-title">{title}</h2>
            <div class="result-detail">{detail}</div>
            <div class="detected-type">
                <b>{t['detected_type']}:</b> {detailed_grade}
            </div>
            <div class="patient-info">
                <b>{t['patient_info']}:</b> {p_name} &nbsp;·&nbsp; {p_age} yrs &nbsp;·&nbsp; {p_gender} &nbsp;·&nbsp; <b>{t['diabetes_label']}:</b> {p_diabetes}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{t["dr_grade"]}</div><div class="metric-value">{grade}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{t["confidence"]}</div><div class="metric-value">{conf*100:.1f}%</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{t["risk_level"]}</div><div class="metric-value">{risk}</div></div>', unsafe_allow_html=True)

        st.write("")

        if r.get("referral_needed"):
            st.error(t["referral_recommended"])
        else:
            st.success(t["no_referral"])

        if r.get("gradcam_url"):
            st.markdown(f'<div class="section-label">{t["gradcam_section"]}</div>', unsafe_allow_html=True)
            st.caption(t["gradcam_caption"])
            st.image(f"{API_URL}{r['gradcam_url']}", use_container_width=True)

        explanations = r.get("explanations", {})
        lang_key = "English"
        if "Hindi" in st.session_state.language:
            lang_key = "Hindi"
        elif "Odia" in st.session_state.language:
            lang_key = "Odia"
        elif "Bengali" in st.session_state.language:
            lang_key = "Bengali"

        explanation_text = explanations.get(lang_key, explanations.get("English", ""))

        if explanation_text:
            st.markdown(f'<div class="section-label">{t["explanation_section"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="explain-box">{explanation_text}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-label">{t["probabilities_section"]}</div>', unsafe_allow_html=True)
        for label_name, score in r["all_scores"].items():
            st.progress(score, text=f"{label_name} — {score*100:.1f}%")

        if grade == "No DR":
            st.markdown("---")
            st.markdown(f'<div class="section-label">{t["clinical_note"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="explain-box">{t["no_dr_note"]}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="footer-note">{t["footer"]}</div>', unsafe_allow_html=True)