import pytest
from src.url_classifier import URLClassifier


class TestURLClassifierUHQ:
    def test_mega_nz_classified_as_uhq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://mega.nz/file/abc123") == "UHQ"
    
    def test_mediafire_classified_as_uhq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://www.mediafire.com/file/xyz789") == "UHQ"
    
    def test_mega_nz_case_insensitive(self):
        classifier = URLClassifier()
        assert classifier.classify("https://MEGA.NZ/file/abc") == "UHQ"
        assert classifier.classify("https://Mega.Nz/file/abc") == "UHQ"
    
    def test_mediafire_case_insensitive(self):
        classifier = URLClassifier()
        assert classifier.classify("https://MEDIAFIRE.COM/file/xyz") == "UHQ"
        assert classifier.classify("https://MediaFire.com/file/xyz") == "UHQ"


class TestURLClassifierHQ:
    def test_justpaste_classified_as_hq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://justpaste.io/abc123") == "HQ"
    
    def test_google_drive_classified_as_hq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://drive.google.com/file/d/abc123") == "HQ"
        assert classifier.classify("https://google.com/drive/file/abc") == "HQ"
    
    def test_justpaste_case_insensitive(self):
        classifier = URLClassifier()
        assert classifier.classify("https://JUSTPASTE.IO/test") == "HQ"
        assert classifier.classify("https://JustPaste.Io/test") == "HQ"
    
    def test_google_drive_case_insensitive(self):
        classifier = URLClassifier()
        assert classifier.classify("https://DRIVE.GOOGLE.COM/file") == "HQ"
        assert classifier.classify("https://Drive.Google.com/file") == "HQ"
    
    def test_google_without_drive_not_hq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://google.com/search") == "BAD"
    
    def test_drive_without_google_not_hq(self):
        classifier = URLClassifier()
        assert classifier.classify("https://onedrive.com/file") == "BAD"


class TestURLClassifierBAD:
    def test_unknown_domain_classified_as_bad(self):
        classifier = URLClassifier()
        assert classifier.classify("https://example.com/file") == "BAD"
    
    def test_dropbox_classified_as_bad(self):
        classifier = URLClassifier()
        assert classifier.classify("https://dropbox.com/file/abc") == "BAD"
    
    def test_onedrive_classified_as_bad(self):
        classifier = URLClassifier()
        assert classifier.classify("https://onedrive.com/file/xyz") == "BAD"


class TestURLClassifierEdgeCases:
    def test_empty_string_returns_bad(self):
        classifier = URLClassifier()
        assert classifier.classify("") == "BAD"
    
    def test_none_returns_bad(self):
        classifier = URLClassifier()
        assert classifier.classify(None) == "BAD"
    
    def test_uhq_takes_priority_over_hq(self):
        classifier = URLClassifier()
        url_with_both = "https://mega.nz/share/justpaste.io"
        assert classifier.classify(url_with_both) == "UHQ"
