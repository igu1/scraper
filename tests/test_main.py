import pytest
from unittest.mock import MagicMock, patch, call

# Attempt to import DataGather and WebAccess, handling potential ImportError
try:
    from main import DataGather
    from utils.webAccess import WebAccess # For spec
    # utils.image is imported as 'image' in main.py, so patch target is 'main.image.create_image'
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from main import DataGather
    from utils.webAccess import WebAccess # For spec

class TestDataGather:

    @patch('main.image.create_image') # Correct patch target
    def test_dataGather_get_info_calls_dependencies(self, mock_create_image_func):
        character_name = "TestCharacter"
        data_gatherer = DataGather(character_name)

        # Create a mock WebAccess instance
        # Using spec=WebAccess ensures the mock only has methods available on the real WebAccess
        mock_web_access_instance = MagicMock(spec=WebAccess)
        mock_web_access_instance.searchForSiteInGoogle.return_value = ["http://site1.com", "http://site2.com"]

        data_gatherer.get_info(mock_web_access_instance)

        # Assertions for WebAccess calls
        mock_web_access_instance.searchInGoogle.assert_called_once_with(character_name)
        mock_web_access_instance.searchForSiteInGoogle.assert_called_once_with()

        mock_web_access_instance.extractData.assert_has_calls([
            call("http://site1.com", character_name),
            call("http://site2.com", character_name)
        ], any_order=True)
        assert mock_web_access_instance.extractData.call_count == 2

        # Assertion for create_image call
        mock_create_image_func.assert_called_once_with(character_name, 2) # 2 is hardcoded in main.py


    @patch('main.image.create_image') # Correct patch target
    def test_dataGather_get_info_no_sites_found(self, mock_create_image_func_no_sites):
        character_name_no_sites = "NoSiteChar"
        data_gatherer_no_sites = DataGather(character_name_no_sites)

        mock_web_access_no_sites = MagicMock(spec=WebAccess)
        mock_web_access_no_sites.searchForSiteInGoogle.return_value = [] # No sites found

        data_gatherer_no_sites.get_info(mock_web_access_no_sites)

        # Assertions for WebAccess calls
        mock_web_access_no_sites.searchInGoogle.assert_called_once_with(character_name_no_sites)
        mock_web_access_no_sites.searchForSiteInGoogle.assert_called_once_with()
        mock_web_access_no_sites.extractData.assert_not_called()

        # Assertion for create_image call (should still be called)
        mock_create_image_func_no_sites.assert_called_once_with(character_name_no_sites, 2)
