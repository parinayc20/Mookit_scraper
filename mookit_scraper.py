from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from getpass import getpass
import csv
import time

try:
    login_url = "https://hello.iitk.ac.in/index.php/user/login"
    
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')

    driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options) 

    driver.get(login_url) 

    username = input("Username: ")
    password = getpass()    

    driver.find_element("name", "name").send_keys(username)							
    driver.find_element("name", "pass").send_keys(password)	
    driver.find_element("name", "op").click()

    course = input("Enter the name of the course\neg- If course name is TA201A enter ta201a\n")
    course = course.lower()
    driver.get(f"https://hello.iitk.ac.in/{course}2223/#/home")

    print("Please Wait...")

    # time.sleep(5)

    weeks = driver.find_elements("class name", "weekDetailsBox")

    week_num = 0
    lecture_data = list()
    total_lectures = 0

    for week in weeks:
        week_num = week_num + 1
        headings = week.find_elements("tag name", "li")
        for heading in headings:
            heading_name = heading.find_element("class name", "weekListItemTitle").text
            lectures = heading.find_elements("class name", "lectureItem")
            for lecture in lectures: 

                lecture_name = lecture.find_element("class name", "lectureInfoBoxText").text
                try:
                    resources = lecture.find_element("class name", "lectureInfoBoxResources")
                except:
                    resources = lecture.find_element("class name", "lectureInfoBoxResourcesWatched")
                try:
                    resource_link = resources.find_element("tag name", "a").get_property('href')
                except:
                    try:
                        resources.find_element("tag name", "img").click()
                        links = driver.find_elements("class name", "lectureResourcesDialogBox")
                        resource_link = ""
                        for link in links:
                            resource_link = resource_link + link.find_element("tag name", "a").get_property('href') + "\n"
                        driver.find_element("class name", "dialogExitButton").click()
                        time.sleep(1)
                    except:
                        resource_link = "No Resource Provided"

                data = dict()
                data['Week'] = 'Week ' + str(week_num)
                data['Heading'] = heading_name
                data['Name'] = lecture_name
                data['Resource Link'] = resource_link
                lecture_time = lecture.find_element("class name", "lectureInfoBoxLength").text
                if heading_name != '':
                    if lecture_time == '00:00':
                        data['Lecture Link'] = "No Lecture Video"
                    else:
                        data['Lecture Link'] = lecture.find_element("tag name", "a").get_property('href')
                        
                lecture_data.append(data)
                total_lectures = total_lectures + 1

    driver.find_element("tag name", 'body').send_keys(Keys.CONTROL + Keys.HOME)
    week_toggle  = driver.find_elements("class name", "weekItem")

    for week in week_toggle:
        time.sleep(1)
        week.click()

    total_lectures = 0

    for week in weeks:
        headings = week.find_elements("tag name", "li")
        for heading in headings:
            heading_name = heading.find_element("class name", "weekListItemTitle").text
            lectures = heading.find_elements("class name", "lectureItem")
            for lecture in lectures: 
                lecture_name = lecture.find_element("class name", "lectureInfoBoxText").text
                if lecture_data[total_lectures]['Heading'] == '':
                    lecture_data[total_lectures]['Heading'] = heading_name
                    lecture_data[total_lectures]['Name'] = lecture_name
                    lecture_time = lecture.find_element("class name", "lectureInfoBoxLength").text
                    if lecture_time == '00:00':
                        lecture_data[total_lectures]['Lecture Link'] = "No Lecture Video"
                    else:
                        lecture_data[total_lectures]['Lecture Link'] = lecture.find_element("tag name", "a").get_property('href')    
                total_lectures = total_lectures + 1

    print()
        
    if total_lectures == 0:
        print("No lectures found")
        driver.close()
        exit(0)

    n = total_lectures

    # n = int(input("Enter the number of lectures to scrape\n"))

    # if n > total_lectures:
    #     print(f'Only {total_lectures} lectures found')
    #     choice = input("Do you want to scrape all? (Yes/No)\n")
    #     while(True):
    #         if(choice == "Yes"):
    #             n = total_lectures
    #             break
    #         elif(choice == "No"):
    #             driver.close()
    #             exit(0)
    #         else:
    #             print("Enter a valid choice")
    #             choice = input("Do you want to scrape all? (Yes/No)\n")

    if n == 0:
        exit(0)

    lecture_data.reverse()
    filename = open("LectureData.csv", "w", newline='')
    headers = ['Heading', 'Name', 'Week', 'Resource Link', 'Lecture Link']
    writer = csv.DictWriter(filename, fieldnames = headers)
    writer.writeheader()
    writer.writerow(dict())

    print("Scraping Please Wait...")

    for index in range(0,n):
        data = lecture_data[index]
        if data['Lecture Link'] == "No Lecture Video":
            writer.writerow(data)
            continue
        driver.get(data['Lecture Link'])
        time.sleep(1.5)
        try:
            # action = ActionChains(driver)
            # controller = driver.find_element("id", "speedPlus")
            # action.move_to_element(controller).perform()
            # try:
            #     resolutions = driver.find_element("id", "videoResoultions").find_elements("tag name", "span")
            #     resolutions[5].click()
            #     time.sleep(1)
            # except:
            #     pass
            video_link = driver.find_element("tag name", "iframe").get_property("src")
            # video_link = video.find_element("tag name", "source").get_property("src")
        except:
            video_link = driver.find_element("id", "youtubePlayer").get_property("src")
        data['Lecture Link'] = video_link
        writer.writerow(data)

    print("Done")

finally:
    driver.close()

