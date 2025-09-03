# 📊 Data Analyst Agent

An API-powered **data analyst agent** that leverages **LLMs** to source, prepare, analyze, and visualize data.  
It accepts tasks and optional datasets via `POST` requests and returns structured answers, plots, and insights — all within **3 minutes**.

---

## 🔗 API Endpoint
POST https://app.example.com/api/

### 🛠️ Example Usage
```bash
curl "https://app.example.com/api/" \
  -F "questions.txt=@questions.txt" \
  -F "data.csv=@data.csv" \
  -F "image.png=@image.png"
```

## 📦 Features

- Accepts natural language analysis tasks with optional datasets (CSV, JSON, images).  
- Returns answers in requested format (JSON, text, plots).  
- Supports data scraping, statistical analysis, ML-based insights, and visualization.  
- Responds in < 3 minutes per task.  

## Example Task
Scrape the list of highest grossing films from Wikipedia.
1. How many $2bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5bn?
3. What's the correlation between Rank and Peak?
4. Draw a scatterplot of Rank vs Peak with a dotted red regression line.

## Output
``` json
[
  1,
  "Titanic",
  0.485782,
  "data:image/png;base64,iVBORw0KG..."
]
```

