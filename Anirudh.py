import streamlit as st
from googlesearch import search
from langchain_community.llms import Ollama
from bs4 import BeautifulSoup
from better_profanity import profanity
import requests

profanity.load_censor_words()

def fetch_links(query, num=5):
    try:
        raw_links = list(search(query, num_results=num))
        links = [link for link in raw_links if link.startswith("http://") or link.startswith("https://")]
        return links
    except Exception as e:
        st.error(f"Error fetching links: {e}")
        return []

def extract_text(url, max_chars=10000):
    try:
        headers = {"User-Ani": "Brave/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[:max_chars]
    except Exception as e:
        return ""

def find_profanity(text):
    words = text.split()
    found = [word for word in words if profanity.contains_profanity(word)]
    return found

def summarise(web_content, query, comp_name):
    prompt = f"""
Think as a business specialist. Based on the following web search summaries, provide a structured and concise competitor analysis for: {query}

Company: {comp_name}

Web Results:
{web_content}

Your summary should include:
1. Introduction about the company/tool
2. Its competitors and alternatives
3. What else the competitors are offering
4. How {comp_name} can improve
5. A conclusion

Use the name "{comp_name}" throughout. Keep the tone analytical and helpful.
"""
    llm = Ollama(model="llama3.2")
    return llm.invoke(prompt)

def validate_input_type(input_text):
    validation_prompt = f"""
Is the following input a specific company name or a tool name?
Respond with "YES" if it is, and "NO" if it is a general query (like weather, news, a question, etc.), a person's name, or anything other than a company/tool.

Input: "{input_text}"

Answer:
"""
    llm = Ollama(model="llama3.2")
    response = llm.invoke(validation_prompt).strip().upper()
    return response == "YES"

st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #0a0a23;
            color: #f0f0f0;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #f0f0f0;
        }

        .stTextInput > div > div > input {
            background-color: #1a1a3d;
            color: white;
            border: 1px solid #5e239d;
        }

        .stTextArea textarea {
            background-color: #1a1a3d;
            color: white;
            border: 1px solid #5e239d;
        }

        .stButton > button {
            background-color: #5e239d;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1em;
            transition: background-color 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #7e3dc4;
        }

        .css-1cpxqw2 {  /* input labels and general text color */
            color: #f0f0f0 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("AI-Powered Competitor Analysis Tool (Simplified)")

comp_name = st.text_input("Enter a company or tool name for competitor analysis")

if st.button("Run Analysis") and comp_name:
    with st.spinner("Validating input..."):
        is_valid_input = validate_input_type(comp_name)

    if is_valid_input:
        query = f"{comp_name} competitor analysis 2025"
        st.write(f"Searching for: {query}")
        links = fetch_links(query)

        if links:
            st.subheader("Links Found")
            for i, link in enumerate(links):
                st.write(f"{i+1}. {link}")

            st.write("Extracting content...")
            texts = ""
            for i, link in enumerate(links):
                content = extract_text(link)
                if content:
                    offensive_words = find_profanity(content)
                    if offensive_words:
                        continue
                    texts += f"Source {i+1}: {link}\n{content}\n\n"

            if texts.strip():
                st.write("Generating summary...")
                summary = summarise(texts, query, comp_name)
                st.subheader("Competitor Analysis Summary")
                st.markdown(summary)
            else:
                st.error("No usable content found after filtering.")
        else:
            st.error("No links found.")
    else:
        st.warning("Please enter a valid company or tool name.")