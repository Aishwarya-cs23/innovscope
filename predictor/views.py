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


        # Predict using ML model
        result = model.predict(vec)


        # Convert idea to lowercase
        idea_lower = idea.lower()


        # Default business scores
        demand = 50
        competition = 50
        feasibility = 50
        innovation = 50
        investor = 50
        scalability = 50


        # AI Industry
        if any(word in idea_lower for word in [
            "ai", "artificial intelligence", "chatbot"
        ]):

            demand += 35
            innovation += 40
            investor += 35
            scalability += 30
            competition += 25
            feasibility += 20

        # Healthcare
        if any(word in idea_lower for word in [
            "health", "medical", "doctor", "hospital", "medicine"
        ]):
            demand += 30
            investor += 30
            feasibility += 25
            scalability += 20

        # FinTech
        if any(word in idea_lower for word in [
            "finance", "payment", "banking", "fintech", "money"
        ]):
            demand += 28
            investor += 35
            competition += 30
            scalability += 25

        # Agriculture
        if any(word in idea_lower for word in [
            "farm", "farming", "agriculture", "agritech"
        ]):
            demand += 25
            feasibility += 30
            innovation += 20

        # Cybersecurity
        if any(word in idea_lower for word in [
            "cybersecurity", "security", "cyber"
        ]):
            demand += 30
            investor += 28
            competition += 22

        # Education
        if any(word in idea_lower for word in [
            "education", "learning", "e learning",
            "elearning", "school", "student", "course"
        ]):
            scalability += 25
            demand += 20
            feasibility += 20

        # Food Delivery
        if any(word in idea_lower for word in [
            "food", "restaurant", "delivery", "kitchen"
        ]):
            demand += 25
            scalability += 20
            investor += 15

        # Electric Vehicles
        if any(word in idea_lower for word in [
            "electric vehicle", "ev", "charging"
        ]):
            demand += 35
            investor += 35
            innovation += 30
            scalability += 30

        # Old businesses
        if any(word in idea_lower for word in [
            "dvd", "pager", "fax", "floppy",
            "typewriter", "vcr", "cassette",
            "telephone booth"
        ]):
            demand -= 35
            investor -= 30
            scalability -= 25
            innovation -= 20

        # Women Safety
        if any(word in idea_lower for word in [
            "women", "safety", "security app"
        ]):
            demand += 25
            innovation += 20
            investor += 15

        # Renewable Energy
        if any(word in idea_lower for word in [
            "renewable", "solar", "wind", "energy"
        ]):
            demand += 35
            investor += 35
            innovation += 30
            scalability += 25

        # Fitness
        if any(word in idea_lower for word in [
            "fitness", "health tracking", "exercise"
        ]):
            demand += 25
            scalability += 20
            investor += 15

        # Job Portal
        if any(word in idea_lower for word in [
            "job", "recruitment", "career"
        ]):
            demand += 30
            scalability += 25
            investor += 20

        # Limit score values

        demand = min(max(demand, 10), 100)
        competition = min(max(competition, 10), 100)
        feasibility = min(max(feasibility, 10), 100)
        innovation = min(max(innovation, 10), 100)
        investor = min(max(investor, 10), 100)
        scalability = min(max(scalability, 10), 100)


        # Final startup success score calculation

        prob = (
            demand * 0.25 +
            feasibility * 0.20 +
            innovation * 0.20 +
            investor * 0.15 +
            scalability * 0.15 +
            (100 - competition) * 0.05
        )

        prob = round(prob, 1)

        # Suggestions list
        suggestions = []

                # Prediction result based on score

        if prob >= 75:

            output = "🚀 Excellent Startup Idea"

            suggestions.append(
                "🚀 Startup idea has very high growth potential"
            )

        elif prob >= 55:

            output = "✅ Good Startup Idea"

            suggestions.append(
                "✔ Startup idea shows positive growth potential"
            )

        else:

            output = "⚠️ Needs Improvement"

            suggestions.append(
                "⚠ Startup idea may require more innovation"
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

            user=request.user if request.user.is_authenticated else None,

            idea=idea,
            result=output,
            score=round(prob, 2),

            demand=demand,
            competition=competition,
            feasibility=feasibility

        )

        return render(request, "result.html", {

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

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "register.html",
                {
                    "error": "Username already exists"
                }
            )

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

    excellent_ideas = ideas.filter(
        result__contains="Excellent"
    ).count()

    good_ideas = ideas.filter(
        result__contains="Good"
    ).count()

    bad_ideas = ideas.filter(
        result__contains="Improvement"
    ).count()

    context = {

        "total_ideas": total_ideas,
        "avg_score": round(avg_score, 2),

        "excellent_ideas": excellent_ideas,
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