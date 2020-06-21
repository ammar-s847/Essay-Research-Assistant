from flask import Flask, redirect, url_for, render_template, request, flash
from bs4 import BeautifulSoup
from requests import get

def get_html_code(url):
	return get(url).text

def get_google_html(query, keywords):
	query = query.replace(" ", "+")
	url = f"https://google.com/search?q={query}"

	if keywords:
		for word in keywords:
			url += f"+\"{word}\"+OR"
		url = url[:-3]

	return get_html_code(url)

def get_paragraphs(url, query, keywords):
	html_code = get_html_code(url)
	soup = BeautifulSoup(html_code, "html.parser")
	paragraphs = []

	for paragraph in soup("p"):
		paragraph = " ".join(paragraph.get_text().split())
		if not paragraph == "" and (query in paragraph or
			any(kw in keywords for kw in paragraph)):
			paragraphs.append(paragraph)

	return paragraphs

def get_top_links(html_code):
	soup = BeautifulSoup(html_code, "html.parser")
	avoidLinks = tuple(["https://www.youtube", "http://scholar.google"])
	links = []

	for div in soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd"):
		div.decompose()

	for div in soup.find_all("div", class_="kCrYT"):
		for link in div.find_all("a"):
			currentLink = link.get("href")
			if "&sa=" in currentLink and not any(al in currentLink for al in avoidLinks):
				links.append(currentLink[7:currentLink.index("&sa=")])

	return links

# BS4 Stuff
###########################################################################################
# Flask Stuff

app = Flask(__name__)   # Initializes app instance 
app.secret_key = "0RjiQhdtLs"
temp = "#"


@app.route("/", methods=["POST", "GET"])    # Sets URL tag for home page and initializes HTTP protocols 
@app.route("/#", methods=["POST", "GET"]) 
def home():                                 # Defines and renders home page
	if request.method == "POST":
		user_input = []
		paragraphs = []

		topic = request.form["research"]
		user_input = request.form["keywords"].split(", ")

		links = get_top_links(get_google_html(topic, user_input))

		for link in links:
			paragraphs.append(get_paragraphs(link, topic, user_input))

		check_empty = False
		for word in user_input:
			if not word:    
				check_empty =True

		if check_empty:
			flash("Fill in all the boxes!")
			return redirect(url_for("home"))

		return redirect(url_for("research", words=["12", "34", "56"]))
	else: 
		return render_template("home.html")

@app.route("/<words>")                                      # Sets URL tag for research page
def research(words):                                        # Defines and renders research page
	paragraphs = []
	paragraphs = words[1:len(words)-1].split(", ")			# Turns words from a string to a list to be printed

	return render_template("research.html", content=["test1", "test2", "test3"])	# Renders website
	
if __name__ == "__main__":  # Runs website
	app.run(debug=True)
