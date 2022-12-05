"""
    Start/Stop mining on an S9 running Braiins OS
"""
import requests
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


class BraiinsS9:
    def __init__(self, ip_address="192.168.1.100", username="root", password="admin"):
        """
        Set up a logged in requests.Session for status calls.

        Set up a logged in webdriver.Chrome headless instance to enable/disable hashboards
        """
        self.ip_address = ip_address
        self.session = requests.Session()
        data = dict(luci_username=username, luci_password=password)
        res = self.session.post(f"http://{ip_address}/cgi-bin/luci/", data=data)
        if res.status_code != 200:
            raise Exception(f"ERROR: status_code: {res.status_code}")

        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.service = Service('/usr/lib/chromium-browser/chromedriver')
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.get(f"http://{ip_address}/cgi-bin/luci")

        el_username = self.driver.find_element(By.NAME, "luci_username")
        el_username.clear()
        el_username.send_keys(username)
        el_password = self.driver.find_element(By.NAME, "luci_password")
        el_password.clear()
        el_password.send_keys(password)
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()


    def quit(self):
        self.driver.quit()
        self.service.stop()
        self.display.stop()


    def __del__(self):
        self.quit()


    def build_mining_config(self, board_1: bool = True, board_2: bool= True, board_3: bool = True):
        self.driver.get(f"http://{self.ip_address}/cgi-bin/luci/admin/miner/config")

        speed = self.driver.find_element(By.NAME, 'speed').get_attribute("value")
        if speed == '':
            speed = 20
        else:
            speed = int(speed)

        return {
            "data":{
                "hash_chain":{
                    "6":{
                        "enabled": board_1
                    },
                    "7":{
                        "enabled": board_2
                    },
                    "8":{
                        "enabled": board_3
                    }
                },
                "temp_control":{
                    "target_temp": int(self.driver.find_element(By.NAME, 'target_temp').get_attribute("value")),
                    "hot_temp": int(self.driver.find_element(By.NAME, 'hot_temp').get_attribute("value")),
                    "dangerous_temp": int(self.driver.find_element(By.NAME, 'dangerous_temp').get_attribute("value"))
                },
                "fan_control":{
                    "speed": speed,
                    "min_fans": int(self.driver.find_element(By.NAME, 'min_fans').get_attribute("value"))
                },
                "group":[
                    {
                        "name": self.driver.find_element(By.NAME, 'name').get_attribute("value"),
                        "pool":[
                            {
                                "enabled": True,
                                "url": self.driver.find_element(By.NAME, 'url').get_attribute("value"),
                                "user": self.driver.find_element(By.NAME, 'user').get_attribute("value"),
                                "password": self.driver.find_element(By.NAME, 'password').get_attribute("value")
                            }
                        ]
                    }
                ],
                "autotuning":{
                    # "enabled": False,   # Assume we've already let autotune run its full course
                    "enabled": True,
                    "psu_power_limit": int(self.driver.find_element(By.NAME, 'psu_power_limit').get_attribute("value"))
                },
                "power_scaling":{
                    "enabled": True,
                    "power_step": int(self.driver.find_element(By.NAME, 'power_step').get_attribute("value"))
                }
            }
        }


    @property
    def is_mining(self):
        res = self.session.get(f"http://{self.ip_address}/cgi-bin/luci/admin/miner/api_status/")
        cur_hashrate = res.json()["summary"][0]["SUMMARY"][0]["MHS 5s"]
        return cur_hashrate > 0.0


    def start_mining(self, board_1: bool = True, board_2: bool= True, board_3: bool = True):
        """ Enable the hashboards """
        # Must populate the full json POST data built from all the fields on the page
        data = self.build_mining_config(board_1, board_2, board_3)
        res = self.session.post(url=f"http://{self.ip_address}/cgi-bin/luci/admin/miner/cfg_save/", json=data)

        # Must send a GET request to `cfg_apply` to apply the changes
        self.session.get(f"http://{self.ip_address}/cgi-bin/luci/admin/miner/cfg_apply/")


    def stop_mining(self):
        """ Disable the hashboards """
        # Must populate the full json POST data built from all the fields on the page
        data = self.build_mining_config(False, False, False)
        res = self.session.post(url=f"http://{self.ip_address}/cgi-bin/luci/admin/miner/cfg_save/", json=data)

        # Must send a GET request to `cfg_apply` to apply the changes
        self.session.get(f"http://{self.ip_address}/cgi-bin/luci/admin/miner/cfg_apply/")
