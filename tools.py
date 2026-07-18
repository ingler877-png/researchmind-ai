from langchain.tools import tool
from bs4 import BeautifulSoup
from tavily import TavilyClient
import streamlit as st
import requests
import os
from dotenv import load_dotenv


# upload env file
load_dotenv()


# read tavily from local environment
tavily_api_key = os.getenv("TAVILY_API_KEY")



if not tavily_api_key:
    try:
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
    except Exception:
        tavily_api_key = None


# if any key is missing then show proper error
if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY is missing. "
        "Add it to the local .env file or Streamlit Cloud Secrets."
    )


# craete Tavily client
tavily = TavilyClient(api_key=tavily_api_key)


@tool
def web_search(query: str) -> str:
    """
    Search the web for recent and reliable information.
    Returns titles, URLs and content snippets.
    """
    try:
        response = tavily.search(
            query=query,
            max_results=6,
            search_depth="basic"
        )

        results = response.get("results", [])

        if not results:
            return "No relevant search results were found."

        formatted_results = []

        for index, item in enumerate(results, start=1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "No description available")

            formatted_results.append(
                f"{index}. Title: {title}\n"
                f"URL: {url}\n"
                f"Content: {content}\n"
            )

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and return clean text content from a URL.
    """
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
                )
            }
        )

        # HTTP errors from HTML
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Unnecessary HTML elements remove karo
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside"]
        ):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if not text:
            return "No readable content was found on this URL."

        return text[:5000]

    except requests.exceptions.Timeout:
        return "Could not scrape URL: Request timed out."

    except requests.exceptions.RequestException as e:
        return f"Could not scrape URL: {str(e)}"

    except Exception as e:
        return f"Could not process URL: {str(e)}"
    
