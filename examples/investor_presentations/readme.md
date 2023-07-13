# Downloading Investor Presentations

## Motivation

Many publicly traded companies upload investor presentations to their website, usually once a quarter, to accompany their earnings calls. Entire businesses — like Bloomberg, Capital IQ, FactSet, and others — exist to collate financial data from these companies, but such datasets usually are limited to the (relatively) well-formatted, well-structured tabular financial data that these same companies file with the SEC. Investor presentations are not always uploaded to the same services and managed databases, but rather live on the companies' websites. 

Accordingly, at least some part of a financial analyst's job is to find these presentations and peruse them for any potentially interesting material. In order to do that, they have to be able to navigate through and find the link to such presentations. For humans, this is obviously a trivial task; it is easy for anyone to navigate through a new website and find what they need, especially if they generally come to expect a certain form or flow to the category of websites they browser, even if the flows may differ from website to website. 

It is not as easy to imagine programming a script which can, given any company's website, download the latest investor presentation. This is because there are a myriad edge cases which may be unique to each website. The HTML tags, classes, and divs may differ from site to site; sometimes, it is on the front page of the investor relations page and other times you may have to seek out a "presentations" tab; sometimes, the company may not have uploaded a presentation at all! 

The reasoning capability of LLMs help address some of these challenges. In particular, LLM agents can uniquely reason about their environment and decide, like a human, whether they have accomplished the objective or if they have to take further steps. By contrast, a traditional piece of software is hardcoded; it is inert, and cannot adapt to its environment. It breaks when encountering a situation it has not explicitly been given guidelines to address. 

## Architecture

See the code file in this directory. Below is a summary.

`AgenticGPT` is initialized with the following actions:

```python
actions = [
    Action(
        name="get_company_website",
        description="Given a stock ticker, visit Yahoo! Finance to get its corporate website.",
        function=get_company_website,
    ),
    Action(
        name="get_all_links",
        description="Get relevant links from a url.",
        function=get_self_links_and_pdf_links_from_url,
    ),
    Action(
        name="get_pdf_links",
        description="Get all the PDF links from a url.",
        function=get_pdf_links,
    ),
    Action(
        name="choose_investor_relations_url",
        description="Given a list of links, choose the one that is most likely to be the investor relations URL.",
        function=choose_investor_relations_url,
    ),
    Action(
        name="choose_events_and_presentation_url",
        description='Given a list of links, choose the one that is most likely to be the "Events and Presentations" URL.',
        function=choose_events_and_presentation_url,
    ),
    Action(
        name="choose_latest_presentation_url",
        description="Given a list of links, choose the one that is most likely to be the latest presentation URL.",
        function=choose_latest_presentation_url,
    ),
    Action(
        name="download_pdf",
        description="Download a PDF from a url",
        function=download_pdf,
    ),
]
```

... and it was initialized as follows, with the below prompt: 

```python
ticker = "EQT"
todays_date = datetime.datetime.today().strftime("%Y-%m-%d")
objective = f"""For the given ticker {ticker}:
1. Get to the company's website.
2. Find the investor relations page from the website. It should be a self link. Sometimes it will be called "Investors", "Investor Relations", or "IR".
3. If there is an "Events and Presentations" page, go to that page. If there is a separate Events or Calendar page and a Presentations page, then choose the Presentations page. 
4. Get all the PDF links from that page.
5. Find the latest presentation link and download it. Today's date is {todays_date}. The link must end with ".pdf"."""
agent = AgenticGPT(
    objective, actions_available=actions, model="gpt-3.5-turbo-16k"
)
```

## Running

You run it as you would a normal script:

`python download_investor_presentations.py`.

## Commentary 

- Notice the decomposition of the problem into a set of building blocks. We give `AgenticGPT` seven capabilities (in addition to the ones that it comes with out of the box), as well as a prompt with a fairly detailed set of steps, to make sure it doesn't veer off. Even then, as of this writing (07/12/2023), it still doesn't get it right 100% of the time.
- Notice the verbiage of the prompt. If you have prompt engineered before (or maybe had an intern who was still learning the ropes), you probably can tell which parts were added through trial and error: the date and reminder that the presentation has to be a PDF.