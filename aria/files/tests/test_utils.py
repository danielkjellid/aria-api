import pytest

from aria.files.models import BaseImageModel
from aria.files.utils import asset_get_static_upload_path


class TestFilesUtils:
    def test_util_asset_get_static_upload_path(self):
        """
        Test that the asset_get_static_upload_path util correctly throws error and
        that output is as expected.
        """

        model = BaseImageModel

        with pytest.raises(RuntimeError):
            asset_get_static_upload_path(instance=model, filename="filename.jpg")

        model.UPLOAD_PATH = "folder/subfolder"
        path = asset_get_static_upload_path(instance=model, filename="filename.jpg")

        expected_upload_path = "folder/subfolder/filename.jpg"

        assert path == expected_upload_path
