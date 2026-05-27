import pandas as pd
import random

good_ideas = [

    "AI healthcare assistant",
    "smart farming platform",
    "online learning app",
    "digital payment system",
    "cybersecurity solution",
    "AI recruitment platform",
    "food delivery app",
    "electric vehicle charging station",
    "fitness tracking app",
    "renewable energy startup",
    "online doctor consultation",
    "virtual event platform",
    "AI stock market assistant",
    "women safety app",
    "telemedicine platform",
    "AI chatbot for students",
    "cloud kitchen startup",
    "language learning app",
    "job portal platform",
    "home automation system"

]

bad_ideas = [

    "dvd rental shop",
    "pager communication business",
    "fax machine repair",
    "typewriter repair center",
    "cassette tape business",
    "floppy disk sales",
    "old newspaper printing",
    "telephone booth service",
    "vcr rental shop",
    "manual telegram service",
    "cd burning shop",
    "old radio repair",
    "film camera processing",
    "landline phone repair",
    "offline ticket booking center",
    "analog clock repair",
    "old printing press",
    "manual typing service",
    "physical dictionary sales",
    "cyber cafe with old computers"

]

data = []

for i in range(250):

    idea = random.choice(good_ideas)

    data.append([idea, 1])

for i in range(250):

    idea = random.choice(bad_ideas)

    data.append([idea, 0])

random.shuffle(data)

df = pd.DataFrame(data, columns=["idea", "success"])

df.to_csv("data.csv", index=False)

print("500 Dataset Created Successfully!")