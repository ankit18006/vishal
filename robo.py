import streamlit as st
import wolframalpha
import wikipedia
import pyttsx3
import threading

import toml

# Load configuration
config = toml.load("config.toml")
api_key = config["api"]["wolframalpha_key"]

# Initialize WolframAlpha client
client = wolframalpha.Client(api_key)


# Initialize text-to-speech engine
engine = pyttsx3.init()

st.set_page_config(
    page_title="Mini Wikipedia",  # Title that appears on the browser tab
    page_icon=":book:",           # Icon for the tab (optional)
    layout="wide"                 # Layout of the page (optional)
)

def get_wolframalpha_result(query):
    try:
        res = client.query(query)
        if res['@success'] == 'true' and 'pod' in res:
            return next(res.results).text
        else:
            return "No result."
    except Exception as e:
        return f"Error fetching result: {e}"

def get_wikipedia_summary(query, max_sentences=10):
    try:
        # Fetch full summary
        full_summary = wikipedia.summary(query)
        
        # Split into sentences
        sentences = full_summary.split('. ')
        
        # Limit to the desired number of sentences
        truncated_summary = '. '.join(sentences[:max_sentences]) + ('.' if len(sentences) > max_sentences else '')
        
        return truncated_summary
    except wikipedia.exceptions.DisambiguationError:
        return "The query is too ambiguous. Please refine your query."
    except wikipedia.exceptions.PageError:
        return "No page found for the query. Please check your query."
    except Exception as e:
        return f"Error fetching Wikipedia summary: {e}"

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Streamlit App
st.title("Mini Wikipedia")
st.write("Enter a command below:")

query = st.text_input("Command")

if st.button("Submit"):
    if query:
        st.write("Processing your request...")

        # Get results
        wiki_res = get_wikipedia_summary(query, max_sentences=10)
        wolfram_res = get_wolframalpha_result(query)

        #st.write("### WolframAlpha Result:")
        #st.write(wolfram_res)
        
        #st.write("### Wikipedia Summary:")
        st.text_area("Summary:", wiki_res, height=300)

        # Run text-to-speech in a separate thread
        threading.Thread(target=speak, args=(wolfram_res,)).start()
        threading.Thread(target=speak, args=(wiki_res,)).start()
    else:
        st.warning('Please enter a command.')
