import pickle
import requests

from django.shortcuts import render, redirect
from pytrends.request import TrendReq

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import StartupIdea

from .trends import get_google_trend

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

        startup_name = request.POST.get(
            'startup_name'
        )
        domain_extension = request.POST.get(
            "domain_extension"
        )

        request.session["domain_extension"] = domain_extension

        request.session["startup_name"] = startup_name

        industry = request.POST.get(
            'industry'
        )
        
        request.session["industry"] = industry

        target_customers = request.POST.get(
            'target_customers'
        )

        budget = request.POST.get("budget", "").strip()

        team_size = request.POST.get("team_size", "").strip()

        print("Budget from form =", budget)
        print("Team Size from form =", team_size)
        
        request.session["budget"] = budget
        request.session["team_size"] = team_size

        print("Saved Budget =", request.session["budget"])
        print("Saved Team =", request.session["team_size"])
        
        try:
            team_size = int(team_size)
        except:
            team_size = 1
                
        keyword = f"{startup_name} {industry}"

        google_trend_score = get_google_trend(startup_name)

        print("Google Trend Score:", google_trend_score)

        news_count, headlines = get_news_data(keyword)
        
        # -------------------------
        # Convert news count into score
        # -------------------------

        if news_count >= 1000:
            news_score = 100
        elif news_count >= 500:
            news_score = 80
        elif news_count >= 200:
            news_score = 60
        elif news_count >= 50:
            news_score = 40
        else:
            news_score = 20
        
        competition = get_competition_score(news_count)

        print("Competition Score:", competition)

        if news_count > 5000:

            market_interest = "High"

        elif news_count > 1000:

            market_interest = "Medium"

        else:

            market_interest = "Low"

        if google_trend_score >= 70:

            trend_status = "Growing"

        elif google_trend_score >= 40:

            trend_status = "Stable"

        else:

            trend_status = "Low Interest"
        
        idea_lower = idea.lower()

        # Use the selected industry from the dropdown
        industries = [industry]

        recommended_investors = get_investors(industries)

        roadmap_steps = generate_roadmap(
            industries
        )

        business_canvas = generate_business_model(
            industry
        )

        request.session[
            "business_canvas"
        ] = business_canvas
        

        funding_data = generate_funding_plan(
        industry,
        budget,
        team_size
        )

        request.session[
            "funding_data"
        ] = funding_data
        
        request.session["budget"] = budget
        request.session["team_size"] = team_size
        request.session["industry"] = industry
        
        print(request.session["industry"])
        print(request.session["budget"])
        print(request.session["team_size"])

        request.session["roadmap_steps"] = roadmap_steps

        government_schemes = get_government_schemes(industries)

        # Get trend scores
        google_trend_scores = []

        for industry in industries:

             score = get_market_trend(industry)

             google_trend_scores.append(score)
        if google_trend_scores:

            industry_google_trend_score = round(
                sum(google_trend_scores) / len(google_trend_scores)
            )

        else:

            industry_google_trend_score = google_trend_score

        # Default demand
        demand = industry_google_trend_score
            
        trend_scores = []

        for industry in industries:
            score = get_market_trend(industry)
            trend_scores.append(score)

        if trend_scores:
            industry_trend_score = round(sum(trend_scores) / len(trend_scores))
        else:
            industry_trend_score = 50

        # Calculate market demand
        demand = round(
            google_trend_score * 0.4 +
            news_score * 0.3 +
            industry_trend_score * 0.3
        )

        if google_trend_score >= 80:

             trend_status = "Rapidly Growing"

        elif google_trend_score >= 60:

            trend_status = "Growing"

        elif google_trend_score >= 40:

            trend_status = "Stable"

        else:

            trend_status = "Declining"


        # Vectorize idea
        vec = vectorizer.transform([idea])

        # Predict using ML model
        result = model.predict(vec)

        # ==========================================================
# IMPROVED STARTUP SCORING SYSTEM
# ==========================================================

        # Base scores
        feasibility = 55
        innovation = 55
        investor = 55
        scalability = 55

        # Competition comes from market/news analysis
        competition = min(max(competition, 10), 100)
        demand = min(max(demand, 10), 100)

        # ----------------------------------------------------------
        # 1. INDUSTRY BASED SCORING
        # ----------------------------------------------------------

        industry_scores = {

            "Healthcare": {
                "demand": 12,
                "innovation": 10,
                "feasibility": 8,
                "investor": 12,
                "scalability": 10
            },

            "Artificial Intelligence": {
                "demand": 15,
                "innovation": 18,
                "feasibility": 8,
                "investor": 15,
                "scalability": 18
            },

            "FinTech": {
                "demand": 14,
                "innovation": 12,
                "feasibility": 6,
                "investor": 16,
                "scalability": 15
            },

            "Agriculture": {
                "demand": 12,
                "innovation": 10,
                "feasibility": 10,
                "investor": 8,
                "scalability": 10
            },

            "Cybersecurity": {
                "demand": 14,
                "innovation": 14,
                "feasibility": 8,
                "investor": 13,
                "scalability": 15
            },

            "Education": {
                "demand": 12,
                "innovation": 10,
                "feasibility": 12,
                "investor": 9,
                "scalability": 12
            },

            "Legal services": {
                "demand": 10,
                "innovation": 12,
                "feasibility": 10,
                "investor": 8,
                "scalability": 10
            }
        }


        if industry in industry_scores:

            scores = industry_scores[industry]

            demand += scores["demand"]
            innovation += scores["innovation"]
            feasibility += scores["feasibility"]
            investor += scores["investor"]
            scalability += scores["scalability"]


        # ----------------------------------------------------------
        # 2. IDEA QUALITY ANALYSIS
        # ----------------------------------------------------------

        idea_lower = idea.lower()

        # Strong startup keywords
        strong_keywords = [
            "ai",
            "artificial intelligence",
            "automation",
            "smart",
            "platform",
            "analytics",
            "digital",
            "online",
            "personalized",
            "management",
            "tracking",
            "security",
            "prediction",
            "recommendation",
            "marketplace",
            "payment",
            "health",
            "finance",
            "education",
            "agriculture",
            "cybersecurity"
        ]

        keyword_matches = 0

        for word in strong_keywords:
            if word in idea_lower:
                keyword_matches += 1


        # Reward meaningful startup concepts
        innovation += min(keyword_matches * 3, 18)
        scalability += min(keyword_matches * 2, 12)


        # ----------------------------------------------------------
        # 3. PROBLEM-SOLVING KEYWORDS
        # ----------------------------------------------------------

        problem_keywords = [
            "reduce",
            "save",
            "manage",
            "solve",
            "prevent",
            "improve",
            "help",
            "monitor",
            "connect",
            "simplify",
            "track"
        ]

        problem_matches = 0

        for word in problem_keywords:
            if word in idea_lower:
                problem_matches += 1


        demand += min(problem_matches * 3, 15)
        feasibility += min(problem_matches * 2, 10)


        # ----------------------------------------------------------
        # 4. WEAK / GENERIC IDEA DETECTION
        # ----------------------------------------------------------

        weak_keywords = [
            "simple",
            "basic",
            "random",
            "funny",
            "just an app",
            "normal app",
            "another app",
            "nothing",
            "useless",
            "calculator",
            "clock"
        ]

        weak_matches = 0

        for word in weak_keywords:
            if word in idea_lower:
                weak_matches += 1


        if weak_matches > 0:

            innovation -= weak_matches * 8
            demand -= weak_matches * 5
            scalability -= weak_matches * 5


        # ----------------------------------------------------------
        # 5. IDEA LENGTH / DETAIL
        # ----------------------------------------------------------

        word_count = len(idea.split())

        if word_count >= 15:

            innovation += 8
            feasibility += 5
            demand += 5

        elif word_count >= 8:

            innovation += 5
            feasibility += 3

        elif word_count <= 3:

            innovation -= 8
            demand -= 5


        # ----------------------------------------------------------
        # 6. BUDGET SCORE
        # ----------------------------------------------------------

        try:
            budget_value = float(
                str(budget).replace(",", "").split()[0]
            )
        except:
            budget_value = 5


        if budget_value >= 50:

            feasibility += 20

        elif budget_value >= 20:

            feasibility += 15

        elif budget_value >= 10:

            feasibility += 10

        elif budget_value >= 5:

            feasibility += 5

        else:

            feasibility -= 5


        # ----------------------------------------------------------
        # 7. TEAM SIZE SCORE
        # ----------------------------------------------------------

        team_score = min(team_size * 20, 100)

        if team_size >= 8:

            feasibility += 10
            scalability += 10

        elif team_size >= 5:

            feasibility += 8
            scalability += 7

        elif team_size >= 3:

            feasibility += 5
            scalability += 5

        elif team_size <= 1:

            feasibility -= 5
            scalability -= 5


        # ----------------------------------------------------------
        # 8. MARKET TREND
        # ----------------------------------------------------------

        if google_trend_score >= 80:

            demand += 15
            investor += 10

        elif google_trend_score >= 60:

            demand += 10
            investor += 7

        elif google_trend_score >= 40:

            demand += 5

        else:

            demand -= 5
            investor -= 5


        # ----------------------------------------------------------
        # 9. NEWS / MARKET INTEREST
        # ----------------------------------------------------------

        if news_count >= 1000:

            demand += 12
            investor += 8

        elif news_count >= 500:

            demand += 8
            investor += 5

        elif news_count >= 200:

            demand += 5

        elif news_count < 50:

            demand -= 5


        # ----------------------------------------------------------
        # 10. COMPETITION EFFECT
        # ----------------------------------------------------------

        if competition >= 80:

            innovation -= 5
            investor -= 5
            scalability -= 5

        elif competition >= 60:

            innovation -= 3
            investor -= 2

        elif competition <= 30:

            demand += 5
            scalability += 5


        # ----------------------------------------------------------
        # 11. SPECIAL HIGH-POTENTIAL IDEAS
        # ----------------------------------------------------------

        # DailyExpense Pad type of idea
        if (
            ("expense" in idea_lower or
            "spending" in idea_lower or
            "budget" in idea_lower)
            and
            ("track" in idea_lower or
            "manage" in idea_lower or
            "finance" in idea_lower)
        ):

            demand += 12
            innovation += 10
            feasibility += 12
            scalability += 10
            investor += 8


        # AI-based solutions
        if "ai" in idea_lower or "artificial intelligence" in idea_lower:

            demand += 8
            innovation += 10
            scalability += 8
            investor += 8


        # Healthcare solutions
        if "health" in idea_lower or "medical" in idea_lower:

            demand += 8
            innovation += 7
            investor += 7


        # Finance solutions
        if (
            "finance" in idea_lower
            or "payment" in idea_lower
            or "banking" in idea_lower
        ):

            demand += 8
            investor += 8
            scalability += 7


        # ----------------------------------------------------------
        # 12. LIMIT ALL SCORES
        # ----------------------------------------------------------

        demand = min(max(demand, 10), 100)
        competition = min(max(competition, 10), 100)
        feasibility = min(max(feasibility, 10), 100)
        innovation = min(max(innovation, 10), 100)
        investor = min(max(investor, 10), 100)
        scalability = min(max(scalability, 10), 100)


        # ----------------------------------------------------------
        # 13. FINAL STARTUP SUCCESS SCORE
        # ----------------------------------------------------------

        prob = (

            demand * 0.25 +

            feasibility * 0.18 +

            innovation * 0.18 +

            investor * 0.14 +

            scalability * 0.12 +

            (100 - competition) * 0.05 +

            google_trend_score * 0.08

        )

        prob = round(prob, 1)
        # Suggestions list
        suggestions = []

        # ------------------------------------
# Score Explanation
# ------------------------------------

        innovation_score = innovation
        innovation_reason = ""

        if innovation >= 80:
            innovation_reason = "Your startup idea is highly innovative and different from existing solutions."
        elif innovation >= 60:
            innovation_reason = "Your idea contains some innovative features."
        else:
            innovation_reason = "Try adding more unique features to improve innovation."


        market_score = demand

        if demand >= 80:
           market_reason = (
                f"Google Trends score is {google_trend_score}/100,"
                f"indicating {trend_status.lower()} public interest."
            )
        elif demand >= 60:
            market_reason = "Market demand is moderate."
        else:
            market_reason = "Current market demand appears to be low."


        competition_score = competition

        if competition >= 70:
            competition_reason = "Competition is high in this market."
        elif competition >= 40:
            competition_reason = "Competition is moderate."
        else:
            competition_reason = "Competition is relatively low."


        budget_score = feasibility

        if feasibility >= 80:
            budget_reason = "Your available budget is sufficient."
        elif feasibility >= 60:
            budget_reason = "Budget is acceptable for an MVP."
        else:
            budget_reason = "Budget may not be enough to build the product."


        team_score = min(team_size * 20, 100)

        if team_score >= 80:
            team_reason = "Your team size is sufficient."
        elif team_score >= 60:
            team_reason = "Your team can build the initial version."
        else:
            team_reason = "Consider adding more team members."


        scalability_score = scalability

        if scalability >= 80:
            scalability_reason = "Your startup can scale quickly."
        elif scalability >= 60:
            scalability_reason = "Your startup has moderate growth potential."
        else:
            scalability_reason = "Scalability needs improvement."

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
        
        karnataka_schemes = {

        "Artificial Intelligence":[

        {
        "name":"Karnataka AI Mission",
        "description":"AI innovation and startup support.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Funding for AI startups.",
        "url":"https://elevate.karnataka.gov.in"
        },

        {
        "name":"K-Tech Innovation Hub",
        "description":"Technology incubation.",
        "url":"https://k-tech.karnataka.gov.in"
        }

        ],

        "Healthcare":[

        {
        "name":"BioNest Karnataka",
        "description":"Healthcare and biotech startup support.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Karnataka Biotechnology Policy",
        "description":"Funding for biotech startups.",
        "url":"https://kbiotechhub.org"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Healthcare innovation grants.",
        "url":"https://elevate.karnataka.gov.in"
        }

        ],

        "FinTech":[

        {
        "name":"Karnataka FinTech Policy",
        "description":"FinTech startup ecosystem.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Funding support for FinTech startups.",
        "url":"https://elevate.karnataka.gov.in"
        },

        {
        "name":"K-Tech",
        "description":"Innovation programs for finance startups.",
        "url":"https://k-tech.karnataka.gov.in"
        }

        ],

        "Agriculture":[

        {
        "name":"Raitha Mitra",
        "description":"Agriculture innovation schemes.",
        "url":"https://raitamitra.karnataka.gov.in"
        },

        {
        "name":"Krishi Bhagya",
        "description":"Water conservation support.",
        "url":"https://raitamitra.karnataka.gov.in"
        },

        {
        "name":"Raitha Samparka Kendra",
        "description":"Farmer advisory centres.",
        "url":"https://raitamitra.karnataka.gov.in"
        },

        {
        "name":"Organic Farming Mission",
        "description":"Organic farming promotion.",
        "url":"https://raitamitra.karnataka.gov.in"
        }

        ],

        "Cybersecurity":[

        {
        "name":"K-Tech Cyber Security Initiative",
        "description":"Cybersecurity startup ecosystem.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Funding for cybersecurity startups.",
        "url":"https://elevate.karnataka.gov.in"
        },

        {
        "name":"Karnataka Startup Policy",
        "description":"Technology startup support.",
        "url":"https://k-tech.karnataka.gov.in"
        }

        ],

        "Education":[

        {
        "name":"Karnataka Innovation Authority",
        "description":"EdTech innovation support.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Funding for EdTech startups.",
        "url":"https://elevate.karnataka.gov.in"
        },

        {
        "name":"K-Tech",
        "description":"Startup mentoring and incubation.",
        "url":"https://k-tech.karnataka.gov.in"
        }

        ],

        "Legal services":[

        {
        "name":"Karnataka Startup Policy",
        "description":"Support for LegalTech startups.",
        "url":"https://k-tech.karnataka.gov.in"
        },

        {
        "name":"Elevate Karnataka",
        "description":"Funding for LegalTech innovation.",
        "url":"https://elevate.karnataka.gov.in"
        }

        ]

        }
        
        india_schemes = {

        "Artificial Intelligence":[

        {
        "name":"INDIAai Mission",
        "description":"National AI Mission.",
        "url":"https://indiaai.gov.in"
        },

        {
        "name":"Startup India",
        "description":"Government startup recognition.",
        "url":"https://www.startupindia.gov.in"
        },

        {
        "name":"MeitY Startup Hub",
        "description":"Technology startup ecosystem.",
        "url":"https://meitystartuphub.in"
        },

        {
        "name":"Digital India",
        "description":"Digital innovation support.",
        "url":"https://digitalindia.gov.in"
        }

        ],

        "Healthcare":[

        {
        "name":"BIRAC",
        "description":"Healthcare startup funding.",
        "url":"https://birac.nic.in"
        },

        {
        "name":"Startup India",
        "description":"Startup support.",
        "url":"https://www.startupindia.gov.in"
        },

        {
        "name":"Ayush Startup Challenge",
        "description":"AYUSH healthcare innovation.",
        "url":"https://ayush.gov.in"
        }

        ],

        "FinTech":[

        {
        "name":"RBI Innovation Hub",
        "description":"FinTech innovation.",
        "url":"https://rbihub.in"
        },

        {
        "name":"Startup India",
        "description":"FinTech startup support.",
        "url":"https://www.startupindia.gov.in"
        },

        {
        "name":"Digital India",
        "description":"Digital finance ecosystem.",
        "url":"https://digitalindia.gov.in"
        }

        ],

        "Agriculture":[

        {
        "name":"PM-KISAN",
        "description":"Farmer income support.",
        "url":"https://pmkisan.gov.in"
        },

        {
        "name":"RKVY",
        "description":"Agriculture innovation.",
        "url":"https://rkvy.nic.in"
        },

        {
        "name":"Agriculture Infrastructure Fund",
        "description":"Infrastructure funding.",
        "url":"https://agriinfra.dac.gov.in"
        },

        {
        "name":"eNAM",
        "description":"National Agriculture Market.",
        "url":"https://enam.gov.in"
        }

        ],

        "Cybersecurity":[

        {
        "name":"Indian Computer Emergency Response Team (CERT-In)",
        "description":"Cybersecurity initiatives.",
        "url":"https://www.cert-in.org.in"
        },

        {
        "name":"MeitY Startup Hub",
        "description":"Cybersecurity startup support.",
        "url":"https://meitystartuphub.in"
        },

        {
        "name":"Startup India",
        "description":"Technology startup recognition.",
        "url":"https://www.startupindia.gov.in"
        }

        ],

        "Education":[

        {
        "name":"Digital India",
        "description":"Digital education initiatives.",
        "url":"https://digitalindia.gov.in"
        },

        {
        "name":"Startup India",
        "description":"EdTech startup ecosystem.",
        "url":"https://www.startupindia.gov.in"
        },

        {
        "name":"AICTE IDEA Lab",
        "description":"Innovation support in education.",
        "url":"https://www.aicte-india.org"
        }

        ],

        "Legal services":[

        {
        "name":"Startup India",
        "description":"Support for LegalTech startups.",
        "url":"https://www.startupindia.gov.in"
        },

        {
        "name":"Digital India",
        "description":"Digital governance and LegalTech.",
        "url":"https://digitalindia.gov.in"
        },

        {
        "name":"India Code",
        "description":"Official Indian legal portal.",
        "url":"https://www.indiacode.nic.in"
        }

        ]

        }
        
        return render(request, "result.html", {

        "result": output,
        "score": round(prob, 2),

        "demand": demand,
        "competition": competition,
        "feasibility": feasibility,

        "innovation": innovation,
        "investor": investor,
        "scalability": scalability,

        "suggestions": suggestions,

        "google_trend_score": google_trend_score,
        "trend_status": trend_status,

        "industries": industries,

        "news_count": news_count,

        "market_interest": market_interest,
        "headlines": headlines,

        "recommended_investors": recommended_investors,

        "government_schemes": government_schemes,

        # ADD THESE TWO LINES
        "karnataka_schemes": karnataka_schemes.get(industry, []),
        "india_schemes": india_schemes.get(industry, []),

        "startup_name": startup_name,

        "industry": industry,

        "target_customers": target_customers,

        "budget": budget,

        "team_size": team_size,

        "roadmap_steps": roadmap_steps,

        "innovation_score": innovation_score,
        "innovation_reason": innovation_reason,

        "market_score": market_score,
        "market_reason": market_reason,

        "competition_score": competition_score,
        "competition_reason": competition_reason,

        "budget_score": budget_score,
        "budget_reason": budget_reason,

        "team_score": team_score,
        "team_reason": team_reason,

        "scalability_score": scalability_score,
        "scalability_reason": scalability_reason,

    })

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

    ideas = StartupIdea.objects.all().order_by("-created_at")

    return render(
        request,
        "history.html",
        {
            "ideas": ideas
        }
    )

def get_market_trend(keyword):

    try:

        pytrends = TrendReq()

        kw_list = [keyword]

        pytrends.build_payload(
            kw_list,
            timeframe='today 12-m'
        )

        data = pytrends.interest_over_time()

        if not data.empty:

            return int(data[keyword].iloc[-1])

        return 50

    except:

        return 50
def get_google_trend_score(keyword):

    try:

        pytrends = TrendReq()

        pytrends.build_payload([keyword])

        data = pytrends.interest_over_time()

        if not data.empty:

            return int(data[keyword].mean())

    except:

        pass

    return 50
def get_news_data(keyword):

    api_key = "6f720920ffc9482e9eeb7ca57e2e3e84"

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={keyword}&sortBy=publishedAt&apiKey={api_key}"
    )

    try:

        response = requests.get(url)

        data = response.json()

        news_count = data["totalResults"]

        headlines = []

        for article in data["articles"][:5]:

            headlines.append(article["title"])

        return news_count, headlines

    except:

        return 0, []

def get_investors(industries):

    if "Healthcare" in industries:

        return [
            {
                "name": "Sequoia Capital",
                "reason": "Invests heavily in healthcare technology."
            },
            {
                "name": "General Catalyst",
                "reason": "Strong healthcare startup portfolio."
            },
            {
                "name": "Andreessen Horowitz",
                "reason": "Interested in AI healthcare innovation."
            }
        ]

    elif "Agriculture" in industries:

        return [
            {
                "name": "S2G Ventures",
                "reason": "Focuses on agriculture innovation."
            },
            {
                "name": "Finistere Ventures",
                "reason": "Invests in AgriTech companies."
            },
            {
                "name": "AgFunder",
                "reason": "Specialized agriculture investor."
            }
        ]

    elif "FinTech" in industries:

        return [
            {
                "name": "Ribbit Capital",
                "reason": "FinTech specialist."
            },
            {
                "name": "QED Investors",
                "reason": "Invests in payments and banking."
            },
            {
                "name": "Accel",
                "reason": "Funds financial technology startups."
            }
        ]

    elif "Education" in industries:

        return [
            {
                "name": "Owl Ventures",
                "reason": "Largest EdTech investor."
            },
            {
                "name": "Reach Capital",
                "reason": "Focuses on education innovation."
            },
            {
                "name": "Learn Capital",
                "reason": "Supports learning platforms."
            }
        ]

    elif "Cybersecurity" in industries:

        return [
            {
                "name": "Ten Eleven Ventures",
                "reason": "Cybersecurity specialist."
            },
            {
                "name": "SYN Ventures",
                "reason": "Invests in security startups."
            },
            {
                "name": "Forgepoint Capital",
                "reason": "Strong cybersecurity portfolio."
            }
        ]

    elif "Artificial Intelligence" in industries:

        return [
            {
                "name": "Andreessen Horowitz",
                "reason": "Major AI investor."
            },
            {
                "name": "Sequoia Capital",
                "reason": "Funds AI innovation."
            },
            {
                "name": "Lightspeed Venture Partners",
                "reason": "Invests in scalable AI products."
            }
        ]

    return [
        {
            "name": "Y Combinator",
            "reason": "Invests across many startup sectors."
        },
        {
            "name": "Accel",
            "reason": "Supports early-stage startups."
        },
        {
            "name": "Sequoia Capital",
            "reason": "Global venture capital firm."
        }
    ]

def get_government_schemes(industries):

    schemes = []

    for industry in industries:

        if industry == "Agriculture":

            schemes.extend([

                {
                    "name": "RKVY-RAFTAAR",
                    "description": "Supports AgriTech startups with funding and incubation.",
                    "link": "https://www.manage.gov.in/managecia/RKVYProg.aspx"
                },

                {
                    "name": "Agri Udaan",
                    "description": "Supports agriculture innovation startups.",
                    "link": "https://agristartup.gov.in/"
                }

            ])

        elif industry == "Healthcare":

            schemes.extend([

                {
                    "name": "BIRAC",
                    "description": "Supports biotech and healthcare startups.",
                    "link": "https://birac.nic.in"
                },

                {
                    "name": "Startup India",
                    "description": "Funding, mentorship and startup recognition.",
                    "link": "https://www.startupindia.gov.in"
                }

            ])

        elif industry == "FinTech":

            schemes.extend([

                {
                    "name": "Digital India",
                    "description": "Supports digital innovation startups.",
                    "link": "https://www.digitalindia.gov.in"
                },

                {
                    "name": "Startup India",
                    "description": "Government startup support program.",
                    "link": "https://www.startupindia.gov.in"
                }

            ])

        elif industry == "Education":

            schemes.extend([

                {
                    "name": "Startup India",
                    "description": "Supports education startups.",
                    "link": "https://www.startupindia.gov.in"
                }

            ])

        elif industry == "Cybersecurity":

            schemes.extend([

                {
                    "name": "Digital India",
                    "description": "Supports cybersecurity innovation.",
                    "link": "https://www.digitalindia.gov.in"
                }

            ])

    schemes.append({

        "name": "Karnataka Startup Policy",

        "description": "State support for Karnataka startups.",

        "link": "https://startup.karnataka.gov.in"

    })

    return schemes


def generate_roadmap(industries):

    if "Artificial Intelligence" in industries:

        return [
            "Research AI market and identify problem",
            "Collect and prepare training datasets",
            "Develop and train AI model",
            "Build AI-powered MVP",
            "Deploy on cloud and scale globally"
        ]

    elif "Healthcare" in industries:

        return [
            "Research hospitals and patient needs",
            "Develop healthcare MVP",
            "Pilot testing with hospitals",
            "Apply for BIRAC funding",
            "Expand to clinics and healthcare providers"
        ]

    elif "FinTech" in industries:

        return [
            "Research RBI regulations and compliance",
            "Develop secure payment platform",
            "Integrate banking and UPI APIs",
            "Launch beta with selected customers",
            "Expand financial services nationwide"
        ]

    elif "Agriculture" in industries:

        return [
            "Identify farmers' pain points",
            "Develop smart farming solution",
            "Conduct pilot testing in villages",
            "Partner with agriculture departments",
            "Expand across multiple states"
        ]

    elif "Cybersecurity" in industries:

        return [
            "Identify cybersecurity threats",
            "Develop security monitoring system",
            "Perform penetration testing",
            "Obtain cybersecurity certifications",
            "Offer enterprise security services"
        ]

    elif "Education" in industries:

        return [
            "Research student learning requirements",
            "Create educational platform",
            "Develop courses and assessments",
            "Launch pilot with schools and colleges",
            "Expand with certification programs"
        ]

    elif "Legal services" in industries:

        return [
            "Research legal industry requirements",
            "Develop legal document automation",
            "Partner with lawyers and law firms",
            "Launch online legal consultation platform",
            "Expand LegalTech services nationwide"
        ]

    return [
        "Validate startup idea",
        "Develop MVP",
        "Launch beta version",
        "Acquire first customers",
        "Seek investment"
    ]

    if "Healthcare" in industries:

        return [
            "Research hospitals and patient needs",
            "Build healthcare MVP",
            "Pilot testing with hospitals",
            "Apply for BIRAC funding",
            "Scale across healthcare providers"
        ]

    elif "Agriculture" in industries:

        return [
            "Research farmer requirements",
            "Build agriculture prototype",
            "Conduct field testing",
            "Apply for Agri Udaan support",
            "Expand to multiple regions"
        ]

    elif "Artificial Intelligence" in industries:

        return [
            "Collect training data",
            "Develop AI model",
            "Build MVP",
            "Beta testing",
            "Scale using cloud infrastructure"
        ]

    return [
        "Validate startup idea",
        "Build MVP",
        "Launch beta version",
        "Acquire customers",
        "Seek funding"
    ]   

def generate_funding_plan(industry, budget, team_size):

    # --------------------------
    # Convert budget and team size
    # --------------------------
    try:
        budget = int(str(budget).split()[0])
    except:
        budget = 10

    try:
        team_size = int(team_size)
    except:
        team_size = 3

    # --------------------------
    # Funding based on Industry
    # --------------------------

    if industry == "Healthcare":

        stages = {
            "MVP Development": budget * 0.20,
            "Clinical Testing": budget * 0.25,
            "Doctor Partnerships": budget * 0.15,
            "Medical Marketing": budget * 0.15,
            "Expansion": budget * 0.25
        }

        growth = 1.8

    elif industry == "Artificial Intelligence":

        stages = {
            "MVP Development": budget * 0.30,
            "Model Training": budget * 0.25,
            "Cloud Infrastructure": budget * 0.15,
            "Marketing": budget * 0.10,
            "Expansion": budget * 0.20
        }

        growth = 2.8

    elif industry == "FinTech":

        stages = {
            "MVP Development": budget * 0.25,
            "Security & Compliance": budget * 0.25,
            "Bank Integration": budget * 0.15,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        growth = 2.4

    elif industry == "Agriculture":

        stages = {
            "Prototype": budget * 0.20,
            "Farmer Testing": budget * 0.20,
            "Equipment": budget * 0.25,
            "Marketing": budget * 0.10,
            "Expansion": budget * 0.25
        }

        growth = 1.6

    elif industry == "Cybersecurity":

        stages = {
            "MVP Development": budget * 0.25,
            "Security Testing": budget * 0.25,
            "Compliance": budget * 0.20,
            "Marketing": budget * 0.10,
            "Expansion": budget * 0.20
        }

        growth = 2.2

    elif industry == "Education":

        stages = {
            "Platform Development": budget * 0.30,
            "Content Creation": budget * 0.20,
            "Teacher Partnership": budget * 0.15,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        growth = 1.9

    elif industry == "Legal services":

        stages = {
            "Platform Development": budget * 0.20,
            "Legal Research": budget * 0.20,
            "Lawyer Partnership": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.25
        }

        growth = 2.0

    else:

        stages = {
            "MVP Development": budget * 0.25,
            "Testing": budget * 0.20,
            "Team Hiring": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        growth = 2.0

    # --------------------------
    # Increase Team Hiring cost
    # --------------------------

    if "Team Hiring" in stages:
        stages["Team Hiring"] += team_size * 0.5

    elif "Doctor Partnerships" in stages:
        stages["Doctor Partnerships"] += team_size * 0.4

    elif "Lawyer Partnership" in stages:
        stages["Lawyer Partnership"] += team_size * 0.4

    elif "Teacher Partnership" in stages:
        stages["Teacher Partnership"] += team_size * 0.4

    elif "Cloud Infrastructure" in stages:
        stages["Cloud Infrastructure"] += team_size * 0.5

    elif "Equipment" in stages:
        stages["Equipment"] += team_size * 0.4

    elif "Compliance" in stages:
        stages["Compliance"] += team_size * 0.4

    # --------------------------
    # Revenue Forecast
    # --------------------------

    year1 = budget * growth
    year2 = year1 * 2
    year3 = year2 * 1.7

    # --------------------------
    # Convert stages for template
    # --------------------------

    formatted_stages = {}

    for stage, amount in stages.items():
        formatted_stages[stage] = f"₹{amount:.1f} Lakhs"

    # --------------------------
    # Return
    # --------------------------

    return {

        "stages": formatted_stages,

        "year1": f"₹{year1:.1f} Lakhs",

        "year2": f"₹{year2:.1f} Lakhs",

        "year3": f"₹{year3:.1f} Lakhs",

    }

    budget = float(budget)
    team_size = int(team_size)

    # ----------------------------
    # Healthcare
    # ----------------------------
    if industry == "Healthcare":

        stages = {
            "MVP Development": budget * 0.20,
            "Clinical Testing": budget * 0.25,
            "Doctor Partnerships": budget * 0.15,
            "Medical Marketing": budget * 0.15,
            "Expansion": budget * 0.25
        }

        year1 = budget * 1.8
        year2 = budget * 3.5
        year3 = budget * 6

    # ----------------------------
    # Artificial Intelligence
    # ----------------------------
    elif industry == "Artificial Intelligence":

        stages = {
            "AI Model Training": budget * 0.30,
            "Cloud Servers": budget * 0.20,
            "Dataset Collection": budget * 0.20,
            "Marketing": budget * 0.10,
            "Expansion": budget * 0.20
        }

        year1 = budget * 2
        year2 = budget * 4
        year3 = budget * 7

    # ----------------------------
    # FinTech
    # ----------------------------
    elif industry == "FinTech":

        stages = {
            "App Development": budget * 0.25,
            "Security": budget * 0.20,
            "Compliance": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        year1 = budget * 2
        year2 = budget * 4
        year3 = budget * 6

    # ----------------------------
    # Agriculture
    # ----------------------------
    elif industry == "Agriculture":

        stages = {
            "Field Testing": budget * 0.20,
            "Equipment": budget * 0.25,
            "Farmer Awareness": budget * 0.15,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.25
        }

        year1 = budget * 1.5
        year2 = budget * 3
        year3 = budget * 5

    # ----------------------------
    # Cybersecurity
    # ----------------------------
    elif industry == "Cybersecurity":

        stages = {
            "Security Research": budget * 0.25,
            "Pen Testing": budget * 0.20,
            "Infrastructure": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        year1 = budget * 2
        year2 = budget * 4
        year3 = budget * 7

    # ----------------------------
    # Education
    # ----------------------------
    elif industry == "Education":

        stages = {
            "Platform Development": budget * 0.25,
            "Course Creation": budget * 0.20,
            "Teacher Hiring": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.20
        }

        year1 = budget * 1.8
        year2 = budget * 3.8
        year3 = budget * 6

    # ----------------------------
    # Legal services
    # ----------------------------
    elif industry == "Legal services":

        stages = {
            "Platform Development": budget * 0.20,
            "Lawyer Onboarding": budget * 0.20,
            "Compliance": budget * 0.20,
            "Marketing": budget * 0.15,
            "Expansion": budget * 0.25
        }

        year1 = budget * 2
        year2 = budget * 3.5
        year3 = budget * 5

    # ----------------------------
    # Default
    # ----------------------------
    else:

        stages = {
            "Development": budget * 0.20,
            "Testing": budget * 0.20,
            "Team": budget * 0.20,
            "Marketing": budget * 0.20,
            "Expansion": budget * 0.20
        }

        year1 = budget * 2
        year2 = budget * 3
        year3 = budget * 5

    # Team Adjustment

    if team_size >= 10:
        stages["Team Hiring"] = budget * 0.30
    elif team_size >= 5:
        stages["Team Hiring"] = budget * 0.20
    else:
        stages["Team Hiring"] = budget * 0.10

    return {

    "stages": {

        list(stages.keys())[0]: f"₹{stages[list(stages.keys())[0]]:.1f} Lakhs",

        list(stages.keys())[1]: f"₹{stages[list(stages.keys())[1]]:.1f} Lakhs",

        "Team Hiring": f"₹{stages['Team Hiring']:.1f} Lakhs",

        list(stages.keys())[3]: f"₹{stages[list(stages.keys())[3]]:.1f} Lakhs",

        list(stages.keys())[4]: f"₹{stages[list(stages.keys())[4]]:.1f} Lakhs",

    },

    "year1": f"₹{year1:.1f} Lakhs",

    "year2": f"₹{year2:.1f} Lakhs",

    "year3": f"₹{year3:.1f} Lakhs",

    }

    try:
        budget = int(str(budget).split()[0])
    except:
        budget = 5

    try:
        team_size = int(team_size)
    except:
        team_size = 1


    funding_percent = {

        "Healthcare": {
            "mvp": 0.30,
            "testing": 0.20,
            "team": 0.20,
            "marketing": 0.10,
            "expansion": 0.20
        },

        "Artificial Intelligence": {
            "mvp": 0.35,
            "testing": 0.10,
            "team": 0.25,
            "marketing": 0.10,
            "expansion": 0.20
        },

        "FinTech": {
            "mvp": 0.25,
            "testing": 0.20,
            "team": 0.25,
            "marketing": 0.10,
            "expansion": 0.20
        },

        "Agriculture": {
            "mvp": 0.20,
            "testing": 0.20,
            "team": 0.20,
            "marketing": 0.20,
            "expansion": 0.20
        },

        "Cybersecurity": {
            "mvp": 0.30,
            "testing": 0.20,
            "team": 0.20,
            "marketing": 0.10,
            "expansion": 0.20
        },

        "Education": {
            "mvp": 0.20,
            "testing": 0.15,
            "team": 0.20,
            "marketing": 0.20,
            "expansion": 0.25
        },

        "Legal services": {
            "mvp": 0.20,
            "testing": 0.15,
            "team": 0.20,
            "marketing": 0.20,
            "expansion": 0.25
        }

    }


    plan = funding_percent.get(
        industry,
        funding_percent["Artificial Intelligence"]
    )


    mvp = round(budget * plan["mvp"], 1)

    testing = round(budget * plan["testing"], 1)

    team = round(budget * plan["team"], 1)

    marketing = round(budget * plan["marketing"], 1)

    expansion = round(budget * plan["expansion"], 1)


    if team_size > 15:

        team += 2

    elif team_size > 8:

        team += 1


    return {

        "mvp": f"₹{mvp} Lakhs",

        "testing": f"₹{testing} Lakhs",

        "team": f"₹{team} Lakhs",

        "marketing": f"₹{marketing} Lakhs",

        "expansion": f"₹{expansion} Lakhs",

        "year1": f"₹{budget*2} Lakhs",

        "year2": f"₹{budget*5} Lakhs",

        "year3": f"₹{budget*9} Lakhs"

    }

def roadmap(request):

    roadmap_steps = request.session.get(
        "roadmap_steps",
        []
    )
    
    return render(
        request,
        "roadmap.html",
        {
            "roadmap_steps": roadmap_steps
        }
    )

def funding(request):

    funding_data = request.session.get("funding_data", {})

    industry = request.session.get("industry", "")

    budget = request.session.get("budget", "")

    team_size = request.session.get("team_size", "")

    return render(
        request,
        "funding.html",
        {
            "funding_data": funding_data,
            "industry": industry,
            "budget": budget,
            "team_size": team_size
        }
    )

def check_domain(domain):

    url = f"https://dns.google/resolve?name={domain}"

    try:

        response = requests.get(url)

        data = response.json()

        if "Answer" in data:

            return False

        return True

    except:

        return None

def legal_audit(request):

    startup_name = request.session.get(
        "startup_name",
        ""
    )

    extension = request.session.get(
        "domain_extension",
        ".com"
    )

    domain_name = (
        startup_name
        .replace(" ", "")
        .lower()
        + extension
    )

    domain_available = check_domain(domain_name)

    protected_brands = [
        "google",
        "amazon",
        "apple",
        "microsoft",
        "uber",
        "flipkart",
        "zomato",
        "swiggy",
        "netflix"
    ]

    if any(brand in startup_name.lower() for brand in protected_brands):

        trademark_risk = "Critical"

    elif domain_available is False:

        trademark_risk = "High"

    elif domain_available is True:

        trademark_risk = "Low"

    else:

        trademark_risk = "Unknown"
        
    print(domain_available)
    print(type(domain_available))

    return render(
        request,
        "legal_audit.html",
        {
            "startup_name": startup_name,
            "domain_name": domain_name,
            "domain_available": domain_available,
            "trademark_risk": trademark_risk
        }
    )
    
def business_model(request):
    
    industry = request.session.get("industry", "")
    
    all_canvas = {

        "Healthcare": {

            "Key Partners": [
                "Hospitals",
                "Doctors",
                "Medical Equipment Suppliers",
                "Insurance Companies"
            ],

            "Key Activities": [
                "Telemedicine",
                "Patient Care",
                "Health Monitoring",
                "Medical Consultation"
            ],

            "Value Proposition": [
                "Affordable healthcare",
                "24/7 medical support",
                "Fast diagnosis",
                "Remote consultation"
            ],

            "Customer Relationships": [
                "Doctor Follow-up",
                "Patient Support",
                "Health Notifications"
            ],

            "Customer Segments": [
                "Patients",
                "Hospitals",
                "Clinics",
                "Medical Professionals"
            ],

            "Key Resources": [
                "Doctors",
                "Medical Database",
                "Cloud Platform",
                "Health Records"
            ],

            "Channels": [
                "Website",
                "Mobile App",
                "Hospitals"
            ],

            "Cost Structure": [
                "Doctor Salaries",
                "Cloud Hosting",
                "Medical Equipment"
            ],

            "Revenue Streams": [
                "Consultation Fees",
                "Subscription Plans",
                "Hospital Partnerships"
            ]

        },

        "Artificial Intelligence": {

            "Key Partners": [
                "Cloud Providers",
                "Technology Companies",
                "Research Institutes"
            ],

            "Key Activities": [
                "AI Model Development",
                "Machine Learning",
                "Automation",
                "Data Analysis"
            ],

            "Value Proposition": [
                "AI-powered automation",
                "Faster decision making",
                "Reduced operational cost"
            ],

            "Customer Relationships": [
                "Technical Support",
                "Developer Community",
                "Dedicated Assistance"
            ],

            "Customer Segments": [
                "Businesses",
                "Developers",
                "Enterprises",
                "Startups"
            ],

            "Key Resources": [
                "AI Models",
                "GPU Servers",
                "Training Datasets"
            ],

            "Channels": [
                "Website",
                "API",
                "Cloud Marketplace"
            ],

            "Cost Structure": [
                "Cloud Computing",
                "Research",
                "Server Maintenance"
            ],

            "Revenue Streams": [
                "Subscriptions",
                "API Usage",
                "Enterprise Licensing"
            ]

        },

        "FinTech": {

            "Key Partners": [
                "Banks",
                "Payment Gateways",
                "Financial Institutions"
            ],

            "Key Activities": [
                "Digital Payments",
                "Financial Analytics",
                "Loan Processing"
            ],

            "Value Proposition": [
                "Secure payments",
                "Quick transactions",
                "Financial accessibility"
            ],

            "Customer Relationships": [
                "Customer Support",
                "Online Banking",
                "Personal Finance Assistance"
            ],

            "Customer Segments": [
                "Individuals",
                "Businesses",
                "Merchants"
            ],

            "Key Resources": [
                "Payment Platform",
                "Bank APIs",
                "Security Systems"
            ],

            "Channels": [
                "Mobile App",
                "Website",
                "Bank Integration"
            ],

            "Cost Structure": [
                "Server Costs",
                "Security",
                "Compliance"
            ],

            "Revenue Streams": [
                "Transaction Fees",
                "Premium Accounts",
                "Merchant Services"
            ]

        },

        "Agriculture": {

            "Key Partners": [
                "Farmers",
                "Government",
                "Agricultural Suppliers"
            ],

            "Key Activities": [
                "Crop Monitoring",
                "Smart Farming",
                "Weather Prediction"
            ],

            "Value Proposition": [
                "Increase crop yield",
                "Reduce farming costs",
                "Better market access"
            ],

            "Customer Relationships": [
                "Farmer Support",
                "Training",
                "SMS Alerts"
            ],

            "Customer Segments": [
                "Farmers",
                "Agri Businesses",
                "Cooperatives"
            ],

            "Key Resources": [
                "Weather Data",
                "IoT Sensors",
                "Agriculture Experts"
            ],

            "Channels": [
                "Mobile App",
                "Government Centres",
                "Website"
            ],

            "Cost Structure": [
                "Equipment",
                "Cloud Services",
                "Field Operations"
            ],

            "Revenue Streams": [
                "Subscriptions",
                "Government Funding",
                "Marketplace Commission"
            ]

        },

        "Cybersecurity": {

            "Key Partners": [
                "Security Vendors",
                "Cloud Providers",
                "IT Companies"
            ],

            "Key Activities": [
                "Threat Detection",
                "Network Monitoring",
                "Security Audits"
            ],

            "Value Proposition": [
                "Protect digital assets",
                "Prevent cyber attacks",
                "Real-time monitoring"
            ],

            "Customer Relationships": [
                "24/7 Support",
                "Security Reports",
                "Training"
            ],

            "Customer Segments": [
                "Businesses",
                "Government",
                "Educational Institutions"
            ],

            "Key Resources": [
                "Security Software",
                "Threat Intelligence",
                "SOC Team"
            ],

            "Channels": [
                "Website",
                "Security Portal"
            ],

            "Cost Structure": [
                "Security Tools",
                "Analysts",
                "Infrastructure"
            ],

            "Revenue Streams": [
                "Subscriptions",
                "Consulting",
                "Managed Security Services"
            ]

        },

        "Education": {

            "Key Partners": [
                "Schools",
                "Colleges",
                "Teachers"
            ],

            "Key Activities": [
                "Online Learning",
                "Course Development",
                "Student Assessment"
            ],

            "Value Proposition": [
                "Accessible education",
                "Interactive learning",
                "Skill development"
            ],

            "Customer Relationships": [
                "Student Support",
                "Teacher Community",
                "Learning Assistance"
            ],

            "Customer Segments": [
                "Students",
                "Teachers",
                "Institutions"
            ],

            "Key Resources": [
                "Learning Platform",
                "Educational Content",
                "Faculty"
            ],

            "Channels": [
                "Website",
                "Mobile App"
            ],

            "Cost Structure": [
                "Content Creation",
                "Platform Maintenance"
            ],

            "Revenue Streams": [
                "Course Fees",
                "Subscriptions",
                "Institution Licences"
            ]

        },

        "Legal services": {

            "Key Partners": [
                "Law Firms",
                "Government",
                "Legal Advisors"
            ],

            "Key Activities": [
                "Legal Consultation",
                "Document Verification",
                "Contract Review"
            ],

            "Value Proposition": [
                "Affordable legal advice",
                "Quick legal assistance",
                "Online document management"
            ],

            "Customer Relationships": [
                "Legal Support",
                "Appointment Booking",
                "Client Assistance"
            ],

            "Customer Segments": [
                "Individuals",
                "Businesses",
                "Startups"
            ],

            "Key Resources": [
                "Lawyers",
                "Legal Database",
                "Document Repository"
            ],

            "Channels": [
                "Website",
                "Mobile App",
                "Video Consultation"
            ],

            "Cost Structure": [
                "Lawyer Fees",
                "Technology",
                "Cloud Storage"
            ],

            "Revenue Streams": [
                "Consultation Fees",
                "Subscription Plans",
                "Legal Documentation Services"
            ]

        }

    }
    
    business_canvas = all_canvas.get(
    industry,
    all_canvas["Artificial Intelligence"]
    )
    
    return render(
    request,
    "business_model.html",
    {
        "business_canvas": business_canvas
    }
    )
def generate_business_model(industry):

    models = {

        "Healthcare": {

            " Who are your customers?":[
                "Patients",
                "Hospitals",
                "Clinics",
                "Diagnostic Centers"
            ],

            " What problem are you solving?":[
                "Faster diagnosis",
                "Affordable healthcare",
                "Reduce waiting time"
            ],

            " How will you earn money?":[
                "Hospital subscriptions",
                "Premium plans",
                "Consultation fees"
            ],

            " How will customers find you?":[
                "Hospitals",
                "Google Search",
                "Social Media"
            ],

            " Key Partners":[
                "Doctors",
                "Hospitals",
                "BIRAC"
            ],

            " Growth Strategy":[
                "Expand to multiple cities",
                "Partner with hospitals",
                "Launch mobile app"
            ],

            " Challenges":[
                "Government regulations",
                "Patient trust",
                "Medical compliance"
            ],

            " AI Recommendation":[
                "Launch MVP in one city before scaling."
            ]
        },

        "Artificial Intelligence": {

            " Who are your customers?":[
                "Businesses",
                "Students",
                "IT Companies"
            ],

            " What problem are you solving?":[
                "Automation",
                "Reduce manual work",
                "Increase productivity"
            ],

            " How will you earn money?":[
                "SaaS Subscription",
                "API Access",
                "Enterprise License"
            ],

            " How will customers find you?":[
                "Website",
                "LinkedIn",
                "Google Ads"
            ],

            " Key Partners":[
                "Cloud Providers",
                "OpenAI",
                "Microsoft Azure"
            ],

            " Growth Strategy":[
                "API Integration",
                "International expansion",
                "Enterprise sales"
            ],

            " Challenges":[
                "High competition",
                "GPU costs",
                "Rapid technology changes"
            ],

            " AI Recommendation":[
                "Focus on one niche before expanding."
            ]
        },

        "Education": {

            " Who are your customers?":[
                "Students",
                "Schools",
                "Colleges",
                "Teachers"
            ],

            " What problem are you solving?":[
                "Online learning",
                "Skill development",
                "Exam preparation"
            ],

            " How will you earn money?":[
                "Course fees",
                "Subscription",
                "Certificates"
            ],

            " How will customers find you?":[
                "Schools",
                "Social Media",
                "Website"
            ],

            " Key Partners":[
                "Educational Institutions",
                "Teachers",
                "EdTech Companies"
            ],

            " Growth Strategy":[
                "Launch new courses",
                "Partner with colleges"
            ],

            " Challenges":[
                "Content quality",
                "Student retention"
            ],

            " AI Recommendation":[
                "Provide free trial courses."
            ]
        },

        "Agriculture": {

            " Who are your customers?":[
                "Farmers",
                "Agriculture Companies",
                "Cooperatives"
            ],

            " What problem are you solving?":[
                "Increase crop yield",
                "Smart farming"
            ],

            " How will you earn money?":[
                "Equipment sales",
                "Subscription",
                "Government projects"
            ],

            " How will customers find you?":[
                "Farmer Associations",
                "Government Programs"
            ],

            " Key Partners":[
                "Krishi Centers",
                "Government",
                "NGOs"
            ],

            " Growth Strategy":[
                "Expand district-wise",
                "Introduce IoT devices"
            ],

            " Challenges":[
                "Weather",
                "Farmer awareness"
            ],

            " AI Recommendation":[
                "Target one crop before nationwide expansion."
            ]
        },

        "FinTech": {

            " Who are your customers?":[
                "Banks",
                "Small Businesses",
                "Individuals"
            ],

            " What problem are you solving?":[
                "Easy digital payments",
                "Financial management"
            ],

            " How will you earn money?":[
                "Transaction fees",
                "Premium services"
            ],

            " How will customers find you?":[
                "Banks",
                "App Store",
                "Website"
            ],

            " Key Partners":[
                "Banks",
                "RBI",
                "Payment Gateways"
            ],

            " Growth Strategy":[
                "Launch UPI features",
                "Expand merchant network"
            ],

            " Challenges":[
                "Cybersecurity",
                "Government compliance"
            ],

            " AI Recommendation":[
                "Obtain security certifications early."
            ]
        },

        "Cybersecurity": {

            " Who are your customers?":[
                "Companies",
                "Banks",
                "Government"
            ],

            " What problem are you solving?":[
                "Protect digital assets",
                "Prevent cyber attacks"
            ],

            " How will you earn money?":[
                "Annual subscriptions",
                "Security audits"
            ],

            " How will customers find you?":[
                "LinkedIn",
                "Business Conferences"
            ],

            " Key Partners":[
                "Cloud Companies",
                "Security Vendors"
            ],

            " Growth Strategy":[
                "Enterprise solutions",
                "International clients"
            ],

            " Challenges":[
                "Rapidly changing threats",
                "Customer trust"
            ],

            " AI Recommendation":[
                "Offer free vulnerability assessments."
            ]
        },

        "Restaurant": {

            " Who are your customers?":[
                "Families",
                "Office Employees",
                "Students"
            ],

            " What problem are you solving?":[
                "Healthy food",
                "Fast delivery"
            ],

            " How will you earn money?":[
                "Food sales",
                "Delivery charges"
            ],

            " How will customers find you?":[
                "Swiggy",
                "Zomato",
                "Instagram"
            ],

            " Key Partners":[
                "Food Suppliers",
                "Delivery Partners"
            ],

            " Growth Strategy":[
                "Open more branches",
                "Cloud kitchens"
            ],

            " Challenges":[
                "High competition",
                "Food wastage"
            ],

            " AI Recommendation":[
                "Start with one outlet before expansion."
            ]
        },

        "Travel": {

            " Who are your customers?":[
                "Tourists",
                "Families",
                "Corporate Travelers"
            ],

            " What problem are you solving?":[
                "Affordable travel planning",
                "Easy booking"
            ],

            " How will you earn money?":[
                "Booking commission",
                "Travel packages"
            ],

            " How will customers find you?":[
                "Google",
                "Instagram",
                "Travel Blogs"
            ],

            " Key Partners":[
                "Hotels",
                "Airlines",
                "Travel Agencies"
            ],

            " Growth Strategy":[
                "International packages",
                "Corporate tours"
            ],

            " Challenges":[
                "Seasonal demand",
                "Travel restrictions"
            ],

            " AI Recommendation":[
                "Focus on domestic tourism initially."
            ]
        },

        "Legal services": {

            " Who are your customers?":[
                "Startups",
                "SMEs",
                "Individuals"
            ],

            " What problem are you solving?":[
                "Affordable legal consultation",
                "Quick documentation"
            ],

            " How will you earn money?":[
                "Consultation fees",
                "Monthly subscription"
            ],

            " How will customers find you?":[
                "Website",
                "LinkedIn",
                "Google Search"
            ],

            " Key Partners":[
                "Law Firms",
                "CA Firms"
            ],

            " Growth Strategy":[
                "Expand online legal services",
                "Corporate partnerships"
            ],

            " Challenges":[
                "Legal compliance",
                "Customer trust"
            ],

            " AI Recommendation":[
                "Offer free legal templates to attract users."
            ]
        },

        "E-commerce": {

            " Who are your customers?":[
                "Online shoppers",
                "Retailers"
            ],

            " What problem are you solving?":[
                "Easy online shopping",
                "Fast delivery"
            ],

            " How will you earn money?":[
                "Product sales",
                "Commission"
            ],

            " How will customers find you?":[
                "Google",
                "Instagram",
                "Facebook"
            ],

            " Key Partners":[
                "Suppliers",
                "Courier Services"
            ],

            " Growth Strategy":[
                "Increase product categories",
                "Expand nationwide"
            ],

            " Challenges":[
                "Returns",
                "Price competition"
            ],

            " AI Recommendation":[
                "Start with one product category before scaling."
            ]
        }

    }

    return models.get(industry, {

        " Who are your customers?":["General Customers"],

        " What problem are you solving?":[
            "Provide a unique solution."
        ],

        " How will you earn money?":[
            "Subscription"
        ],

        " How will customers find you?":[
            "Website",
            "Google Search"
        ],

        " Key Partners":[
            "Investors"
        ],

        " Growth Strategy":[
            "Launch MVP",
            "Acquire Customers"
        ],

        " Challenges":[
            "Competition"
        ],

        " AI Recommendation":[
            "Validate the market before investing."
        ]

    })
    
def get_competition_score(news_count):

    if news_count > 5000:
        return 90

    elif news_count > 3000:
        return 75

    elif news_count > 1500:
        return 60

    elif news_count > 500:
        return 40

    else:
        return 20