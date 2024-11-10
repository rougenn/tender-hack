from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import process_url  # Импорт вашего process_url

app = FastAPI()

class UrlsRequest(BaseModel):
    urls: List[str]

class UrlResponse(BaseModel):
    url: str
    criteria: List[int]  # Предполагаем, что результат анализа - массив из 6 чисел

@app.post("/process-urls", response_model=List[UrlResponse])
async def process_urls(request: UrlsRequest):
    response = []
    for url in request.urls:
        try:
            _, analysis_results = process_url.process_url(url)
            if isinstance(analysis_results, list) and len(analysis_results) == 6:
                response.append({"url": url, "criteria": analysis_results})
            else:
                response.append({"url": url, "criteria": [0, 0, 0, 0, 0, 0]})  # Заглушка для ошибки
        except Exception as e:
            response.append({"url": url, "criteria": [0, 0, 0, 0, 0, 0]})  # Заглушка для ошибки
    return response
