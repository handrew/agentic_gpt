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

## Output
It doesn't always get it right, but the below was a correct run.

```
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I should start by getting the company's website using the ticker EQT.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To find the investor relations page and proceed with the objective, I need to first get the company's website.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: get_company_website
INFO:agentic_gpt.agent.agentic_gpt:Completed action get_company_website. Result: https://www.eqt.com
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained the company's website URL, which is 'https://www.eqt.com'. Now I need to find the investor relations page.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to find the investor relations page from the company's website.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: get_all_links
INFO:pyppeteer.launcher:Browser listening on: ws://127.0.0.1:56574/devtools/browser/afc271ef-01ac-41d0-867a-7cdcb56e8655
INFO:agentic_gpt.agent.agentic_gpt:Completed action get_all_links. Result: ['https://media.eqt.com', 'https://www.eqt.com/connect-with-us/', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-Reports-Fourth-Quarter-and-Full-Year-2022-Results-and-Provides-2023-Guidance/default.aspx', 'https://www.eqt.com/sitemap/', 'https://www.eqt.com/wp-content/uploads/2023/06/News-Release-Signing-of-Fiscal-Responsibility-Act-6-2-23.pdf', 'https://www.eqt.com/community/eqt-foundation/', 'https://www.eqt.com/community/engagement/', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-Corporation-Schedules-First-Quarter-2023-Earnings-Release-and-Conference-Call/default.aspx', 'https://www.eqt.com/about/corporate-profile/', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-And-Wheeling-Park-Commission-Launch-Forestry-Management-Program-at-Oglebay/default.aspx', 'https://www.eqt.com/about/management-team/', 'https://www.eqt.com/operations/commercial/', 'https://www.eqt.com/contact/', 'https://www.eqt.com/operations/service-providers/', 'https://www.eqt.com/careers/', 'https://www.eqt.com/about/faq/', 'https://www.eqt.com/land-resources/forms-and-faqs/', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-Announces-CFO-Transition-Plan/default.aspx', 'https://www.eqt.com/privacy/', 'https://www.eqt.com/request-an-accommodation/', 'https://www.eqt.com/wp-content/uploads/2023/06/esg-2022.pdf', 'https://www.eqt.com/wp-content/uploads/2023/06/News-Release-Debt-Ceiling-Approval-Updated-6-2-23.pdf', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-And-Context-Labs-Announce-Strategic-Partnership/default.aspx', 'http://ir.eqt.com', 'https://www.eqt.com/land-resources/', 'https://www.eqt.com/land-resources/leasing-with-eqt/', 'https://www.eqt.com/community/', 'https://www.eqt.com/about/', 'https://www.eqt.com/responsibility/', 'https://ir.eqt.com/investor-relations/news/news-release-details/2023/EQT-Donates-Production-Equipment-to-Ukraine/default.aspx', 'https://www.eqt.com/equal-employment-opportunity/', 'https://www.eqt.com/terms-conditions/', 'https://www.eqt.com/about/board-of-directors/', 'https://www.eqt.com/land-resources/owner-relations/', 'https://www.eqt.com/responsibility/unleashing-us-lng/', 'https://www.eqt.com/responsibility/environment/', 'https://esg.eqt.com/', 'https://www.eqt.com/responsibility/safety/', 'https://www.eqt.com/operations/production/', 'https://www.eqt.com/responsibility/pneumatic-device-replacement/', 'https://www.eqt.com/operations/', 'https://media.eqt.com/investor-relations/news/default.aspx']
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained a list of URLs from the company's website. Now I need to choose the investor relations URL.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to select the URL that is most likely to be the investor relations page.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: choose_investor_relations_url
INFO:agentic_gpt.agent.agentic_gpt:Completed action choose_investor_relations_url. Result: https://ir.eqt.com/investor-relations/news/default.aspx
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained the investor relations URL, which is '{{choose_investor_relations_url_result}}'. Now I need to find the 'Events and Presentations' page.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to find the 'Events and Presentations' page from the investor relations URL.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: get_all_links
INFO:pyppeteer.launcher:Browser listening on: ws://127.0.0.1:56589/devtools/browser/65810033-23a3-45ee-9dcf-66bdedeb5957
INFO:agentic_gpt.agent.agentic_gpt:Completed action get_all_links. Result: ['https://ir.eqt.com/investor-relations/news/default.aspx', '//s24.q4cdn.com/922296017/files/doc_financials/2023/q1/Q1-2023-Earnings-Hedge-Table.pdf', 'https://www.eqt.com/contact/', 'https://ir.eqt.com/investor-relations/resources/investor-faqs/default.aspx', 'https://www.eqt.com/sitemap/', 'https://ir.eqt.com/investor-relations/events-and-presentations/events-calendar/default.aspx', 'https://ir.eqt.com/investor-relations/stock-information/dividend-plan/default.aspx', 'https://ir.eqt.com/investor-relations/resources/investor-email-alerts/default.aspx', 'https://www.eqt.com/', 'https://ir.eqt.com/investor-relations/stock-information/form-8937/default.aspx', 'https://ir.eqt.com/investor-relations/stock-information/analyst-coverage/default.aspx', '//s24.q4cdn.com/922296017/files/doc_financials/2023/q1/EQT-Q1-2023-Earnings-Guidance.pdf', 'https://ir.eqt.com/investor-relations/resources/rss-feeds/default.aspx', 'https://www.eqt.com/careers/', 'https://ir.eqt.com/investor-relations/stock-information/stock-info/default.aspx', 'https://www.eqt.com/about/management-team', 'https://ir.eqt.com/investor-relations/stock-information/dividend-history/default.aspx', 'https://www.eqt.com/privacy/', 'https://ir.eqt.com/investor-relations/governance/contact-the-board/default.aspx', 'https://ir.eqt.com/investor-relations/resources/advisory-to-user/default.aspx', 'https://ir.eqt.com/newsroom/news-releases/default.aspx', 'https://ir.eqt.com/newsroom/media-hq/default.aspx', 'https://ir.eqt.com/investor-relations/resources/investor-contacts/default.aspx', 'https://www.eqt.com/about/board-directors', 'https://ir.eqt.com/investor-relations/events-and-presentations/presentations/default.aspx', 'https://www.eqt.com/responsibility/', 'https://ir.eqt.com/investor-relations/financials/sec-filings/default.aspx', 'https://ir.eqt.com/investor-relations/financials/quarterly-results/default.aspx', 'https://www.eqt.com/terms-conditions/', 'https://ir.eqt.com/investor-relations/governance/governance-documents/default.aspx', 'https://ir.eqt.com/investor-relations/financials/annual-reports/default.aspx', 'https://ir.eqt.com/investor-relations/governance/committee-composition/default.aspx', 'https://ir.eqt.com/investor-relations/overview/default.aspx', 'https://ir.eqt.com/investor-relations/stock-information/transfer-agent-info/default.aspx']
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained a list of URLs from the investor relations page. Now I need to choose the 'Events and Presentations' URL.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to select the URL that is most likely to be the 'Events and Presentations' page.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: choose_events_and_presentation_url
INFO:agentic_gpt.agent.agentic_gpt:Completed action choose_events_and_presentation_url. Result: https://ir.eqt.com/investor-relations/events-and-presentations/presentations/default.aspx
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained the 'Events and Presentations' URL, which is '{{choose_events_and_presentation_url_result}}'. Now I need to get all the PDF links from that page.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to find all the PDF links from the 'Events and Presentations' page.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: get_pdf_links
INFO:pyppeteer.launcher:Browser listening on: ws://127.0.0.1:56619/devtools/browser/d0d22018-7803-448e-a6a1-57fa67048076
INFO:agentic_gpt.agent.agentic_gpt:Completed action get_pdf_links. Result: ['//s24.q4cdn.com/922296017/files/doc_financials/2023/q1/Q1-2023-Earnings-Hedge-Table.pdf', '//s24.q4cdn.com/922296017/files/doc_financials/2023/q1/EQT-Q1-2023-Earnings-Guidance.pdf', 'https://s24.q4cdn.com/922296017/files/doc_presentations/2023/EQT-Q4-2022-Earnings-Presentation.pdf', 'https://s24.q4cdn.com/922296017/files/doc_financials/2023/q1/EQT-Q1-2023-Earnings-Presentation.pdf']
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained the PDF links from the 'Events and Presentations' page. Now I need to choose the latest presentation link and download it.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To proceed with the objective, I need to select the latest presentation link and download the PDF file.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: choose_latest_presentation_url
INFO:agentic_gpt.agent.agentic_gpt:Completed action choose_latest_presentation_url. Result: https://s24.q4cdn.com/922296017/files/doc_financials/2023/q1/EQT-Q1-2023-Earnings-Presentation.pdf
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have obtained the latest presentation link, which is '{{choose_latest_presentation_url_result}}'. Now I need to download the PDF file.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: To complete the objective, I need to download the latest presentation PDF file.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: download_pdf
INFO:agentic_gpt.agent.agentic_gpt:Completed action download_pdf. Result: None
INFO:agentic_gpt.agent.agentic_gpt:

Thoughts: I have already completed all the necessary actions to achieve the objective. I have obtained the latest presentation link and downloaded the PDF file.
INFO:agentic_gpt.agent.agentic_gpt:Reasoning: Based on the previous actions and results, I have successfully completed the objective.
INFO:agentic_gpt.agent.agentic_gpt:Chosen action: declare_done
INFO:agentic_gpt.agent.agentic_gpt:Completed action declare_done. Result: None
INFO:agentic_gpt.agent.agentic_gpt:You have completed your objective!
INFO:pyppeteer.launcher:terminate chrome process...
INFO:pyppeteer.launcher:terminate chrome process...
INFO:pyppeteer.launcher:terminate chrome process...
```

## Commentary 

- Obviously, the heavy lifting of decision-making is being done by the `choose_..._url` functions, which, given a set of URLs and a description, asks an LLM to select the URL most rrelevant to the description. 
- Notice the decomposition of the problem into a set of building blocks. We give `AgenticGPT` seven capabilities (in addition to the ones that it comes with out of the box), as well as a prompt with a fairly detailed set of steps, to make sure it doesn't veer off. Even then, as of this writing (07/12/2023), it still doesn't get it right 100% of the time.
- Notice the verbiage of the prompt. If you have prompt engineered before (or maybe had an intern who was still learning the ropes), you probably can tell which parts were added through trial and error: the date and reminder that the presentation has to be a PDF.

