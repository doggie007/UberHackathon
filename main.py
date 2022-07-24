from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import numpy as np
from io import StringIO
from typing import List
import os




def run(input_values):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get("http://climatemodels.uchicago.edu/isam/isam.html")

    # input_values = ["1", "2", "3", "4", "5", "6"]
    input_ids = ["i2015", "i2020", "i2025", "i2050", "i2075", "i2100"]
    for val, input_id in zip(input_values, input_ids):
        el = driver.find_element(By.ID, input_id)
        el.clear()
        try:
            float(val)
            el.send_keys(val)
        except:
            raise Exception("Invalid non float input")

    #Move to another input so model runs and is saved
    driver.find_element(By.ID, "l2015").send_keys("")
    #Wait for page to reload
    time.sleep(3)
    driver.find_element(By.ID, "rawModel").click()
    driver.switch_to.window(driver.window_handles[1])
    file = StringIO(driver.find_element(By.XPATH, "//pre").text)

    lines = file.readlines()

    temperature = []
    for line in lines[715-1:782-1+1]:
        temperature.append(list(map(float, line.split())))
    temperature = np.array(temperature)

    carbon = []
    for line in lines[10-1:77-1+1]:
        carbon.append(list(map(float, line.split())))
    carbon = np.array(carbon)

    years = temperature[:,0]
    temperature = temperature[:, 2]
    carbon = carbon[:, 8]

    return (list(years), list(temperature), list(carbon))




app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/run")
async def run_main(item: List[str]):
    arr = item
    if len(arr) != 6:
        raise HTTPException(status_code=400, detail="Bad request")
    years, temperature, carbon = run(arr)
    return {"years": years, "temperatures": temperature, "carbons": carbon}

