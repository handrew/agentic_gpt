"""Use AgenticGPT to download investor presentations."""
import datetime
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup

load_dotenv()
from agentic_gpt.agent import AgenticGPT
from agentic_gpt.agent.utils.llm_providers import get_completion
from agentic_gpt.agent.action import Action
from playwright.sync_api import sync_playwright


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def _get_domain_of_url(url):
    """From https://www.example.com, get example.com."""
    netloc = urlparse(url).netloc
    return ".".join(netloc.split(".")[-2:])


def get_company_website(ticker):
    """Visits Yahoo! Finance to get the company website."""
    url = f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    profile = soup.find("div", {"class": "asset-profile-container"})
    return profile.findAll("a")[-1]["href"]


def get_self_links_and_pdf_links_from_url(url):
    """Visits a url and grabs all the links that link back to itself."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        links = page.query_selector_all("a")
        original_domain = _get_domain_of_url(url)
        relevant_links = []
        for link in links:
            href = link.get_attribute("href")
            if href is None:
                continue
            domain = _get_domain_of_url(href)
            if domain == original_domain or href.startswith("/") or href.endswith(
                ".pdf"
            ):
                relevant_links.append(href)

        browser.close()
        return relevant_links


def get_pdf_links(url):
    """Visits a url and grabs all the links that end with pdf."""
    links = get_self_links_and_pdf_links_from_url(url)
    pdf_links = []
    for link in links:
        if link.endswith(".pdf"):
            pdf_links.append(link)
    return pdf_links


def _choose_url_template(urls, where_am_i=None, objective=None):
    """Set up a prompt to OpenAI to ask for what the right link is."""
    assert (
        where_am_i is not None
    ), "Must give a description of where the urls came from."
    assert objective is not None, "Must give an objective for choosing the urls."
    prompt = f"""Below, you are given a list of URLs found on a publicly traded company's front page.

{objective}\n\n"""

    for url in urls:
        prompt += f"{url}\n"

    prompt += "\nPlease return your answer with the URL alone, with no other commentary or HTML tags. Do not enclose it in quotes as a string."
    prompt += "\nYour answer: "
    completion = get_completion(prompt, model="gpt-3.5-turbo-16k")
    return completion


def choose_investor_relations_url(urls):
    """In the list of urls given, find the one that links to the investor relations page."""
    objective = """I would like to get to the investor relations page, and in particular, any "events and presentations" page that may exist.
It shouldn\'t be a url that leads to a specific announcement, but rather to the page which contains all the announcements.
Sometimes it will be called "Investors", "Investor Relations", or "IR".
It should be the shortest link that leads to the investor relations page.
Please choose the url which links to the investor relations page or which you think will most likely link to the investor relations page."""
    return _choose_url_template(
        urls, where_am_i="publicly traded company's front page", objective=objective
    )


def choose_events_and_presentation_url(urls):
    """In the list of urls given, find the one that links to the events and presentations url."""
    objective = """I would like to get to the events and presentations page, or better yet, to the latest presentation.
It shouldn\'t be a url that leads to a specific announcement, but rather to the page which contains all the presentations.
It should be the shortest link that leads to events and presentations page, or ideally, just the presentations page."""
    return _choose_url_template(
        urls,
        where_am_i="publicly traded company's investor relations page",
        objective=objective,
    )


def choose_latest_presentation_url(urls):
    """In the list of urls given, find the one that links to the latest presentation."""
    todays_date = datetime.datetime.now().strftime("%Y-%m-%d")
    objective = "I would like to get to the latest investor presentation or earnings presentation. Today's date is {todays_date}."
    return _choose_url_template(
        urls,
        where_am_i="publicly traded company's events and presentations page",
        objective=objective,
    )


def download_pdf(url):
    """Download a PDF from a url."""
    assert url.endswith(".pdf"), "Provided url must be a PDF."
    if url.startswith("//"):
        url = "https:" + url

    response = requests.get(url)
    response.raise_for_status()

    save_path = url.split("/")[-1]
    if not save_path.endswith(".pdf"):
        save_path += ".pdf"
    with open(save_path, "wb") as file:
        file.write(response.content)


def main():
    actions = [
        Action(
            name="get_company_website",
            description="Given a stock ticker, visit Yahoo! Finance to get its corporate website.",
            function=get_company_website,
        ),
        Action(
            name="get_all_links",
            description="Get relevant links from a url (links that link back to its own domain and links to PDFs).",
            function=get_self_links_and_pdf_links_from_url,
        ),
        Action(
            name="get_pdf_links",
            description="Get all the PDF links from a url.",
            function=get_pdf_links,
        ),
        Action(
            name="choose_investor_relations_url",
            description="Given a list of links, choose the one that is most likely to be the investor relations URL. Usually called after `get_all_links`.",
            function=choose_investor_relations_url,
        ),
        Action(
            name="choose_events_and_presentation_url",
            description='Given a list of links, choose the one that is most likely to be the "Events and Presentations" URL. Usually called after `get_all_links`',
            function=choose_events_and_presentation_url,
        ),
        Action(
            name="choose_latest_presentation_url",
            description="Given a list of links, choose the one that is most likely to be the latest presentation URL. Always called after `get_pdf_links`",
            function=choose_latest_presentation_url,
        ),
        Action(
            name="download_pdf",
            description="Download a PDF from a url",
            function=download_pdf,
        ),
    ]

    ticker = "EQT"
    objective = f"""For the given ticker {ticker}:
1. Get to the company's website.
2. Find the investor relations page from the website.
3. If there is an "Events and Presentations" page, go to that page.
4. Get all the PDF links from that page.
5. Find the latest presentation link and download it. The link must end with ".pdf".
6. Then you're done!"""

    agent = AgenticGPT(
        objective, actions_available=actions, model="gpt-3.5-turbo-16k", max_steps=15
    )
    agent.run()


if __name__ == "__main__":
    main()
