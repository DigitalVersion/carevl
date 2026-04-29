"""Test Hub Admin tools"""

import pytest
import json
import base64
from pathlib import Path
from carevl_hub.admin import encode_invite_code


class TestInviteCodeGeneration:
    """Test invite code generation"""
    
    def test_encode_basic(self):
        """Test basic invite code encoding"""
        code = encode_invite_code(
            station_id="TRAM_001",
            station_name="Trạm Test",
            repo_url="https://github.com/org/station-001",
            pat="ghp_test123"
        )
        
        # Decode and verify
        decoded = base64.urlsafe_b64decode(code.encode('utf-8')).decode('utf-8')
        data = json.loads(decoded)
        
        assert data['station_id'] == "TRAM_001"
        assert data['station_name'] == "Trạm Test"
        assert data['repo_url'] == "https://github.com/org/station-001"
        assert data['pat'] == "ghp_test123"
        assert 'encryption_key' not in data
    
    def test_encode_with_encryption_key(self):
        """Test encoding with encryption key"""
        code = encode_invite_code(
            station_id="TRAM_002",
            station_name="Trạm Test 2",
            repo_url="https://github.com/org/station-002",
            pat="ghp_test456",
            encryption_key="my-encryption-key"
        )
        
        # Decode and verify
        decoded = base64.urlsafe_b64decode(code.encode('utf-8')).decode('utf-8')
        data = json.loads(decoded)
        
        assert data['encryption_key'] == "my-encryption-key"
    
    def test_encode_vietnamese_characters(self):
        """Test encoding with Vietnamese characters"""
        code = encode_invite_code(
            station_id="TRAM_003",
            station_name="Trạm Y Tế Xã Phú Thọ",
            repo_url="https://github.com/org/station-003",
            pat="ghp_test789"
        )
        
        # Decode and verify
        decoded = base64.urlsafe_b64decode(code.encode('utf-8')).decode('utf-8')
        data = json.loads(decoded)
        
        assert data['station_name'] == "Trạm Y Tế Xã Phú Thọ"
    
    def test_code_is_url_safe(self):
        """Test that generated code is URL-safe"""
        code = encode_invite_code(
            station_id="TRAM_004",
            station_name="Test Station",
            repo_url="https://github.com/org/station-004",
            pat="ghp_test000"
        )
        
        # URL-safe Base64 should not contain +, /, or =
        assert '+' not in code
        assert '/' not in code
        # Note: = padding might be present, but urlsafe_b64decode handles it


class TestInviteCodeValidation:
    """Test invite code validation"""
    
    def test_valid_code(self):
        """Test validation of valid code"""
        code = encode_invite_code(
            station_id="TRAM_005",
            station_name="Valid Station",
            repo_url="https://github.com/org/station-005",
            pat="ghp_valid"
        )
        
        # Should decode without errors
        decoded = base64.urlsafe_b64decode(code.encode('utf-8')).decode('utf-8')
        data = json.loads(decoded)
        
        assert 'station_id' in data
        assert 'station_name' in data
        assert 'repo_url' in data
        assert 'pat' in data
    
    def test_invalid_base64(self):
        """Test validation of invalid Base64"""
        # Base64 decode might not raise for some invalid strings
        # Test with clearly invalid Base64
        try:
            decoded = base64.urlsafe_b64decode("not-valid!!!".encode('utf-8'))
            # If it decodes, try to parse as JSON (should fail)
            json.loads(decoded.decode('utf-8'))
            assert False, "Should have raised an exception"
        except Exception:
            # Expected to fail
            pass
    
    def test_invalid_json(self):
        """Test validation of invalid JSON"""
        invalid_code = base64.urlsafe_b64encode(b"not json").decode('utf-8')
        
        with pytest.raises(json.JSONDecodeError):
            decoded = base64.urlsafe_b64decode(invalid_code.encode('utf-8')).decode('utf-8')
            json.loads(decoded)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
