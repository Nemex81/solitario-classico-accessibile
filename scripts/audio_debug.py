import sys, os
sys.path.insert(0, os.getcwd())  # ensure workspace root in path
from src.infrastructure.di.dependency_container import DependencyContainer
am = DependencyContainer().get_audio_manager()
print('available', getattr(am,'is_available',None))
try:
    cache = am.sound_cache._cache
    print('cache items', list(cache.keys()))
except Exception as e:
    print('cache error', e)
