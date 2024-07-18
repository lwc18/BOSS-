import time
import requests
from PIL import Image
from io import BytesIO
from playwright.sync_api import sync_playwright


class JobScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.url = None

    def launch_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def login_page(self):
        self.navigate_to_page("https://www.zhipin.com/web/user/?ka=header-login")
        self.page.wait_for_load_state('networkidle')
        self.page.query_selector(".wx-login-btn").click()
        self.page.wait_for_selector(".mini-qrcode")
        image_element = self.page.query_selector('.mini-qrcode')
        if image_element:
            src = image_element.get_attribute('src')
            # print(src)
            self.download_and_show_image(src)
        else:
            print("微信登录二维码拉取失败")

    def navigate_to_page(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state('load')  # 等待页面加载完成

    def download_and_show_image(self, url):
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image.show()

    def input_url(self):
        self.url = input("请输入搜索的url")

    def scrape_jobs(self):
        # 每天的次数限制是100 自动投递数量是三页 90个
        # 留了十个位置可以自己手动筛选投递
        for x in range(1, 4):
            self.navigate_to_page(
                f"{self.url}&page={x}"
            )
            self.page.wait_for_selector('.job-list-box', timeout=10000)  # 等待包含工作列表的ul元素加载
            job_list = self.page.query_selector('.job-list-box')
            job_elements = job_list.query_selector_all('li.job-card-wrapper')  # 获取ul中的所有li元素
            for element in job_elements:
                time.sleep(1)
                element.hover()
                element.wait_for_selector('text="立即沟通"', timeout=20000)
                chat_button = element.query_selector('text="立即沟通"')
                if chat_button:
                    chat_button.click()
                    self.page.wait_for_selector('text="留在此页"', timeout=20000)
                    stay_button = self.page.query_selector('text="留在此页"')
                    if stay_button:
                        stay_button.click()
                job_name = element.query_selector('.job-name')
                company_name = element.query_selector('.company-name')
                if job_name and company_name:
                    job_name_text = job_name.text_content().strip()
                    company_name_text = company_name.text_content().strip()
                    print(f"已投递 Job Name: {job_name_text}, Company Name: {company_name_text}")

            specific_element = self.page.wait_for_selector('i.ui-icon-arrow-right', timeout=20000)
            if specific_element:
                specific_element.click()

    def close_browser(self):
        self.browser.close()
        self.playwright.__exit__()


if __name__ == "__main__":
    scraper = JobScraper()
    scraper.launch_browser()
    scraper.login_page()
    scraper.input_url()
    scraper.scrape_jobs()
    scraper.close_browser()
