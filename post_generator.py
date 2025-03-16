from llm_helper import llm
from few_shot import FewShotPosts
import pymongo

# Initialize FewShotPosts object
few_shot = FewShotPosts()

# Function to connect to MongoDB
def init_mongo_connection():
    client = pymongo.MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URI if needed
    return client

# Fetch data from MongoDB (e.g., topics, tags, etc.)
def fetch_data_from_mongo():
    client = init_mongo_connection()
    db = client['linkedin_posts_db']   # Database name
    collection = db['posts']           # Collection name
    
    # Fetch all documents from the 'posts' collection
    return list(collection.find())

# Helper function to get length string based on input
def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"

# Function that generates a LinkedIn post using LLM model
def generate_post(length, language, tag):
    prompt = get_prompt(length, language, tag)
    
    # Invoke LLM with the generated prompt
    response = llm.invoke(prompt)
    
    return response.content

# Function that creates a prompt for the LLM based on inputs and examples from MongoDB
def get_prompt(length, language, tag):
    length_str = get_length_str(length)

    # Create a basic prompt structure for generating LinkedIn posts
    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}
    
    If Language is Hinglish then it means it is a mix of Hindi and English. 
    The script for the generated post should always be in English.
    '''

    # Fetch example posts from MongoDB using FewShotPosts object (if available)
    examples = few_shot.get_filtered_posts(length, language, tag)

    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f'\n\n Example {i+1}: \n\n {post_text}'
            
            if i == 1:  # Use maximum two examples
                break
    
    return prompt

if __name__ == "__main__":
    # Example usage: Generate a post on "Mental Health" with medium length in English
    print(generate_post("Medium", "English", "Mental Health"))