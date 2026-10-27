import requests
import cv2
import numpy as np
import time


def capture_and_save_image(max_attempts=5, delay=1, timeout=10):
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get("http://10.8.4.33:8123/capture", timeout=timeout)
            response.raise_for_status()  # Raise exception for non-200 status codes

            content = response.content
            if not content:
                raise ValueError("Empty response content received.")

            # Validate if it's a valid image
            img_array = np.frombuffer(content, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image content.")

            with open("image.jpg", "wb") as f:
                f.write(content)
            print(f"Image captured and saved successfully on attempt {attempt}.")
            return  # Success, exit the function

        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Failed to capture image after {max_attempts} attempts: {str(e)}"
                )
            time.sleep(delay)  # Wait before retrying


def capture_image(max_attempts=5, delay=1, timeout=10):
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get("http://10.8.4.33:8123/capture", timeout=timeout)
            response.raise_for_status()  # Raise exception for non-200 status codes

            content = response.content
            if not content:
                raise ValueError("Empty response content received.")

            # Validate if it's a valid image
            img_array = np.frombuffer(content, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image content.")

            print(f"Image captured successfully on attempt {attempt}.")
            return content  # Success, return the content

        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Failed to capture image after {max_attempts} attempts: {str(e)}"
                )
            time.sleep(delay)  # Wait before retrying


def main():
    capture_and_save_image()


if __name__ == "__main__":
    main()
