from .user import User
from .animal import Animal
# __init__.py로 인해 models 외부(create_table.py)에서 from models.animal.animalModel import Animal 가 아닌 from models import Animal와 같이 접근 가능