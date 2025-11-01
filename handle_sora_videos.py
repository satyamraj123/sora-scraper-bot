from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import traceback
import asyncio

WEBSITE = "https://savesora.com/sora-watermark-remover"

#this function goes to this savesora website and scrapes sora video
async def handle_sora_video(video_link: str):
    print(rf'[INFO] Classified {video_link} as SORA !')
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option("prefs", {
        "safebrowsing.enabled": True
    })
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # enable network logs
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    try:
        driver.get(WEBSITE)
        time.sleep(1)

        # Wait for textarea to appear
        textarea = wait.until(EC.presence_of_element_located((By.ID, "link-input")))

        #if the text area appears then copy the video link there
        if textarea:
            print("[SUCCESS] Textarea found !")
            textarea.clear()
            textarea.send_keys(video_link)
            print("[SUCCESS] Textarea filled with video link.")
        else:
            print("[ERROR] Textarea not found — check your selector or frame.")
            raise Exception("Textarea not found !")

        # Wait for the first download button to become clickable (enabled)
        print("[INFO] Waiting for download button to be enabled...")
        wait.until(EC.element_to_be_clickable((By.ID, "download-btn")))
        download_button = driver.find_element(By.ID, "download-btn")
        print("[SUCCESS] First Download button is now enabled, clicking...")
        download_button.click()
        print("[INFO] First Download button clicked wait 3 seconds.")
        time.sleep(1)

        # Wait for video result container to appear
        print("[INFO] Waiting for video result container to appear...")
        wait.until(EC.presence_of_element_located((By.ID, "video-result-container")))
        print("[SUCCESS] Video container appeared.")

        # Wait for final “Download (No Watermark)” button
        print("[INFO] Waiting for final download button to appear...")
        final_btn = wait.until(EC.element_to_be_clickable((By.ID, "download-no-watermark-btn")))
        print("[SUCCESS] Final download button is ready, clicking now.")
        final_btn.click()
        print("[INFO] Final Download button clicked wait 2 seconds.")
        time.sleep(3)
        
        # Fetch network logs and extract downloadable video URL
        logs = driver.get_log("performance")
        video_url = None
        for entry in logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if (msg["method"] == "Page.downloadWillBegin" and "url" in msg["params"].keys()):
                    video_url = msg["params"]["url"]
            except Exception:
                continue
        if not video_url:
            raise Exception("[ERROR] Could not find video URL in network logs.")
        else:
            print("[SUCCESS] Found video URL:", video_url)

        #return downloadable video url
        return video_url
    except Exception as e:
        print(rf"[ERROR] {e}")
        traceback.print_exc()
        return "ERROR"
    finally:

        driver.quit()

