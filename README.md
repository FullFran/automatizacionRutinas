# 💪 AI-Powered Workout Routine Organizer API

## 🚀 Why This Project Matters

In today's fast-paced world, staying organized with your workout routines is essential. Whether you're planning strength training, cardio sessions, or flexibility workouts, having a clear, structured routine can boost your productivity and consistency.

This project revolutionizes how you manage your training routines by using AI to convert unstructured text into a dynamic, visually appealing Google Slides presentation. With seamless Telegram integration, simply send your workout details, and receive a beautifully formatted presentation—ideal for sharing, tracking, or even consulting with a trainer or if you are a trainer, send the routine to your atlethes! 

## 🛠️ Technologies Used

Built with state-of-the-art tools, this project ensures efficiency, scalability, and ease-of-use:
- **FastAPI** – A high-performance web framework for building APIs.
- **Google Generative AI (Gemini) via Langchain** – Transforms unstructured workout texts into structured JSON.
- **Google Slides API** – Automatically creates and populates Google Slides presentations.
- **Telegram Bot API** – Enables real-time communication and interaction.
- **Docker** – Containerizes the application for lightweight, resource-efficient deployment.
- **Python & Pydantic** – Provides robust data validation and error handling.

## 🎯 Features

- **Seamless Telegram Integration**  
  Easily send your workout routines to the bot and receive a professionally formatted presentation in return.

- **AI-Driven Routine Parsing**  
  Leverage the power of Gemini AI to convert raw workout texts into structured, actionable data.

- **Automated Google Slides Creation**  
  Instantly transform your routines into dynamic presentations, with individual slides for each exercise.

- **Optimized Resource Usage**  
  Designed to run efficiently on resource-constrained servers without compromising performance.

- **Modular & Scalable Codebase**  
  A clean, modular structure that is easy to maintain and extend, making it perfect for integrating into larger fitness or productivity systems.

## 🏗️ Setup Instructions

### Prerequisites
- **Python 3.11+**
- **Docker** (optional, for containerized deployment)
- A **Google Cloud Project** with the Google Slides API enabled.
- A **Telegram Bot Token**.
- A **Gemini API Key** (from Google Generative AI).
- **Google Service Account Credentials** (JSON).

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_CREDENTIALS=your_google_service_account_json_content
WEBHOOK_URL=https://your-domain.com/webhook
```

> **Note:** For platforms like Railway, store your `GOOGLE_CREDENTIALS` as a secret and generate the JSON file at runtime.

### Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YourUsername/your-workout-bot.git
   cd your-workout-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API Locally**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🐳 Deploying with Docker

1. **Build the Docker Image**
   ```bash
   docker build -t workout-organizer-api .
   ```

2. **Run the Docker Container**
   ```bash
   docker run -p 8000:8000 workout-organizer-api
   ```
   Your API will be live at [http://localhost:8000](http://localhost:8000).

## 🔥 How It Works

1. **Send Your Routine via Telegram**  
   Message your workout routine to the bot.

2. **AI Parses and Structures the Routine**  
   Gemini AI processes the text and converts it into structured JSON.

3. **Create a Google Slides Presentation**  
   The API generates a Google Slides presentation, creating a dedicated slide for each exercise.

4. **Receive Your Presentation Link**  
   The bot sends back a link to your new, formatted presentation for easy sharing and access.

## 💡 Future Enhancements

- **Interactive Web UI:** Develop a user-friendly web interface for routine uploads and management.
- **Enhanced Error Handling:** Improve logging and user feedback for a smoother experience.
- **Additional Integrations:** Expand compatibility with other fitness and productivity platforms.

## 📩 Need Help?

If you have questions, encounter issues, or have suggestions, please open an issue on GitHub or contact me directly. Your feedback is invaluable!

---

If you like this project, please give it a star ⭐ and share it with your network. Let's revolutionize workout planning with AI!