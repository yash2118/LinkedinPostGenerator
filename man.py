import streamlit as st
import pymongo
from llm_helper import llm
from few_shot import FewShotPosts

# Initialize FewShotPosts object
few_shot = FewShotPosts()

# Connect to MongoDB
@st.cache_resource
def init_mongo_connection():
    client = pymongo.MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URI if needed
    return client

# Fetch influencers from MongoDB
def fetch_influencers_from_mongo():
    client = init_mongo_connection()
    db = client['linkedin_posts_db']   # Database name
    collection = db['posts']           # Collection name for posts
    
    # Fetch all unique influencer names from the 'posts' collection
    return collection.distinct("influencer")

# Fetch topics for a specific influencer from MongoDB
def fetch_topics_for_influencer(influencer_name):
    client = init_mongo_connection()
    db = client['linkedin_posts_db']   # Database name
    collection = db['posts']           # Collection name for posts
    
    # Find all posts by the influencer and extract unique topics (tags)
    posts = collection.find({"influencer": influencer_name})
    
    topics = set()
    for post in posts:
        topics.update(post.get('tags', []))  # Add tags to the set to ensure uniqueness
    
    return list(topics)

# Generate a LinkedIn post using LLM based on selected options
def generate_post(length, language, topic):
    prompt = get_prompt(length, language, topic)
    
    # Invoke LLM with the generated prompt
    response = llm.invoke(prompt)
    
    return response.content

# Create a prompt for LLM based on inputs and examples from MongoDB
def get_prompt(length, language, topic):
    length_str = get_length_str(length)

    # Create a basic prompt structure for generating LinkedIn posts
    prompt = f'''
    Generate a LinkedIn post using the below information. No preamble.

    1) Topic: {topic}
    2) Length: {length_str}
    3) Language: {language}
    
    If Language is Hinglish then it means it is a mix of Hindi and English. 
    The script for the generated post should always be in English.
    '''

    # Fetch example posts from MongoDB using FewShotPosts object (if available)
    examples = few_shot.get_filtered_posts(length, language, topic)

    if len(examples) > 0:
        prompt += "\n4) Use the writing style as per the following examples."

        for i, post in enumerate(examples):
            post_text = post['text']
            prompt += f'\n\n Example {i+1}: \n\n {post_text}'
            
            if i == 1:  # Use maximum two examples
                break
    
    return prompt

# Helper function to get length string based on input
def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"

# Main app layout
def main():
    st.title("LinkedIn Post Generator")

    # Fetch influencers from MongoDB and display them in a dropdown menu
    influencers = fetch_influencers_from_mongo()
    
    if not influencers:
        st.error("No influencers found in the database.")
        return
    
    selected_influencer = st.selectbox("Select Influencer", options=influencers)
    
    if selected_influencer:
        # Fetch topics for the selected influencer dynamically from MongoDB
        topics = fetch_topics_for_influencer(selected_influencer)
        
        if not topics:
            st.error(f"No topics found for {selected_influencer}.")
            return
        
        selected_topic = st.selectbox("Select Topic", options=topics)
        
        # Dropdowns for selecting length and language of the post
        length_options = ["Short", "Medium", "Long"]
        language_options = ["English", "Hinglish"]
        
        selected_length = st.selectbox("Select Length", options=length_options)
        selected_language = st.selectbox("Select Language", options=language_options)

        # Generate Button to create a new LinkedIn post based on user selections
        if st.button("Generate Post"):
            generated_post_content = generate_post(selected_length, selected_language, selected_topic)
            
            # Display the generated post content on the screen
            st.subheader("Generated Post")
            st.write(generated_post_content)

if __name__ == "__main__":
    main()