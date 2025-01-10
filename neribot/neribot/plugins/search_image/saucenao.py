from pathlib import Path
from nonebot.log import logger
from .http_utils import AsyncHttpx
from neribot.configs.config import ASUCENAO_API_KEY
from typing import Union, List
import random
from nonebot.adapters.onebot.v11.message import MessageSegment


TEMP_PATH = Path(__file__).parent / "TMP"
API_URL_SAUCENAO = "https://saucenao.com/search.php"
API_URL_ASCII2D = "https://ascii2d.net/search/url/"
API_URL_IQDB = "https://iqdb.org/"


async def get_saucenao_image(url: str) -> Union[str, List[str]]:
    api_key = ASUCENAO_API_KEY
    if not api_key:
        return "Saucenao 缺失API_KEY！"

    params = {
        "output_type": 2,
        "api_key": api_key,
        "testmode": 1,
        "numres": 6,
        "db": 999,
        "url": url,
    }
    data = (await AsyncHttpx.post(API_URL_SAUCENAO, params=params)).json()
    if data["header"]["status"] != 0:
        return f"Saucenao识图失败..status：{data['header']['status']}"
    data = data["results"]
    data = data if len(data) < 3 else data[:3]
    msg_list = []
    index = random.randint(0, 10000)
    if await AsyncHttpx.download_file(
            url, TEMP_PATH / f"saucenao_search_{index}.jpg"
    ):
        msg_list.append(MessageSegment.image(TEMP_PATH / f"saucenao_search_{index}.jpg"))
    for info in data:
        try:
            similarity = info["header"]["similarity"]
            tmp = f"相似度：{similarity}%\n"
            for x in info["data"].keys():
                if x != "ext_urls":
                    tmp += f"{x}：{info['data'][x]}\n"
            try:
                if "source" not in info["data"].keys():
                    tmp += f'source：{info["data"]["ext_urls"][0]}\n'
            except KeyError:
                tmp += f'source：{info["header"]["thumbnail"]}\n'
            msg_list.append(tmp[:-1])
        except Exception as e:
            logger.warning(f"识图获取图片信息发生错误 {type(e)}：{e}")
    return msg_list
