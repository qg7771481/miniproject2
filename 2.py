from fastapi import FastAPI, Query, HTTPException
import httpx
from bs4 import BeautifulSoup

app = FastAPI()


@app.get("/parse")
async def parse_page(url: str = Query(..., description="сторінка для парсингу")):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="url має починит ися")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Помилка при запиті: {e}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Не вдалося отримати сторінку")

    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    developer_tag = soup.find("th", string="Developer")
    os_tag = soup.find("th", string="Operating system")
    license_tag = soup.find("th", string="License")

    def extract_value(th_tag):
        return th_tag.find_next_sibling("td").get_text(strip=True) if th_tag else None

    developer = extract_value(developer_tag)
    os = extract_value(os_tag)
    license_ = extract_value(license_tag)

    return {
        "Developer": developer,
        "OS": os,
        "License": license_
    }
