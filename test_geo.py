import sys
import logging

logging.basicConfig(level=logging.INFO)

from api.geo_utils import get_coordinates

def test_without_mmdb():
    print("Testing without mmdb...")
    # This should use GEO_MOCK and log a warning
    coords = get_coordinates("185.15.2.22")
    print("Without mmdb:", coords)
    
if __name__ == "__main__":
    test_without_mmdb()
