# Product Requirements Document (PRD)

## AI-Powered Workout Routine Organizer API

### 1. Introduction

This project aims to revolutionize workout routine management by using Artificial Intelligence to convert unstructured text descriptions into visually appealing, structured Google Slides presentations. The system interacts with users via a Telegram Bot, providing a seamless experience for trainers and athletes.

### 2. Objectives

- **Automate Routine Creation:** Eliminate manual formatting of workout plans.
- **AI Integration:** Use Google Gemini to intelligently parse natural language into structured workout data.
- **User Convenience:** Enable interaction through a familiar interface (Telegram).
- **Professional Output:** Generate high-quality Google Slides presentations automatically.

### 3. Architecture & Quality Assurance

The project is currently undergoing a refactor towards Clean Architecture. This establishes a strict separation of concerns and specific quality standards for different parts of the codebase.

#### 3.1. Legacy Code

- **Scope:** Existing code, primarily located in folders not adhering to the `src/` modular structure (e.g., `func/`, `legacy/`).
- **Testing Requirement:** **NO TESTING REQUIRED.** This code is considered stable but deprecated and will eventually be phased out.

#### 3.2. Clean Architecture (New Implementation)

- **Scope:** All new code located within the `src/` directory.
- **Structure:**
  - `domain/`: Entities and business logic.
  - `application/`: Use cases and application logic.
  - `infrastructure/`: External implementations (DB, APIs, etc.).
  - `api/`: Controllers and routes.
- **Testing Requirement:** **MUST BE TESTED.**
  - **Framework:** `pytest`
  - **Coverage:** Unit tests for domain logic and integration tests for API endpoints.
  - **Standards:** All new features must include corresponding tests to ensure reliability and maintainability.

### 4. Functional Requirements

#### 4.1. Telegram Integration

- **Webhook:** The system must expose a webhook endpoint to receive messages from Telegram.
- **Interaction:** Users send a text message describing a workout routine.
- **Response:** The bot replies with a link to the generated Google Slides presentation.

#### 4.2. AI Routine Parsing

- **Input:** Unstructured text from the Telegram message.
- **Processing:** Google Gemini (via Langchain) analyzes the text.
- **Output:** Structured JSON data representing the workout routine (exercises, sets, reps, rest headers).

#### 4.3. Google Slides Generation

- **Template:** Use a predefined Google Slides template.
- **Generation:** Create a new presentation for each routine.
- **Content:**
  - One slide per exercise.
  - Fill placeholders with data parsed by the AI.
- **Delivery:** Return a shareable link to the user.

### 5. Technical Requirements

- **Language:** Python 3.11+
- **Framework:** FastAPI (hosting the API and Webhook).
- **Dependency Management:** `requirements.txt`.
- **Environment config:** Pydantic settings reading from `.env`.
- **Containerization:** Docker support for easy deployment.
- **External APIs:**
  - Telegram Bot API
  - Google Generative AI (Gemini)
  - Google Slides API

### 6. Non-Functional Requirements

- **Performance:** Fast response time for the webhook acknowledgement.
- **Scalability:** Capable of handling concurrent requests via async processing.
- **Maintainability:** Adherence to Clean Architecture principles in `src/`.
