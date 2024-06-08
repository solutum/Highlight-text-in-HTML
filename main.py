import warnings
import requests
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def insert_tag_at_index(text, index, tag):
	if index < 0 or index > len(text):
		raise ValueError("Index is out of range")
	
	before = text[:index]
	after = text[index:]
	
	new_text = before + tag + after
	return new_text


def highlight_string(html, search_text, highlight_tag):
	match_counter = 0

	new_html = html
	end_string = None
	
	for i in range(len(html)):
		soup = BeautifulSoup(html[i:], 'html.parser')
		html_without_tags = soup.get_text()
		# ADD OPEN TEG
		if html_without_tags.startswith(search_text):
			if html[i:i+1] != "<":
				# print(f"index = {i}")
				new_html = insert_tag_at_index(new_html, i + (len(highlight_tag['start']+highlight_tag['end']) * match_counter), highlight_tag['start']) # + offset
				match_counter += 1

				parts = html_without_tags.split(search_text)
	
				end_string = parts[1].strip() if len(parts) > 1 else ''
				# print(f"{end_string=}")

		# ADD CLOSING TAG
		if end_string and html_without_tags.startswith(end_string):
			# if html[i:i+1] != "<":
			# print(f"end_index = {i}")
			new_html = insert_tag_at_index(new_html, i + (len(highlight_tag['start'] * match_counter) + len(highlight_tag['end'] * (match_counter-1))), highlight_tag['end'])
			end_string = None
		# print(html[i:])
	return new_html


def all_elements_in_string(elements, string):
    return all(element in string for element in elements)


def find_all_deepest_tags_with_text(soup, search_words):
    result = []

    def search_tag(tag, search_words):
        # CHECK if current tag has the text and no child tags also have the text
        if all_elements_in_string(search_words, tag.get_text(strip=True)):
            child_has_text = False
            for child in tag.find_all(True, recursive=False):
                if all_elements_in_string(search_words, child.get_text(strip=True)):
                    child_has_text = True
                    search_tag(child, search_words)
            if not child_has_text:
                result.append(tag)
    
    search_tag(soup, search_words)
    return result


def main(url, search_text, highlight_tag):
	search_words = search_text.split()
	modified_html = None

	response = requests.get(url)
	if response.status_code != 200:
		print("Error getting URL")
		exit()
	html = response.text

	# with open('page_content.html', 'r', encoding='utf-8') as file:
	# 	html = file.read()

	soup = BeautifulSoup(html, 'html.parser')
	str_soup = str(soup)

	result_tags = find_all_deepest_tags_with_text(soup, search_words)

	if result_tags:
		print(f"Total results for '{search_text}': {len(result_tags)}")
		for tag in result_tags:
			if search_text in tag.get_text():
				# print(tag)
				decode_contents = tag.decode_contents()
				new_html = highlight_string(decode_contents, search_text, highlight_tag)

				# print(f'\nModified HTML-code:\n{new_html}\n')
				modified_html = str_soup.replace(decode_contents, new_html)

		# SAVE
		if modified_html:
			save_to = "modified_page.html"
			with open(save_to, "w", encoding='utf-8') as file:
				file.write(str(modified_html))
				print(f"Modified HTML file saved to: {save_to}")
	else:
		print(f"No results for: {search_text}")


if __name__ == "__main__":
	url = "https://en.wikipedia.org/wiki/Elon_Musk"
	search_text = "A member of the wealthy South African Musk family, Musk was born in Pretoria and briefly attended the University of Pretoria before immigrating to Canada at age 18"
	# search_text = "and CTO of"
	# search_text = "a spaceflight services company, in 2002"
	# search_text = "Notes and references"
	highlight_tag = {
		'start': "<span style='background-color: red; color: white;'>",
		'end': "</span>"
	}

	main(url, search_text, highlight_tag) # -> modified_page.html
