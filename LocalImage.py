from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import urllib
import os
import requests   #seems not used, but must have this library

def download_image(img_url,file_name,file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_suffix = os.path.splitext(img_url)[1]
        #print(file_suffix)
        # 拼接图片名（包含路径）
        filename = '{}{}{}{}'.format(file_path, os.sep, file_name, file_suffix)
        #print(filename)
        # 下载图片，并保存到文件夹中

        urllib.request.urlretrieve(img_url, filename=filename)
        message = 'success'
        #image=requests.get(img_url)
        #print(image)
        #with open(file_name,'wb') as f:
        #   f.write(image.content)
    except IOError as e:
        message="IOError"
        print(message)
    except Exception as e:
        message="Exception"
        print(message)
    return message

def get_now_time():
    a=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date=datetime.now().strftime("%d")
    hour=datetime.now().strftime("%H")
    min=datetime.now().strftime("%M")
    time_now=date+hour+min              #Date+Hour+Mins
    return time_now

def get_int_time(str_time):
    if(str_time[4] + str_time[5]=='00'):
        min=0
    else:
        min = int(str_time[4] + str_time[5])
    if(min>=10):
        int_min=str((int(min/10))*10)
    else:
        int_min='00'
    int_time=str_time[0]+str_time[1]+str_time[2]+str_time[3]+int_min
    return int_time

def last_10_mins_calculation(str_time):

    try:
        min=int(str_time[4]+str_time[5])        #min value from 0 to 59
    except ValueError:
        print(str_time[4]+str_time[5], 'mins error')
        min=0



    if (min>=20):
        str_min=str((int(min/10)-1)*10)
        str_hour=str_time[2]+str_time[3]
        str_date=str_time[0]+str_time[1]

    elif (min==10):
        str_min='00'
        str_hour =str_time[2]+str_time[3]
        str_date =str_time[0]+str_time[1]

    else:
        str_min='50'
        try:
            int_hour = int(str_time[2]+str_time[3])               #int_hour value from 0 to 23
        except ValueError:
            print(str_time[2]+str_time[3])
            int_hour=0

        if  (int_hour>=11):
            #print('work A')
            str_hour=str(int_hour-1)
            str_date=str_time[0]+str_time[1]
        elif ((int_hour>=1)&(int_hour<11)):
            #print('work B',int_hour)
            str_hour='0'+str(int_hour-1)
            str_date = str_time[0] + str_time[1]
        else:
            #print('work c')
            str_hour='23'
            int_date=int(str_time[0]+str_time[1])
            str_date=str(int_date-1)   #since only for this project, date range from 20-31 works

    a=str_date+str_hour+str_min             # should be strings
    return a

# get a time before
def get_HKO_UTC_time(str_time):

    try:
        ori_min=int(str_time[4]+str_time[5]) #00, 10, 20, 30, 40, 50
    except ValueError:
        ori_min=0
    try:
        ori_hour=int(str_time[2]+str_time[3])
    except ValueError:
        ori_hour=0

    if (ori_min>=20):
        UTC_min=str(ori_min-10)

        if (ori_hour>=9):
            if (ori_hour-8>=10):
                UTC_hour=str(ori_hour-8)
                UTC_date = str_time[0] + str_time[1]
            else:
                UTC_hour = '0'+str(ori_hour - 8)
                UTC_date=str_time[0]+str_time[1]
        elif(ori_hour==8):
            UTC_hour='00'
            UTC_date=str_time[0]+str_time[1]
        else:
            UTC_hour=str(16+ori_hour)
            UTC_date=str(int(str_time[0]+str_time[1])-1)            #date is not works for 1st
    elif(ori_min==10):
        UTC_min='00'
        if (ori_hour >= 9):
            if (ori_hour-8>=10):
                UTC_hour=str(ori_hour-8)
            else:
                UTC_hour = '0'+str(ori_hour - 8)

            UTC_date = str_time[0] + str_time[1]
        elif (ori_hour==8):
            UTC_hour = '00'
            UTC_date = str_time[0] + str_time[1]
        else:
            UTC_hour = str(16 + ori_hour)
            UTC_date = str(int(str_time[0] + str_time[1]) - 1)      #date is not works for 1st
    else:
        UTC_min='50'
        if (ori_hour >= 10):
            if((ori_hour - 9)>=10):
                UTC_hour = str(ori_hour - 9)
            else:
                UTC_hour = '0'+str(ori_hour - 9)
            UTC_date = str_time[0] + str_time[1]
        elif (ori_hour==9):
            UTC_hour = '00'
            UTC_date = str_time[0] + str_time[1]
        else:
            UTC_hour = str(15 + ori_hour)
            UTC_date = str(int(str_time[0] + str_time[1]) - 1)  # date is not works for 1st
    UTC_time=UTC_date+UTC_hour+UTC_min
    return UTC_time

#prepare pairs for HKO url
def pair_list_generation(time_now,number):
    init_time=get_int_time(time_now)
    time_pair=[]
    for i in range(0,number):
        record_local_time=last_10_mins_calculation(init_time)
        record_UTC_time=get_HKO_UTC_time(record_local_time)
        pair=[]
        pair=[record_local_time,record_UTC_time]

        time_pair.append(pair)
        init_time=record_local_time

    return time_pair

#refined_pair could be useful for change interval of image(from every 10 mins to other interval)
def image_interval(time_pair,interval,number):
    refined_pair=[]
    for i in range(number):
        if (i%interval==0):
            refined_pair.append(time_pair[i])
    return refined_pair

def get_url_list(time_pair):
    url_list=[]
    for item in time_pair:
        url="https://www.hko.gov.hk/wxinfo/intersat/satellite/image/e_infrared/201808"+item[0]+"+"+item[1]+"H08.nb_10S_50N_75_150E--L1B.H08_IR1_non_gis.jpg"
        url_list.append(url)
    return url_list

def func_HKO():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'HKO Start')
    current_time=get_now_time()
    original_list=pair_list_generation(current_time,36)
    display_list=image_interval(original_list,3,36)       # modify interval and time duration

    url_list=get_url_list(display_list)
    url_list.reverse()               # to get image by timeseries order

    #download images
    number = 0
    for i in url_list:
        try:
            a=download_image(i,str(number),'D:/UN Intership/IDD SAS Works/Task real time satellite/HKO')
            if (a=='success'):
                number = number + 1
        except ValueError:
            print('invalid url')
    Number_of_Images=number
    print(Number_of_Images)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'HKO Download Finish')
    chrome_options = Options()
    chrome_options.add_argument("--kiosk")
    chrome_options.add_argument("--disable-infobars")
    driver=webdriver.Chrome(r'C:\Webdriver\chromedriver.exe',chrome_options=chrome_options)
    #driver.maximize_window()
    driver.implicitly_wait(10)
    wait_time=36/Number_of_Images
    for times in range(5):
        for i in range(Number_of_Images):
            address='D:/UN Intership/IDD SAS Works/Task real time satellite/HKO/'+str(i)+'.jpg'
            driver.get(address)
            time.sleep(wait_time)                 #control refresh rate
            driver.implicitly_wait(10)
    driver.quit()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'HKO End')

# JMA PART
def get_latest_JMA_time():
    date = int(datetime.now().strftime("%d"))
    hour = int(datetime.now().strftime("%H"))
    min = int(datetime.now().strftime("%M"))

    if (hour >= 7):  # actually not need work, the UTC_hour range should be 1 to 10 in office hour
        UTC_hour = hour - 7
        UTC_date = date
    else:
        UTC_hour = hour + 17
        UTC_date = date - 1  # only if date is not the first day of the month

    if (UTC_date < 10):
        url_date = '0' + str(UTC_date)
    else:
        url_date = str(UTC_date)

    if (min >= 10) & (min < 20):  # to garrentee get the image, 10 mins delay
        url_min = '00'
        if (UTC_hour < 10):
            url_hour = '0' + str(UTC_hour)
        else:
            url_hour = str(UTC_hour)
    elif (min >= 20):
        url_min = str((int(min / 10) - 1) * 10)
        if (UTC_hour < 10):
            url_hour = '0' + str(UTC_hour)
        else:
            url_hour = str(UTC_hour)
    else:
        url_min = '50'
        if (UTC_hour < 11):
            url_hour = '0' + str(UTC_hour - 1)
        else:
            url_hour = str(UTC_hour - 1)

    url_time = url_date + url_hour + url_min
    return url_time
def last_10_mins_calculation_JP(str_time):

    try:
        min=int(str_time[4]+str_time[5])        #min value from 0 to 59
    except ValueError:
        print(str_time[4]+str_time[5], 'mins error')
        min=0



    if (min>=20):
        str_min=str((int(min/10)-1)*10)
        str_hour=str_time[2]+str_time[3]
        str_date=str_time[0]+str_time[1]

    elif (min==10):
        str_min='00'
        str_hour =str_time[2]+str_time[3]
        str_date =str_time[0]+str_time[1]

    else:
        str_min='50'
        try:
            int_hour = int(str_time[2]+str_time[3])               #int_hour value from 0 to 23
        except ValueError:
            print(str_time[2]+str_time[3])
            int_hour=0

        if  (int_hour>=11):
            #print('work A')
            str_hour=str(int_hour-1)
            str_date=str_time[0]+str_time[1]
        elif ((int_hour>=1)&(int_hour<11)):
            #print('work B',int_hour)
            str_hour='0'+str(int_hour-1)
            str_date = str_time[0] + str_time[1]
        else:
            #print('work c')
            str_hour='23'
            int_date=int(str_time[0]+str_time[1])
            str_date=str(int_date-1)   #since only for this project, date range from 20-31 works

    a=str_date+str_hour+str_min             # should be strings
    return a

def get_url_time_list_JP(url_time,number):
    initial_time=url_time
    url_time_list=[]
    url_time_list.append(url_time)
    for i in range(number):
        record_time=last_10_mins_calculation_JP(initial_time)
        url_time_list.append(record_time)
        initial_time=record_time
    return url_time_list

def get_JMA_list(url_time_list):
    url_list = []
    for item in url_time_list:
        url="http://www.jma.go.jp/en/gms/imgs_c/6/visible/1/201808"+item+"-00.png"          # only for august lol
        url_list.append(url)
    return url_list
def image_interval_JP(time_pair,interval,number):
    refined_pair=[]
    for i in range(number):
        if (i%interval==0):
            refined_pair.append(time_pair[i])
    return refined_pair

def func_JMA():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'JMA Start')
    latest_time=get_latest_JMA_time()
    #print(latest_time)
    original_list=get_url_time_list_JP(latest_time,36)
    display_list = image_interval_JP(original_list, 3, 36)
    #print(display_list)
    url_list = get_JMA_list(display_list)
    url_list.reverse()               # to get image by timeseries order
    print('ready for downloading')

    # download images
    number = 0
    for i in url_list:
        try:
            a=download_image(i, str(number), 'D:/UN Intership/IDD SAS Works/Task real time satellite/JMA')
            if (a=='success'):
                number = number + 1
        except ValueError:
            print('invalid url')
    Number_of_Images = number
    print(Number_of_Images)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'JMA Download Finish')


    driver=webdriver.Chrome(r'C:\Webdriver\chromedriver.exe')
    driver.maximize_window()
    driver.implicitly_wait(10)
    wait_time=(36/Number_of_Images)
    for times in range(5):
        for i in range(Number_of_Images):
            #JMA photo in png
            address='D:/UN Intership/IDD SAS Works/Task real time satellite/JMA/'+str(i)+'.png'
            driver.get(address)
            time.sleep(wait_time)                 #control refresh rate
            driver.implicitly_wait(10)
    driver.quit()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'JMA End')


#China

def get_int_time_CN(str_time):
    hour = str_time[2] + str_time[3]
    date = str_time[0] + str_time[1]
    int_time = hour + date + '00'
    return int_time


def get_1hour_before_CN(str_time):
    ori_hour = int(str_time[2] + str_time[3])
    ori_date = int(str_time[0] + str_time[1])
    if (ori_hour >= 11):
        new_hour = str(ori_hour - 1)
        new_date = str(ori_date)  # valid for 20-31
    elif (ori_hour < 11) & (ori_hour >= 1):
        new_hour = '0' + str(ori_hour - 1)
        new_date = str(ori_date)
    else:
        new_hour = '23'
        new_date = str(ori_date - 1)
    new_time = new_date + new_hour + '00'
    return new_time


def get_UTC_Time_CN(str_time):
    new_time = str_time
    for i in range(7):
        new_time = get_1hour_before_CN(new_time)
    return new_time


def get_CN_time_List(ini_time, number):
    raw_ini_time = get_UTC_Time_CN(ini_time)
    initial_time = raw_ini_time[0] + raw_ini_time[1] + '_' + raw_ini_time[2] + raw_ini_time[3] + '00'
    CN_time_list = []
    CN_time_list.append(initial_time)
    for i in range(number):
        raw_record = get_1hour_before_CN(raw_ini_time)
        record = raw_record[0] + raw_record[1] + '_' + raw_record[2] + raw_record[3] + '00'
        CN_time_list.append(record)
        raw_ini_time = raw_record
    return CN_time_list


def get_CN_url_List(time_list):
    url_list = []
    for item in time_list:
        url = "http://img.nsmc.org.cn/CLOUDIMAGE/FY2G/lan/FY2G_LAN_VIS_GRA_201808" + item + ".jpg"
        url_list.append(url)
    return url_list


def func_NSMC():
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'NSMC Start')
    latest_time = get_now_time()
    time_list = get_CN_time_List(latest_time, 12)
    url_list = get_CN_url_List(time_list)
    url_list.reverse()
    #print(url_list)
    # download images
    number = 0
    for i in url_list:
        try:
            a = download_image(i, str(number), 'D:/UN Intership/IDD SAS Works/Task real time satellite/NSMC')
            if (a == 'success'):
                number = number + 1
        except ValueError:
            print('invalid url')
    Number_of_Images = number
    print(Number_of_Images)
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'NSMC Download Finish')

    driver = webdriver.Chrome(r'C:\Webdriver\chromedriver.exe')
    driver.maximize_window()
    driver.implicitly_wait(10)
    waiting_time = 36 / Number_of_Images
    for times in range(5):
        for i in range(Number_of_Images):
            address = 'D:/UN Intership/IDD SAS Works/Task real time satellite/NSMC/' + str(i) + '.jpg'
            driver.get(address)
            time.sleep(waiting_time)  # control refresh rate
            driver.implicitly_wait(10)
    driver.quit()
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'NSMC End')


scheduler =BlockingScheduler()

#scheduler.add_job(func_NSMC,'date',next_run_time=datetime.now())
#scheduler.add_job(func_HKO,'date',next_run_time=datetime.now()+timedelta(seconds=5))
scheduler.add_job(func_HKO,'interval',seconds =530,next_run_time=datetime.now())
scheduler.add_job(func_JMA,'interval',seconds =530,next_run_time=datetime.now()+timedelta(seconds=175))
scheduler.add_job(func_NSMC,'interval',seconds =530,next_run_time=datetime.now()+timedelta(seconds=355))
scheduler.start()

'''
img_url='https://www.hko.gov.hk/wxinfo/intersat/satellite/image/e_infrared/201808201410+200600H08.nb_10S_50N_75_150E--L1B.H08_IR1_non_gis.jpg'
file_name="haha1"
file_path='D:/UN Intership/IDD SAS Works/Task real time satellite/HKO'
download_image(img_url,file_name,file_path)
'''