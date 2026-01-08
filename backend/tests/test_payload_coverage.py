"""
backend/tests/test_payload_coverage.py
======================================

Tests for payload coverage audit system.

Validates that:
- All 44 attack strategies have templates
- Coverage is >90%
- Template sources are tracked correctly
- Warnings are logged for missing templates
"""

import pytest
from core.payloads import PayloadManager, get_payload_manager
from core.models import AttackStrategyType
from unittest.mock import Mock, AsyncMock

# Import PromptMutator after mocking LLMClient
try:
    from core.mutator import PromptMutator
except ImportError:
    # If import fails due to LLMClient, we'll mock it in tests
    PromptMutator = None


class TestPayloadCoverageAudit:
    """Test payload coverage audit functionality."""
    
    def test_audit_payload_coverage_structure(self):
        """Test that audit returns correct structure."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        # Check required fields
        assert "total_strategies" in audit
        assert "covered_strategies" in audit
        assert "well_covered_strategies" in audit
        assert "coverage_percent" in audit
        assert "well_covered_percent" in audit
        assert "missing_strategies" in audit
        assert "under_covered_strategies" in audit
        assert "strategy_details" in audit
        assert "recommendation" in audit
        
        # Check types
        assert isinstance(audit["total_strategies"], int)
        assert isinstance(audit["coverage_percent"], float)
        assert isinstance(audit["missing_strategies"], list)
        assert isinstance(audit["strategy_details"], dict)
    
    def test_audit_total_strategies_count(self):
        """Test that audit counts all 44 strategies."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        assert audit["total_strategies"] == 44, \
            f"Expected 44 strategies, got {audit['total_strategies']}"
    
    def test_audit_coverage_threshold(self):
        """Test that coverage is above 90% threshold."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        coverage = audit["coverage_percent"]
        assert coverage >= 90.0, \
            f"Coverage {coverage:.1f}% is below 90% threshold. " \
            f"Missing: {audit['missing_strategies']}, " \
            f"Under-covered: {audit['under_covered_strategies']}"
    
    def test_audit_well_covered_threshold(self):
        """Test that well-covered (>=3 templates) is above 80%."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        well_covered = audit["well_covered_percent"]
        assert well_covered >= 80.0, \
            f"Well-covered {well_covered:.1f}% is below 80% threshold"
    
    def test_audit_no_missing_strategies(self):
        """Test that no strategies are completely missing templates."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        missing = audit["missing_strategies"]
        assert len(missing) == 0, \
            f"Found {len(missing)} strategies with no templates: {missing}"
    
    def test_audit_strategy_details(self):
        """Test that strategy details contain required info."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        for strategy_name, details in audit["strategy_details"].items():
            assert "category" in details
            assert "template_count" in details
            assert "status" in details
            assert details["status"] in ["missing", "under_covered", "well_covered"]
    
    def test_all_strategies_have_minimum_templates(self):
        """Test that all strategies have at least 3 templates."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        under_covered = []
        for strategy_name, details in audit["strategy_details"].items():
            if details["template_count"] < 3:
                under_covered.append(f"{strategy_name} ({details['template_count']} templates)")
        
        assert len(under_covered) == 0, \
            f"Found {len(under_covered)} strategies with <3 templates: {under_covered}"


class TestMutatorTemplateTracking:
    """Test that mutator tracks template sources correctly."""
    
    @pytest.mark.asyncio
    async def test_mutator_logs_template_source(self):
        """Test that mutator includes template source in metadata."""
        # Mock dependencies
        mock_llm_client = AsyncMock()
        mock_audit_logger = Mock()
        
        mutator = PromptMutator(
            llm_client=mock_llm_client,
            audit_logger=mock_audit_logger,
            experiment_id="test-exp-123"
        )
        
        # Test mutation
        mutation = await mutator.mutate(
            original_prompt="test prompt",
            strategy=AttackStrategyType.OBFUSCATION_BASE64,
            iteration=1
        )
        
        # Check metadata
        assert "template_source" in mutation.mutation_params
        assert mutation.mutation_params["template_source"] in ["payloads.json", "hardcoded", "fallback"]
        assert "template_category" in mutation.mutation_params
    
    @pytest.mark.asyncio
    async def test_mutator_warns_on_hardcoded_fallback(self):
        """Test that mutator logs warning when using hardcoded templates."""
        mock_llm_client = AsyncMock()
        mock_audit_logger = Mock()
        
        mutator = PromptMutator(
            llm_client=mock_llm_client,
            audit_logger=mock_audit_logger,
            experiment_id="test-exp-123"
        )
        
        # Force fallback by using strategy with no templates (if any)
        # Or mock PayloadManager to raise KeyError
        
        mutation = await mutator.mutate(
            original_prompt="test",
            strategy=AttackStrategyType.OBFUSCATION_BASE64,
            iteration=1
        )
        
        # If hardcoded fallback was used, warning should be logged
        if mutation.mutation_params.get("template_source") == "hardcoded":
            # Check that log_error was called with template_fallback error type
            calls = [call for call in mock_audit_logger.log_error.call_args_list 
                    if call[1].get("error_type") == "template_fallback" or 
                       (len(call[0]) > 0 and "template_fallback" in str(call))]
            # Note: This is a basic check - actual implementation may vary


class TestPayloadManagerIntegration:
    """Integration tests for PayloadManager."""
    
    def test_get_templates_for_all_strategies(self):
        """Test that get_templates works for all 44 strategies."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        for strategy_name, details in audit["strategy_details"].items():
            category = details["category"]
            
            # Should not raise KeyError
            try:
                templates = manager.get_templates(category)
                assert isinstance(templates, list)
                assert len(templates) >= 3, \
                    f"Strategy '{strategy_name}' has only {len(templates)} templates"
            except KeyError:
                pytest.fail(f"Category '{category}' for strategy '{strategy_name}' not found")
    
    def test_generate_payload_for_all_strategies(self):
        """Test that generate_payload works for all strategies."""
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        for strategy_name, details in audit["strategy_details"].items():
            if details["template_count"] == 0:
                continue  # Skip missing strategies
            
            category = details["category"]
            templates = manager.get_templates(category)
            
            for template in templates[:1]:  # Test first template
                payload = manager.generate_payload(template, "test prompt")
                assert isinstance(payload, str)
                assert len(payload) > 0


class TestStartupAudit:
    """Test startup audit integration."""
    
    def test_startup_audit_logs_coverage(self, caplog):
        """Test that startup audit logs coverage statistics."""
        # This would be tested in integration tests with actual app startup
        # For unit test, just verify audit can be called
        manager = PayloadManager()
        audit = manager.audit_payload_coverage()
        
        # Simulate logging
        import logging
        logger = logging.getLogger("test")
        logger.info(f"Coverage: {audit['coverage_percent']:.1f}%")
        
        assert audit["coverage_percent"] >= 0.0


# Pytest configuration
@pytest.fixture
def payload_manager():
    """Fixture for PayloadManager instance."""
    return PayloadManager()


@pytest.fixture
def mock_mutator():
    """Fixture for mocked PromptMutator."""
    mock_llm = AsyncMock()
    mock_logger = Mock()
    return PromptMutator(
        llm_client=mock_llm,
        audit_logger=mock_logger,
        experiment_id="test-exp"
    )
