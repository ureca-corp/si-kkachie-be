"""routes 모델 (backward compatibility)

다른 모듈에서 RouteHistory 모델을 import할 때 사용.
실제 정의는 _models.py에 있음.
"""

from ._models import RouteHistory, get_coords, make_point

__all__ = ["RouteHistory", "get_coords", "make_point"]
