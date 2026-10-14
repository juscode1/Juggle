# Juggle: Personalized Workload Management System

A to-do list that helps students organize tasks, track deadlines, manage their available time, and get personalized recommendations based on their work style and workload.

---

## Project Overview

Juggle helps individuals to manage their academic, personal, and work-related tasks by considering deadlines, estimated durations, priorities, available time, and individual work styles.

The system provides personalized recommendations to help users make better workload decisions and organize their tasks more effectively.

## Features

- **Task Management** — Create, organize, and manage tasks.
- **Work Style Assessment** — Identify work preferences to personalize recommendations.
- **Workload Analysis** — Analyze estimated task durations against available time.
- **Personalized Recommendations** — Suggest tasks based on work style, deadlines, priorities, and available time.
- **Workload Planning** — Review tasks and organize upcoming commitments.
- **Authentication** — Use Supabase for user authentication.
- **Activity Tracking** — Track completed tasks and display activity history.

## Technologies Used

| Technology | Purpose |
|:---|:---|
| Python | Core application logic |
| Streamlit | User interface |
| Supabase | Authentication and database services |
| Git | Version control |
| GitHub | Source code hosting |

## Project Structure

```text
Juggle/
├── app.py
├── supabase_client.py
├── models/
│   ├── Task.py
│   ├── TaskTypes.py
│   ├── user.py
│   └── workstyle.py
├── services/
│   └── workload_analyzer.py
├── ui/
│   ├── activity.py
│   ├── assessment.py
│   ├── home.py
│   ├── login.py
│   ├── recommendation.py
│   ├── styles.py
│   ├── tasks.py
│   └── workload.py
├── .streamlit/
│   └── config.toml
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/juscode1/Juggle.git
cd Juggle
```

### 2. Install Dependencies

Make sure Python is installed on your computer. Install the required packages using pip:

```bash
pip install streamlit supabase
```

Install any additional packages required by the application.

### 3. Configure Supabase

Create a `secrets.toml` file inside the `.streamlit/` directory.

Add your Supabase credentials:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-key"
```

Replace the placeholder values with your actual Supabase project credentials.

**Important:** Never upload your actual credentials or authentication session files to a public repository.

### 4. Run the Application

Run the following command from the project root:

```bash
streamlit run app.py
```

The application should open in your default web browser.

## How Juggle Works

1. **Assess Work Style** — The user completes an assessment to identify their work preferences.
2. **Manage Tasks** — The user adds tasks with deadlines, estimated durations, priorities, and categories.
3. **Analyze Workload** — The system evaluates the tasks against the user's available time.
4. **Receive Recommendations** — The system suggests a task based on the user's work style and current workload.
5. **Review Progress** — The user manages ongoing tasks and tracks completed work.

## Work Style-Based Recommendations

| Work Style | Recommendation Approach |
|:---|:---|
| Focused Planner | Prioritizes longer tasks first |
| Quick Starter | Prioritizes shorter tasks first |
| Deadline Driven | Prioritizes tasks with the nearest deadlines |

Available time and other task details are also considered when generating recommendations.

## Project Purpose

Juggle aims to help students make informed decisions about their workload by combining task management, workload analysis, and personalized recommendations in one application.

## Version Control

This project uses Git for tracking source code changes and GitHub for repository hosting.

Repository: [Juggle on GitHub](https://github.com/juscode1/Juggle)

## Security

- Keep `.streamlit/secrets.toml` out of version control.
- Do not commit `.env` files containing private credentials.
- Exclude saved authentication sessions from version control.
- Never publish private API keys or access tokens.

## License

No license has been specified for this project yet.
