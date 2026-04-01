# Swipe2Eat LLM Recommendation Service

This is a Python Flask microservice that generates personalized food recommendations
using GPT-2 based on user likes, dislikes, spice level, and budget from AWS DB.

## How to run locally

1. Install dependencies:
```bash
pip install -r requirements.txt
# LLM Recommendation Process

## 📌 Overview
This module generates personalized food recommendations using a Large Language Model (LLM) by aggregating user preferences and contextual data.

The process is designed to be modular, scalable, and resilient with a fallback mechanism.

---

## 🔄 End-to-End Flow

1. **Data Collection**
   - User swipe data
   - Order history
   - Preferences (likes, dislikes, cuisines)

2. **Aggregation Layer**
   - Consolidates all user data into a unified profile
   - Handles missing/null values
   - Normalizes input for LLM processing

3. **LLM Processing**
   - Sends structured prompt to LLM (e.g., Mistral via Ollama)
   - Generates personalized recommendations

4. **Post-Processing**
   - Parses and formats LLM output
   - Filters invalid or unavailable items

5. **Fallback Mechanism**
   - If LLM fails or times out:
     - Return default or rule-based recommendations

---

## 🧠 Key Components

### Aggregator (`aggregator.py`)
- Combines multiple data sources into a single user profile
- Ensures consistency and completeness of input data

### LLM Service (`main.py`)
- Handles prompt construction
- Communicates with LLM model
- Returns recommendation results

### Utilities
- **db_handler.py** → Fetches user data from database  
- **gpu_check.py** → Verifies GPU availability for model optimization  

---

# ✅ Design Considerations

- **Modularity**: Clear separation between aggregation and LLM layers  
- **Scalability**: Can be deployed as an independent microservice  
- **Reliability**: Fallback ensures uninterrupted user experience  
- **Extensibility**: Easy to integrate new data sources or models  

---

## 🚀 Future Enhancements

- Add embedding-based recommendation refinement  
- Introduce caching for repeated queries  
- Implement monitoring and logging for LLM responses  
- Optimize prompts for better accuracy  

---

## ⚠️ Notes

- LLM responses may vary based on prompt design  
- Ensure proper validation before returning recommendations  

# LLM Recommendation Process

## 📌 Overview
This module generates personalized food recommendations using a Large Language Model (LLM) by aggregating user preferences and contextual data.

The system is designed with a modular architecture and includes a fallback mechanism to ensure reliability.

---

## 🔄 End-to-End Flow

1. **Data Collection**
   - User swipe data
   - Order history
   - Preferences (likes, dislikes, cuisines)

2. **Aggregation Layer**
   - Consolidates all user data into a unified profile
   - Handles null/missing values
   - Normalizes inputs for LLM

3. **LLM Processing**
   - Constructs prompt using aggregated data
   - Sends request to LLM (e.g., Mistral via Ollama)
   - Generates recommendations

4. **Post-Processing**
   - Parses LLM output
   - Filters unavailable or invalid items

5. **Fallback Mechanism**
   - Returns default recommendations if LLM fails

---

## 🧠 Example Prompt (Sent to LLM)
You are a food recommendation assistant.

User Preferences:

Favorite cuisines: ["Italian", "Indian"]
Likes: ["spicy", "noodles"]
Dislikes: ["seafood"]

Available Food:
["Chicken Biryani", "Margherita Pizza", "Pad Thai", "Grilled Fish"]

Task:
Recommend 3 food items for the user with short explanations.


---

## 🤖 Example LLM Response

Chicken Biryani – Matches preference for spicy Indian cuisine.
Margherita Pizza – Suitable for Italian cuisine preference.
Pad Thai – Contains noodles and aligns with user's likes."# Swipe2Eat_LLM_recommendation_service" 
