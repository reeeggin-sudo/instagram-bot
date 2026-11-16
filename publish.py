
import os
import time
import requests

TOKEN = os.environ["IG_ACCESS_TOKEN"]
IG_ID = os.environ["IG_USER_ID"]

API_VERSION = "v26.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

VIDEO_URL = (
    "https://reeeggin-sudo.github.io/"
    "instagram-bot/video_fast.mp4"
)

CAPTION = "#nword"


def request_api(method, endpoint, **kwargs):
    response = requests.request(
        method,
        f"{BASE_URL}/{endpoint}",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=60,
        **kwargs
    )

    if not response.ok:
        raise RuntimeError(
            f"API error {response.status_code}: "
            f"{response.text}"
        )

    return response.json()


def create_container():
    result = request_api(
        "POST",
        f"{IG_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": VIDEO_URL,
            "caption": CAPTION,
            "share_to_feed": "true"
        }
    )

    return result["id"]


def wait_until_ready(container_id):
    for attempt in range(30):
        result = request_api(
            "GET",
            container_id,
            params={"fields": "status_code"}
        )

        status = result["status_code"]
        print(f"Processing status: {status}", flush=True)

        if status == "FINISHED":
            return

        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(
                f"Instagram processing failed: {result}"
            )

        if attempt < 29:
            time.sleep(20)

    raise TimeoutError("Video processing timed out")


def publish(container_id):
    result = request_api(
        "POST",
        f"{IG_ID}/media_publish",
        data={"creation_id": container_id}
    )

    return result["id"]


def main():
    print("Starting daily Instagram upload...", flush=True)

    container_id = create_container()
    print(f"Container created: {container_id}", flush=True)

    wait_until_ready(container_id)

    media_id = publish(container_id)

    print(f"Successfully published: {media_id}", flush=True)


if __name__ == "__main__":
    main()
