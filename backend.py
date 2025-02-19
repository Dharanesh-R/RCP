from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from docx import Document

# Configure Google Generative AI
genai.configure(api_key="AIzaSyA4JzK--BBSuxvuJnj_MNJs_xvzfoY9PCw")

app = Flask(__name__)
CORS(app)

MAX_SPRINT_CAPACITY = 20

# Function to extract text from a Word document
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

# Function to generate tasks from a user story
def generate_tasks(user_story):
    model = genai.GenerativeModel("gemini-pro")
    try:
        response = model.generate_content(
            f"Break this user story into detailed development tasks:\n{user_story}"
        )
        tasks = response.text.split("\n")
        return [task for task in tasks if task.strip()]
    except Exception as e:
        print(f"Error generating tasks: {e}")
        return []

# Function to estimate effort in story points
def estimate_effort(task):
    return random.randint(1, 8)

# Function to categorize tasks as Frontend or Backend
def categorize_task(task):
    frontend_keywords = ['UI', 'UX', 'design', 'frontend', 'client-side']
    backend_keywords = ['API', 'database', 'backend', 'server-side', 'logic']
    is_frontend = any(keyword.lower() in task.lower() for keyword in frontend_keywords)
    is_backend = any(keyword.lower() in task.lower() for keyword in backend_keywords)
    return "Frontend & Backend" if is_frontend and is_backend else "Frontend" if is_frontend else "Backend" if is_backend else "General"

# Function to organize tasks into sprints
def organize_tasks_into_sprints(tasks):
    sprints = []
    current_sprint = []
    current_sprint_effort = 0
    start_date = datetime.today()
    
    for task in tasks:
        effort = task['Effort (Story Points)']
        if current_sprint_effort + effort > MAX_SPRINT_CAPACITY:
            sprints.append(current_sprint)
            current_sprint = []
            current_sprint_effort = 0
        task_due_date = start_date + timedelta(days=current_sprint_effort * 2)
        task['Due Date'] = task_due_date.strftime('%Y-%m-%d')
        current_sprint.append(task)
        current_sprint_effort += effort
    
    if current_sprint:
        sprints.append(current_sprint)
    return sprints

# Function to create a sprint plan PDF
def create_pdf(sprint_plan, filename="sprint_plan.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    y = height - 50
    sprint_number = 1
    for sprint in sprint_plan:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, f"Sprint {sprint_number}:")
        y -= 30
        c.setFont("Helvetica", 12)
        for task in sprint:
            c.drawString(30, y, f"Task: {task['Task']}")
            y -= 20
            c.drawString(30, y, f"Effort: {task['Effort (Story Points)']}")
            y -= 20
            c.drawString(30, y, f"Resources: {task['Resources']}")
            y -= 20
            c.drawString(30, y, f"Due Date: {task['Due Date']}")
            y -= 30
        sprint_number += 1
        y -= 20
    c.save()

# API endpoint to upload Word document and generate a sprint plan
@app.route('/upload_docx', methods=['POST'])
def upload_docx():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    file_path = "uploaded.docx"
    file.save(file_path)
    user_story = extract_text_from_docx(file_path)
    tasks = generate_tasks(user_story)
    sprint_plan = [{"Task": task.strip(), "Effort (Story Points)": estimate_effort(task), "Resources": categorize_task(task)} for task in tasks]
    sprints = organize_tasks_into_sprints(sprint_plan)
    return jsonify(sprints)

# API endpoint to generate a sprint plan and download as PDF
@app.route('/download_sprint_plan', methods=['POST'])
def download_sprint_plan():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    file_path = "uploaded.docx"
    file.save(file_path)
    user_story = extract_text_from_docx(file_path)
    tasks = generate_tasks(user_story)
    sprint_plan = [{"Task": task.strip(), "Effort (Story Points)": estimate_effort(task), "Resources": categorize_task(task)} for task in tasks]
    sprints = organize_tasks_into_sprints(sprint_plan)
    filename = "sprint_plan.pdf"
    create_pdf(sprints, filename)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
