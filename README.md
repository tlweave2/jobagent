# Job Application Automation Agent

This repository contains a starter scaffold for building an autonomous agent that can search for jobs, navigate to job listings on LinkedIn (or other platforms), and automatically apply using "Easy Apply" style forms. The design is intentionally modular so you can swap out components, add more capabilities or integrate with other systems over time.

## Overview

The high‑level flow of this system is:

1. **Search for jobs.** A script builds a LinkedIn search URL from configurable presets (see `data/linkedin_search.yaml`) and loads the search results in a Playwright browser session.
2. **Identify Easy Apply jobs.** Job cards are parsed from the search results page and filtered to include only those that support the Easy Apply workflow.
3. **Open each job.** For each Easy Apply job the browser navigates to the job detail page and clicks the Easy Apply button. A modal form appears on top of the page.
4. **Interact with the form.** The current page snapshot (HTML, visible text and a list of clickable or fillable elements) is sent to a local language model which returns a list of actions such as filling text fields, uploading a resume or clicking "Next" or "Submit". These actions are executed via Playwright. The process repeats until the form is completed or fails.
5. **Recovery.** If the UI appears to be stuck (for example the DOM structure doesn’t change for a period of time) the fallback model can be invoked. This secondary model (e.g. Claude or GPT‑4 via API) attempts to recover from modal popups or unexpected states and suggests recovery actions.
6. **Log and repeat.** After each job is processed, details such as job title, company, status and timestamp are logged to a history file. The agent then proceeds to the next job in the search results.

The goal of this project is to demonstrate how local and cloud language models can be orchestrated with a browser automation tool to perform multi‑step interactions on dynamic websites.

## Directory Structure

```
jobagent/
├── agent/
│   ├── controller.py         # Main loop for a single Easy Apply flow
│   ├── search_controller.py  # Orchestrates job search and batch applications
│   ├── profile_agent.py      # Reads user_profile.yaml and provides answers to screening questions
│   ├── memory_manager.py     # Persists job application history and form mappings (optional)
│   └── recovery_agent.py     # Uses a cloud model to recover from stalled UI states
│
├── browser/
│   ├── playwright_driver.py  # Wraps Playwright interactions: load pages, click, fill, upload
│   └── dom_utils.py          # Helpers for parsing and monitoring DOM changes
│
├── models/
│   ├── local_llm.py          # Interface to the local language model (e.g. LLaMA via Ollama)
│   └── cloud_llm.py          # Interface to a fallback cloud model (e.g. Claude or GPT‑4)
│
├── data/
│   ├── user_profile.yaml     # Contains your personal info and default answers to screening questions
│   └── linkedin_search.yaml  # Specifies job search presets (title, location, filters)
│
├── search/
│   ├── linkedin_url_builder.py  # Builds LinkedIn search URLs from presets
│   └── job_card_extractor.py    # Parses job cards from search results
│
├── scripts/
│   ├── apply_once.py         # CLI entry point to apply to a single job URL
│   └── apply_batch.py        # CLI entry point to search and apply to many jobs
│
├── langchain_agent.py       # Entry point for an optional LangChain‑based agent
├── .env.example             # Example environment variables for configuring AI models
└── requirements.txt         # Python dependencies
```

## Getting Started

1. **Install dependencies.** Install Python dependencies in your environment. You’ll need Python 3.10+ and Playwright. After cloning this repository, run:

```bash
pip install -r requirements.txt
python -m playwright install
```

2. **Configure your profile.** Edit `data/user_profile.yaml` with your name, email, resume path and any default answers to common screening questions.

3. **Set up search presets.** Edit `data/linkedin_search.yaml` to define what jobs you want to search for. For example you can specify job titles, locations, experience levels or whether to filter to remote roles.

4. **Run a single application.** Use `python scripts/apply_once.py --url <job_url>` to test the flow on one LinkedIn Easy Apply job. This will open a browser window, click the Easy Apply button, and step through the form using the local model.

5. **Run batch applications.** Use `python scripts/apply_batch.py` to search and apply to many jobs based on your presets. See the source code for details on how the batch script works.

The provided Python files are mostly placeholders with docstrings and function definitions. You’ll need to implement the logic for parsing pages, calling models and executing actions. This scaffolding provides a structure to start building a fully automated job application agent.