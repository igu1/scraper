import pytest
from unittest.mock import patch

# Attempt to import create_image, handling potential ImportError for local testing vs. environment
try:
    from utils.image import create_image
except ImportError:
    # This path adjustment is sometimes needed if 'utils' is not directly in PYTHONPATH
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from utils.image import create_image

# Test for create_image function
class TestCreateImage:

    @patch('utils.image.GoogleImageCrawler')
    def test_create_image_calls_crawler(self, mock_GoogleImageCrawler):
        # Get the mock instance that GoogleImageCrawler() would return
        mock_crawler_instance = mock_GoogleImageCrawler.return_value

        character_name = "TestCharacter"
        num_images = 5

        create_image(character_name, num_images)

        # Assert that GoogleImageCrawler was initialized correctly
        mock_GoogleImageCrawler.assert_called_once_with(
            storage={"root_dir": f"img/{character_name}"}
        )

        # Assert that the crawl method was called on the instance with the correct arguments
        mock_crawler_instance.crawl.assert_called_once_with(
            keyword=character_name,
            max_num=num_images,
            overwrite=True
        )
