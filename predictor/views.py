import pickle

from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import StartupIdea

# Load AI Model
model = pickle.load(open("../model.pkl", "rb"))
vectorizer = pickle.load(open("../vectorizer.pkl", "rb"))


# Home Page
def home(request):

    return render(request, "index.html")


# Prediction Function
def predict(request):

    if request.method == "POST":

        idea = request.POST['idea']

        # Convert text
        vec = vectorizer.transform([idea])

        # Predict
        result = model.predict(vec)

        # Success score
        prob = model.predict_proba(vec)[0][1] * 100

        # Convert idea to lowercase
        idea_lower = idea.lower()

        # Default scores
        demand = 50
        competition = 50
        feasibility = 50
        innovation = 50
        investor = 50
        scalability = 50

        # AI Industry
        if "ai" in idea_lower:

            demand += 35
            innovation += 40
            investor += 35
            scalability += 30
            competition += 25
            feasibility += 20

        # Healthcare
        if "health" in idea_lower or "medical" in idea_lower:

            demand += 30
            investor += 30
            feasibility += 25
            scalability += 20

        # FinTech
        if "finance" in idea_lower or "payment" in idea_lower:

            demand += 28
            investor += 35
            competition += 30
            scalability += 25

        # Agriculture
        if "farm" in idea_lower or "agriculture" in idea_lower:

            demand += 25
            feasibility += 30
            innovation += 20

        # Cybersecurity
        if "cybersecurity" in idea_lower:

            demand += 30
            investor += 28
            competition += 22

        # Education
        if "education" in idea_lower or "learning" in idea_lower:

            scalability += 25
            demand += 20
            feasibility += 20

        # Old businesses
        if "dvd" in idea_lower or "pager" in idea_lower or "fax" in idea_lower:

            demand -= 35
            investor -= 30
            scalability -= 25
            innovation -= 20

        # Limit values
        demand = max(10, min(demand, 100))
        competition = max(10, min(competition, 100))
        feasibility = max(10, min(feasibility, 100))
        innovation = max(10, min(innovation, 100))
        investor = max(10, min(investor, 100))
        scalability = max(10, min(scalability, 100))

        # Suggestions list
        suggestions = []

        # Prediction result
        if result[0] == 1:

            output = "✅ Good Startup Idea"

            suggestions.append(
                "✔ Startup idea shows positive growth potential"
            )

        else:

            output = "❌ Needs Improvement"

            suggestions.append(
                "⚠ Startup idea may require more innovation"
            )

        # Demand suggestions
        if demand > 85:

            suggestions.append(
                "📈 Market demand is extremely strong"
            )

        elif demand > 70:

            suggestions.append(
                "✔ Market demand looks promising"
            )

        else:

            suggestions.append(
                "⚠ Market demand appears moderate"
            )

        # Competition suggestions
        if competition > 70:

            suggestions.append(
                "⚠ Competition is very high"
            )

        elif competition > 50:

            suggestions.append(
                "⚠ Moderate competition detected"
            )

        else:

            suggestions.append(
                "✔ Competition level is manageable"
            )

        # Feasibility suggestions
        if feasibility > 85:

            suggestions.append(
                "✔ Feasibility is excellent"
            )

        elif feasibility > 70:

            suggestions.append(
                "✔ Business implementation looks practical"
            )

        else:

            suggestions.append(
                "⚠ Feasibility may require improvement"
            )

        # Market trends
        if "ai" in idea_lower:

            suggestions.append(
                "🔥 AI startups are rapidly growing worldwide"
            )

        if "health" in idea_lower or "medical" in idea_lower:

            suggestions.append(
                "🏥 Healthcare technology demand is increasing"
            )

        if "finance" in idea_lower or "payment" in idea_lower:

            suggestions.append(
                "💰 FinTech sector attracts strong investments"
            )

        if "farm" in idea_lower or "agriculture" in idea_lower:

            suggestions.append(
                "🌱 AgriTech startups are trending globally"
            )

        # Save in database
        StartupIdea.objects.create(

            user=request.user,

            idea=idea,
            result=output,
            score=round(prob, 2),

            demand=demand,
            competition=competition,
            feasibility=feasibility

        )

        return render(request, "index.html", {

            "result": output,
            "score": round(prob, 2),

            "demand": demand,
            "competition": competition,
            "feasibility": feasibility,

            "innovation": innovation,
            "investor": investor,
            "scalability": scalability,

            "suggestions": suggestions

        })

    return render(request, "index.html")


# Register
def register_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('/login/')

    return render(request, "register.html")


# Login
def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/')

    return render(request, "login.html")


# Logout
def logout_user(request):

    logout(request)

    return redirect('/login/')


# Dashboard
def dashboard(request):

    ideas = StartupIdea.objects.all()

    total_ideas = ideas.count()

    avg_score = 0

    if total_ideas > 0:

        avg_score = sum(
            idea.score for idea in ideas
        ) / total_ideas

    good_ideas = ideas.filter(
        result__contains="Good"
    ).count()

    bad_ideas = ideas.filter(
        result__contains="Needs"
    ).count()

    context = {

        "total_ideas": total_ideas,
        "avg_score": round(avg_score, 2),

        "good_ideas": good_ideas,
        "bad_ideas": bad_ideas,

    }

    return render(
        request,
        "dashboard.html",
        context
    )


# History
def history(request):

    ideas = StartupIdea.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        "history.html",
        {"ideas": ideas}
    )