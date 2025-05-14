from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import streamlit as st
import random

api_key = st.secrets["GOOGLE_GEMINI_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    google_api_key=api_key,
    temperature=0.4 
)

if "suggested_books" not in st.session_state:
    st.session_state.suggested_books = []

st.title("📚 Book Recommendation")

genre = st.text_input("📖 Genre / Type (e.g. Sci-fi, Literary Fiction, Magical Realism)")
language = st.text_input("🌍 Language of Summary")
region = st.selectbox("🌐 Prefer a Region", ["No Preference", "Japanese", "Russian", "European", "Latin American", "Middle Eastern", "African", "Southeast Asian", "Eastern European"])
manual_exclude = st.text_input("🚫 Exclude These Books or Authors (comma separated)")
paragraph = st.number_input("📝 Summary: Number of Paragraphs", min_value=1, max_value=5, value=2)

literary_hints = [
    "focus on underrepresented literary voices",
    "highlight works by postmodern or surrealist writers",
    "avoid bestselling or overly commercial titles",
    "recommend award-winning but less globally known works",
    "suggest experimental or nonlinear narratives",
    "focus on authors who challenge traditional literary forms",
    "prioritize philosophical or existential themes",
    "include magical realism or speculative fiction influences",
    "avoid books adapted into Hollywood films",
    "explore literature dealing with memory, trauma, or identity",
    "recommend novels inspired by folklore or mythology",
    "highlight writers known for poetic prose or ambiguity",
    "focus on classic and contemporary works from Russian literature",
    "recommend books from the Silver Age of Russian poetry or Soviet-era writers",
    "highlight philosophical depth and psychological complexity found in Russian novels",
    "explore Japanese literature emphasizing minimalism and emotional restraint",
    "recommend works influenced by Zen aesthetics or mono no aware themes in Japanese writing",
    "highlight novels by Japanese authors exploring urban alienation or traditional vs modern identity",
]


random_hint = random.choice(literary_hints)

if genre and language:
    excluded_list = [x.strip() for x in manual_exclude.split(",") if x.strip()]
    excluded_list += st.session_state.suggested_books
    excluded_clause = f"Exclude the following: {', '.join(set(excluded_list))}. " if excluded_list else ""

    region_clause = f"Prefer books from {region} literature. " if region != "No Preference" else ""

    prompt_template = PromptTemplate(
        input_variables=["genre", "language", "paragraph", "excluded_clause", "region_clause", "literary_hint"],
        template=(
            "Recommend a unique, high-quality book in the {genre} genre. "
            "{excluded_clause}"
            "{region_clause}"
            "Avoid well-known commercial or mainstream titles. Instead, {literary_hint}. "
            "Summarize the recommended book in {paragraph} short paragraph(s) in {language}."
        )
    )

    query = prompt_template.format(
        genre=genre,
        language=language,
        paragraph=paragraph,
        excluded_clause=excluded_clause,
        region_clause=region_clause,
        literary_hint=random_hint
    )

    response = llm.invoke(query)
    content = response.content.strip()

    if "</think>" in content:
        content = content.split("</think>")[-1].strip()

    first_line = content.splitlines()[0]
    if first_line:
        book_title = first_line.split(".")[0].strip("–-•* ")
        if book_title and book_title not in st.session_state.suggested_books:
            st.session_state.suggested_books.append(book_title)

    st.subheader("📘 Recommended Book:")
    st.write(content)
