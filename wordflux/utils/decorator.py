
import logging
import functools
import time
from tqdm import tqdm

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def timer(func):
    """Đo thời gian thực thi của function"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger = logging.getLogger(func.__name__.upper())
        logger.info(f"⏱️  {func.__name__.upper()} took {elapsed:.2f}s")
        return result
    return wrapper


def log_errors(func):
    """Bắt và log lỗi một cách đẹp hơn"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__name__)
            logger.error(f"❌ {func.__name__} failed: {e}")
            raise
    return wrapper


def retry(max_attempts=3, delay=1):
    """Tự động retry khi function bị lỗi"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"❌ {func.__name__} failed after {max_attempts} attempts")
                        raise
                    logger.warning(f"⚠️  Attempt {attempt}/{max_attempts} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

def progress_tracker(item_name='items', use_tqdm=True):
    """
    Thanh tiến trình với manual update (dùng khi cần update từng item trong loop)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            
            # Tìm total items
            total = None
            start_idx = 1 if args and hasattr(args[0], '__dict__') else 0
            for arg in args[start_idx:]:
                if isinstance(arg, (list, dict)):
                    total = len(arg)
                    break
            
            if total and use_tqdm:
                logger.info(f"🔄 Processing {total} {item_name}...")
                
                with tqdm(total=total, desc=f"function {func.__name__} is processing {item_name}", 
                         unit=item_name.split()[-1]) as pbar:
                    
                    # Inject progress callback
                    kwargs['progress_callback'] = lambda: pbar.update(1)
                    result = func(*args, **kwargs)
                
                logger.info(f"☑️ Completed {total} {item_name}")
                return result
            
            elif total:
                logger.info(f"🔄 Processing {total} {item_name}...")
                result = func(*args, **kwargs)
                logger.info(f"☑️ Completed {total} {item_name}")
                return result
            
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator