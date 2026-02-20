"""Integration tests for Profile System DI container integration.

Tests that ProfileService and ProfileStorage are correctly wired through DI,
ensuring proper singleton behavior and dependency injection.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.infrastructure.di_container import DIContainer
from src.domain.services.profile_service import ProfileService
from src.infrastructure.storage.profile_storage import ProfileStorage


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def container(temp_data_dir):
    """Create a fresh DI container for each test."""
    container = DIContainer()
    container.reset_all()
    return container


class TestDIProfileIntegration:
    """Test suite for Profile System DI integration."""
    
    def test_profile_storage_is_singleton(self, container):
        """Test that ProfileStorage is created as singleton."""
        # Get storage twice
        storage1 = container.get_profile_storage()
        storage2 = container.get_profile_storage()
        
        # Should be same instance
        assert storage1 is storage2
        assert isinstance(storage1, ProfileStorage)
    
    def test_profile_service_is_singleton(self, container):
        """Test that ProfileService is created as singleton."""
        # Get service twice
        service1 = container.get_profile_service()
        service2 = container.get_profile_service()
        
        # Should be same instance
        assert service1 is service2
        assert isinstance(service1, ProfileService)
    
    def test_profile_service_dependencies_injected(self, container):
        """Test that ProfileService receives correct dependencies via DI."""
        service = container.get_profile_service()
        storage = container.get_profile_storage()
        
        # Service should have storage injected
        assert service.storage is storage
        assert service.aggregator is not None
        
        # Storage should be the singleton instance
        assert isinstance(service.storage, ProfileStorage)
    
    def test_basic_crud_flow_through_di(self, container, temp_data_dir):
        """Test basic CRUD operations work through DI."""
        # Create a service with temp storage
        from src.infrastructure.storage.profile_storage import ProfileStorage
        from src.domain.services.profile_service import ProfileService
        from src.domain.services.stats_aggregator import StatsAggregator
        
        # Create custom instances for temp directory
        storage = ProfileStorage(data_dir=temp_data_dir)
        service = ProfileService(storage=storage, aggregator=StatsAggregator())
        
        # Create profile
        profile = service.create_profile("TestUser", is_guest=False)
        assert profile is not None
        assert profile.profile_name == "TestUser"
        
        # Load profile (sets as active)
        load_success = service.load_profile(profile.profile_id)
        assert load_success is True
        assert service.active_profile is not None
        assert service.active_profile.profile_id == profile.profile_id
        assert service.active_profile.profile_name == "TestUser"
        
        # List profiles
        profiles = service.list_profiles()
        assert len(profiles) == 1
        assert profiles[0]["profile_name"] == "TestUser"
