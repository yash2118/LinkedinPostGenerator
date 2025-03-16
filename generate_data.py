from faker import Faker
import random
import json
from datetime import date

# Initialize Faker
fake = Faker()

# List of possible topics and languages
topics = ["Data Science", "Marketing", "Career Guidance", "Technology", "Health", "Fitness", "Entrepreneurship"]
languages = ["English", "Hinglish"]
lengths = ["Short", "Medium", "Long"]

# Function to generate fake post data for an influencer
def generate_fake_post(influencer):
    return {
        "influencer": influencer,
        "author": influencer,
        "content": fake.text(max_nb_chars=200),
        "tags": random.sample(topics, 2),  # Randomly select 2 topics
        "language": random.choice(languages),
        "length": random.choice(lengths),
        "engagement": {
            "likes": random.randint(10, 500),
            "comments": random.randint(0, 100),
            "shares": random.randint(0, 50)
        },
        "date_posted": fake.date_this_year()  # This will be a datetime.date object
    }

# Generate posts for all influencers
def generate_influencer_posts():
    influencers = [fake.name() for _ in range(10)]  # Generate 10 fake influencer names
    posts = []
    for influencer in influencers:
        # Generate between 1 to 5 posts per influencer
        num_posts = random.randint(1, 5)
        for _ in range(num_posts):
            posts.append(generate_fake_post(influencer))
    return posts

# Custom JSON encoder to handle date objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()  # Convert date object to ISO format string (YYYY-MM-DD)
        return super().default(obj)

# Save generated posts to a JSON file (with custom encoder for dates)
def save_to_json(posts, filename="fake_posts.json"):
    with open(filename, 'w') as f:
        json.dump(posts, f, indent=4, cls=DateTimeEncoder)  # Use custom encoder

if __name__ == "__main__":
    # Generate the fake posts
    fake_posts = generate_influencer_posts()
    
    # Save them to a JSON file
    save_to_json(fake_posts)
    
    # Print some of the generated posts (for debugging)
    print(fake_posts[:2])  # Print first two posts as a sample