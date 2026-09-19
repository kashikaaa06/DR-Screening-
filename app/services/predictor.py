import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from app.config import settings

LABELS = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
RISK_MAP = {
    "No DR": "Low",
    "Mild": "Low",
    "Moderate": "Moderate",
    "Severe": "High",
    "Proliferative DR": "High"
}

DETAILED_GRADES = {
    "No DR": "No Diabetic Retinopathy",
    "Mild": "Mild Non-Proliferative DR (NPDR)",
    "Moderate": "Moderate Non-Proliferative DR (NPDR)",
    "Severe": "Severe Non-Proliferative DR (NPDR)",
    "Proliferative DR": "Proliferative Diabetic Retinopathy (PDR)"
}

EXPLANATIONS = {
    "English": {
        "No DR": "The model predicts No Diabetic Retinopathy. The Grad-CAM highlights the retinal regions that contributed most to this decision.",
        "Mild": "The model predicts Mild Diabetic Retinopathy. The Grad-CAM highlights regions that influenced the model's decision and can be reviewed for early retinal abnormalities.",
        "Moderate": "The model predicts Moderate Diabetic Retinopathy. The Grad-CAM highlights retinal regions that contributed strongly to this prediction. These regions can be visually compared with DR-related features such as microaneurysms, hemorrhages and exudates.",
        "Severe": "The model predicts Severe Diabetic Retinopathy. The Grad-CAM highlights retinal regions that strongly influenced the prediction and can be reviewed for visible retinal abnormalities.",
        "Proliferative DR": "The model predicts Proliferative Diabetic Retinopathy. The Grad-CAM highlights regions that contributed strongly to the prediction and can be reviewed for abnormal retinal features and vessel changes.",
        "confidence_label": "Confidence",
        "disclaimer": "Grad-CAM indicates model attention and does not independently confirm a specific lesion."
    },
    "Hindi": {
        "No DR": "मॉडल का अनुमान है कि कोई डायबिटिक रेटिनोपैथी नहीं है। Grad-CAM उन रेटिना क्षेत्रों को दर्शाता है जिन्होंने इस निर्णय में सबसे अधिक योगदान दिया।",
        "Mild": "मॉडल का अनुमान है कि हल्की डायबिटिक रेटिनोपैथी है। Grad-CAM उन क्षेत्रों को दर्शाता है जिन्होंने मॉडल के निर्णय को प्रभावित किया और प्रारंभिक रेटिना असामान्यताओं के लिए समीक्षा की जा सकती है।",
        "Moderate": "मॉडल का अनुमान है कि मध्यम डायबिटिक रेटिनोपैथी है। Grad-CAM उन रेटिना क्षेत्रों को दर्शाता है जिन्होंने इस भविष्यवाणी में मजबूत योगदान दिया। इन क्षेत्रों की तुलना माइक्रोएन्यूरिज्म, रक्तस्राव और एक्सयूडेट जैसी DR-संबंधित विशेषताओं से की जा सकती है।",
        "Severe": "मॉडल का अनुमान है कि गंभीर डायबिटिक रेटिनोपैथी है। Grad-CAM उन रेटिना क्षेत्रों को दर्शाता है जिन्होंने भविष्यवाणी को दृढ़ता से प्रभावित किया।",
        "Proliferative DR": "मॉडल का अनुमान है कि प्रोलिफरेटिव डायबिटिक रेटिनोपैथी है। Grad-CAM उन क्षेत्रों को दर्शाता है जिन्होंने भविष्यवाणी में मजबूत योगदान दिया।",
        "confidence_label": "विश्वास",
        "disclaimer": "Grad-CAM मॉडल के ध्यान को इंगित करता है और स्वतंत्र रूप से किसी विशिष्ट घाव की पुष्टि नहीं करता है।"
    },
    "Odia": {
        "No DR": "ମଡେଲ ଅନୁମାନ କରେ ଯେ କୌଣସି ଡାଇବେଟିକ ରେଟିନୋପାଥି ନାହିଁ। Grad-CAM ସେହି ରେଟିନା ଅଞ୍ଚଳଗୁଡ଼ିକୁ ଦର୍ଶାଏ ଯାହା ଏହି ନିଷ୍ପତ୍ତିରେ ସର୍ବାଧିକ ଅବଦାନ ଦେଇଛି।",
        "Mild": "ମଡେଲ ଅନୁମାନ କରେ ଯେ ମୃଦୁ ଡାଇବେଟିକ ରେଟିନୋପାଥି ଅଛି। Grad-CAM ସେହି ଅଞ୍ଚଳଗୁଡ଼ିକୁ ଦର୍ଶାଏ ଯାହା ମଡେଲର ନିଷ୍ପତ୍ତିକୁ ପ୍ରଭାବିତ କରିଛି।",
        "Moderate": "ମଡେଲ ଅନୁମାନ କରେ ଯେ ମଧ୍ୟମ ଡାଇବେଟିକ ରେଟିନୋପାଥି ଅଛି। Grad-CAM ସେହି ରେଟିନା ଅଞ୍ଚଳଗୁଡ଼ିକୁ ଦର୍ଶାଏ ଯାହା ଏହି ପୂର୍ବାନୁମାନରେ ଦୃଢ଼ ଅବଦାନ ଦେଇଛି। ଏହି ଅଞ୍ଚଳଗୁଡ଼ିକୁ ମାଇକ୍ରୋଆନିଉରିଜିମ, ରକ୍ତସ୍ରାବ ଏବଂ ଏକ୍ସୁଡେଟ ଭଳି DR-ସମ୍ପର୍କିତ ଲକ୍ଷଣ ସହିତ ତୁଳନା କରାଯାଇପାରେ।",
        "Severe": "ମଡେଲ ଅନୁମାନ କରେ ଯେ ଗମ୍ଭୀର ଡାଇବେଟିକ ରେଟିନୋପାଥି ଅଛି। Grad-CAM ସେହି ରେଟିନା ଅଞ୍ଚଳଗୁଡ଼ିକୁ ଦର୍ଶାଏ ଯାହା ପୂର୍ବାନୁମାନକୁ ଦୃଢ଼ ଭାବରେ ପ୍ରଭାବିତ କରିଛି।",
        "Proliferative DR": "ମଡେଲ ଅନୁମାନ କରେ ଯେ ପ୍ରୋଲିଫେରେଟିଭ ଡାଇବେଟିକ ରେଟିନୋପାଥି ଅଛି। Grad-CAM ସେହି ଅଞ୍ଚଳଗୁଡ଼ିକୁ ଦର୍ଶାଏ ଯାହା ପୂର୍ବାନୁମାନରେ ଦୃଢ଼ ଅବଦାନ ଦେଇଛି।",
        "confidence_label": "ଆତ୍ମବିଶ୍ୱାସ",
        "disclaimer": "Grad-CAM ମଡେଲର ଧ୍ୟାନକୁ ସୂଚାଏ ଏବଂ ସ୍ୱାଧୀନ ଭାବରେ ଏକ ନିର୍ଦ୍ଦିଷ୍ଟ କ୍ଷତକୁ ନିଶ୍ଚିତ କରେ ନାହିଁ।"
    },
    "Bengali": {
        "No DR": "মডেল অনুমান করে যে কোনো ডায়াবেটিক রেটিনোপ্যাথি নেই। Grad-CAM সেই রেটিনা অঞ্চলগুলি হাইলাইট করে যা এই সিদ্ধান্তে সবচেয়ে বেশি অবদান রেখেছে।",
        "Mild": "মডেল অনুমান করে যে হালকা ডায়াবেটিক রেটিনোপ্যাথি আছে। Grad-CAM সেই অঞ্চলগুলি হাইলাইট করে যা মডেলের সিদ্ধান্তকে প্রভাবিত করেছে।",
        "Moderate": "মডেল অনুমান করে যে মাঝারি ডায়াবেটিক রেটিনোপ্যাথি আছে। Grad-CAM সেই রেটিনা অঞ্চলগুলি হাইলাইট করে যা এই পূর্বাভাসে দৃঢ়ভাবে অবদান রেখেছে। এই অঞ্চলগুলিকে মাইক্রোঅ্যানিউরিজম, রক্তক্ষরণ এবং এক্সুডেটের মতো DR-সম্পর্কিত বৈশিষ্ট্যের সাথে তুলনা করা যেতে পারে।",
        "Severe": "মডেল অনুমান করে যে গুরুতর ডায়াবেটিক রেটিনোপ্যাথি আছে। Grad-CAM সেই রেটিনা অঞ্চলগুলি হাইলাইট করে যা পূর্বাভাসকে দৃঢ়ভাবে প্রভাবিত করেছে।",
        "Proliferative DR": "মডেল অনুমান করে যে প্রলিফারেটিভ ডায়াবেটিক রেটিনোপ্যাথি আছে। Grad-CAM সেই অঞ্চলগুলি হাইলাইট করে যা পূর্বাভাসে দৃঢ়ভাবে অবদান রেখেছে।",
        "confidence_label": "আত্মবিশ্বাস",
        "disclaimer": "Grad-CAM মডেলের মনোযোগ নির্দেশ করে এবং স্বাধীনভাবে একটি নির্দিষ্ট ক্ষত নিশ্চিত করে না।"
    }
}

NOT_RETINAL_EXPLANATION = {
    "English": "This image does not appear to be a valid retinal fundus image. Please capture or upload a proper retinal image using a fundus camera for accurate diagnosis.",
    "Hindi": "यह छवि एक वैध रेटिना फंडस छवि प्रतीत नहीं होती है। सटीक निदान के लिए कृपया फंडस कैमरा का उपयोग करके उचित रेटिना छवि कैप्चर या अपलोड करें।",
    "Odia": "ଏହି ଚିତ୍ରଟି ଏକ ବୈଧ ରେଟିନା ଫଣ୍ଡସ ଚିତ୍ର ପରି ଦେଖାଯାଉନାହିଁ। ସଠିକ ନିର୍ଣ୍ଣୟ ପାଇଁ ଦୟାକରି ଏକ ଫଣ୍ଡସ କ୍ୟାମେରା ବ୍ୟବହାର କରି ଉପଯୁକ୍ତ ରେଟିନା ଚିତ୍ର କ୍ୟାପଚର କିମ୍ବା ଅପଲୋଡ କରନ୍ତୁ।",
    "Bengali": "এই ছবিটি একটি বৈধ রেটিনা ফান্ডাস ছবি বলে মনে হচ্ছে না। সঠিক রোগ নির্ণয়ের জন্য অনুগ্রহ করে একটি ফান্ডাস ক্যামেরা ব্যবহার করে উপযুক্ত রেটিনা ছবি ক্যাপচার বা আপলোড করুন।"
}

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"Loading model from {settings.MODEL_PATH}...")
        _model = load_model(settings.MODEL_PATH)
        print("Model loaded")
    return _model

def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def make_gradcam_heatmap(img_array, model, last_conv_layer_name):
    base_model = model.get_layer("resnet50")
    grad_model = tf.keras.models.Model(
        inputs=base_model.input,
        outputs=[
            base_model.get_layer(last_conv_layer_name).output,
            base_model.output
        ]
    )
    with tf.GradientTape() as tape:
        conv_outputs, base_output = grad_model(img_array, training=False)
        x = base_output
        x = model.get_layer("global_average_pooling2d")(x)
        x = model.get_layer("dropout")(x, training=False)
        predictions = model.get_layer("dense")(x)
        predicted_class = tf.argmax(predictions[0])
        class_score = predictions[:, predicted_class]

    grads = tape.gradient(class_score, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(1, 2))
    conv_outputs = conv_outputs[0]
    pooled_grads = pooled_grads[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)
    heatmap /= tf.maximum(tf.reduce_max(heatmap), 1e-8)
    return heatmap.numpy()

def save_gradcam_overlay(image_path, heatmap, output_path):
    original_img = cv2.imread(image_path)
    original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

    heatmap_resized = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(original_img, 0.6, heatmap_color, 0.4, 0)
    cv2.imwrite(output_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    return output_path

def get_explanations_all_languages(stage, confidence):
    result = {}
    conf_str = f"{confidence * 100:.2f}%"
    for lang, exps in EXPLANATIONS.items():
        base = exps.get(stage, "Prediction generated.")
        conf_label = exps["confidence_label"]
        disclaimer = exps["disclaimer"]
        result[lang] = f"{base}\n\n{conf_label}: {conf_str}\n\n{disclaimer}"
    return result

def is_retinal_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ch, cw = h // 3, w // 3
        center = gray[ch:2*ch, cw:2*cw].mean()

        qh, qw = h // 4, w // 4
        corners = np.concatenate([
            gray[:qh, :qw].flatten(),
            gray[:qh, -qw:].flatten(),
            gray[-qh:, :qw].flatten(),
            gray[-qh:, -qw:].flatten()
        ])
        corner_mean = corners.mean()

        ratio = center / max(corner_mean, 1)
        aspect_ratio = w / h
        aspect_ok = 0.6 < aspect_ratio < 1.7

        b = int(min(h, w) * 0.05)
        border = np.concatenate([
            gray[:b, :].flatten(),
            gray[-b:, :].flatten(),
            gray[:, :b].flatten(),
            gray[:, -b:].flatten()
        ])
        border_mean = border.mean()

        is_retinal = (
            ratio > 1.5 and
            center > 50 and
            aspect_ok and
            border_mean < center * 0.8
        )

        print(f"[Quality Check] center={center:.1f}, corners={corner_mean:.1f}, ratio={ratio:.2f}, border={border_mean:.1f}, aspect={aspect_ratio:.2f} -> is_retinal={is_retinal}")

        return is_retinal
    except Exception as e:
        print(f"[Quality Check] Error: {e}")
        return False

def predict_dr(image_path):
    model = get_model()

    if not is_retinal_image(image_path):
        return {
            "grade": "Not Suitable",
            "detailed_grade": "Not Suitable for Diagnosis",
            "grade_code": -1,
            "confidence": 0.0,
            "risk_level": "Unknown",
            "all_scores": {label: 0.0 for label in LABELS},
            "gradcam_filename": None,
            "explanations": NOT_RETINAL_EXPLANATION,
            "not_retinal": True
        }

    img_array = preprocess_image(image_path)
    preds = model.predict(img_array, verbose=0)[0]
    class_idx = int(np.argmax(preds))
    confidence = float(preds[class_idx])
    grade = LABELS[class_idx]
    risk = RISK_MAP[grade]
    detailed_grade = DETAILED_GRADES.get(grade, grade)

    gradcam_filename = None
    try:
        heatmap = make_gradcam_heatmap(img_array, model, settings.LAST_CONV_LAYER)
        base = os.path.splitext(os.path.basename(image_path))[0]
        gradcam_filename = f"{base}_gradcam.jpg"
        gradcam_path = os.path.join(settings.GRADCAM_DIR, gradcam_filename)
        os.makedirs(settings.GRADCAM_DIR, exist_ok=True)
        save_gradcam_overlay(image_path, heatmap, gradcam_path)
    except Exception as e:
        print(f"Grad-CAM failed: {e}")
        gradcam_filename = None

    return {
        "grade": grade,
        "detailed_grade": detailed_grade,
        "grade_code": class_idx,
        "confidence": round(confidence, 4),
        "risk_level": risk,
        "all_scores": {LABELS[i]: round(float(preds[i]), 4) for i in range(5)},
        "gradcam_filename": gradcam_filename,
        "explanations": get_explanations_all_languages(grade, confidence),
        "not_retinal": False
    }