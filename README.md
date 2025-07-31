# TitleGenerator
This project generates news-style headlines from long articles using a transformer-based model fine-tuned for summarization. Built with Hugging Face Transformers and deployed via Gradio, it's lightweight, fast, and easy to use.


## Model

We use the publicly available fine-tuned model:

- https://huggingface.co/Michau/t5-base-en-generate-headline

Based on T5-base, trained specifically for generating English news-style headlines.

## Features

- Accepts long-form news articles
- Generates concise, relevant headlines
- Supports CPU and GPU
- Clean Gradio interface
- Deployable to Hugging Face Spaces or Docker

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/headline-generator.git
cd blog_title_project
```

### 2. Run the Server

```bash
python manage.py runserver
```

### 3. Test it
max_suggestion is 3 (default) and can go upto 5
```bash
curl -X POST http://localhost:8000/api/blog/suggest-titles/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Japan’s history spans thousands of years, deeply influencing its cultural heritage and shaping Japanese societies. One of the most iconic aspects of Japan’s culture and tradition is the traditional tea ceremony, or chanoyu. This practice reflects Japanese principles such as harmony, respect, purity, and tranquility. The ritualistic preparation and consumption of matcha, a powdered green tea, transcend mere tea drinking; they encompass an appreciation for the aesthetics and mindfulness embedded in every step of the process",
    "max_suggestions": 3
  }'
```


