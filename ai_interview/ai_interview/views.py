import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import Resume, Interview, Result


# ============================================================
# FAKE AI ENGINE — Question Banks, Resume Analysis, Evaluation
# ============================================================

SKILLS_KEYWORDS = {
    "python": 10, "django": 10, "flask": 7, "sql": 8, "mysql": 6,
    "postgresql": 7, "html": 5, "css": 5, "javascript": 8,
    "react": 8, "angular": 7, "vue": 7, "node": 7, "express": 6,
    "git": 5, "github": 4, "docker": 7, "aws": 7, "azure": 6,
    "linux": 5, "machine learning": 10, "deep learning": 9,
    "data analysis": 8, "pandas": 7, "numpy": 6, "tensorflow": 8,
    "java": 9, "spring": 7, "c++": 7, "c#": 7, "php": 5,
    "mongodb": 6, "api": 6, "rest": 6, "agile": 4, "scrum": 4,
    "oop": 6, "data structures": 7, "algorithms": 7,
    "communication": 4, "teamwork": 3, "leadership": 4,
    "problem solving": 5, "critical thinking": 5,
}

QUESTION_BANKS = {
    "Python Developer": {
        "questions": [
            "What is Python and what are its key features?",
            "Explain the difference between a list and a tuple in Python.",
            "What is Object-Oriented Programming? Explain with Python examples.",
            "What is the difference between a shallow copy and a deep copy?",
            "Explain how Django handles a web request from URL to response.",
        ],
        "expected_keywords": [
            ["interpreted", "high-level", "dynamic", "easy", "readable", "general purpose"],
            ["mutable", "immutable", "ordered", "list", "tuple", "changeable", "brackets"],
            ["class", "object", "inheritance", "encapsulation", "polymorphism", "abstraction"],
            ["shallow", "deep", "copy", "nested", "reference", "independent", "module"],
            ["url", "view", "template", "model", "request", "response", "middleware", "routing"],
        ]
    },
    "Web Developer": {
        "questions": [
            "What is HTML and what role does it play in web development?",
            "Explain the CSS Box Model.",
            "What is JavaScript and why is it important for the web?",
            "What is the DOM and how do you manipulate it?",
            "Explain the concept of responsive web design.",
        ],
        "expected_keywords": [
            ["markup", "structure", "tags", "elements", "hypertext", "semantic", "page"],
            ["margin", "border", "padding", "content", "width", "height", "box"],
            ["scripting", "interactive", "dynamic", "browser", "client", "event", "function"],
            ["document", "object", "model", "tree", "elements", "manipulate", "node", "getelementby"],
            ["media queries", "flexible", "viewport", "mobile", "breakpoint", "grid", "fluid"],
        ]
    },
    "Data Analyst": {
        "questions": [
            "What is data analysis and why is it important?",
            "Explain the difference between structured and unstructured data.",
            "What is SQL and what are its main commands?",
            "What are the key Python libraries used in data analysis?",
            "Explain the process of data cleaning.",
        ],
        "expected_keywords": [
            ["inspect", "clean", "transform", "model", "insight", "decision", "pattern", "business"],
            ["structured", "rows", "columns", "database", "unstructured", "text", "images", "format"],
            ["query", "select", "insert", "update", "delete", "join", "table", "database", "where"],
            ["pandas", "numpy", "matplotlib", "seaborn", "scipy", "dataframe", "visualization"],
            ["missing", "duplicate", "outlier", "null", "inconsistent", "format", "transform", "quality"],
        ]
    },
    "Java Developer": {
        "questions": [
            "What is Java and what are its main features?",
            "Explain the difference between JDK, JRE, and JVM.",
            "What is inheritance in Java? Explain its types.",
            "What are Collections in Java?",
            "Explain exception handling in Java.",
        ],
        "expected_keywords": [
            ["platform independent", "object oriented", "robust", "secure", "portable", "jvm", "class"],
            ["jdk", "jre", "jvm", "development", "runtime", "virtual machine", "compiler", "bytecode"],
            ["extends", "single", "multilevel", "hierarchical", "parent", "child", "super", "class"],
            ["list", "set", "map", "arraylist", "hashmap", "interface", "iterator", "framework"],
            ["try", "catch", "finally", "throw", "throws", "exception", "error", "handle", "runtime"],
        ]
    },
    "Full Stack Developer": {
        "questions": [
            "What is Full Stack Development?",
            "Explain the MVC architecture pattern.",
            "What is a REST API and how does it work?",
            "Explain the difference between SQL and NoSQL databases.",
            "What is version control and why is Git important?",
        ],
        "expected_keywords": [
            ["frontend", "backend", "database", "full stack", "client", "server", "both", "end-to-end"],
            ["model", "view", "controller", "separation", "concerns", "pattern", "architecture", "logic"],
            ["representational", "state", "transfer", "http", "get", "post", "put", "delete", "endpoint", "json"],
            ["relational", "nosql", "table", "document", "schema", "flexible", "mongodb", "mysql", "structured"],
            ["git", "repository", "commit", "branch", "merge", "pull", "push", "collaboration", "history"],
        ]
    },
}

JOB_ROLES = list(QUESTION_BANKS.keys())

ROLE_SKILL_SETS = {
    "Python Developer": ["python", "django", "flask", "sql", "oop", "algorithms", "data structures", "rest", "api", "git"],
    "Web Developer": ["html", "css", "javascript", "react", "vue", "angular", "node", "express", "responsive", "api"],
    "Data Analyst": ["pandas", "numpy", "data analysis", "sql", "visualization", "statistics", "data cleaning", "python"],
    "Java Developer": ["java", "spring", "oop", "jvm", "collections", "multithreading", "exceptions", "api", "mvn"],
    "Full Stack Developer": ["frontend", "backend", "database", "api", "mvc", "git", "html", "css", "javascript", "node"],
}


def get_role_skill_keywords(role):
    role_list = ROLE_SKILL_SETS.get(role, [])
    return {skill: SKILLS_KEYWORDS.get(skill, 5) for skill in role_list}


def analyze_resume(text, role=None):
    """Rule-based resume matching: role-focused keyword scoring."""
    text_lower = text.lower()
    score = 0
    found_skills = []
    missing_skills = []
    suggestions = []

    role_ref = get_role_skill_keywords(role) if role else {}
    high_priority = set(role_ref.keys())

    # Generic skill match adds to score; role skills weighted higher.
    for skill, weight in SKILLS_KEYWORDS.items():
        if skill in text_lower:
            multiplier = 1.5 if skill in high_priority else 1.0
            score += weight * multiplier
            found_skills.append(skill.title())

    # Role-specific gaps
    for skill in sorted(high_priority):
        if skill not in text_lower:
            missing_skills.append(skill.title())

    score = min(round(score), 100)

    if score < 40:
        suggestions.append("Your resume needs more role-specific keywords and clear project experience.")
    if not any(lang in text_lower for lang in ["python", "java", "javascript"]):
        suggestions.append("Add a primary programming language such as Python, Java, or JavaScript.")
    if "git" not in text_lower:
        suggestions.append("Include version control workflow (Git/GitHub) in your resume.")
    if "project" not in text_lower and "experience" not in text_lower:
        suggestions.append("Add concrete project or work experience details.")
    if len(text_lower) < 250:
        suggestions.append("The document is short; add more detail on achievements and tools used.")

    if high_priority:
        if not missing_skills:
            suggestions.append(f"Great! Your resume looks aligned with {role} requirements.")
        else:
            suggestions.append(f"Role gaps detected for {role}: {', '.join(missing_skills[:5])}.")

    if not found_skills:
        suggestions.append("No keywords detected. Add technical details and role-relevant skills.")

    return {
        'score': score,
        'found_skills': found_skills,
        'missing_skills': missing_skills[:8],
        'suggestions': suggestions,
    }


def evaluate_answer(answer, expected_keywords):
    """Fake AI: Evaluate a single answer using keyword matching."""
    answer_lower = answer.lower().strip()
    score = 0
    matched = []

    if not answer_lower:
        return 0, "No answer provided. Try to write at least a few sentences.", []

    for keyword in expected_keywords:
        if keyword in answer_lower:
            score += 1
            matched.append(keyword)

    # Normalize: keywords matched out of total, scaled to 10
    keyword_score = min((score / max(len(expected_keywords), 1)) * 7, 7)

    # Length bonus
    length_bonus = 0
    if len(answer) > 100:
        length_bonus = 3
    elif len(answer) > 50:
        length_bonus = 2
    elif len(answer) > 20:
        length_bonus = 1

    total = min(round(keyword_score + length_bonus), 10)

    if total >= 8:
        feedback = "Excellent answer! You demonstrated strong understanding."
    elif total >= 6:
        feedback = "Good answer. Consider adding more specific details."
    elif total >= 4:
        feedback = "Fair answer. Try to include more technical terms and examples."
    else:
        feedback = "Needs improvement. Review the topic and try to use relevant keywords."

    return total, feedback, matched


# ============================================================
# VIEW FUNCTIONS
# ============================================================

def home(request):
    return render(request, 'website/index.html')


def about(request):
    return render(request, 'website/About.html')


def contact(request):
    return render(request, 'website/Contact.html')


@login_required(login_url='/users/login/')
def dashboard(request):
    user = request.user
    resumes = Resume.objects.filter(user=user).order_by('-uploaded_at')
    interviews = Interview.objects.filter(user=user).order_by('-created_at')
    results = Result.objects.filter(user=user).order_by('-created_at')

    latest_resume = resumes.first()
    latest_result = results.first()

    avg_score = 0
    if results.exists():
        avg_score = round(sum(r.total_score for r in results) / results.count())

    context = {
        'resume_count': resumes.count(),
        'interview_count': interviews.count(),
        'result_count': results.count(),
        'avg_score': avg_score,
        'latest_resume': latest_resume,
        'latest_result': latest_result,
        'recent_results': results[:5],
    }
    return render(request, 'website/dashboard.html', context)


@login_required(login_url='/users/login/')
def upload_resume(request):
    role = request.session.get('selected_role')
    if not role or role not in JOB_ROLES:
        return redirect('role')

    if request.method == 'POST':
        if 'resume' not in request.FILES:
            return render(request, 'website/upload.html', {'error': 'Please select a file.'})

        resume_file = request.FILES['resume']

        # Save file
        file_path = os.path.join(settings.MEDIA_ROOT, resume_file.name)
        with open(file_path, 'wb+') as dest:
            for chunk in resume_file.chunks():
                dest.write(chunk)

        # Extract text
        text_content = ""
        if resume_file.name.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        else:
            text_content = (
                f"[File: {resume_file.name}] — This is a local resume parser simulation. "
                "Use clear role-specific skills and project context."
            )

        # Analyze with role-aware matching
        analysis = analyze_resume(text_content, role=role)

        # Save to DB
        resume_obj = Resume.objects.create(
            user=request.user,
            resume_file=resume_file,
            resume_text=text_content,
            resume_score=analysis['score'],
        )
        resume_obj.set_suggestions(analysis['suggestions'])
        resume_obj.save()

        # Store resume ID in session for flow
        request.session['last_resume_id'] = resume_obj.id

        return redirect('analysis')

    return render(request, 'website/upload.html', {'role': role})


@login_required(login_url='/users/login/')
def analysis(request):
    role = request.session.get('selected_role')
    if not role or role not in JOB_ROLES:
        return redirect('role')

    resume_id = request.session.get('last_resume_id')
    if not resume_id:
        latest = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        if latest:
            resume_id = latest.id
        else:
            return redirect('upload')

    resume = Resume.objects.get(id=resume_id)
    analysis_data = analyze_resume(resume.resume_text, role=role)

    context = {
        'resume': resume,
        'role': role,
        'score': analysis_data['score'],
        'found_skills': analysis_data['found_skills'],
        'missing_skills': analysis_data['missing_skills'],
        'suggestions': analysis_data['suggestions'],
    }
    return render(request, 'website/analysis.html', context)


@login_required(login_url='/users/login/')
def select_role(request):
    if request.method == 'POST':
        role = request.POST.get('role', '')
        if role in JOB_ROLES:
            request.session['selected_role'] = role
            request.session.pop('last_resume_id', None)
            request.session.pop('last_interview_id', None)
            request.session.pop('last_result_id', None)
            return redirect('upload')
    return render(request, 'website/role.html', {'roles': JOB_ROLES})


@login_required(login_url='/users/login/')
def interview(request):
    role = request.session.get('selected_role')
    if not role or role not in QUESTION_BANKS:
        return redirect('role')

    # Ensure resume is uploaded before interview starts
    if 'last_resume_id' not in request.session:
        return redirect('upload')

    bank = QUESTION_BANKS[role]
    questions = bank['questions']
    expected_keywords = bank['expected_keywords']

    # Get current question index
    question_index = int(request.GET.get('q', 0))
    if question_index >= len(questions):
        question_index = 0

    # Initialize answers in session if not exists
    if 'interview_answers' not in request.session:
        request.session['interview_answers'] = {}

    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        # Save answer for current question
        request.session['interview_answers'][str(question_index)] = answer
        request.session.modified = True

        # Move to next question
        next_index = question_index + 1
        if next_index >= len(questions):
            # All questions answered, evaluate
            answers = []
            scores = []
            feedbacks = []
            matched_keywords = []

            for i in range(len(questions)):
                ans = request.session['interview_answers'].get(str(i), '')
                answers.append(ans)
                s, fb, matched = evaluate_answer(ans, expected_keywords[i])
                scores.append(s)
                feedbacks.append(fb)
                matched_keywords.append(matched)

            total_score = sum(scores)

            interview_obj = Interview.objects.create(
                user=request.user,
                job_role=role,
                questions=json.dumps(questions),
                answers=json.dumps(answers),
                scores=json.dumps(scores),
                feedback=json.dumps(feedbacks),
                total_score=total_score,
            )

            request.session['last_interview_id'] = interview_obj.id

            # Create Result
            resume_id = request.session.get('last_resume_id')
            resume_obj = None
            resume_score = 0
            if resume_id:
                try:
                    resume_obj = Resume.objects.get(id=resume_id)
                    resume_score = resume_obj.resume_score
                except Resume.DoesNotExist:
                    pass

            # Build strengths/weaknesses
            strengths = []
            weaknesses = []
            for i, s in enumerate(scores):
                if s >= 7:
                    strengths.append(f"Q{i+1}: Strong answer on '{questions[i][:40]}...'")
                elif s <= 4:
                    weaknesses.append(f"Q{i+1}: Needs work on '{questions[i][:40]}...'")

            if resume_score >= 70:
                strengths.append("Strong resume with good skill coverage")
            elif resume_score > 0:
                weaknesses.append("Resume could benefit from more technical skills")

            result_suggestions = []
            if total_score < 25:
                result_suggestions.append("Practice more interview questions for this role.")
            if resume_score < 50:
                result_suggestions.append("Improve your resume by adding more relevant skills.")
            result_suggestions.append("Keep practicing regularly to improve your scores!")

            result_obj = Result.objects.create(
                user=request.user,
                resume=resume_obj,
                interview=interview_obj,
                resume_score=resume_score,
                interview_score=total_score,
                total_score=resume_score + total_score,
                strengths=json.dumps(strengths),
                weaknesses=json.dumps(weaknesses),
                suggestions=json.dumps(result_suggestions),
            )
            request.session['last_result_id'] = result_obj.id

            # Clear session data
            del request.session['interview_answers']

            return redirect('result')
        else:
            return redirect(f'/interview/?q={next_index}')

    # Get current answer if exists
    current_answer = request.session['interview_answers'].get(str(question_index), '')

    context = {
        'role': role,
        'question': questions[question_index],
        'question_number': question_index + 1,
        'total_questions': len(questions),
        'current_answer': current_answer,
        'is_last': question_index == len(questions) - 1,
    }
    return render(request, 'website/interview.html', context)


@login_required(login_url='/users/login/')
def result(request):
    result_id = request.session.get('last_result_id')
    if not result_id:
        latest = Result.objects.filter(user=request.user).order_by('-created_at').first()
        if latest:
            result_id = latest.id
        else:
            return redirect('dashboard')

    result_obj = Result.objects.get(id=result_id)
    interview_obj = result_obj.interview

    qa_pairs = []
    if interview_obj:
        qs = interview_obj.get_questions()
        ans = interview_obj.get_answers()
        scs = interview_obj.get_scores()
        fbs = interview_obj.get_feedback()
        for i in range(len(qs)):
            qa_pairs.append({
                'number': i + 1,
                'question': qs[i] if i < len(qs) else '',
                'answer': ans[i] if i < len(ans) else '',
                'score': scs[i] if i < len(scs) else 0,
                'feedback': fbs[i] if i < len(fbs) else '',
            })

    context = {
        'result': result_obj,
        'interview': interview_obj,
        'qa_pairs': qa_pairs,
        'strengths': result_obj.get_strengths(),
        'weaknesses': result_obj.get_weaknesses(),
        'suggestions': result_obj.get_suggestions(),
        'score_percent': round(result_obj.total_score / 150 * 100) if result_obj.total_score else 0,
    }
    return render(request, 'website/result.html', context)


@login_required(login_url='/users/login/')
def progress(request):
    results = Result.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'results': results,
        'total_sessions': results.count(),
        'avg_score': round(sum(r.total_score for r in results) / results.count()) if results.exists() else 0,
        'best_score': max((r.total_score for r in results), default=0),
    }
    return render(request, 'website/progress.html', context)