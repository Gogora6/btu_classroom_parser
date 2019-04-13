import requests
from bs4 import BeautifulSoup
import re

def connect(post_login_url, payload, request_url):
    with requests.Session() as session:
        post = session.post(post_login_url, data=payload)  # ავტორიზაცია
        source = session.get(request_url)  # გვერდი რომლის ჩატვირთვაც გვინდა

        source = source.text
        soup = BeautifulSoup(source, "html.parser")

        return soup


def only_course_names(soup):
    table = soup.find('table')
    tbody = table.find('tbody')
    courses = tbody.find_all('td')  # კურსებზე ინფორმაცია

    result = {}  # ახლანდელი კურსები და ქულები

    names = []
    try:
        course_names = (courses[2::][0::6])[0:6]
        for name in course_names:
            names.append(name.text.strip('\n').strip('\t'))

        scores = []
        student_scores = courses[3::][0::6]
        for score in student_scores:
            scores.append(score.text.strip('\n').strip('\t'))

        for index, course in enumerate(names):
            result[course] = scores[index]

        return result

    except IndexError: # easy solution :Dd
        return result


def get_urls(post_login_url, request_url, payload):
    soup = connect(post_login_url, payload, request_url)
    urls = []

    table = soup.find('table')
    tbody = table.find('tbody')

    for link in tbody.findAll('a', attrs={'href': re.compile("^https://")}):
        urls.append(link.get('href'))

    return urls


def get_scores(post_login_url, payload):
    request_url = "https://classroom.btu.edu.ge/ge/student/me/courses"

    scores = {}

    urls = get_urls(post_login_url, request_url, payload)

    for item in urls:
        item = item.replace('index', 'scores')
        request_url = item 
        soup = connect(post_login_url, payload, request_url)

        course_name = soup.find('legend').text

        table = soup.find('table')
        tbody = table.find('tbody')

        tests = tbody.findAll("td", {"class" : "info"})
        tests = [test.text.strip() for test in tests]
        
        evaluation = tbody.findAll("div", {"style" : "padding-left:20px"})
        evaluation = [ev.text.strip() for ev in evaluation]
        
        course_data = dict(zip(tests, evaluation))
        scores[course_name] = course_data

    return scores


def messages(post_login_url, payload):
    request_url = "https://classroom.btu.edu.ge/ge/messages"

    urls = get_urls(post_login_url, request_url, payload)

    messages_data = {}

    for index, item in enumerate(urls):
        request_url = item # url-ების გამოყენებით მთლიანი მესიჯის ნახვა
        soup = connect(post_login_url, payload, request_url)

        table = soup.find('fieldset')
        sender = soup.find('legend')
        time = sender.find('date')
 
        message = table.find("div", {"id" : "message_body"})
        messages_data[index] = [{"sender" : sender.text[:-17].strip()},{"time" : time.text},
                                 {"message" : message.text}]



    return messages_data
