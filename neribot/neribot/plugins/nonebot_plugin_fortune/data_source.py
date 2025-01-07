from pathlib import Path
from typing import Union
from .utils import drawing
class FortuneManager:
    @staticmethod
    async def divine(gid: str, uid: str, is_today_fortuned: bool,
                custom_title: Union[str, None], custom_text: Union[str, None]):
        """
        今日运势抽签
        """
        if is_today_fortuned:
            img_path: Path = Path(__file__).parent / "resource" / "out" / f"{gid}_{uid}.png"
            return img_path, None
        else:
            try:
                img_path, card = drawing(gid, uid, custom_title, custom_text)
            except (FileNotFoundError, ValueError) as e:
                return None, None
            return img_path, card
        

    @staticmethod
    async def clean_out_pics() -> None:
        """
        Clean all the pictures saved at yesterday.
        """
        dirPath: Path = Path(__file__).parent / "resource" / "out"
        for pic in dirPath.iterdir():
            pic.unlink()


fortune_manager = FortuneManager()
