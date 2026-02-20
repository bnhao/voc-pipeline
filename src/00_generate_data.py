import pandas as pd
import random
from faker import Faker
import datetime

# Configure the zone to be in Canada
fake = Faker('en_CA')

NUM_ROWS = 3000  # Size of dataset
OUTPUT_FILE = 'data/atb_large_dataset.csv'

# ATB Branches
branches = [
    "Calgary - Country Hills", "Calgary - 17th Ave", "Calgary - Chinook",
    "Edmonton - Southgate", "Edmonton - Whythe Ave", "Red Deer - Gaetz Ave",
    "Lethbridge - West", "Digital (App/Web)", "Digital (App/Web)", "Digital (App/Web)" # Heavy weighting on Digital
]

# ATB Products
products = [
    "Springboard Savings", "Unlimited Chequing", "Gold Cash Rewards Mastercard",
    "No-Fee All-In Digital", "Mortgage", "Business Operating Account", "GIC"
]

# mix "Templates" with "Keywords" to create unique sentences

# 1. NEGATIVE TEMPLATES (The problems you need to find)
negative_templates = [
    "The {product} is giving me trouble, {issue}.",
    "I tried to use the {channel} but {issue}.",
    "Wait times at {branch} are {adjective}, I waited {time}.",
    "Why does the app always {issue} when I try to pay bills?",
    "Disappointed with the {product}, the fees are too high.",
    "Customer service was {adjective} when I called about my {product}.",
    "Biometric login on the app {issue} every time after the update.",
    "Fraud protection locked my card while I was in {location}, very {adjective}.",
    "The new interface is confusing, I can't find my {product} details."
]

negative_issues = [
    "crash on startup", "freeze at the login screen", "fail to send e-Transfer",
    "log me out randomly", "show the wrong balance", "reject my cheque deposit",
    "ask for security questions I didn't set", "decline my card"
]

negative_adjectives = [
    "unacceptable", "frustrating", "ridiculous", "horrible", "painful", "slow"
]

wait_times = ["45 minutes", "an hour", "forever", "20 mins", "too long"]

# 2. POSITIVE TEMPLATES (To confuse the model - "False Positives")
positive_templates = [
    "I love the new {product}, it helps me save money.",
    "The staff at {branch} were so {adjective} today.",
    "Finally, the app works for {product}!",
    "Great experience with the {product} application process.",
    "The teller at {branch} was very {adjective} and solved my issue.",
    "Best bank in Alberta, specifically for {product}.",
]

positive_adjectives = [
    "helpful", "friendly", "amazing", "quick", "efficient", "kind"
]

# --- GENERATOR FUNCTIONS ---

def generate_comment(sentiment):
    """Generates a fake but realistic client comment."""
    product = random.choice(products)
    branch = random.choice(branches)
    
    if sentiment == "Negative":
        template = random.choice(negative_templates)
        return template.format(
            product=product,
            channel="mobile app",
            issue=random.choice(negative_issues),
            branch=branch,
            adjective=random.choice(negative_adjectives),
            time=random.choice(wait_times),
            location="Banff"
        )
    elif sentiment == "Positive":
        template = random.choice(positive_templates)
        return template.format(
            product=product,
            branch=branch,
            adjective=random.choice(positive_adjectives)
        )
    else: # Neutral/Messy
        return random.choice([
            "I have a question about my account.",
            "What are your hours?",
            "Call me back@@.",
            "Statement update.",
            "???"
        ])

def generate_dataset():
    data = []
    print(f"🚀 Generating {NUM_ROWS} rows of synthetic ATB feedback...")
    
    for _ in range(NUM_ROWS):
        # 60% Negative (Real feedback is usually complaints), 30% Positive, 10% Neutral
        rand_val = random.random()
        if rand_val < 0.60:
            sentiment = "Negative"
        elif rand_val < 0.90:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"
            
        comment = generate_comment(sentiment)
        
        # Add some noise (Nulls and Empty strings) to test your cleaning pipeline
        if random.random() < 0.02: # 2% chance of bad data
            comment = None
        
        data.append({
            "feedback_id": fake.uuid4(),
            "date": fake.date_between(start_date='-1y', end_date='today'),
            "branch": random.choice(branches),
            "product": random.choice(products),
            "client_comment": comment,
            "source": random.choice(["Mobile App Survey", "Email", "Call Center Log"])
        })
        
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Successfully created '{OUTPUT_FILE}' with {len(df)} rows.")
    print(df.head())

if __name__ == "__main__":
    generate_dataset()